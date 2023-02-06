import dataclasses


@dataclasses.dataclass
class Response:
    content: dict
    status: int = 200
