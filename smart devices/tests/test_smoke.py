from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import binascii
import logging
import os.path
import py
import pytest
import random
import threading
import yatest.common as yc
import yatest.common.network as ycn
from contextlib import suppress


logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def port():
    yield ycn.PortManager().get_port()


class RequestHandler(BaseHTTPRequestHandler):
    update_data = b"asdfqwerasdf"
    update_num = random.randint(0, 2 ** 64 - 1)
    update_version = "1.48.4.12.849860797.{}".format(update_num)
    update_url = "quasar-{}.zip".format(update_num)
    downloaded_update_name = "update_{}.zip".format(update_version)
    port = None
    update_sent = False

    def set_content_length(self, length):
        self.send_header("Content-Length", str(length))

    def do_GET(self):
        if 'check_updates' in self.requestline:
            if not RequestHandler.update_sent:
                resp_json = """{{
    "crc32":{crc32},
    "critical":true,
    "downloadUrl":"http://localhost:{port}/{update_file}",
    "hasUpdate":true,
    "version":"{update_version}",
    "updateScript":"#!/bin/bash\\ntouch smoke_update_script_applied",
    "updateScriptSign":"lFPr8qbixfSwYrNbuD/Cj+goaNPntGkdo4jv0c0wrfZeY+DWzKvJGYBlMgoj1cIqdlZV1ifPxod2/8E8UrCfjX/EufDOE9E9bBrGJnyyBqryK3H5Dgh6cYEdkKPJHJ2vCIvUiBQ16AGoB2ZM6J4rfahj2yG/ZlwN7lklKM7DOVjOl2vP8ucZJNHpEDi4932B5Dcihp9ADYqUtiDgtzy/7UkS0YuHoR/m2m/AX8vH6xi/dyJfDAwvKuKgkKc1ah1WmrLacXymH0JIIk/qAMrxi1RNhhaQ0WZ+uZ+M7p0rhJsWrWZ4VVrmhlg/O7xnQqp0w3wCg04eLTsH6O6GBzWfLfS8d8s14q57cKlCUSgTOviIIu5UOINkyo49S/X55moa+2sq1ulkN2UjWvmK0wFRO0BxKMINNRhk7OusIdv8llLsoUEjRNsO/L5xO8Gg6hO0Yvex50c48dyeOZH3hjpqgoZyWjcMcwcu3/hxDBBEUItdna36Rwe/viSu/YWkRZT6PJHU2RWJvYMnjcywSbtIpuFrc9gOuHDReY0DDhFTPjay0NoEN+/9gwcN7g3yWfe1V4AcoBsxdq+E104s9n7zunslTViZbgU6NSv3CD1UGEs7QvVwJu4yQ+XrzFYx78JQAQl6ZIDyPqzdwMaxaVQlBTSIW8GJDvsq3dFWsrQNfU4=",
    "updateScriptTimestamp": 1610963855
}}""".format(
                    crc32=binascii.crc32(RequestHandler.update_data),
                    port=RequestHandler.port,
                    update_file=RequestHandler.update_url,
                    update_version=RequestHandler.update_version,
                ).encode(
                    "ascii"
                )
            else:
                resp_json = """{"hasUpdate": false}"""
            content_length = len(resp_json)
            self.send_response(code=200)
            self.set_content_length(content_length)
            self.end_headers()
            self.wfile.write(resp_json)
        else:
            self.send_response(code=200)
            self.set_content_length(len(RequestHandler.update_data))
            self.end_headers()
            self.wfile.write(self.update_data)
            RequestHandler.update_sent = True
        return


@pytest.fixture(scope="class")
def quasmockdrom(port):
    RequestHandler.port = port
    server = ThreadingHTTPServer(('localhost', port), RequestHandler)
    logger.debug('Quasmockdrom starting ...')
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    yield "http://localhost:{}/check_updates".format(port)
    server.shutdown()


@pytest.fixture(scope="function")
def workdir(tmpdir):
    # https://st.yandex-team.ru/DEVTOOLSSUPPORT-5680
    def recursive_mkdir(*args):
        tmp = py.path.local(args[0])
        with suppress(py.error.EEXIST):
            tmp.mkdir()
        for sub in args[1:]:
            tmp = tmp.join(sub)
            with suppress(py.error.EEXIST):
                tmp.mkdir()
        return tmp

    ramDrivePath = yc.output_ram_drive_path()
    if ramDrivePath is None:
        if len(str(tmpdir)) < 90:
            return tmpdir
        else:
            return recursive_mkdir("/tmp", str(random.randint(0, 2 ** 64 - 1)), tmpdir.basename)
    else:
        if len(ramDrivePath) > 90:
            return recursive_mkdir("/tmp", str(random.randint(0, 2 ** 64 - 1)), tmpdir.basename)
        else:
            return recursive_mkdir(ramDrivePath, tmpdir.basename)


def test_smoke(workdir, quasmockdrom):
    updater_bin = yc.binary_path("smart_devices/tools/updater/test_app/test_updater")
    try:
        yc.execute([updater_bin, str(workdir), quasmockdrom], shell=True, timeout=50, cwd=str(workdir))
    except yc.process.ExecutionTimeoutError:
        pass
    assert any(map(lambda x: 'updater_full_update_script' in x, os.listdir(str(workdir))))
    assert any(map(lambda x: 'ca-certificates' in x, os.listdir(str(workdir))))
    assert os.path.exists(workdir.join(RequestHandler.downloaded_update_name))
    assert os.path.exists(workdir.join('/updater.sock'))
    with open(workdir.join(RequestHandler.downloaded_update_name), "rb") as f:
        file_crc32 = binascii.crc32(f.read())
    assert binascii.crc32(RequestHandler.update_data) == file_crc32
    assert os.path.exists(workdir.join(RequestHandler.downloaded_update_name + "_applied"))
    assert os.path.exists(workdir.join("smoke_update_script_applied"))
