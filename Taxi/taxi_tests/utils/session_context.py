import typing


class MockserverInfo(typing.NamedTuple):
    host: str
    port: str
    base_url: str


class SessionContext:
    mockserver: typing.Optional[MockserverInfo] = None
