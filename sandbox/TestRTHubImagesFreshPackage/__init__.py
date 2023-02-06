# coding: utf-8
import binascii
import logging
import os
import platform
import subprocess
import thread
from os.path import join as pj

from sandbox import sdk2
from sandbox import common
from sandbox.common.platform import get_arch_from_platform
from sandbox.sandboxsdk.network import wait_port_is_free
from sandbox.projects.rthub.TestRTHubCommon import RTHubImagesTestTask

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

DEFAULT_TVM_DAEMON_PORT = 15424
DEFAULT_MDS_PORT = 13000


class MdsRunner:
    def __init__(self, server_address, handler_class):
        self._httpd = HTTPServer(server_address, handler_class)
        self._logger = logging.getLogger("mds_run_logger")

    def shutdown(self):
        self._logger.info("Shutting down web server")
        self._httpd.shutdown()

    def start(self):
        self._logger.info("Starting web server")
        self._logger.info("running server on port: {}".format(self._httpd.server_port))
        thread.start_new_thread(self._httpd.serve_forever, ())


class MdsMockHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.protocol_version = 'HTTP/1.1'
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write("""
        {
            "group-id": 3964,
            "imagename": "2a00000170ea620c4108627cea4652c84a93",
            "meta": {
                "crc64": "9F4419C007084F11",
                "expires-at": "Thu, 19 Mar 2020 21:24:19 GMT",
                "md5": "317ca97f12a7d7f8c1d4371c8ce29cb9",
                "modification-time": 1584480259,
                "orig-animated": false,
                "orig-format": "JPEG",
                "orig-orientation": "0",
                "orig-size": {
                    "x": 1680,
                    "y": 1050
                },
                "orig-size-bytes": 243508,
                "processed_by_computer_vision": false,
                "processed_by_computer_vision_description": "computer vision is disabled",
                "processing": "finished"
            },
            "sizes": {
                "n_13": {
                    "height": 1050,
                    "path": "/get-fast-images/3964/2a00000170ea620c4108627cea4652c84a93/n_13",
                    "width": 1680
                },
                "orig": {
                    "height": 1050,
                    "path": "/get-fast-images/3964/2a00000170ea620c4108627cea4652c84a93/orig",
                    "width": 1680
                }
            }
        }""")


class TestRTHubImagesFreshPackage(RTHubImagesTestTask):

    def get_config_path(self, test_dir):
        return pj(test_dir, "conf/conf-production/images-fresh.pb.txt")

    def get_tvmtool(self):
        current_arch = get_arch_from_platform(platform.platform())
        resource = sdk2.Resource.find(type="TVM_TOOL_BINARY", arch=current_arch).first()
        return str(sdk2.ResourceData(resource).path)

    def run_rthub(self, pkg_dir, cfg, test_data, output_dir):
        if not wait_port_is_free(port=DEFAULT_TVM_DAEMON_PORT):
            raise SandboxTaskFailureError("Tvmtool daemon port=%d is busy" % DEFAULT_TVM_DAEMON_PORT)

        if not wait_port_is_free(port=DEFAULT_MDS_PORT):
            raise SandboxTaskFailureError("Mds port=%d is busy" % DEFAULT_MDS_PORT)

        tvmtool_conf = """
        {
            "BbEnvType": 0,
            "clients": {
                "images_avatars_upload": {
                    "secret": "fake_secret",
                    "dsts": {
                        "avatars": {
                            "dst_id": 2002150
                        }
                    }
                }
            }
        }
        """
        tvmtool_conf_path = pj(pj(os.getcwd(), 'rthub_test'), "tvm.conf")
        with open(tvmtool_conf_path, "w+") as f:
            f.write(tvmtool_conf)

        os.environ["QLOUD_TVM_TOKEN"] = binascii.hexlify(os.urandom(16))
        os.environ["TVM_DAEMON_PORT"] = str(DEFAULT_TVM_DAEMON_PORT)
        os.environ["MDS_SERVER_NAME"] = "localhost"

        mds = MdsRunner(("localhost", DEFAULT_MDS_PORT), handler_class=MdsMockHandler)
        with sdk2.helpers.ProcessLog(self, logger='custom_tvmtool') as tl:
            logging.info("Running: {}".format(self.get_tvmtool()))
            tvm = subprocess.Popen([self.get_tvmtool(), "-c", tvmtool_conf_path, "--port", str(DEFAULT_TVM_DAEMON_PORT), "-u"], stdout=tl.stdout, stderr=tl.stdout)
            mds.start()

            RTHubImagesTestTask.run_rthub(self, pkg_dir, cfg, test_data, output_dir)

            mds.shutdown()
            tvm.kill()

