import pytest
from src.shared_cache import CachingService

@pytest.mark.asyncio
async def test_set_and_get():
    cache = CachingService(maxsize=2)

    await cache.set('key1', 'value1')
    result = await cache.get('key1')
    assert result == 'value1'

    # Test default value when key is not present
    result = await cache.get('non_existent_key', default='default_value')
    assert result == 'default_value'

@pytest.mark.asyncio
async def test_clear():
    cache = CachingService(maxsize=2)

    await cache.set('key1', 'value1')
    await cache.set('key2', 'value2')

    await cache.clear()

    result = await cache.get('key1', default='default_value')
    assert result == 'default_value'

    result = await cache.get('key2', default='default_value')
    assert result == 'default_value'

@pytest.mark.asyncio
async def test_maxsize():
    cache = CachingService(maxsize=2)

    await cache.set('key2', 'value2')
    await cache.set('key3', 'value3')

    result1 = await cache.get('key1', default='default_value')
    result2 = await cache.get('key2', default='value2')
    result3 = await cache.get('key3', default='value3')

    # Assuming that the first key inserted ('key1') will be evicted if maxsize is reached.
    assert result1 == 'default_value'
    assert result2 == 'value2'
    assert result3 == 'value3'
