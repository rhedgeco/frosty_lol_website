import uuid
import datetime

import falcon

from datetime import datetime as dt

from general_falcon_webserver.backend.general_manager.databases import SqliteDatabase

TIME_FORMAT = '%d/%m/%Y %H:%M:%S'
TIME_EXPIRE = 600


class DatabaseManager:
    def __init__(self, db: SqliteDatabase):
        self.db = db

    def sign_in_or_create_oauth_user(self, user_id: str, nickname: str, photo: str):
        self.db.send_query(f"INSERT OR IGNORE INTO users (user_id, nickname, photo) "
                           f"VALUES ('{user_id}', '{nickname}', '{photo}')")
        session = uuid.uuid4().hex
        self._reset_user_session(user_id, session)
        return session

    def get_user_info(self, session: str):
        user = self._get_user_from_database(session)
        user = {
            "id": user['user_id'],
            "nickname": user['nickname'],
            "photo": user['photo'],
        }

        return user

    def _get_user_from_database(self, session: str):
        user = self.db.fetchone_query(f"SELECT * FROM users WHERE session_id='{session}'")
        if not user:
            raise falcon.HTTPBadRequest('Could not validate session')
        self._validate_user_session(user['user_id'])
        return user

    def _get_user_by_id(self, user_id: str):
        user = self.db.fetchone_query(f"SELECT * FROM users WHERE user_id='{user_id}'")
        if not user:
            raise falcon.HTTPBadRequest('Could not locate user.')
        return user

    def _validate_user_session(self, user_id: str):
        user = self.db.fetchone_query(f"SELECT * FROM users WHERE user_id = '{user_id}'")
        if not user:
            raise falcon.HTTPBadRequest('User ID not accepted.')

        user_expire = dt.strptime(user['session_timeout'], TIME_FORMAT)
        if user_expire < dt.now():
            raise falcon.HTTPUnauthorized(f'User session has timed out.')
        session = user['session_id']
        self._reset_user_session(user_id, session)

    def _reset_user_session(self, user_id: str, session: str):
        self.db.send_query(f"UPDATE users SET session_id='{session}', "
                           f"session_timeout='{(dt.now() + datetime.timedelta(0, TIME_EXPIRE)).strftime(TIME_FORMAT)}' "
                           f"WHERE user_id='{user_id}'")
