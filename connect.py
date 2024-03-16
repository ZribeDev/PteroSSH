import asyncio
import json
import requests
import sys
from aioconsole import ainput, aprint
import websockets

CONFIG_FILE = 'config.json'

def load_or_create_config():
    try:
        with open(CONFIG_FILE, 'r') as file:
            config = json.load(file)
        if 'api_key' not in config or 'panel_url' not in config:
            raise ValueError("Invalid config: 'api_key' or 'panel_url' is missing.")
    except (FileNotFoundError, ValueError):
        api_key = input('Enter your Pterodactyl API key: ')
        panel_url = input('Enter the Pterodactyl panel URL: ')
        config = {'api_key': api_key, 'panel_url': panel_url}
        with open(CONFIG_FILE, 'w') as file:
            json.dump(config, file)
    return config

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
    
    print(f"Connecting to WebSocket at {socket_url}")
    try:
        async with websockets.connect(socket_url) as websocket:
            print(f"Connected to WebSocket")
            await websocket.send(json.dumps({"event": "auth", "args": [token]}))

            async def send_commands():
                while True:
                    command = await ainput("")
                    await websocket.send(json.dumps({"event": "send command", "args": [command]}))
                    
            async def receive_messages():
                global ignoreafter
                while True:
                    message = await websocket.recv()
                    message_data = json.loads(message)
                    if message_data.get("event") == "console output":
                        await aprint(f"Console Output: {list(message_data.get('args'))[0]}")

                    #elif message_data.get("event") == "stats":
                    #    await aprint(f"Stats: {message_data.get('args')}")
                    #else:
                    #    await aprint(f"Message: {message}")

            sender_task = asyncio.create_task(send_commands())
            receiver_task = asyncio.create_task(receive_messages())

            await asyncio.gather(sender_task, receiver_task)
    except websockets.exceptions.WebSocketException as e:
        if e.status_code == 403:
            print("")
            print("")
            print("Failed to connect to Web Socket.")
            print("")
            print("If you are a server owner, you need to follow the guide on our GitHub repo: https://github.com/ZribeDev/PteroSSH\n\n"
                  "If you are a client, please contact your provider.")
def main():
    if len(sys.argv) != 2:
        print("Usage: connect.py <server_id>")
        return

    server_id = sys.argv[1]
    config = load_or_create_config()
    api_key = config['api_key']
    panel_url = config['panel_url']

    token, socket_url = get_websocket_details(panel_url, server_id, api_key)

    asyncio.run(interact_with_websocket(socket_url, token))

if __name__ == '__main__':
    main()
