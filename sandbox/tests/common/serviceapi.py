import collections
import json
import socket
import threading as th

import six
import pytest
from six.moves.urllib import parse as urlparse


def remap_query(query, save_query=False):
    limit = int(query.pop("limit", [1])[0])
    offset = int(query.pop("offset", [0])[0])

    if "order" in query:
        query.pop("order")

    if save_query:
        query["limit"] = limit
        query["offset"] = offset

    return query, offset, limit


class ServiceAPIHandler(six.moves.BaseHTTPServer.BaseHTTPRequestHandler):
    def get_list_query(self):
        query = urlparse.parse_qs(urlparse.urlparse(self.path).query)
        if "limit" not in query:
            raise KeyError("Limit required")
        return query

    def send_ok_response(self, response):
        self.send_response(six.moves.http_client.OK)
        self.send_header("Content-Length", str(len(response)))
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(six.ensure_binary(response))

    def send_error_response(self, code, ex):
        self.send_response(code)
        self.send_header("Content-Length", str(len(str(ex))))
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(six.ensure_binary(str(ex)))

    def create_list_response(self, data, offset, limit):
        return {
            "items": data,
            "offset": offset,
            "limit": limit,
            "total": len(data)
        }

    def get_empty_response(self):
        response = json.dumps({})
        self.send_ok_response(response)

    def get_resources(self):
        try:
            query = self.get_list_query()
            query, offset, limit = remap_query(query)
            data = self.server.get_data(query, offset, limit, "resources")
            response = json.dumps(self.create_list_response(data, offset, limit))
            self.send_ok_response(response)
        except Exception as ex:
            self.send_error_response(six.moves.http_client.BAD_REQUEST, ex)

    def get_resource(self):
        try:
            query = {"id": self.path.split("/")[-1]}
            response = json.dumps(self.server.get_data(query, 0, 1, "resources")[0])
            self.send_ok_response(response)
        except Exception as ex:
            self.send_error_response(six.moves.http_client.BAD_REQUEST, ex)

    def post_resource(self, data):
        try:
            response = json.dumps(self.server.post_data(data, "resources"))
            self.send_ok_response(response)
        except Exception as ex:
            self.send_error_response(six.moves.http_client.BAD_REQUEST, ex)

    def get_current_user(self):
        try:
            token = self.headers.get("Authorization")
            query = {"token": token}
            data = self.server.get_data(query, 0, 1, "users")[0]
            data.pop("id", None)
            data.pop("token", None)
            response = json.dumps(data)
            self.send_ok_response(response)
        except Exception as ex:
            self.send_error_response(six.moves.http_client.BAD_REQUEST, ex)

    def post_user(self, data):
        try:
            response = json.dumps(self.server.post_data(data, "users"))
            self.send_ok_response(response)
        except Exception as ex:
            self.send_error_response(six.moves.http_client.BAD_REQUEST, ex)

    GET_HANDLERS_PREFIX = (
        ("/api/v1.0/resource/", get_resource),
        ("/api/v1.0/resource", get_resources),
        ("/api/v1.0/service/banned_networks", get_empty_response),
        ("/api/v1.0/service/banned_resources", get_empty_response),
        ("/api/v1.0/service/whitelist_resources", get_empty_response),
        ("/api/v1.0/user/current", get_current_user)
    )

    POST_HANDLERS_PREFIX = (
        ("/api/v1.0/resource", post_resource),
        ("/api/v1.0/user", post_user),
    )

    def do_GET(self):
        for prefix, func in self.GET_HANDLERS_PREFIX:
            if self.path.startswith(prefix):
                func(self)
                return
        self.send_error_response(six.moves.http_client.NOT_FOUND, "Method not found")

    def do_POST(self):
        content_length = self.headers.get("Content-Length")
        if content_length is not None:
            content_length = int(content_length)
        data = six.ensure_str(self.rfile.read(content_length))
        content_type = self.headers.get("Content-Type")
        if content_type and content_type.startswith("application/json"):
            data = json.loads(data)
        for prefix, func in self.POST_HANDLERS_PREFIX:
            if self.path.startswith(prefix):
                func(self, data)
                return
        self.send_error_response(six.moves.http_client.NOT_FOUND, "Method not found")


class ServiceAPISimulator(six.moves.BaseHTTPServer.HTTPServer):
    address_family = socket.AF_INET6

    def __init__(self, *args, **kws):
        self.storage = collections.defaultdict(list)
        six.moves.BaseHTTPServer.HTTPServer.__init__(self, *args, **kws)

    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        six.moves.BaseHTTPServer.HTTPServer.server_bind(self)

    def get_data(self, query, offset, limit, collection):
        result = []
        for obj in self.storage[collection]:
            if limit <= 0:
                break
            is_result = True
            for key, value in query.items():
                if str(obj.get("key")) in value:
                    is_result = False
                    break
            if is_result:
                if offset <= 0:
                    result.append(obj)
                    limit -= 1
                else:
                    offset -= 1
        return result

    def post_data(self, data, collection):
        data["id"] = len(self.storage[collection]) + 1
        self.storage[collection].append(data)
        return data


@pytest.fixture
def serviceapi_simulator(request, serviceapi_port, config_path, monkeypatch):
    server = ServiceAPISimulator(("localhost", serviceapi_port), ServiceAPIHandler)
    server_thread = th.Thread(target=server.serve_forever)
    server_thread.setDaemon(True)
    server_thread.start()

    def finalizer():
        server.shutdown()
        server.server_close()
        server_thread.join()

    request.addfinalizer(finalizer)
    return server
