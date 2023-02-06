import string
from plugins.gemini import *
from common.libs.plugins.reporter import *
import pytest
from robot.gemini.protos.castor_pb2 import TResultInfo
from google.protobuf.text_format import Merge


def pytest_funcarg__html_config(request):
    return html_config(
        name="index",
        description="""https://jira.yandex-team.ru/browse/ROBOT-3142""",
        directory="canonizations"
    )

def prepare(self):
    self.create_configs()
    self.prepare_mainurl()

    was = open(
        os.path.join(self.homeDir, "BASE/0/cur/weak_hash_2_main_url"),
        "r"
    ).read()

    new = open(
        os.path.join(self.homeDir, "BASE/0/cur/weak_hash_2_main_url"),
        "w"
    )
    new.write(was.replace("http://www.ya.ru/", "http://www.ya.ru/weak"))
    new.close()

    new = open(
        os.path.join(self.homeDir, "BASE/0/cur/strong_hash_2_main_url"),
        "w"
    )
    new.write(was.replace("http://www.ya.ru/", "http://www.ya.ru/strong"))
    new.close()

    self.create_index()

    self._prepare()



def pytest_funcarg__gemini_config(request):
    main_url = {
        "http://www.ya.ru/": "http://www.ya.ru/",
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

    return gemini_config(main_url, exec_after=exec_after, initializer=prepare)


def remove_whitespaces(s):
    for c in string.whitespace:
        s = s.replace(c, "")
    return s


def test_weak(gemini, html):
    html.test(
        name="Weak",
        suite="geminicl",
        description="Weak type canonization request for http://lenta.ru/kino/?utm_source=twit"
    )
    (out, err, retcode) = gemini.geminicl.request(
        url="http://www.ya.ru/",
        type="weak",
    )
    pb = TResultInfo()
    Merge(out, pb)
    expected = """
    Response {
      OriginalUrl: "http://www.ya.ru/"
      CanonizedUrl: "http://www.ya.ru/"
      MainUrl: "http://www.ya.ru/weak"
      CanonizationType: WEAK
      Region: "UNK"
      BaseInfo {
        IndexTimestamp: 1363781920
        MirrorsTimestamp: 1363781920
        RflTimestamp: 1363781920
      }
    }
    Status: 0
    """
    message = "Wrong response from gemini:\n%s" % expected_received_table(expected, out)
    assert "CanonizationType: WEAK" in out, message
    assert pb.Response.OriginalUrl == "http://www.ya.ru/", message
    assert pb.Response.CanonizedUrl == "http://www.ya.ru/", message
    assert pb.Response.MainUrl[0] == "http://www.ya.ru/weak", message


def test_strong(gemini, html):
    html.test(
        name="Strong",
        suite="geminicl",
        description="Strong type canonization request for http://lenta.ru/kino/?utm_source=twit"
    )
    (out, err, retcode) = gemini.geminicl.request(
        url="http://www.ya.ru/",
        type="strong",
    )
    pb = TResultInfo()
    Merge(out, pb)
    expected = """
    Response {
      OriginalUrl: "http://www.ya.ru/"
      CanonizedUrl: "http://www.ya.ru/"
      MainUrl: "http://www.ya.ru/weak"
      CanonizationType: STRONG
      Region: "UNK"
      BaseInfo {
        IndexTimestamp: 1363781920
        MirrorsTimestamp: 1363781920
        RflTimestamp: 1363781920
      }
    }
    Status: 0
    """
    message = "Wrong response from gemini:\n%s" % expected_received_table(expected, out)
    assert "CanonizationType: STRONG" in out, message
    assert pb.Response.OriginalUrl == "http://www.ya.ru/", message
    assert pb.Response.CanonizedUrl == "http://www.ya.ru/", message
    assert pb.Response.MainUrl[0] == "http://www.ya.ru/weak", message
