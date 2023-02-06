import six
import json
import pytest
import threading


# noinspection PyPep8Naming
class ABCSimulatorHandler(six.moves.BaseHTTPServer.BaseHTTPRequestHandler):
    DATA = json.dumps({"results": [{"id": "1"}]})
    MEMBERS_DATA = json.dumps({"results": [{"person": {"login": "test-rest-user"}}]})

    def do_GET(self):
        result = self.DATA
        if self.path.startswith("/services/members/") or self.path.startswith("/services/responsibles/"):
            result = self.MEMBERS_DATA

        self.send_response(six.moves.http_client.OK)
        self.send_header("Content-Length", len(result))
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(six.ensure_binary(result))

    def do_POST(self):
        self.send_response(six.moves.http_client.OK)
        self.send_header("Content-Length", len(self.DATA))
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(six.ensure_binary((self.DATA)))


class ABCSimulator(six.moves.BaseHTTPServer.HTTPServer):
    def __init__(self, *args, **kwargs):
        six.moves.BaseHTTPServer.HTTPServer.__init__(self, *args, **kwargs)


@pytest.fixture
def abc_simulator(request, abc_port, config_path):
    server = ABCSimulator(("localhost", abc_port), ABCSimulatorHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.setDaemon(True)
    server_thread.start()

    def finalizer():
        server.shutdown()
        server.server_close()
        server_thread.join()

    request.addfinalizer(finalizer)
    return server
