import string
from plugins.gemini import *
from common.libs.plugins.reporter import *
import pytest
from robot.gemini.protos.castor_pb2 import TResultInfo
from google.protobuf.text_format import Merge


def pytest_funcarg__html_config(request):
    return html_config(
        name="two_polluxes",
        description="""Smoke test. Starts castor and two polluxes, makes geminicl requests""",
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


def test_second_pollux(gemini, html):
    html.test(
        name="Request to second pollux",
        suite="Two Polluxes",
        description="Weak type canonization requests"
    )
    (out, err, retcode) = gemini.geminicl.request(
        url="http://lenta.ru/kino/?utm_source=twit",
        type="weak",
    )
    pb = TResultInfo()
    Merge(out, pb)
    expected = """
    Response {
      OriginalUrl: "http://lenta.ru/kino/?utm_source=twit"
      CanonizedUrl: "http://lenta.ru/kino/?utm_source=twit"
      MainUrl: "http://lenta.ru/kino/"
      CanonizationType: WEAK
      BaseInfo {
        IndexTimestamp: 1364188709
        MirrorsTimestamp: 1363264068
        RflTimestamp: 1363593273
      }
    }
    Status: 0
    """
    message = "Wrong response from gemini:\n%s" % expected_received_table(expected, out)
    assert pb.Response.OriginalUrl == "http://lenta.ru/kino/?utm_source=twit", message
    assert pb.Response.CanonizedUrl == "http://lenta.ru/kino/?utm_source=twit", message
    assert pb.Response.MainUrl[0] == "http://lenta.ru/kino/", message
    assert pb.Response.HasField("BaseInfo"), message
    assert len(pb.Response.MainUrl) == 1, message

    stats = gemini.polluxes[0].get_sensors().RequestStats
    html.comment(
        header="First pollux sensors",
        message="<pre>%s</pre>" % str(stats)
    )
    assert stats.NUrlRequests == 0

    stats = gemini.polluxes[1].get_sensors().RequestStats
    html.comment(
        header="Second pollux sensors",
        message="<pre>%s</pre>" % str(stats)
    )
    assert stats.NUrlRequests == 1
    stats = gemini.castor.get_sensors().GlobalStats.ReqCount
    html.comment(
        header="Castor sensors",
        message="<pre>%s</pre>" % str(stats)
    )
    assert stats.NumReq == 1


def test_first_pollux(gemini, html):
    html.test(
        name="Request to first pollux",
        suite="Two Polluxes",
        description="Weak type canonization requests"
    )
    (out, err, retcode) = gemini.geminicl.request(
        url="http://www.yandex.ru/catalog/",
        type="strong",
        )
    pb = TResultInfo()
    Merge(out, pb)
    expected = """
     Response {
       OriginalUrl: "http://www.yandex.ru/catalog/"
       CanonizedUrl: "http://www.yandex.ru/catalog/"
       MainUrl: "http://www.yandex.ru/catalog/"
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
    assert pb.Response.OriginalUrl == "http://www.yandex.ru/catalog/", message
    assert pb.Response.CanonizedUrl == "http://www.yandex.ru/catalog", message
    assert pb.Response.MainUrl[0] == "http://www.yandex.ru/catalog/", message
    assert pb.Response.HasField("BaseInfo"), message
    assert len(pb.Response.MainUrl) == 1, message

    stats = gemini.polluxes[0].get_sensors().RequestStats
    html.comment(
        header="First pollux sensors",
        message="<pre>%s</pre>" % str(stats)
    )
    assert stats.NUrlRequests == 1

    stats = gemini.polluxes[1].get_sensors().RequestStats
    html.comment(
        header="Second pollux sensors",
        message="<pre>%s</pre>" % str(stats)
    )
    assert stats.NUrlRequests == 1

    stats = gemini.castor.get_sensors().GlobalStats.ReqCount
    html.comment(
        header="Castor sensors",
        message="<pre>%s</pre>" % str(stats)
    )
    assert stats.NumReq == 2

