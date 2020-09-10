import json
import falcon

from backend.chat_websocket import ChatWebsocket
from backend.backend_utils import validate_params
from backend.database_manager import DatabaseManager


class ChatApi:
    def __init__(self, manager: DatabaseManager):
        self._chat_socket = ChatWebsocket(80, manager)

    def on_get(self, req, resp):
        resp.body = json.dumps(self._chat_socket.storage.get_storage(), ensure_ascii=True)
