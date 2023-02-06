from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from aiohttp import web
from http import HTTPStatus

from urllib.parse import urlparse
from yarl import URL

from rtnmgr_agent.anc import AncClient


class AncClientTestCase(AioHTTPTestCase):
    async def get_application(self):
        async def mapping(request):
            return web.Response(text=f"{request.url}")

        app = web.Application()
        app.router.add_get("/mapping", mapping)
        return app

    @unittest_run_loop
    async def test_successful(self):
        c = AncClient("http://localhost:60888", self.client)
        # return relative URL
        c._build_url = lambda int_ip, ext_ip: f"/mapping?internal_ip={int_ip}&external_ip={ext_ip}"

        status, body = await c.apply_mapping("1.2.3.4", "5.6.7.8")
        assert HTTPStatus.OK == status

        url = urlparse(body)
        assert c._build_url("1.2.3.4", "5.6.7.8") == "%s?%s" % (url.path, url.query)
