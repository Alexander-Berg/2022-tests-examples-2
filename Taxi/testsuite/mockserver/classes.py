import dataclasses
import typing

import aiohttp.web

from testsuite import annotations
from testsuite.utils import callinfo
from testsuite.utils import http
from testsuite.utils import url_util

RequestType = typing.TypeVar('RequestType')
GenericRequestHandler = typing.Callable[
    [RequestType], annotations.MaybeAsyncResult[aiohttp.web.Response],
]
GenericRequestDecorator = typing.Callable[
    [GenericRequestHandler[RequestType]], callinfo.AsyncCallQueue,
]
JsonRequestHandler = typing.Callable[
    [RequestType],
    annotations.MaybeAsyncResult[
        typing.Union[aiohttp.web.Response, annotations.JsonAnyOptional]
    ],
]
JsonRequestDecorator = typing.Callable[
    [JsonRequestHandler[RequestType]], callinfo.AsyncCallQueue,
]
MockserverRequest = http.Request


@dataclasses.dataclass(frozen=True)
class SslCertInfo:
    cert_path: str
    private_key_path: str


@dataclasses.dataclass(frozen=True)
class MockserverInfo:
    host: str
    port: int
    base_url: str
    ssl: typing.Optional[SslCertInfo]

    def url(self, path: str) -> str:
        """Concats ``base_url`` and provided ``path``."""
        return url_util.join(self.base_url, path)


class MockserverSslInfo(MockserverInfo):
    ssl: SslCertInfo


MockserverInfoFixture = MockserverInfo
MockserverSslInfoFixture = typing.Optional[MockserverInfo]
