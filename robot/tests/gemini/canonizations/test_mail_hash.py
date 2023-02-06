import string
from plugins.gemini import *
from common.libs.plugins.reporter import *
import pytest
from robot.gemini.protos.castor_pb2 import TResultInfo
from google.protobuf.text_format import Merge


def pytest_funcarg__html_config(request):
    return html_config(
        name="two_mail_hash",
        description="""MAIL_HASH <a href="https://st.yandex-team.ru/GEMINI-24">GEMINI-24</a>""",
        directory="canonizations"
    )


def pytest_funcarg__gemini_config(request):
    main_url = {
        "http://lenta.ru/kino/?utm_source=twit": "http://lenta.ru/kino/",
        "http://lenta.ru/kino/": "http://lenta.ru/kino/",
        "http://yandex.ru/catalog/": "http://www.yandex.ru/catalog/",
        "http://www.yandex.ru/catalog/": "http://www.yandex.ru/catalog/",
        "http://yandex.com.tr": "http://www.yandex.com.tr/",
        "http://www.yandex.com.tr": "http://www.yandex.com.tr/"
    }
    def exec_after(gemini):
        gemini.run_pollux([
            "-w1",
            "-le",
            "-m1"
        ])
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

    return gemini_config(main_url, exec_after=exec_after, points_no=2)


def remove_whitespaces(s):
    for c in string.whitespace:
        s = s.replace(c, "")
    return s


def test_mail_hash(gemini, html, narrator):
    html.test(
        name="Request to second pollux",
        suite="Two Polluxes",
        description="Weak type canonization requests"
    )
    for hashes in gemini.hashes:
        for hash in hashes:
            (out, err, retcode) = gemini.geminicl.request(
                type="mail_hash",
                stdin=hash
            )
            pb = TResultInfo()
            Merge(out, pb)

            assert pb.Response.MainUrl[0] == hashes[hash]
            assert pb.Response.OriginalUrl == hash

