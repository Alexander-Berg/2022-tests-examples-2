from typing import Any
from typing import Mapping

import aiohttp
import cached_property

from generated.clients import testpalm
from taxi.clients import http_client
from taxi.codegen import clients as clients_utils


class TestpalmClient(testpalm.TestpalmClient):
    def __init__(
            self,
            context: Any,
            middlewares: Mapping,
            statistics_fallbacks_enabled: bool,
            base_url: str,
            **kwargs,
    ) -> None:
        super().__init__(
            context, middlewares, statistics_fallbacks_enabled, base_url,
        )
        self._context = context
        self._session = http_client.HTTPClient(
            cookie_jar=aiohttp.DummyCookieJar(),
        )

    @cached_property.cached_property
    def _extra_headers(self):
        secdist = self._context.secdist
        token = secdist['settings_override']['TESTPALM_OAUTH']
        return {
            'Accept': 'application/json',
            'Authorization': f'OAuth {token}',
        }

    async def _pre_send_request_hook(
            self, request: clients_utils.Request,
    ) -> clients_utils.Request:
        request.headers.update(self._extra_headers)
        return request

    async def on_shutdown(self) -> None:
        await self._session.close()
