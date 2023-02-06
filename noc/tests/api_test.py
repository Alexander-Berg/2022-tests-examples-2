from abc import ABCMeta, abstractmethod
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from aiohttp import web
import json
from http import HTTPStatus
from pytest import raises
from urllib.parse import urlparse, urljoin
from yarl import URL

from rtnmgr_agent.api import ApiClient, Mapping


class AioHTTPTestMeta(metaclass=ABCMeta):
    TEST_ROTATE_MANAGER_SERVER = "https://rtnmgr-test.tt.yandex-team.ru"

    NEW_MAPPING_URL = "/api/v2.0/rotation/instances/default/lb/localhost/new"
    EXIST_MAPPING_URL = "/api/v2.0/rotation/instances/default/lb/localhost/last-applied"

    @abstractmethod
    async def get_application(self):
        pass


class ApiClientTestCase(AioHTTPTestCase, AioHTTPTestMeta):
    async def get_application(self):
        async def url_handler(request):
            return web.Response(text=f"{request.url}")

        app = web.Application()
        app.router.add_get(self.NEW_MAPPING_URL, url_handler)
        app.router.add_get(self.EXIST_MAPPING_URL, url_handler)

        return app

    @unittest_run_loop
    async def test_url(self):
        c = ApiClient(self.TEST_ROTATE_MANAGER_SERVER, {}, "localhost", self.client)

        # return relative URL
        c._build_url = lambda: f"/api/v2.0/rotation/instances/default/lb/localhost/"

        assert urljoin(c._build_url(), "new") == c.new_mappings_url
        assert urljoin(c._build_url(), "last-applied") == c.exist_mappings_url

        with raises(AttributeError):
            Mapping.NON_EXIST_RANDOM_ATTRIBUTE

        status, _ = await c.get_mappings("random")
        assert HTTPStatus.BAD_REQUEST == status

        status, body = await c.get_mappings(Mapping.NEW)
        assert HTTPStatus.OK == status
        assert c.new_mappings_url == urlparse(body).path

        status, body = await c.get_mappings(Mapping.EXIST)
        assert HTTPStatus.OK == status
        assert c.exist_mappings_url == urlparse(body).path


class ApiClientJSONTestCase(AioHTTPTestCase, AioHTTPTestMeta):
    JSON_EXAMPLE = """{
    "random_int_value": 200,
    "random_bool_value": true,
    "random_list_str_value": [
        "hello",
        "world"
    ]
}"""

    async def get_application(self):
        async def url_handler(request):
            return web.Response(text=self.JSON_EXAMPLE)

        app = web.Application()
        app.router.add_get(self.NEW_MAPPING_URL, url_handler)
        app.router.add_get(self.EXIST_MAPPING_URL, url_handler)

        return app

    @unittest_run_loop
    async def test_validator(self):
        c = ApiClient(self.TEST_ROTATE_MANAGER_SERVER, {}, "localhost", self.client)

        # return relative URL
        c._build_url = lambda: f"/api/v2.0/rotation/instances/default/lb/localhost/"

        status, answer = await c.get_json(Mapping.NEW)
        assert HTTPStatus.OK == status
        assert json.loads(self.JSON_EXAMPLE) == answer


class ApiClientJSONErrorTestCase(AioHTTPTestCase, AioHTTPTestMeta):
    async def get_application(self):
        async def url_handler(request):
            return web.Response(text="")

        app = web.Application()
        app.router.add_get(self.NEW_MAPPING_URL, url_handler)
        app.router.add_get(self.EXIST_MAPPING_URL, url_handler)

        return app

    @unittest_run_loop
    async def test_json_error(self):
        c = ApiClient(self.TEST_ROTATE_MANAGER_SERVER, {}, "localhost", self.client)

        # return relative URL
        c._build_url = lambda: f"/api/v2.0/rotation/instances/default/lb/localhost/"

        status, answer = await c.get_json(Mapping.NEW)
        assert HTTPStatus.INTERNAL_SERVER_ERROR == status
        assert answer.get("get_json_error", None) is not None


class ApiClientPutTestCase(AioHTTPTestCase, AioHTTPTestMeta):
    async def get_application(self):
        async def url_handler(request):
            return web.Response(text=f"{request.url}")

        app = web.Application()
        app.router.add_put("/api/v2.0/rotation/instances/default/lb/localhost/1", url_handler)

        return app

    @unittest_run_loop
    async def test_put(self):
        c = ApiClient(self.TEST_ROTATE_MANAGER_SERVER, {}, "localhost", self.client)

        # return relative URL
        c._build_rotation_id_url = lambda id: f"/api/v2.0/rotation/instances/default/lb/localhost/{id}"

        status, body = await c.confirm("1")
        assert HTTPStatus.OK == status
        assert c._build_rotation_id_url(1) == urlparse(body).path
