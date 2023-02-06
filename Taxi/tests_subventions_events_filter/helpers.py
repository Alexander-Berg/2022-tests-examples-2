import typing


def set_redis_state(redis_store, state: typing.Mapping[str, str]):
    for key, value in state.items():
        redis_store.set(key, value)


def _extract_keys(redis_store, **kwargs):
    iterator = redis_store.scan_iter(**kwargs)
    return [bytestr.decode() for bytestr in iterator]


def _extract_value(redis_store, key):
    bytestr = redis_store.get(key)
    return bytestr.decode()


def get_redis_state(redis_store) -> typing.Dict[str, str]:
    keys = _extract_keys(redis_store)
    return {key: _extract_value(redis_store, key) for key in keys}
