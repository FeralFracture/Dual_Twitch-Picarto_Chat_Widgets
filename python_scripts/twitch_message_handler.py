from dataclasses import dataclass, field
from typing import Dict, List
from collections import deque

message_history = deque(maxlen=100)

@dataclass
class TwitchMessage:
    username: str
    display_name: str
    color: str
    badges: Dict[str, str] = field(default_factory=dict)
    message: str = ""
    user_id: str = ""
    mod: bool = False
    subscriber: bool = False
    timestamp: int = 0
    emotes: List[str] = field(default_factory=list)

def parse_twitch_message(raw: str) -> TwitchMessage:
        tags_part, rest = raw.split(" ", 1)
        tags = dict(tag.split("=") for tag in tags_part.lstrip("@").split(";") if "=" in tag)

        prefix, command, channel, message = rest.split(" ", 3)
        message = message.lstrip(":").strip()

        username = prefix.split("!")[0]

        badges = {}
        for badge in tags.get("badges", "").split(","):
            if "/" in badge:
                k, v = badge.split("/")
                badges[k] = v

        return TwitchMessage(
            username=username,
            display_name=tags.get("display-name", username),
            color=tags.get("color", "#FFFFFF"),
            badges=badges,
            message=message,
            user_id=tags.get("user-id", ""),
            mod=tags.get("mod") == "1",
            subscriber=tags.get("subscriber") == "1",
            timestamp=int(tags.get("tmi-sent-ts", 0))
        )
        


def handle_message(message: str, socketio, global_badges):
    try:
#        print(message)
        if "PRIVMSG" in message:
            msg_obj = parse_twitch_message(message)
            badge_html = ""
            for badge_set, version in msg_obj.badges.items():
                if badge_set in global_badges and version in global_badges[badge_set]:
                    badge_data = global_badges[badge_set][version]
                    badge_html += (
                        f'<img src="{badge_data["image1x"]}" '
                        f'title="{badge_data["title"]}" '
                        f'style="width:18px;height:18px;vertical-align:middle;margin-right:2px;">'
                    )
            message_data = {
                "id": msg_obj.user_id + "_" + str(msg_obj.timestamp),  # unique ID
                "display_name": msg_obj.display_name,
                "color": msg_obj.color,
                "text": msg_obj.message,
                "badge_html": badge_html
            }
            message_history.append(msg_obj)
            socketio.emit("Twitch_chat_message", message_data)

        elif "CLEARCHAT" in message or "CLEARMSG" in message:
            # Extract the target message ID
            tags_part = message.split(" ", 1)[0].lstrip("@")
            tags = dict(tag.split("=") for tag in tags_part.split(";") if "=" in tag)
            target_msg_id = tags.get("target-msg-id")
            target_user = tags.get("msg-param-login")

            socketio.emit("delete_Twitch_message", {
                "id": target_msg_id,
                "user": target_user
            })

    except Exception as e:
        print("Error parsing Twitch message:", e)






