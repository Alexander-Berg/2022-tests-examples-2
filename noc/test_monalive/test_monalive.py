import contextlib
import gzip
import os.path
import shutil
import socketserver
import tempfile
import threading
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from unittest.mock import patch

from balancer_agent.operations.systems import monalive

import typing
from typing import Union


class HttpHandler(BaseHTTPRequestHandler):
    FILENAME: str

    def do_GET(self):
        self.send_response(HTTPStatus.OK)
        self.end_headers()

        path = os.path.join(os.path.dirname(__file__), self.FILENAME)
        if self.FILENAME.endswith(".gz"):
            with gzip.open(path, "rb") as f:
                shutil.copyfileobj(f, self.wfile)
        else:
            with open(path, "rb") as f:
                shutil.copyfileobj(f, self.wfile)


class UnixHTTPServer(socketserver.UnixStreamServer):
    def __init__(self, server_address: Union[str, bytes], handler) -> None:
        super().__init__(server_address, handler)
        self._x = threading.Thread(target=self.handle_request, daemon=True)

    def get_request(self):
        request, client_address = self.socket.accept()
        if len(client_address) == 0:
            client_address = (self.server_address,)
        return (request, client_address)

    def __enter__(self):
        super().__enter__()
        self._x.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        super().__exit__(exc_type, exc_val, exc_tb)
        self._x.join()


@contextlib.contextmanager
def make_socket(handler_class) -> typing.ContextManager[monalive.Monalive]:
    with tempfile.TemporaryDirectory() as tmpdirname:
        socket = os.path.join(tmpdirname, "monalive.sock")
        with UnixHTTPServer(socket, handler_class):
            with patch("balancer_agent.operations.systems.monalive.SOCK_ADDRESS", socket):
                with monalive.Monalive() as m:
                    yield m


def test_get_some_statuses():
    class H(HttpHandler):
        FILENAME = "sample.json"

    with make_socket(H) as m:
        status: monalive.StatusResponse = m.get_status()

    assert len(status["conf"]) == 4


def test_get_alot_of_statuses():
    class H(HttpHandler):
        FILENAME = "huge.json.gz"

    with make_socket(H) as m:
        cur = time.monotonic()
        status: monalive.StatusResponse = m.get_status()
        elapsed = time.monotonic() - cur

    assert len(status["conf"]) == 1448
    assert elapsed < 0.6
