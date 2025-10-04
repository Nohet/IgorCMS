import asyncio
import inspect

from typing import Callable
from starlette.requests import Request


def dependency_injection(dependency: Callable):
    def inner(func: Callable):
        async def wrapper(request: Request):
            if inspect.iscoroutinefunction(dependency):
                dep_value = await dependency(request)
            else:
                dep_value = await asyncio.to_thread(dependency, request)

            if inspect.iscoroutinefunction(func):
                return await func(request, dep_value)
            else:
                return await asyncio.to_thread(func, request, dep_value)

        return wrapper
    return inner
