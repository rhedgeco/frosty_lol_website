import falcon
import cachecontrol
import google.auth.transport.requests
import requests

from backend.database_manager import DatabaseManager
from backend.backend_utils import validate_params

from google.oauth2 import id_token

CLIENT_ID = '953803778347-laspasf834uni51o66dpsp345crmnpve.apps.googleusercontent.com'


class GoogleOauth:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def on_post(self, req, resp):
        if not validate_params(req.params, 'idtoken'):
            raise falcon.HTTPBadRequest("oauth post requires 'idtoken' parameter")

        token = req.params['idtoken'].replace("'", "").replace('"', '')
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
            resp.status = falcon.HTTP_OK
            resp.body = session_token

        except ValueError:
            raise falcon.HTTPUnauthorized('Token not accepted')
            pass