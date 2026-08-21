import asyncio
import time
from typing import AsyncGenerator, Any
from server.config import settings

class RateLimiter:
    def __init__(self):
        self.tokens = asyncio.Semaphore(settings.max_threads)
        self.last_request_time = 0.0
        self.min_interval = 1.0 / settings.rate_limit_per_second

    async def rate_limited(self, func: AsyncGenerator[Any, None], *args, **kwargs) -> AsyncGenerator[Any, None]:
        """Wrap an async generator to enforce rate limits."""
        async for item in func(*args, **kwargs):
            now = time.time()
            elapsed = now - self.last_request_time
            if elapsed < self.min_interval:
                await asyncio.sleep(self.min_interval - elapsed)
            self.last_request_time = time.time()
            yield item
