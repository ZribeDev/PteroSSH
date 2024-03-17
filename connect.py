import asyncio
import json
import requests
import sys
from aioconsole import ainput, aprint
import websockets
from datetime import datetime
from colorama import init,Fore,Back
init(autoreset=True)
def log_positive(txt):
    now = datetime.now()
    dt_string = now.strftime("%H:%M:%S")
    print(f"{Fore.LIGHTBLACK_EX + dt_string} ({Fore.CYAN}+{Fore.LIGHTBLACK_EX}){Fore.CYAN} {txt}")
def log_negative(txt):
    now = datetime.now()
    dt_string = now.strftime("%H:%M:%S")
    print(f"{Fore.LIGHTBLACK_EX + dt_string} ({Fore.RED}-{Fore.LIGHTBLACK_EX}){Fore.RED} {txt}")
def log_normal(txt):
    now = datetime.now()
    dt_string = now.strftime("%H:%M:%S")
    print(f"{Fore.LIGHTBLACK_EX + dt_string} ({Fore.LIGHTBLUE_EX}~{Fore.LIGHTBLACK_EX}){Fore.LIGHTBLUE_EX} {txt}")

CONFIG_FILE = 'config.json'

def load_or_create_config():
    try:
        with open(CONFIG_FILE, 'r') as file:
            config = json.load(file)
        if 'api_key' not in config or 'panel_url' not in config or 'hide_original_response' not in config:
            raise ValueError("Invalid config: 'api_key' or 'panel_url' is missing.")
    except (FileNotFoundError, ValueError):
        api_key = input('Enter your Pterodactyl API key: ')
        panel_url = input('Enter the Pterodactyl panel URL: ')
        panel_url = panel_url[:-1] if panel_url.endswith('/') else panel_url
        config = {'api_key': api_key, 'panel_url': panel_url, 'hide_original_response': True}
        with open(CONFIG_FILE, 'w') as file:
            json.dump(config, file)
    return config
last_command = ''
config = load_or_create_config()
hidelastcmd = config['hide_original_response']
def get_websocket_details(panel_url, server_id, api_key):
    url = f"{panel_url}/api/client/servers/{server_id}/websocket"
    headers = {"Authorization": f"Bearer {api_key}", "Accept": "application/json", "Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()['data']
        return data['token'], data['socket']
    else:
        raise Exception("Failed to get WebSocket details from the API")

async def interact_with_websocket(socket_url, token):
    global last_command, hidelastcmd
    log_normal(f"Connecting to WebSocket at {socket_url}")
    try:
        async with websockets.connect(socket_url) as websocket:
            log_positive(f"Connected to WebSocket")
            await websocket.send(json.dumps({"event": "auth", "args": [token]}))

            async def send_commands():
                global hidelastcmd, last_command
                while True:
                    command = await ainput("")
                    last_command = command
                    await websocket.send(json.dumps({"event": "send command", "args": [command]}))
                    
            async def receive_messages():
                global ignoreafter, hidelastcmd, last_command
                while True:
                    message = await websocket.recv()
                    message_data = json.loads(message)
                    if message_data.get("event") == "console output":
                        if (hidelastcmd):
                            if not (list(message_data.get('args'))[0] == last_command):
                                await aprint(f"{list(message_data.get('args'))[0]}")
                                last_command = ''
                            continue
                        else:
                            await aprint(f"{list(message_data.get('args'))[0]}")

                    #elif message_data.get("event") == "stats":
                    #    await aprint(f"Stats: {message_data.get('args')}")
                    #else:
                    #    await aprint(f"Message: {message}")

            sender_task = asyncio.create_task(send_commands())
            receiver_task = asyncio.create_task(receive_messages())

            await asyncio.gather(sender_task, receiver_task)
    except websockets.exceptions.WebSocketException as e:
        if e.status_code == 403:
            log_negative("\nFailed to connect to Web Socket.\n")
            log_negative("If you are a server owner, you need to follow the guide on our GitHub repo: https://github.com/ZribeDev/PteroSSH")
            log_negative("\nIf you are a client:")
            log_negative("* Your provider might not have set up PteroSSH correctly.")
            log_negative("* You might not have the correct permissions to the selected server.")
            
    
def main():
    if len(sys.argv) != 2:
        print("Usage: connect.py <server_id>")
        return

    server_id = sys.argv[1]
    config = load_or_create_config()
    api_key = config['api_key']
    panel_url = config['panel_url']

    try:
        token, socket_url = get_websocket_details(panel_url, server_id, api_key)
    except Exception as e:
        log_negative(f"An error occurred: {e}")
        if "Failed to get WebSocket details from the API" in str(e):
            log_negative("Failed to obtain WebSocket details from the API.")
            log_negative("Please check if the API key is correct and has the necessary permissions.")
            log_negative("Also, ensure the panel URL and server ID are correct.")
        return
    asyncio.run(interact_with_websocket(socket_url, token))

if __name__ == '__main__':
    main()
