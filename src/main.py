import signal
import socket
import logging
import threading
from decouple import config
from utils.utils import handle_client_connection

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def main():
    host = config('HOST', default='0.0.0.0')
    port = config('HOST_PORT', default=9091, cast=int)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen()

        print(f"Listening for incoming connections on {host}:{port}...")

        while True:
            try:
                connection, address = server_socket.accept()
                logger.info(f"Connection established from: {address}")
                # Analyzers can hold their connection open, so give each
                # one its own thread instead of blocking the others.
                threading.Thread(
                    target=handle_client_connection,
                    args=(connection, address),
                    daemon=True
                ).start()

            except Exception as e:
                print(f"Exception while accepting incoming connection: {e}")



def signal_handler(signal, frame):
    print("Terminating process...")
    exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    main()
