import json

from backend.chat_websocket import ChatWebsocket


class ChatApi:
    def __init__(self):
        self._chat_socket = ChatWebsocket(80)

    def on_get(self, req, resp):
        resp.body = json.dumps(self._chat_socket.storage.get_storage(), ensure_ascii=True)
