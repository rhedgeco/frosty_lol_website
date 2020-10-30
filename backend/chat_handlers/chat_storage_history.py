import threading

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Chat:
    text: str
    timestamp: datetime
    user: str


class ChatStorageHistory:
    def __init__(self, max_history: int):
        self._max_history = max_history
        self._storage = []
        self._oldest_index = 0
        self._string_count = 0
        self._sorted_storage_cache = []
        self._cache_lock = threading.Lock()

    def add(self, text: str, user: str):
        text = Chat(text, datetime.now(), user)
        with self._cache_lock:
            self._sorted_storage_cache = []
            if self._string_count >= self._max_history:  # storage is full, replace oldest chat
                self._storage[self._oldest_index] = text
                self._oldest_index += 1
                if self._oldest_index == self._max_history:
                    self._oldest_index = 0
            else:  # storage is not full, insert into next open index
                self._storage.append(text)
                self._string_count += 1

    def get_storage(self):
        with self._cache_lock:
            if len(self._sorted_storage_cache) > 0:
                return self._sorted_storage_cache

            for i in range(0, self._string_count):
                i_shift = i + self._oldest_index
                if i_shift >= self._max_history:
                    i_shift -= self._max_history
                chat = self._storage[i_shift]
                chat = [chat.text, chat.timestamp.strftime("[%H:%M]"), chat.timestamp.strftime("%B %d, %Y"), chat.user]
                self._sorted_storage_cache.append(chat)

            return self._sorted_storage_cache
