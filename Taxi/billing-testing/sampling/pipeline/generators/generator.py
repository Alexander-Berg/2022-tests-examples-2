from typing import Any


class Generator:
    def fetch(self) -> Any:
        raise RuntimeError('Fetch not implemented')
