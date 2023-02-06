from unittest import mock

import pytest

from checkist.ann import rtapi


class TestRTApiEnv:
    @pytest.fixture
    def make_request(self):
        patcher = mock.patch("checkist.ann.rtapi.make_request")
        yield patcher.start()
        patcher.stop()

    @pytest.fixture
    def settings(self):
        yield mock.Mock(
            robot=mock.Mock(token="mytoken"),
            rt_staging="rt.staging",
        )

    def _assert_make_request(self, make_request, url, method=None, extra_headers=None, json=None):
        kwargs = {}
        if method:
            kwargs["method"] = method
        if json:
            kwargs["json"] = json
        headers = {"Authorization": "OAuth mytoken"}
        if extra_headers:
            headers.update(extra_headers)
        kwargs["headers"] = headers
        make_request.assert_called_with(url, **kwargs)

    @pytest.mark.asyncio
    async def test_staging_nodes(self, make_request, settings):
        make_request.return_value = (
            '[{"Host":"n5.test","DC":"iva","Tags":["weight=0"]},{"Host":"n6.test","DC":"sas","Tags":["weight=0"]}]'
        )
        ret = await rtapi.RTApiEnv.staging_nodes(settings)
        assert ret == [
            {
                "DC": "iva",
                "Host": "n5.test",
                "Tags": ["weight=0"],
            },
            {
                "DC": "sas",
                "Host": "n6.test",
                "Tags": ["weight=0"]
            },
        ]
        self._assert_make_request(make_request, "rt.staging/v1/node?one=True", extra_headers={"X-App-Version": "1"})

    @pytest.mark.asyncio
    async def test_create_on_node(self, make_request, settings):
        pending_resp = (
            '{"EnvID":"6f368b1a-74d3-4643-94c7-57fb80d0d2df","StatusText":"Pending","Status": 42,'
            '"Endpoints":{"RTAPIHost":"n5.test.racktables.yandex-team.ru","RTAPIPort":"12345"}}'
        )
        success_resp = (
            '{"EnvID":"6f368b1a-74d3-4643-94c7-57fb80d0d2df","StatusText":"Running",'
            '"Endpoints":{"RTAPIHost":"n5.test.racktables.yandex-team.ru","RTAPIPort":"12345"}}'
        )
        make_request.side_effect = [pending_resp, success_resp]
        with mock.patch.object(rtapi.RTApiEnv, "RETRY_TIMEOUT", new=0):
            env = await rtapi.RTApiEnv.create_on_node("n5.test.racktables.yandex-team.ru", settings)

        assert env.env_id == "6f368b1a-74d3-4643-94c7-57fb80d0d2df"
        assert env.status == "Running"
        assert env.rtapi_host == "n5.test.racktables.yandex-team.ru"
        assert env.rtapi_port == 12345
        assert env.invapi_url == "https://env-6f368b1a-74d3-4643-94c7-57fb80d0d2df.n5.test.racktables.yandex-team.ru/api"
        assert not env.do_not_delete

    @pytest.mark.asyncio
    async def test_fetch_from_node(self, make_request, settings):
        make_request.return_value = (
            '{"EnvID":"6f368b1a-74d3-4643-94c7-57fb80d0d2df","StatusText":"Running",'
            '"Endpoints":{"RTAPIHost":"n5.test.racktables.yandex-team.ru","RTAPIPort":"12345"}}'
        )

        env = await rtapi.RTApiEnv.fetch_from_node(
            "n5.test.racktables.yandex-team.ru",
            "6f368b1a-74d3-4643-94c7-57fb80d0d2df",
            settings,
        )

        assert env.env_id == "6f368b1a-74d3-4643-94c7-57fb80d0d2df"
        assert env.status == "Running"
        assert env.rtapi_host == "n5.test.racktables.yandex-team.ru"
        assert env.rtapi_port == 12345
        assert env.invapi_url == "https://env-6f368b1a-74d3-4643-94c7-57fb80d0d2df.n5.test.racktables.yandex-team.ru/api"
        assert not env.do_not_delete

        self._assert_make_request(
            make_request,
            "https://n5.test.racktables.yandex-team.ru/v1/env/6f368b1a-74d3-4643-94c7-57fb80d0d2df",
            extra_headers={"X-App-Version": "1"},
        )

    @pytest.mark.asyncio
    async def test_fetch(self, make_request, settings):
        make_request.return_value = (
            '{"EnvID":"6f368b1a-74d3-4643-94c7-57fb80d0d2df","StatusText":"Running",'
            '"Endpoints":{"RTAPIHost":"n5.test.racktables.yandex-team.ru","RTAPIPort":"12345"}}'
        )
        with mock.patch.object(rtapi.RTApiEnv, "staging_nodes", return_value=[{"DC": "iva", "Host": "n5.test"}]):
            env = await rtapi.RTApiEnv.fetch("6f368b1a-74d3-4643-94c7-57fb80d0d2df", settings)

        assert env.env_id == "6f368b1a-74d3-4643-94c7-57fb80d0d2df"
        assert env.status == "Running"
        assert env.rtapi_host == "n5.test.racktables.yandex-team.ru"
        assert env.rtapi_port == 12345
        assert env.invapi_url == "https://env-6f368b1a-74d3-4643-94c7-57fb80d0d2df.n5.test.racktables.yandex-team.ru/api"
        assert not env.do_not_delete

        self._assert_make_request(
            make_request,
            "https://n5.test/v1/env/6f368b1a-74d3-4643-94c7-57fb80d0d2df",
            extra_headers={"X-App-Version": "1"},
        )

    @pytest.mark.asyncio
    async def test_delete(self, make_request, settings):
        env = rtapi.RTApiEnv(
            env_id="6f368b1a-74d3-4643-94c7-57fb80d0d2df",
            status="Running",
            rtapi_host="n5.test.racktables.yandex-team.ru",
            rtapi_port="12345",
            do_not_delete=True,
            settings=settings,
        )

        await env.delete()
        assert not make_request.called

        env.do_not_delete = False
        await env.delete()
        self._assert_make_request(
            make_request,
            "https://n5.test.racktables.yandex-team.ru/v1/env/6f368b1a-74d3-4643-94c7-57fb80d0d2df",
            method="DELETE",
        )


class TestRTApiROProductionEnv:
    @pytest.mark.asyncio
    async def test_create(self):
        env = await rtapi.RTApiROProductionEnv.create(None)
        assert env.env_id == rtapi.RO
        assert env.status == "Running"
        assert env.rtapi_host == "ro.racktables.yandex-team.ru"
        assert env.rtapi_port == 8036
        assert env.invapi_url == "https://ro.racktables.yandex-team.ru/api"
        assert env._settings is None
        assert env.do_not_delete


@pytest.mark.parametrize("document, expected_cls, expected_attrs, must_fail", (
    (
        {
            "env_id": "6f368b1a-74d3-4643-94c7-57fb80d0d2df",
            "status": "Running",
            "rtapi_host": "n5.test.racktables.yandex-team.ru",
            "rtapi_port": "12345",
            "invapi_url": "https://invapi.n5.test.racktables.yandex-team.ru/api",
            "do_not_delete": True,
            "cls": "RTApiEnv",
        },
        rtapi.RTApiEnv,
        {
            "env_id": "6f368b1a-74d3-4643-94c7-57fb80d0d2df",
            "status": "Running",
            "rtapi_host": "n5.test.racktables.yandex-team.ru",
            "rtapi_port": 12345,
            "invapi_url": "https://invapi.n5.test.racktables.yandex-team.ru/api",
            "_settings": None,
            "do_not_delete": True,
        },
        False,
    ),
    (
        {
            "env_id": "6f368b1a-74d3-4643-94c7-57fb80d0d2df",
            "status": "Running",
            "rtapi_host": "n5.test.racktables.yandex-team.ru",
            "rtapi_port": "12345",
            "cls": "RTApiEnv",
        },
        rtapi.RTApiEnv,
        {
            "env_id": "6f368b1a-74d3-4643-94c7-57fb80d0d2df",
            "status": "Running",
            "rtapi_host": "n5.test.racktables.yandex-team.ru",
            "rtapi_port": 12345,
            "invapi_url": "https://env-6f368b1a-74d3-4643-94c7-57fb80d0d2df.n5.test.racktables.yandex-team.ru/api",
            "_settings": None,
            "do_not_delete": False,
        },
        False,
    ),
    (
        {
            "env_id": "ro",
            "status": "Running",
            "rtapi_host": "ro.racktables.yandex-team.ru",
            "rtapi_port": "8036",
            "cls": "RTApiROProductionEnv",
        },
        rtapi.RTApiROProductionEnv,
        {
            "env_id": rtapi.RO,
            "status": "Running",
            "rtapi_host": "ro.racktables.yandex-team.ru",
            "rtapi_port": 8036,
            "invapi_url": "https://ro.racktables.yandex-team.ru/api",
            "_settings": None,
            "do_not_delete": True,
        },
        False,
    ),
    (
        {
            "env_id": "ro",
            "status": "Running",
            "rtapi_host": "ro.racktables.yandex-team.ru",
            "rtapi_port": "8036",
            "cls": "INVALID",
        },
        None,
        None,
        True,
    ),
))
def test_from_document(document, expected_cls, expected_attrs, must_fail):
    if must_fail:
        with pytest.raises(Exception):
            rtapi.from_document(document)
        return

    env = rtapi.from_document(None, document)
    assert isinstance(env, expected_cls)
    for k, v in expected_attrs.items():
        assert getattr(env, k) == v


def test_to_document():
    env = rtapi.RTApiEnv(
        env_id="6f368b1a-74d3-4643-94c7-57fb80d0d2df",
        status="Running",
        rtapi_host="n5.test.racktables.yandex-team.ru",
        rtapi_port=12345,
        invapi_url="https://invapi.n5.test.racktables.yandex-team.ru/api",
        do_not_delete=True,
        settings=None,
    )
    assert rtapi.to_document(env) == {
        "env_id": "6f368b1a-74d3-4643-94c7-57fb80d0d2df",
        "status": "Running",
        "rtapi_host": "n5.test.racktables.yandex-team.ru",
        "rtapi_port": 12345,
        "invapi_url": "https://invapi.n5.test.racktables.yandex-team.ru/api",
        "do_not_delete": True,
        "cls": "RTApiEnv",
    }
