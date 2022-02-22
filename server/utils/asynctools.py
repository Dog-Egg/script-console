import asyncio
import os
from functools import wraps, partial

from aiofiles import open

__all__ = ['open']


def wrap(func):
    @wraps(func)
    async def run(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(executor=None, func=partial(func, *args, **kwargs))

    return run


exists = wrap(os.path.exists)
