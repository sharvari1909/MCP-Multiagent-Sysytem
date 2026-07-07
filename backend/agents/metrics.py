import time
from contextlib import contextmanager


@contextmanager
def track_latency():
    start = time.time()
    result = {"latency_ms": 0}

    try:
        yield result
    finally:
        result["latency_ms"] = round((time.time() - start) * 1000, 2)


def token_estimate(text: str):
    if not text:
        return 0
    return max(1, len(text.split()) * 2)