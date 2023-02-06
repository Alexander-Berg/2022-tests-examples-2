import signal
import string
from plugins.gemini import *
from common.libs.plugins.reporter import *
import robot.gemini.protos.castor_pb2 as castor_pb2
from google.protobuf import text_format
import pytest
import commands

def pytest_funcarg__html_config(request):
    return html_config(
        name="start_stop_daemon",
        description="""Smoke test. Starts castor and pollux, stops them""",
        directory="smoke"
    )


def remove_whitespaces(s):
    for c in string.whitespace:
        s = s.replace(c, "")
    return s


def pytest_funcarg__gemini_config(request):
    main_url = {
        "http://ya.ru": "http://yandex.ru",
        "http://yandex.ru/": "http://yandex.ru/",
        "http://lenta.ru/kino/?utm_source=twit": "http://lenta.ru/kino/",
        "http://lenta.ru/kino/": "http://lenta.ru/kino/",
        "http://yandex.ru/catalog/": "http://www.yandex.ru/catalog/",
        "http://www.yandex.ru/catalog/": "http://www.yandex.ru/catalog/",
        "http://yandex.com.tr": "http://www.yandex.com.tr",
        "http://www.yandex.com.tr": "http://www.yandex.com.tr"
    }
    def exec_after(gemini):
        gemini.run_pollux(
            [
                "-w2",
                "-le",
                "-m1"
            ],
            daemon=True
        )
        gemini.run_castor(
            [
                "-w2",
                "-le",
                "-m1"
            ],
            daemon=True
        )

    return gemini_config(main_url, initializer=None, exec_after=exec_after)


def request(gemini):
    (out, err, retcode) = gemini.geminicl.request(
        url="http://yandex.ru/"
    )
    expected_response = """
        Response {
            OriginalUrl: "http://yandex.ru/"
            CanonizedUrl: "http://www.yandex.ru/"
            MainUrl: "http://yandex.ru/"
            CanonizationType: WEAK
            Version: "%d:%d:%d"
        }
        Status: 0
    """
    err_msg = "Wrong response from geminicl!\n" + expected_received_table(expected_response, out)
    assert "Status: 0" in out, err_msg


def test_start_stop(gemini, narrator, html):
    assert gemini.castor.daemon.poll() is not None
    assert gemini.pollux.daemon.poll() is not None
    request(gemini)


def test_sighup_pollux(gemini, html, narrator):
    html.comment(header="Sending SIGHUP to pollux", message="")
    commands.getoutput("kill -SIGHUP " + gemini.pollux.pid)
    narrator.pause(2)
    request(gemini)


def test_sighup_castor(gemini, html, narrator):
    html.comment(header="Sending SIGHUP to castor", message="")
    commands.getoutput("kill -SIGHUP " + gemini.castor.pid)
    narrator.pause(2)
    request(gemini)


def test_sigpipe_pollux(gemini, html, narrator):
    html.comment(header="Sending SIGPIPE to pollux", message="")
    commands.getoutput("kill -SIGPIPE " + gemini.pollux.pid)
    narrator.pause(2)
    request(gemini)


def test_sigpipe_castor(gemini, html, narrator):
    html.comment(header="Sending SIGPIPE to castor", message="")
    commands.getoutput("kill -SIGPIPE " + gemini.castor.pid)
    narrator.pause(2)
    request(gemini)

