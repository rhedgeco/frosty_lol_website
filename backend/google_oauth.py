import cachecontrol
import google.auth.transport.requests
import requests

from google.oauth2 import id_token
from sanic.response import json
from sanic.views import HTTPMethodView
from sanic.exceptions import Unauthorized

from backend.backend_utils import validate_required_params
from backend.database_manager import DatabaseManager

CLIENT_ID = '953803778347-laspasf834uni51o66dpsp345crmnpve.apps.googleusercontent.com'


class GoogleOauth(HTTPMethodView):
    def __init__(self, db: DatabaseManager):
        self.db = db

    async def post(self, request):
        args = validate_required_params(request.args, 'idtoken')

        token = args['idtoken'][0].replace("'", "").replace('"', '')
        # example from https://developers.google.com/identity/sign-in/web/backend-auth
        try:
            session = requests.session()
            cached_session = cachecontrol.CacheControl(session)
            request = google.auth.transport.requests.Request(session=cached_session)
            id_info = id_token.verify_oauth2_token(token, request, CLIENT_ID)

            if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')

            user_id = id_info['sub']
            user_nickname = id_info['name']
            user_photo = str(id_info['picture']).replace('=s96-c', '')
            session_token = self.db.sign_in_or_create_oauth_user(user_id, user_nickname, user_photo)
            response = json({'session_id': session_token})
            response.cookies['session_token'] = session_token
            return response

        except ValueError:
            raise Unauthorized('Token not accepted')
            pass
