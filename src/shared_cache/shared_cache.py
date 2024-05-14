from __future__ import annotations

from typing import Any, Hashable
import pickle
from multiprocessing.shared_memory import SharedMemory
import time
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class CacheItem:
    value: Any  # a value that can be pickled
    timestamp: float


class SharedMemoryBackend:
    _is_creator = False

    def __init__(self, maxsize=1_280_000, shm_name="caching_service_memory"):
        self.memory_size = maxsize * 1024  # convert KB to bytes, default 128MB
        self.shm_name = shm_name
        try:
            self.shm = SharedMemory(name=self.shm_name, create=True, size=self.memory_size)
            self._is_creator = True
        except FileExistsError:
            # another worker has already created the shared memory
            self.shm = SharedMemory(name=self.shm_name, create=False)
        if not self.shm.buf[0]:
            # if the first byte is None, memory is empty, initialize it
            self.data = {}

    @property
    def data(self):
        buffer = self.shm.buf[: self.memory_size]
        receiveddata = pickle.loads(buffer)
        return receiveddata

    @data.setter
    def data(self, value: dict[Hashable, CacheItem]):
        serialized_data = pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)
        if len(serialized_data) < self.memory_size:
            self.shm.buf[: len(serialized_data)] = serialized_data
            self.__cleanup_memory()
        else:
            logger.info(f"data is above memory limit {len(serialized_data)} / {self.memory_size}")

    def __cleanup_memory(self):
        sorted_items: list[tuple[Hashable, CacheItem]] = sorted(self.data.items(), key=lambda item: item[1].timestamp)
        # remove the oldest entries until the data size is within (the memory limit / 2) (50%)
        while len(pickle.dumps(self.data)) > self.memory_size // 2:
            oldest_item = sorted_items.pop(0)
            del self.data[oldest_item[0]]
            # logger.info(f"Evicted {oldest_item[0]} to free up space.")

    def __del__(self):
        self.shm.close()
        if self._is_creator:
            self.shm.unlink()

    def __delitem__(self, key):
        del self.data[key]

    def __contains__(self, key):
        return key in self.data

    def __missing__(self, key):
        raise KeyError(key)

    def __getitem__(self, key):
        try:
            return self.data[key].value
        except KeyError:
            return self.__missing__(key)

    def __setitem__(self, key: Hashable, value: Any):
        value = CacheItem(value, time.time())
        self.data = {**self.data, key: value}


class CachingService():
    def __init__(self, maxsize=128):
        self.memory = SharedMemoryBackend(maxsize)

    async def set(self, key: Hashable, value:Any):
        self.memory[key] = value

    async def get(self, key, default=None):
        if key in self.memory:
            return self.memory[key]
        else:
            return default

    async def clear(self):
        self.memory.data = {}
        logger.info("Cache cleared.")
