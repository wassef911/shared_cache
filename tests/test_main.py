from __future__ import annotations

import pytest

from src.shared_cache import Cache


@pytest.mark.asyncio
async def test_set_and_get():
    cache = Cache(maxsize=2)

    await cache.set("key1", "value1")
    result = await cache.get("key1")
    assert result == "value1"
    assert await cache.size() == 1
    await cache.clear()

    # default value when key is not present
    result = await cache.get("non_existent_key", default="default_value")
    assert result == "default_value"

    assert await cache.size() == 0


@pytest.mark.asyncio
async def test_clear():
    cache = Cache(maxsize=2)

    await cache.set("key1", "value1")
    await cache.set("key2", "value2")

    await cache.clear()

    result = await cache.get("key1", default="default_value")
    assert result == "default_value"

    result = await cache.get("key2", default="default_value")
    assert result == "default_value"


@pytest.mark.asyncio
async def test_maxsize():
    cache = Cache(maxsize=2)

    await cache.set("key2", "value2")
    await cache.set("key3", "value3")

    result1 = await cache.get("key1", default="default_value")
    result2 = await cache.get("key2", default="value2")
    result3 = await cache.get("key3", default="value3")

    assert result1 == "default_value"
    assert result2 == "value2"
    assert result3 == "value3"


@pytest.mark.asyncio
async def test_delete():
    cache = Cache(maxsize=2)

    await cache.set("key1", "value1")
    await cache.set("key2", "value2")

    await cache.delete("key1")
    result = await cache.get("key1", default="default_value")
    assert result == "default_value"

    result = await cache.get("key2")
    assert result == "value2"


@pytest.mark.asyncio
async def test_contains():
    cache = Cache(maxsize=2)

    await cache.set("key1", "value1")
    assert await cache.contains("key1") is True

    assert await cache.contains("non_existent_key") is False


@pytest.mark.asyncio
async def test_size():
    cache = Cache(maxsize=2)

    assert await cache.size() == 0

    await cache.set("key1", "value1")
    await cache.set("key2", "value2")

    assert await cache.size() == 2

    await cache.delete("key1")
    assert await cache.size() == 1


@pytest.mark.asyncio
async def test_set_and_get_many():
    cache = Cache(maxsize=1024)
    await cache.set("key1", "value1")
    await cache.set("key2", "value2")
    await cache.set("key3", "value3")

    keys = ["key1", "key2", "key3", "key4"]
    result = await cache.get_many(keys, default="default")

    assert result == {
        "key1": "value1",
        "key2": "value2",
        "key3": "value3",
        "key4": "default",
    }


@pytest.mark.asyncio
async def test_set_many():
    cache = Cache(maxsize=1024)
    items = [("key1", "value1"), ("key2", "value2"), ("key3", "value3")]
    await cache.set_many(items)

    assert await cache.get("key1") == "value1"
    assert await cache.get("key2") == "value2"
    assert await cache.get("key3") == "value3"
    assert await cache.get("key4") is None


@pytest.mark.asyncio
async def test_delete_many():
    cache = Cache(maxsize=1024)
    await cache.set("key1", "value1")
    await cache.set("key2", "value2")

    await cache.delete_many(["key1", "key2"])

    assert await cache.get("key1") is None
    assert await cache.contains("key2") is False
    assert await cache.size() == 0


@pytest.mark.asyncio
async def test_touch():
    cache = Cache(maxsize=1024)
    await cache.touch("key1")
    assert await cache.contains("key1") is True
