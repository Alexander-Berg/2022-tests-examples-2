import json
import random
from typing import Any
from typing import Optional

from . import generator


class RandomInt(generator.Generator):
    def __init__(self, min_val, max_val):
        generator.Generator.__init__(self)
        self._min = min_val
        self._max = max_val

    def fetch(self) -> Any:
        return random.randint(self._min, self._max)


class ObjectToJsonString(generator.Generator):
    def __init__(self, data):
        generator.Generator.__init__(self)
        self._data = data

    def fetch(self) -> Any:
        return json.dumps(self._data)


class OneByOne(generator.Generator):
    def __init__(
            self, data, repeat: Optional[int] = None, default: Any = None,
    ):
        generator.Generator.__init__(self)
        self._data = list(data)
        self._default = default
        self._repeat = repeat
        self._index = 0
        self._repeated = 0
        self._data_size = len(self._data)

    def fetch(self) -> Any:
        self._repeated %= self._data_size
        self._index %= self._data_size
        if self._index >= self._data_size:
            return self._default
        current = self._data[self._index]
        self._index += int(not self._repeat or self._repeated)
        self._repeated += 1
        return current


class Serial(generator.Generator):
    def __init__(self, start=1):
        generator.Generator.__init__(self)
        self._start = start

    def fetch(self) -> Any:
        current = self._start
        self._start += 1
        return current


class Str(generator.Generator):
    def __init__(self, data):
        generator.Generator.__init__(self)
        self._data = data

    def fetch(self) -> Any:
        return str(self._data)
