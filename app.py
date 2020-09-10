from pathlib import Path

from backend.general_manager.databases import SqliteDatabase
from general_falcon_webserver import WebApp

from backend.chat_api import ChatApi
from backend.database_manager import DatabaseManager
from backend.google_oauth import GoogleOauth

app = WebApp()

with open(Path('backend') / 'database_setup.sql') as file:
    db_config = file.read()
db = SqliteDatabase('frosty_lol', db_config)
manager = DatabaseManager(db)

app.add_route('g-oauth', GoogleOauth(manager))
app.add_route('chat', ChatApi(manager))

app.launch_webserver()
