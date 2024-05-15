## Cache Package

### Overview

The `shared_cache` package provides a in-memory storage solution that can be used with FastAPI or any other Python application requiring efficient, inter-process caching.

Internally using the built-in `multiprocessing.shared_memory` and `msgpack`.

### Installation

```sh
pip install shared_cache
```

### Usage

```python
# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, Hashable
import asyncio
from .models import Item

from shared_cache import Cache

app = FastAPI()
cache = Cache(maxsize=1_280_000) # in mb

@app.on_event("startup")
async def startup_event():
    await cache.clear()  # Ensure cache is clear at startup

@app.post("/set")
async def set_item(item: Item):
    await cache.set(item.key, item.value)
    return {"message": "Item set successfully"}

@app.get("/get/{key}")
async def get_item(key: string):
    value = await cache.get(key)
    if value is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"key": key, "value": value}

@app.delete("/delete/{key}")
async def delete_item(key: Hashable):
    await cache.delete(key)
    return {"message": "Item deleted successfully"}

```

```sh
# In both cases below, all 4 workers will have access to the same cache
uvicorn main:app --workers 4
# or
gunicorn --workers 4 -k uvicorn.workers.UvicornWorker main:app
```


### Testing the Package

To test the `Cache` package, you can use the provided test suite. The tests include inter-process communication scenarios to ensure that the cache works correctly across multiple processes.

1. **Run the Tests**:
   ```bash
   pytest tests/test_between_workers.py
   ```

### Contributing

Contributions are welcome! Please open an issue or submit a pull request on the [GitHub repository](https://github.com/wassef911/shared_cache).

### License

This project is licensed under the MIT License.

### Contact

For any questions or inquiries, please contact [wassef911@gmail.com](mailto:wassef911@gmail.com).

---
