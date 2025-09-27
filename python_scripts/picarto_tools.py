import threading
import subprocess
import json
from python_scripts.abstract_classes import Connector, MessageListener

class PicartoConnector(Connector):
    def __init__(self):
        self.listeners = []
        
    def add_listener(self, listener: MessageListener):
        self.listeners.append(listener)

    def notify_listeners(self, message):
        for listener in self.listeners:
            listener.on_message(message)

        # Function to start the Node bot
    def _run(self):
    # Launch the Node bot
        process = subprocess.Popen(
            ["node", "bot/bot.js"],  # just call node directly
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
    )

        for line in process.stdout:
            line = line.strip()
            if not line:
                continue
            try:
                # Node can emit JSON for each message
                message = json.loads(line)
                self.notify_listeners(message)
            except json.JSONDecodeError:
                print("[Node]", line)

    def start(self):
        threading.Thread(target=self._run, daemon=True).start()



class PicartoMsgListener(MessageListener):
    def __init__(self, socketio):
        self.socketio = socketio

    def on_message(self, message):
        self.socketio.emit("Picarto_chat_message", message)
    
