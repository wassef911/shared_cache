from __future__ import annotations

from multiprocessing import Manager
from multiprocessing import Process

import pytest

from src.shared_cache import Cache


def worker_set(cache, key, value):
    import asyncio

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(cache.set(key, value))


def worker_get(cache, key, return_dict):
    import asyncio

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return_dict[key] = loop.run_until_complete(cache.get(key))


@pytest.mark.asyncio
async def test_write_read_multiprocess():
    manager = Manager()
    return_dict = manager.dict()

    cache = Cache(maxsize=1024)

    p1 = Process(target=worker_set, args=(cache, "key1", "value1"))
    p2 = Process(target=worker_get, args=(cache, "key1", return_dict))

    p1.start()
    p1.join()

    p2.start()
    p2.join()

    assert return_dict["key1"] == "value1"


@pytest.mark.asyncio
async def test_write_override_multiprocess():
    manager = Manager()
    return_dict = manager.dict()

    cache = Cache(maxsize=1024)

    p1 = Process(target=worker_set, args=(cache, "key1", "value1"))
    p2 = Process(target=worker_set, args=(cache, "key1", "blabla"))
    p3 = Process(target=worker_get, args=(cache, "key1", return_dict))

    p1.start()
    p1.join()

    p2.start()
    p2.join()

    p3.start()
    p3.join()
    assert return_dict["key1"] == "blabla"
