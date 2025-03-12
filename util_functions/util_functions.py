# Library imports
import time
from functools import wraps

def timer(f):
    @wraps(f)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await f(*args, **kwargs)
        end_time = time.time()

        print(f"{f.__name__} took {end_time- start_time} seconds")
        return result
    return wrapper

def repeat(times):
    def decorator(f):
        @wraps(f)
        async def wrapper(*args, **kwargs):
            for _ in range(times):
                result = await f(*args, **kwargs)
            return result
        return wrapper
    return decorator
