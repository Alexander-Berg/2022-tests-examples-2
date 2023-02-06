import logging
import thread
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer


class S(BaseHTTPRequestHandler):
    def do_POST(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write("{}")


class MdsRunner:
    def __init__(self, server_class=HTTPServer, handler_class=S):
        server_address = ('', 0)
        self._httpd = server_class(server_address, handler_class)

    def _run(self):
        logger = logging.getLogger("mds_run_logger")
        logger.info("running server on port: {}".format(self._httpd.server_port))
        thread.start_new_thread(self._httpd.serve_forever, ())

    def mds_server_port(self):
        return self._httpd.server_port

    def shutdown_mds_server(self):
        logger = logging.getLogger("mds_run_logger")
        logger.info("Shutting down web server")
        self._httpd.shutdown()

    def startup_mds_server(self):
        logger = logging.getLogger("mds_run_logger")
        logger.info("Starting web server")
        self._run()
