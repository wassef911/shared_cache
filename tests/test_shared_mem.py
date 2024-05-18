from __future__ import annotations

import pytest

from src.shared_cache.shared import SharedMemoryBackend


@pytest.mark.asyncio
async def test_iter():
    shared_memory = SharedMemoryBackend()
    shared_memory.data = {"key1": "value1", "key2": "value2"}

    keys = [key for key in shared_memory]
    assert keys == ["key1", "key2"]


@pytest.mark.asyncio
async def test_len():
    shared_memory = SharedMemoryBackend()
    shared_memory.data = {"key1": "value1", "key2": "value2"}

    assert len(shared_memory) == 2


@pytest.mark.asyncio
async def test_str():
    shared_memory = SharedMemoryBackend()
    shared_memory.data = {"key1": "value1", "key2": "value2"}

    assert str(shared_memory) == "{'key1': 'value1', 'key2': 'value2'}"
