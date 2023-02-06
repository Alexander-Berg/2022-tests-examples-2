import datetime as dt
import functools
import json
from typing import Optional

import dateutil.parser


def _make_datetime(datetime_string: str) -> dt.datetime:
    return dateutil.parser.isoparse(datetime_string)


_CONVERTERS = {'$datetime': _make_datetime, '$tuple': tuple}


def load_py_json(content, additional_converters: dict = None):
    hook = functools.partial(
        _py_json_object_hook, additional_converters=additional_converters,
    )
    return json.loads(content, object_hook=hook)


def _py_json_object_hook(obj, additional_converters: dict):
    assert isinstance(obj, dict)
    if len(obj) == 1:
        converter_keys = _get_converter_keys(obj)
        if converter_keys:
            name = converter_keys[0]
            value = obj[name]
            converter = _get_converter(name, additional_converters)
            return converter(value)
    return obj


def _get_converter_keys(obj):
    return [key for key in obj if key.startswith('$')]


def _get_converter(name, additional_converters: Optional[dict]):
    additional_converters = additional_converters or {}
    additional_converter = additional_converters.get(name)
    if additional_converter:
        return additional_converter
    try:
        return _CONVERTERS[name]
    except KeyError:
        allowed_converters = set(_CONVERTERS.keys())
        allowed_converters.update(additional_converters.keys())
        allowed_converters_str = ', '.join(sorted(allowed_converters))
        msg = f'unknown converter {name}, variants: {allowed_converters_str}'
        raise TypeError(msg)
