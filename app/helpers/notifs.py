"""sends a notification to discord"""
# standard library imports
import os

# external library imports
import requests

def send_message_on_discord(message: str) -> None:
    if (discord_server_webhook_url := os.getenv('DISCORD_URL', None)):
        requests.post(
            url=discord_server_webhook_url,
            json={"content": message},
            headers={"Content-Type": "application/json"}
        )
    else:
        print(message)
