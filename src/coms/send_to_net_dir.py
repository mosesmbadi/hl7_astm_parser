from decouple import config
from smb.SMBConnection import SMBConnection


'''
Let's try to send test request in ASTM format to HumaStar 100/200 (or pretty much any equipment that uses the Network shared folders set up)

'''
def send_to_network_folder(
        data: str,
        host=config("NETWORK_EQUIPMENT_IP"),
        username= config("NETWORK_USERNAME"),
        password= config("NETWORK_USER_PASSWORD"),
        shared_folder= config("NETWORK_INPUT_WORKLIST_FILE"),
        ):
    try:
        if not data:
            raise ValueError("Data is null")

        if not host:
            raise ValueError("Host is null")

        if not username:
            raise ValueError("Username is null")

        if not password:
            raise ValueError("Password is null")

        if not shared_folder:
            raise ValueError("Shared folder is null")

        # Attempt SMB connection
        smb_success = send_over_smb(data, host, username, password, shared_folder)
        if smb_success:
            return True

    except Exception as e:
        import traceback

        print("An exception occurred in send_to_network_folder:")
        print(traceback.format_exc())

def send_over_smb(data: str, host, username, password, shared_folder, filename):
    try:
        conn = SMBConnection(username, password, '', '')
        conn.connect(host)

        with conn:
            # Construct the full file path
            full_filepath = f"{shared_folder}/{filename}" 

            with conn.open_file(full_filepath, 'w') as file:
                file.write(data)
                print(f"Sending over SMB to {full_filepath}: {data}")

        return True
    except Exception as e:
        print("SMB Connection failed:", e)
        return False