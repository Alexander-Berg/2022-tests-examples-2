from __future__ import absolute_import, division, unicode_literals

import json
import time
import uuid
import functools

import six
import mock
import pytest
import requests
import responses

from six.moves import urllib

from sandbox.common import auth as common_auth
from sandbox.common import enum
from sandbox.common import rest
from sandbox.common.types import misc as ctm


BASE_URL = "https://test-url.ru"
TEST_TOKEN = "test-token"


@pytest.fixture(scope="function")
def rest_client():
    return rest.Client(base_url=BASE_URL)


def get_path(request):
    query = urllib.parse.urlparse(request.url)
    return query.path


def get_params(request):
    query = urllib.parse.urlparse(request.url).query
    params = {}
    for key, value in six.iteritems(urllib.parse.parse_qs(query)):
        if len(value) == 1:
            params[key] = value.pop()
        else:
            params[key] = value
    return params


class MultipleResponses(object):
    """ Request callback for more than one response on a single endpoint """

    def __init__(self, responses):
        self.responses = iter(responses)

    def __call__(self, request):
        return (207, {}, json.dumps(next(self.responses)))


class TestREST(object):

    def test__misc(self, rest_client):
        assert rest_client.api.resource.DEFAULT_INTERVAL == rest_client.DEFAULT_INTERVAL

    def test__settings(self, monkeypatch):
        try:
            from sandbox.common import config
        except ImportError:
            return

        class MockedSettings(object):
            def __call__(self):
                settings = mock.MagicMock()
                settings.this.id = "mocked-client"
                settings.client.rest_url = BASE_URL
                return settings

        monkeypatch.setattr(config, "Registry", MockedSettings())

        # make sure the correct URL is configured
        with responses.RequestsMock() as mk:
            mk.add("GET", BASE_URL + "/api", json={}, status=200)
            rest.Client(total_wait=1).api.read()

    def test__normalize_params(self):

        class Foo(enum.Enum):
            enum.Enum.lower_case()
            enum.Enum.preserve_order()
            ONE = None
            TWO = None
            THREE = None

        assert rest.normalize_params({"enum": Foo}) == {"enum": ["one", "two", "three"]}
        assert rest.normalize_params({"dict": {"foo": "bar"}}) == {"dict": ['{"foo": "bar"}']}

    def test__get(self, rest_client):

        def request_callback(request):
            return (200, {}, json.dumps([request.method, get_params(request)]))

        url = BASE_URL + "/api/resource"
        with responses.RequestsMock() as mk:
            mk.add_callback("GET", url, callback=request_callback, content_type='application/json')

            # No query parameters

            assert rest_client.api.resource[:] == ["GET", {}]
            assert rest_client.api.resource[...] == ["GET", {}]
            assert rest_client.api.resource.read() == ["GET", {}]

            # With query parameters

            with pytest.raises(ValueError):
                assert rest_client.api.resource["foo", 0:10]

            assert rest_client.api.resource[20:10] == ["GET", {"offset": "20", "limit": "10"}]
            assert rest_client.api.resource[20:10:"-id"] == ["GET", {"offset": "20", "limit": "10", "order": "-id"}]

            resp = rest_client.api.resource[{"offset": 20, "limit": 10}]
            assert resp == ["GET", {"offset": "20", "limit": "10"}]

            resp = rest_client.api.resource[{"type": "OTHER_RESOURCE"}, : 10: "state"]
            assert resp == ["GET", {"type": "OTHER_RESOURCE", "limit": "10", "order": "state"}]

            resp = rest_client.api.resource.read({"offset": 20, "limit": 10})
            assert resp == ["GET", {"offset": "20", "limit": "10"}]

            resp = rest_client.api.resource.read(type="OTHER_RESOURCE", limit=10, order="state")
            assert resp == ["GET", {"type": "OTHER_RESOURCE", "limit": "10", "order": "state"}]

            resp = rest_client.api.resource.read({"foo": {"some_dict": "aaa"}})
            assert resp == ["GET", {"foo": '{"some_dict": "aaa"}'}]

            class YetAnoterIterable(object):
                """ Custom non-list sequence type """
                def __iter__(self):
                    return iter(["a", "b", "c", "d"])

            resp = rest_client.api.resource.read({"foo": YetAnoterIterable()})
            assert resp == ["GET", {"foo": ["a", "b", "c", "d"]}]

        with responses.RequestsMock() as mk:
            mk.add_callback("GET", BASE_URL + "/resource", callback=request_callback, content_type='application/json')
            assert rest_client.resource[:] == ["GET", {}]
            assert rest_client.resource[...] == ["GET", {}]
            assert rest_client.resource.read() == ["GET", {}]

    def test__request(self, rest_client):

        def request_callback(request):
            return (200, {}, json.dumps([request.method, get_params(request)]))

        def raw_request(**kwargs):
            return rest_client._request(requests.get, "/resource", **kwargs).json()

        with responses.RequestsMock() as mk:
            mk.add_callback("GET", BASE_URL + "/resource", callback=request_callback, content_type='application/json')

            assert raw_request(params={}) == ["GET", {}]
            assert raw_request(params={"params": {"foo": {"a": 42}}}) == ["GET", {"foo": '{"a": 42}'}]
            assert raw_request(params={"params": {"foo": 42}}) == ["GET", {"foo": "42"}]
            assert raw_request(params={"params": {"foo": iter(["a", "b"])}}) == ["GET", {"foo": ["a", "b"]}]

    def test__post(self, rest_client):

        class Data(object):
            def __getstate__(self):
                return {"data": 42}

        def request_callback(request):
            return (201, {}, json.dumps([request.method, json.loads(request.body), get_params(request)]))

        data = {"field": "val", "field2": [{"a": "b"}]}
        url = BASE_URL + "/api/resource"
        with responses.RequestsMock() as mk:
            mk.add_callback("POST", url, callback=request_callback, content_type='application/json')
            assert rest_client.api.resource(data) == ["POST", data, {}]
            assert rest_client.api.resource.create(**data) == ["POST", data, {}]
            assert rest_client.api.resource.create(data) == ["POST", data, {}]
            assert rest_client.api.resource.create(data, params={"foo": "42"}) == ["POST", data, {"foo": "42"}]
            assert rest_client.api.resource.create(params={"foo": "42"}, bar=41) == ["POST", None, {"foo": "42"}]
            assert rest_client.api.resource.create(Data()) == ["POST", Data().__getstate__(), {}]

            with pytest.raises(TypeError):
                assert rest_client.api.resource.create(object())

    def test__put(self, rest_client):

        def request_callback(request):
            return (200, {}, json.dumps([request.method, json.loads(request.body), get_params(request)]))

        data = {"field": "val"}

        url = BASE_URL + "/api/resource"
        with responses.RequestsMock() as mk:
            mk.add_callback("PUT", url, callback=request_callback, content_type='application/json')

            rest_client.api.resource = data
            assert mk.calls[-1].response.json() == ["PUT", data, {}]
            assert rest_client.api.resource.update(data) == ["PUT", data, {}]
            assert rest_client.api.resource.update(params={"foo": "bar"}) == ["PUT", None, {"foo": "bar"}]
            assert rest_client.api.resource.update(data, params={"foo": "bar"}) == ["PUT", data, {"foo": "bar"}]
            assert rest_client.api.resource.update(**data) == ["PUT", data, {}]

        url = BASE_URL + "/api/resource/1234"
        with responses.RequestsMock() as mk:
            mk.add_callback("PUT", url, callback=request_callback, content_type='application/json')
            rest_client.api.resource[1234] = data
            assert mk.calls[-1].response.json() == ["PUT", data, {}]

    def test__delete(self, rest_client):
        rest_client.debug = True  # just to cover this code branch, we do not test the logging here
        resource_id = 123
        path = "{}/{}/{}".format(BASE_URL, "resource", resource_id)

        def request_callback(request):
            return (204, {}, json.dumps([request.method, json.loads(request.body), get_params(request)]))

        with responses.RequestsMock() as mk:
            mk.add_callback("DELETE", path, callback=request_callback)

            del rest_client.resource[resource_id]
            assert mk.calls[-1].response.json() == ["DELETE", {}, {}]

            rest_client.resource[resource_id].delete()
            assert mk.calls[-1].response.json() == ["DELETE", {}, {}]

            rest_client.resource[resource_id].delete({"foo": "bar"})
            assert mk.calls[-1].response.json() == ["DELETE", {"foo": "bar"}, {}]

            rest_client.resource[resource_id].delete({"foo": "bar"}, params={"a": "b"})
            assert mk.calls[-1].response.json() == ["DELETE", {"foo": "bar"}, {"a": "b"}]

            rest_client.resource[resource_id].delete(params={"a": "b"})
            assert mk.calls[-1].response.json() == ["DELETE", None, {"a": "b"}]

    def test__path_builder(self, rest_client):
        path = "{}/resource/123/attribute/attr1".format(BASE_URL)

        with responses.RequestsMock() as mk:
            mk.add("GET", path, status=200, json={}, content_type='application/json')
            rest_client.resource[123].attribute["attr1"].read()
            assert mk.calls[-1].request.url == path

    @pytest.mark.parametrize("auth", (TEST_TOKEN, common_auth.OAuth(TEST_TOKEN)))
    def test__authentication(self, auth):
        oauth_rest_client = rest.Client(base_url=BASE_URL, auth=auth)

        url = BASE_URL + "/resource"
        with responses.RequestsMock() as mk:
            mk.add("GET", url, status=200, json={}, content_type="application/json")
            oauth_rest_client.resource.read()
            assert ("Authorization", "OAuth {}".format(TEST_TOKEN)) in set(mk.calls[-1].request.headers.items())

    def test__component(self):
        rest_client = rest.Client(base_url=BASE_URL, component="foobar")

        with responses.RequestsMock() as mk:
            mk.add("GET", BASE_URL + "/resource", status=200, json={}, content_type="application/json")
            rest_client.resource.read()
            assert mk.calls[-1].request.headers[ctm.HTTPHeader.COMPONENT] == "foobar"

    def test__send_headers(self, rest_client):

        headers = rest.Client.HEADERS({"FOO": "1", "BAR": "2"})
        headers["BUZ"] = "3"

        with pytest.raises(ValueError):
            rest_client << {}

        rest_client = rest_client << headers

        with responses.RequestsMock() as mk:
            mk.add("GET", "{}/resource".format(BASE_URL), status=200, json={}, content_type="application/json")
            rest_client.resource.read()

            assert set(headers.headers.request.items()) <= set(mk.calls[-1].request.headers.items())

    def test__read_headers(self, rest_client):

        headers = rest.Client.HEADERS()

        with pytest.raises(ValueError):
            rest_client >> {}

        rest_client = rest_client >> headers

        def request_callback(_):
            return (200, {"FOO": "1", "BAR": "2"}, "")

        with responses.RequestsMock() as mk:
            mk.add_callback("GET", "{}/resource".format(BASE_URL), callback=request_callback)
            rest_client.resource.read()
            assert headers["FOO"] == "1"
            assert headers["BAR"] == "2"

    @pytest.mark.skip(reason="Flaky")
    def test__client_reset(self):
        rest_client = rest.Client()
        new_default_interval = 100
        new_default_timeout = 100

        rest_client.DEFAULT_INTERVAL = new_default_interval
        rest_client.DEFAULT_TIMEOUT = new_default_timeout
        rest_client.reset()

        assert rest_client.interval == new_default_interval
        assert rest_client.timeout == new_default_timeout

    def test__http_error(self, rest_client):

        with responses.RequestsMock() as mk:
            mk.add("GET", url=BASE_URL + "/api/resource", json={"error": "errmsg"}, status=404)

            with pytest.raises(rest_client.HTTPError) as exc_info:
                assert rest_client.api.resource[:]

            assert exc_info.value.status == 404
            assert "404" in str(exc_info.value)
            assert "errmsg" in str(exc_info.value)

    def test__reset_content(self, rest_client):

        with responses.RequestsMock() as mk:
            mk.add("GET", url=BASE_URL + "/api/resource", status=205)
            assert rest_client.api.resource[:] == rest_client.RESET

    def test__retry_and_timeout(self):
        rest_client = rest.Client(base_url=BASE_URL, total_wait=0.1, min_timeout=0.1, min_interval=0.1)

        def request_callback(_):
            time.sleep(0.5)
            return (503, {}, "")

        url = BASE_URL + "/api/resource"
        with responses.RequestsMock() as mk:
            mk.add_callback("GET", url, callback=request_callback)

            with pytest.raises(rest_client.TimeoutExceeded):
                rest_client.api.resource.read()

    def test__dispatchedclient(self):

        threadlocal_client = rest.ThreadLocalCachableClient(BASE_URL)
        with rest.DispatchedClient:
            assert rest.DispatchedClient(BASE_URL) is threadlocal_client

        with rest.DispatchedClient as dispatch:
            dispatch(functools.partial(rest.Client, ua="some-user-agent"))
            assert rest.DispatchedClient(BASE_URL).ua == "some-user-agent"

    def test__rest_client_callback_usage(self, monkeypatch, rest_client):
        reqs = []

        def callback(req):
            assert isinstance(req, rest.Client.Request)
            status_code = req.response.status_code if req.response else None
            assert status_code is None or isinstance(status_code, int)
            reqs.append(req)

        monkeypatch.setattr(rest.Client, "request_callback", staticmethod(callback))

        # regular requests
        path = "{}/resource/123/attribute/attr1".format(BASE_URL)

        with responses.RequestsMock() as mk:
            mk.add("GET", path, status=200, json={}, content_type="application/json")
            rest_client.resource[123].attribute["attr1"].read()
            assert len(reqs) == 1

            mk.add("POST", path, status=201, json={}, content_type="application/json")
            rest_client.resource[123].attribute["attr1"].create(key="value")
            assert len(reqs) == 2

            mk.add("PUT", path, status=204, json={}, content_type="application/json")
            rest_client.resource[123].attribute["attr1"].update(key="value")
            assert len(reqs) == 3

            mk.add("DELETE", path, status=200, json={}, content_type="application/json")
            rest_client.resource[123].attribute["attr1"].delete()
            assert len(reqs) == 4

        rest_client.DEFAULT_TIMEOUT = 0
        rest_client.DEFAULT_INTERVAL = 0

        # various errors

        def success_on_second_retry(request):
            """
            :type request: requests.PreparedRequest
            """
            if ctm.HTTPHeader.RETRY_REASON in request.headers:
                return (200, {}, "")
            else:
                return (503, {}, "")

        before_exceptions = 6
        with responses.RequestsMock() as mk:
            mk.add_callback("GET", path, callback=success_on_second_retry)

            rest_client.resource[123].attribute["attr1"].read()
            assert len(reqs) == before_exceptions  # two requests were made

        def raiser(exc):
            def inner(_):
                raise exc
            return inner

        exceptions_to_test = [
            (requests.HTTPError(response=mock.Mock(status_code=requests.codes.GONE)), rest_client.SessionExpired),
            (RuntimeError("Unhandled exception"), RuntimeError),
        ]
        for iteration, (exception, expected) in enumerate(exceptions_to_test, start=1):
            with responses.RequestsMock() as mk:
                mk.add_callback("GET", path, callback=raiser(exception))
                with pytest.raises(expected):
                    rest_client.resource[123].attribute["attr1"].read()

                assert len(reqs) == before_exceptions + iteration

        # batch requests

        batched_requests_count = 3

        def loose_callback(_):
            response_data = {
                "status": 200,
                "headers": {},
                "body": {"status": "OK"}
            }
            return (200, [], json.dumps([response_data for __ in range(batched_requests_count)]))

        batch_path = "{}/api/v2/batch".format(BASE_URL)
        with responses.RequestsMock() as mk:
            mk.add_callback("PUT", batch_path, callback=loose_callback)
            with rest.Batch(rest_client) as batch:
                futures = [
                    batch.resource[123].attribute["attr1"].create(key="value"),
                    batch.resource[123].attribute["attr1"].read(),
                    batch.resource[123].attribute["attr1"].update(key="value"),
                ]
                assert None not in futures
                assert len(futures) == batched_requests_count

        assert set(_.exception() for _ in futures) == {None}
        assert len(reqs) == before_exceptions + len(exceptions_to_test) + 1

    def test__batch(self, rest_client):

        resps = [
            {"status": 200, "response": {"status": "ok"}, "headers": {"FOO": "42"}},
            {"status": 404, "response": {"status": "error"}},
        ]

        with responses.RequestsMock() as mk:
            mk.add("PUT", BASE_URL + "/api/v2/batch", json=resps)

            with rest.Batch(rest_client) as batch:
                futures = [
                    batch.resource[1].read(foo="bar"),
                    batch.resource[2](foo="bar")
                ]

                with pytest.raises(rest.BatchFuture.NotReadyError):
                    futures[0].result()

                with pytest.raises(rest.BatchFuture.NotReadyError):
                    futures[0].raw_result()

                with pytest.raises(rest.BatchFuture.NotReadyError):
                    futures[0].exception()

            ok, error = futures

            assert 'GET' in repr(ok)
            assert ok.result() == {"status": "ok"}
            assert ok.raw_result() == {"status": 200, "response": {"status": "ok"}, "headers": {"FOO": "42"}}

            with pytest.raises(rest.Client.HTTPError):
                error.result()

            assert isinstance(error.exception(), rest.Client.HTTPError)

    def test__batch_retry(self, rest_client):

        callback = MultipleResponses([
            [{"status": 200, "response": {"ok": 1}}, {"status": 503, "response": {"status": "error"}}],
            [{"status": 200, "response": {"ok": 2}}]
        ])

        with responses.RequestsMock() as mk:
            mk.add_callback("PUT", BASE_URL + "/api/v2/batch", callback=callback, content_type='application/json')

            with rest.Batch(rest_client) as batch:
                futures = [batch.resource[1].read(), batch.resource[2]()]

            assert [f.result() for f in futures] == [{"ok": 1}, {"ok": 2}]

    def test__batch_redirect(self, rest_client):

        callback = MultipleResponses([
            [
                {"status": 200, "response": {"ok": 1}},
                {"status": 301, "response": {}, "headers": {"Location": BASE_URL + "/some/url"}},
                {"status": 424},
            ],
            [{"status": 200, "response": {"ok": 2}}, {"status": 200, "response": {"ok": 3}}],
        ])

        with responses.RequestsMock() as mk:
            mk.add_callback("PUT", BASE_URL + "/api/v2/batch", callback=callback, content_type='application/json')

            with rest.Batch(rest_client) as batch:
                futures = [batch.resource[1].read(), batch.resource[2](), batch.resource[2].update()]

            assert [f.result() for f in futures] == [{"ok": 1}, {"ok": 2}, {"ok": 3}]

    def test__task_token(self):
        token = uuid.uuid4().hex
        auth = common_auth.OAuth(token)

        rest_client = rest.Client()
        assert rest_client.task_token is None

        rest_client = rest.Client(auth=auth)
        assert rest_client.task_token is None

        auth = common_auth.Session(token, None)
        rest_client = rest.Client(auth=auth)
        assert rest_client.task_token is None

        auth = common_auth.Session(None, token)
        rest_client = rest.Client(auth=auth)
        assert rest_client.task_token == token
