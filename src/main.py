import signal
import json

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from coms.send_to_equipment import process_json_data
from coms.send_results_to_lis import send_to_lab_endpoints

from converters.astm_to_json import convert_astm_to_json
from converters.hl7_to_json import convert_hl7_to_json


app = FastAPI()


@app.post("/")
async def receive_data(request: Request):
    try:
        decoded_data = await request.body()
        decoded_data = decoded_data.decode('utf-8')
        print(f"Decoded data is : {decoded_data} ")
        response_msg = f"Data received: {decoded_data}"

        # Check if incoming data is HL7
        if decoded_data.startswith('MSH'):
            converted_data = convert_hl7_to_json(decoded_data)
            print(f'Converted HL7 to JSON: {converted_data}')
            for test_result in converted_data:
                send_to_lab_endpoints(converted_data, 'hl7')

        # Check if incoming data is ASTM
        elif decoded_data.startswith('H|'):
            astm_message_dict = convert_astm_to_json(decoded_data)
            print(f'Converted ASTM to JSON: {astm_message_dict}')
            send_to_lab_endpoints(astm_message_dict, 'astm')
            
        # TODO: Find a more robust way to check for JSON, probably with a library
        # Check if incoming data is JSON
        elif decoded_data.startswith('{'):
            print("Processing incoming JSON data...")
            try:
                json_data = json.loads(decoded_data)
                process_json_data(json_data)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON data: {e}")
                return JSONResponse(content={"error": str(e)}, status_code=400)
        return JSONResponse(content={"message": response_msg})
    except Exception as e:
        print(f"Exception: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)


def signal_handler(signal, frame):
    print("Terminating process...")
    exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    uvicorn.run("src.main:app", host="0.0.0.0", port=9091, reload=True)