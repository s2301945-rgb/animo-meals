"""Small single-process request guard. No raw IPs or request text are persisted."""
from collections import OrderedDict, deque
import hashlib
from threading import Lock
from time import monotonic

from fastapi import HTTPException, Request

_buckets = OrderedDict()
_lock = Lock()


def check_limit(request: Request, scope: str, per_client: int, total: int):
    now = monotonic()
    client = hashlib.sha256((request.client.host if request.client else 'unknown').encode()).hexdigest()
    with _lock:
        for key, maximum in ((f'{scope}:all', total), (f'{scope}:{client}', per_client)):
            bucket = _buckets.setdefault(key, deque())
            _buckets.move_to_end(key)
            while bucket and bucket[0] <= now - 60:
                bucket.popleft()
            if len(bucket) >= maximum:
                raise HTTPException(429, 'Too many requests. Please wait a minute and try again.',
                                    headers={'Retry-After': '60'})
        _buckets[f'{scope}:all'].append(now)
        _buckets[f'{scope}:{client}'].append(now)
        while len(_buckets) > 4096:
            _buckets.popitem(last=False)
