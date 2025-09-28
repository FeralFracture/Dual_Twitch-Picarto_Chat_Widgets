# connector.py
import websocket
import threading
import time
import requests
import config.config as config
from python_scripts.abstract_classes import Connector, MessageListener
from python_scripts.twitch_message_handler import handle_message


class TwitchConnector(Connector):
    def __init__(self):
        self.listeners = []
        self.global_badges = {}

    def add_listener(self, listener: MessageListener):
        self.listeners.append(listener)

    def notify_listeners(self, message: str):
        for listener in self.listeners:
            listener.on_message(message)

    def refresh_oauth_tokens(self):
        url = "https://id.twitch.tv/oauth2/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "client_id": config.CLIENT_ID,
            "client_secret": config.CLIENT_SECRET,
            "grant_type": "refresh_token",
            "refresh_token": config.REFRESH_TOKEN,  
        }

        res = requests.post(url, headers=headers, data=data)
        if res.ok:
            tokens = res.json()
            # Update file and reload globals
            config.refresh_twitch_tokens(tokens["access_token"], tokens["refresh_token"])
        else:
            print("Failed to refresh tokens:", res.status_code, res.text)


    def fetch_global_badges(self):
        url = "https://api.twitch.tv/helix/chat/badges/global"
        headers = {
            "Authorization": f"Bearer {config.TWITCH_CHAT_OAUTH}",
            "Client-Id": config.CLIENT_ID,
        }
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            data = res.json()
            self.global_badges = {
                badge_set["set_id"]: {
                    version["id"]: {
                        "image1x": version["image_url_1x"],
                        "title": version["title"],
                    }
                    for version in badge_set["versions"]
                }
                for badge_set in data["data"]
            }
        elif res.status_code == 401:
            print("refreshing OAuth Token...")
            self.refresh_oauth_tokens()
            

    def start(self):
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        while True:
            try:
                self.fetch_global_badges()
                ws = websocket.WebSocket()
                ws.connect("wss://irc-ws.chat.twitch.tv:443")
                ws.send(
                    "CAP REQ :twitch.tv/tags twitch.tv/commands twitch.tv/membership"
                )
                ws.send(f"PASS oauth:{config.TWITCH_CHAT_OAUTH}")
                ws.send(f"NICK {config.TWITCH_USERNAME}")
                ws.send(f"JOIN #{config.TWITCH_CHANNEL}")
                print("Connecting to Twitch IRC...")

                while True:
                    msg = ws.recv()
                    if msg.startswith("PING"):
                        ws.send("PONG :tmi.twitch.tv")
                    # elif "PRIVMSG" in msg:
                    else:
                        self.notify_listeners(msg)

            except Exception as e:
                print("Twitch WebSocket error:", e)
                time.sleep(5)


class TwitchMsgListener(MessageListener):
    def __init__(self, socketio, global_badges):
        self.socketio = socketio
        self.global_badges = global_badges

    def on_message(self, message: str):
        handle_message(message, self.socketio, self.global_badges)
