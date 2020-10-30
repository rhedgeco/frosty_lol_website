from pathlib import Path
from sanic import Sanic, response
from sanic.websocket import WebSocketProtocol

from backend.chat_websocket import ChatManager
from backend.database_handlers.databases import SqliteDatabase
from backend.database_manager import DatabaseManager
from backend.google_oauth import GoogleOauth

app = Sanic('frosty_lol')

frontend_dir = Path('./frontend')
app.static('/', str(frontend_dir))

with open(Path('backend') / 'database_setup.sql') as file:
    db_config = file.read()
sqlite = SqliteDatabase('frosty_lol', db_config)
db_manager = DatabaseManager(sqlite)

app.add_route(GoogleOauth.as_view(db_manager), '/api/g-oauth')

chat = ChatManager(200, db_manager)
app.add_route(chat.get_chat_log, '/api/chat')
app.add_websocket_route(chat.websocket_runner, '/api/chat/feed')

# noinspection PyUnusedLocal
@app.route('/')
async def index(request):
    return await response.file(str(frontend_dir / 'index.html'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
