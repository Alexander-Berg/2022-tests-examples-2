from typing import Optional

_PREFIX = 'super_duper_secret_'


def encode_entity(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    return _PREFIX + value


def decode_entity(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    return value[len(_PREFIX) :]
