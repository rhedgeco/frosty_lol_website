from general_falcon_webserver import WebApp

from backend.chat_api import ChatApi

app = WebApp()
app.add_route('chat', ChatApi())
app.launch_webserver()
