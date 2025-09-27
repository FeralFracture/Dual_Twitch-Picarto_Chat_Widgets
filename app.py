from flask import Flask, render_template
from flask_socketio import SocketIO
import config.config as config
from python_scripts.picarto_tools import PicartoConnector, PicartoMsgListener
from python_scripts.twitch_tools import TwitchConnector, TwitchMsgListener

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")
global_badges = {}  # Stores global badge info


# ---------- Flask Routes ----------
@app.route("/chat/twitch")
def twitchChat():
    return render_template("twitch_chat.html")


@app.route("/chat/picarto")
def picartoChat():
    return render_template("picarto_chat.html")

config.reload_config()

# Setup connectors
twitchConnector = TwitchConnector()
twitchListener = TwitchMsgListener(socketio, twitchConnector.global_badges)
twitchConnector.add_listener(twitchListener)
twitchConnector.start()

picartoConnector = PicartoConnector()
picartoListener = PicartoMsgListener(socketio)
picartoConnector.add_listener(picartoListener)
picartoConnector.start()

if __name__ == "__main__":
    socketio.run(app, debug=False, use_reloader=False, host="0.0.0.0", port=config.PORT)
