from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from http import HTTPStatus

from rtnmgr_agent.monitoring import WebMonitoring


class ApiClientPutTestCase(AioHTTPTestCase):
    async def get_application(self):
        return WebMonitoring("localhost", 8080).get_app()

    @unittest_run_loop
    async def test_handler(self):
        request = await self.client.request("GET", "/api/v1.0/status")
        assert HTTPStatus.OK == request.status
        assert "OK" in await request.text()
