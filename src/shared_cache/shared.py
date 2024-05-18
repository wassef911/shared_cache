from __future__ import annotations
import collections
import time
from multiprocessing.shared_memory import SharedMemory
from typing import Any
from typing import Dict
from typing import Hashable

import msgpack


class CacheItem:
    def __init__(self, value: Any, timestamp: float):
        self.value = value
        self.timestamp = timestamp


class SharedMemoryBackend(collections.abc.MutableMapping[Hashable, Any]):
    _is_creator = False

    def __init__(self, maxsize=1024, shm_name="caching_service_memory"):
        self.memory_size = maxsize * 1024  # 1KB = 1024 bytes
        self.shm_name = shm_name
        try:
            self.shm = SharedMemory(
                name=self.shm_name, create=True, size=self.memory_size
            )
            self._is_creator = True
            self._initialize_memory()
        except FileExistsError:
            self.shm = SharedMemory(name=self.shm_name, create=False)

    def _initialize_memory(self):
        self.data = {}

    def serialize(self, data: Dict[Hashable, Any]) -> bytes:
        serialized_data = msgpack.packb(data, use_bin_type=True)
        serialized_size = len(serialized_data)
        if serialized_size + 4 > self.memory_size:
            raise MemoryError(
                f"Data size {serialized_size} exceeds memory limit {self.memory_size}"
            )
        return serialized_size.to_bytes(4, "little") + serialized_data

    def deserialize(self, buffer: bytes) -> Dict[Hashable, Any]:
        serialized_size = int.from_bytes(buffer[:4], "little")
        serialized_data = buffer[4 : 4 + serialized_size]
        return msgpack.unpackb(serialized_data, strict_map_key=False)

    @property
    def data(self) -> Dict[Hashable, Any]:
        return self.deserialize(bytes(self.shm.buf[: self.memory_size]))

    @data.setter
    def data(self, value: dict[Hashable, CacheItem]):
        serialized_data = self.serialize(value)
        if not (len(serialized_data) <= self.memory_size):
            self.__cleanup_memory(value)

        self.shm.buf[: len(serialized_data)] = serialized_data
        self.shm.buf[len(serialized_data) :] = bytes(
            self.memory_size - len(serialized_data)
        )

    def __cleanup_memory(self, current_data: dict[Hashable, CacheItem]):
        sorted_items = sorted(current_data.items(), key=lambda item: item[1].timestamp)
        while (
            len(self.serialize(current_data)) > self.memory_size // 2 and sorted_items
        ):
            oldest_item = sorted_items.pop(0)
            del current_data[oldest_item[0]]

            serialized_data = self.serialize(current_data)
        if len(serialized_data) <= self.memory_size:
            self.shm.buf[: len(serialized_data)] = serialized_data
            self.shm.buf[len(serialized_data) :] = bytes(
                self.memory_size - len(serialized_data)
            )
        else:
            raise MemoryError("Unable to fit cleaned data within memory limits.")

    def __del__(self):
        self.shm.close()
        if self._is_creator:
            self.shm.unlink()

    def __delitem__(self, key: Hashable):
        data = self.data
        del data[key]
        self.data = data

    def __contains__(self, key: Hashable) -> bool:
        return key in self.data

    def __missing__(self, key: Hashable):
        raise KeyError(key)

    def __getitem__(self, key: Hashable) -> Any:
        try:
            return self.data[key].value
        except KeyError:
            return self.__missing__(key)

    def __setitem__(self, key: Hashable, value: Any):
        data = self.data
        data[key] = CacheItem(value, time.time())
        self.data = data

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)

    def __str__(self):
        return str(self.data)
