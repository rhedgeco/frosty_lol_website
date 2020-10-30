from asyncio import CancelledError

from sanic.exceptions import InvalidUsage
from sanic.response import json
from sanic.websocket import ConnectionClosed

from backend.chat_handlers.chat_storage_history import ChatStorageHistory
from backend.database_manager import DatabaseManager


class ChatManager:
    def __init__(self, max_chat_length: int, manager: DatabaseManager):
        self.storage = ChatStorageHistory(100)
        self._max_chat_length = max_chat_length
        self._manager = manager
        self._connections = []

    def get_chat_log(self, request):
        return json(self.storage.get_storage())

    async def websocket_runner(self, request, ws):
        self._connections.append(ws)
        user = None
        try:
            while True:
                data = await ws.recv()
                if user:
                    chat = self._clean_chat(data)
                    self.storage.add(chat, user['nickname'])
                    for socket in self._connections:
                        try:
                            await socket.send(chat)
                        except ConnectionClosed:
                            self._connections.remove(socket)
                else:
                    try:
                        user = self._manager.get_user_info(session=data)
                        await ws.send('validated session')
                    except InvalidUsage:
                        await ws.send('invalid session')
        except CancelledError:
            self._connections.remove(ws)

    def _clean_chat(self, chat: str):
        clean = chat

        # check if chat exceeds character limit
        if len(chat) > self._max_chat_length:
            clean = chat[0:self._max_chat_length]

        # check if chat contains any bad characters (inserting html)
        clean = clean.replace('&', '&amp;')
        clean = clean.replace('<', '&lt;')
        clean = clean.replace('>', '&gt;')
        clean = clean.replace('"', '&quot;')
        clean = clean.replace("'", '&#39;')

        return clean
