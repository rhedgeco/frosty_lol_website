import asyncio
import websockets

from backend.chat_storage_history import ChatStorageHistory
from threading import Thread


class ChatWebsocket:
    def __init__(self, max_chat_length: int):
        self.storage = ChatStorageHistory(100)
        self._max_chat_length = max_chat_length
        self._connections = []

        loop = asyncio.new_event_loop()
        t = Thread(target=self._start_chat_socket, args=(loop,), daemon=True)
        t.start()

    def _start_chat_socket(self, loop):
        async def socket_runner(websocket, path):
            self._connections.append(websocket)
            try:
                while True:
                    chat = await websocket.recv()
                    chat = self._clean_chat(chat)
                    self.storage.add(chat)
                    for socket in self._connections:
                        await socket.send(chat)
            except websockets.exceptions.ConnectionClosed:
                pass  # do nothing
            finally:
                self._connections.remove(websocket)

        asyncio.set_event_loop(loop)
        start_socket = websockets.serve(socket_runner, 'localhost', 8765)
        loop.run_until_complete(start_socket)
        loop.run_forever()

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
