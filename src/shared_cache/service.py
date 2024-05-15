from __future__ import annotations

from typing import Any
from typing import Hashable

from .shared import SharedMemoryBackend


class Cache:
    def __init__(
        self,
        maxsize=1024,
        shm_name="caching_service_memory",
        shared_memory_backend: SharedMemoryBackend = None,
    ):
        self.memory = shared_memory_backend or SharedMemoryBackend(maxsize, shm_name)

    def __get_key(self, key: Hashable) -> Hashable:
        return key

    async def set(self, key: Hashable, value: Any):
        data = self.memory.data
        data[self.__get_key(key)] = value
        self.memory.data = data

    async def get(self, key: Hashable, default: Any = None):
        data = self.memory.data
        return data.get(key, default)

    async def delete(self, key: Hashable):
        data = self.memory.data
        if key in data:
            del data[self.__get_key(key)]
            self.memory.data = data

    async def contains(self, key: Hashable) -> bool:
        data = self.memory.data
        return key in data

    async def size(self) -> int:
        data = self.memory.data
        return len(data)

    async def clear(self):
        self.memory.data = {}

    async def get_many(
        self, keys: list[Hashable], default: Any = None
    ) -> dict[Hashable, Any]:
        data = self.memory.data
        return {key: data.get(key, default) for key in keys}

    async def set_many(self, items: list[tuple[Hashable, Any]]):
        data = self.memory.data
        for key, value in items:
            data[self.__get_key(key)] = value
        self.memory.data = data

    async def delete_many(self, keys: list[Hashable]):
        data = self.memory.data
        for key in keys:
            if key in data:
                del data[self.__get_key(key)]
        self.memory.data = data

    async def touch(self, key: Hashable):
        data = self.memory.data
        data[self.__get_key(key)] = {}
        self.memory.data = data
