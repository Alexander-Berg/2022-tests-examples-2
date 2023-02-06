import string
from plugins.gemini import *
from common.libs.plugins.reporter import *
import pytest
from robot.gemini.protos.castor_pb2 import TResultInfo
from google.protobuf.text_format import Merge


def pytest_funcarg__html_config(request):
    return html_config(
        name="restart",
        description="",
        directory="smoke"
    )

def pytest_funcarg__gemini_config(request):
    main_url = {
        "http://lenta.ru/kino/?utm_source=twit": "http://lenta.ru/kino/",
        "http://lenta.ru/kino/": "http://lenta.ru/kino/",
        "http://yandex.ru/catalog/": "http://www.yandex.ru/catalog/",
        "http://www.yandex.ru/catalog/": "http://www.yandex.ru/catalog/",
        "http://yandex.com.tr": "http://www.yandex.com.tr",
        "http://www.yandex.com.tr": "http://www.yandex.com.tr"
    }
    def exec_after(gemini):
        gemini.run_pollux([
            "-w1",
            "-le",
            "-m1"
        ])
        gemini.run_castor([
            "-w1",
            "-le",
            "-m1"
        ])

    return gemini_config(main_url, exec_after=exec_after)


def remove_whitespaces(s):
    for c in string.whitespace:
        s = s.replace(c, "")
    return s


@pytest.mark.skipif("True")
def test_restart_pollux(gemini, html):
    html.test(
        name="Pollux",
        suite="Restart",
        description=""
    )

    gemini.pollux.stop(kill=True)
    gemini.pollux.run()

    gemini.geminicl.request(
        url="http://lenta.ru/kino/?utm_source=twit",
        type="weak",
    )


@pytest.mark.skipif("True")
def test_restart_castor(gemini, html):
    html.test(
        name="Pollux",
        suite="Restart",
        description=""
    )

    gemini.castor.stop()
    gemini.castor.run()

    gemini.geminicl.request(
        url="http://lenta.ru/kino/?utm_source=twit",
        type="weak",
    )
