import time
from functools import wraps
from types import FunctionType, GeneratorType
from typing import Any

from cassandra.cluster import NoHostAvailable
from redis import ConnectionError


CONNECTION_ERRORS = (
    # Cassandra connection error
    NoHostAvailable,

    # Redis connection error
    ConnectionError,
)


def backoff(
    start_sleep_time: int = 0.1,
    factor: int = 2,
    border_sleep_time: int = 10
) -> FunctionType:
    """
    A function to re-execute the function after some time if an error occurs.
    Uses naive exponential growth of retry time (factor) 
    before the border sleep time (border_sleep_time)
    Formula:
        t = start_sleep_time * 2^(n) if t < border_sleep_time
        t = border_sleep_time if t >= border_sleep_time
    :param start_sleep_time: sleep time at start
    :param factor: waiting multiplier
    :param border_sleep_time: higher bound for wainting time
    :return: result of the function
    """
    def func_wrapper(func: FunctionType) -> FunctionType:
        @wraps(func)
        def inner(*args: Any, **kwargs: Any) -> Any:
            n = 0
            t = start_sleep_time
            while True:
                try:
                    result = func(*args, **kwargs)
                    if isinstance(result, GeneratorType):
                        result = list(result)
                except CONNECTION_ERRORS:
                    t = start_sleep_time * factor ** n
                    if t >= border_sleep_time:
                        t = border_sleep_time
                    else:
                        n += 1
                    time.sleep(t)
                else:
                    return result
        return inner
    return func_wrapper
