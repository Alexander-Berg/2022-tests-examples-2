import os
import signal
import string
import shutil
import time

from plugins.gemini import *
from common.libs.plugins.reporter import *
from robot.gemini.protos.castor_pb2 import TResultInfo
from google.protobuf.text_format import Merge
from common.libs.plugins.runners import KWProgram
import pytest


def pytest_funcarg__html_config(request):
    return html_config(
        name="empty_base",
        description="""Test checks load empty base""",
        directory="switch"
    )

def pytest_funcarg__gemini_config(request):
    main_url = {
        "http://www.cur.ru/": "http://www.cur.ru/",
        "http://www.yandex.ru/": "http://www.yandex.ru/",
        "http://lenta.ru/kino/?utm_source=twit": "http://lenta.ru/kino/",
        "http://lenta.ru/kino/": "http://lenta.ru/kino/",
        "http://yandex.ru/catalog/": "http://www.yandex.ru/catalog/",
        "http://www.yandex.ru/catalog/": "http://www.yandex.ru/catalog/",
        "http://yandex.com.tr": "http://www.yandex.com.tr",
        "http://www.yandex.com.tr": "http://www.yandex.com.tr"
    }
    def exec_after(gemini):
        gemini.run_pollux([
            "-w2",
            "-le",
            "-m1"
        ])
        gemini.run_castor([
            "-w2",
            "-le",
            "-m1"
        ])
    return gemini_config(main_url, exec_after=exec_after)



def test_empty_base(gemini, narrator, html):

    gemini.castor.stop()
    gemini.pollux.stop()
    for fn in os.listdir(gemini.homeDir + "/BASE/0/cur"):
        fo = open(gemini.homeDir + "/BASE/0/cur" + "/" + fn, "w")
        fo.close()
    try:
        gemini.pollux.run()
    except:
        pass  # pollux should not start here
    gemini.castor.run()

    (out, err, retcode) = gemini.geminicl.request(
        "--running-time-limit=1",
        url="http://www.cur.ru/",
        check_expected_retcode=False
    )

    narrator.pause(60)

    (out, err, retcode) = gemini.geminicl.request(
        "--running-time-limit=3",
        url="http://www.cur.ru/",
        check_expected_retcode=False
    )
    pb = TResultInfo()
    Merge(out, pb)
    expected_response = """
        Response {
          CanonizedUrl: "http://www.cur.ru/"
          MainUrl: "http://www.cur.ru/"
          CanonizationType: WEAK
          Error: ALL_REPLICA_DOWN
        }
        Status: 0"""
    message = "Wrong response from gemini:\n%s" % expected_received_table(expected_response, out)
    assert "Error: ALL_REPLICA_DOWN" in out, message
