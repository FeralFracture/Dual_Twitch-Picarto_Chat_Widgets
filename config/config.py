import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "data.json")

TWITCH_CHAT_OAUTH = None
CLIENT_ID = None
CLIENT_SECRET = None
REFRESH_TOKEN = None
TWITCH_USERNAME = None
TWITCH_CHANNEL = None
PORT = None

def reload_config():
    global TWITCH_CHAT_OAUTH, CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN, TWITCH_USERNAME, TWITCH_CHANNEL, PORT
    with open(CONFIG_PATH, "r") as f:
        data = json.load(f)

    TWITCH_CHAT_OAUTH = data["twitch"]["oauth_tkn"]
    CLIENT_ID = data["twitch"]["client_id"]
    CLIENT_SECRET = data["twitch"]["client_secret"]
    REFRESH_TOKEN = data["twitch"]["refresh_tkn"]
    TWITCH_USERNAME = data["twitch"]["username"]
    TWITCH_CHANNEL = data["twitch"]["channel"]
    PORT = data["flask"]["port"]

def refresh_twitch_tokens(oauth_tkn,refresh_tkn):
    # Load current data
    with open(CONFIG_PATH, "r") as f:
        data = json.load(f)
    
    data["twitch"]["oauth_tkn"] = oauth_tkn
    data["twitch"]["refresh_tkn"] = refresh_tkn
    
    with open(CONFIG_PATH, "w") as f:
        json.dump(data, f, indent=4)

    reload_config()

    return True