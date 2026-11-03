import json
import logging
from datetime import datetime
from coms.process_json_data import process_json_data
from converters.astm_to_json import convert_astm_to_json
from converters.hl7_to_json import convert_hl7_to_json
from coms.send_results_to_lis import send_to_lab_endpoints

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ASTM E1381 control characters
ENQ = b'\x05'
ACK = b'\x06'
NAK = b'\x15'
STX = b'\x02'
ETX = b'\x03'
ETB = b'\x17'
EOT = b'\x04'

# HL7 MLLP framing
MLLP_START = b'\x0b'
MLLP_END = b'\x1c\r'


def send_response(connection, message):
    """Sends a response message back to the client."""
    try:
        connection.sendall(message.encode('utf-8'))
    except Exception as e:
        print(f"Error sending response: {e}")


def describe(runs):
    """'2 run(s): DDLR00012-2026 (35 results), ...' -- no patient details."""
    parts = [f"{run['sample_id'] or 'no sample code'} ({len(run['results'])} results)" for run in runs]
    return f"{len(runs)} run(s): {', '.join(parts)}" if runs else "no results"


def process_full_data(decoded_data, connection, address):
    """
    Process one complete message from an analyzer.

    Returns True when its results are safe -- stored by EasyMed, or spooled
    for retry -- and False when the message could not be read at all.
    """
    try:
        logger.info(f"Processing full data from {address}")
        logger.debug(f"Raw message from {address}: {decoded_data!r}")

        # Check if incoming data is HL7
        if "MSH" in decoded_data:
            try:
                runs = convert_hl7_to_json(decoded_data)
            except Exception as e:
                logger.error(f"Could not read HL7 message: {e}. Raw: {decoded_data!r}", exc_info=True)
                return False
            logger.info(f"Read HL7 message from {address}: {describe(runs)}")
            send_to_lab_endpoints(runs, decoded_data, 'hl7')
            return True

        # Check if incoming data is ASTM
        elif decoded_data.lstrip().startswith('H|'):
            try:
                runs = convert_astm_to_json(decoded_data)
            except Exception as e:
                logger.error(f"Could not read ASTM message: {e}. Raw: {decoded_data!r}", exc_info=True)
                return False
            logger.info(f"Read ASTM message from {address}: {describe(runs)}")
            send_to_lab_endpoints(runs, decoded_data, 'astm')
            return True

        # Check if incoming data is JSON
        elif '{' in decoded_data:
            logger.debug("Detected JSON data.")
            try:
                json_start = decoded_data.find('{')
                json_part = decoded_data[json_start:]

                json_objects = []
                while '{' in json_part:
                    json_end = json_part.find('}') + 1
                    json_object = json_part[:json_end]
                    json_objects.append(json_object)
                    json_part = json_part[json_end:]

                for json_object in json_objects:
                    try:
                        json_data = json.loads(json_object, strict=False)
                        logger.info(f"Processing JSON data: {json_data}")
                        process_json_data(json_data)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Error decoding JSON data: {e}")

            except json.JSONDecodeError as e:
                logger.warning(f"Error decoding JSON data: {e}")

    except Exception as e:
        logger.error(f"Unexpected error processing data: {e}", exc_info=True)
        return False

    return True


def checksum_ok(frame):
    """frame runs from the frame number through ETX/ETB, then two hex checksum chars."""
    expected = sum(frame[:-2]) % 256
    return frame[-2:].upper() == f"{expected:02X}".encode()


def build_hl7_ack(hl7_message, code='AA'):
    """
    Builds an MLLP-wrapped ACK for the message's control ID (MSH-10).
    AA once the results are safe (stored or spooled), AE when the message
    could not be read, so the analyzer flags it instead of assuming success.
    """
    msh = hl7_message.split('\r')[0].split('|')
    control_id = msh[9] if len(msh) > 9 else ''
    version = msh[11] if len(msh) > 11 else '2.3.1'
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    ack = (
        f"MSH|^~\\&|LIS||{msh[2] if len(msh) > 2 else ''}||{timestamp}||ACK^R01|{control_id}|P|{version}\r"
        f"MSA|{code}|{control_id}\r"
    )
    return MLLP_START + ack.encode('utf-8') + MLLP_END


def handle_client_connection(connection, address):
    """
    Reads from an analyzer until it disconnects. Handles:
    - ASTM E1381: ENQ, then STX frames each ACKed, then EOT
    - HL7 over MLLP: <VT>message<FS><CR>, answered with an HL7 ACK
    - Unframed data (the test scripts in ./coms), processed when the peer closes
    """
    buffer = b''
    astm_frames = []

    try:
        while True:
            received_data = connection.recv(4096)
            if not received_data:
                break
            buffer += received_data

            while buffer:
                first = buffer[:1]

                if first == ENQ:
                    logger.info(f"Received ENQ from {address}, sending ACK")
                    connection.sendall(ACK)
                    astm_frames = []
                    buffer = buffer[1:]

                elif first == EOT:
                    logger.info(f"Received EOT from {address}")
                    if astm_frames:
                        astm_message = b''.join(astm_frames).decode('utf-8', errors='ignore')
                        process_full_data(astm_message, connection, address)
                    astm_frames = []
                    buffer = buffer[1:]

                elif first == STX:
                    end = min((i for i in (buffer.find(ETX), buffer.find(ETB)) if i != -1), default=-1)
                    # Wait for <ETX|ETB> C1 C2 <CR> <LF>
                    if end == -1 or len(buffer) < end + 5:
                        break
                    frame = buffer[1:end + 3]
                    if checksum_ok(frame):
                        # Drop the frame number and the ETX/ETB + checksum
                        astm_frames.append(frame[1:-3])
                        connection.sendall(ACK)
                    else:
                        logger.warning(f"Bad ASTM checksum from {address}, sending NAK")
                        connection.sendall(NAK)
                    buffer = buffer[end + 5:]

                elif first == MLLP_START:
                    end = buffer.find(MLLP_END)
                    if end == -1:
                        break
                    hl7_message = buffer[1:end].decode('utf-8', errors='ignore')
                    buffer = buffer[end + len(MLLP_END):]
                    accepted = process_full_data(hl7_message, connection, address)
                    connection.sendall(build_hl7_ack(hl7_message, 'AA' if accepted else 'AE'))

                elif first in (b'\r', b'\n', b' '):
                    buffer = buffer[1:]

                else:
                    # Unframed data; wait for the peer to close
                    break

        if buffer.strip():
            process_full_data(buffer.decode('utf-8', errors='ignore'), connection, address)

    except Exception as e:
        logger.error(f"Error handling client connection: {e}", exc_info=True)

    finally:
        connection.close()
        logger.info(f"Connection closed: {address}")
