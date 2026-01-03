import json
import os
from src.server import UDPServer

CONFIG_PATH = os.path.join("config", "server.conf.json")

def load_config():
    try:
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Critical: Config file not found at {CONFIG_PATH}")
        exit(1)

def main():
    config = load_config()
    
    server = UDPServer(
        host=config["host"],
        port=config["port"]
    )
    
    server.start()

if __name__ == "__main__":
    main()