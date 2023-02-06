import string
from plugins.gemini import *
from common.libs.plugins.reporter import *
import pytest
from robot.gemini.protos.castor_pb2 import TResultInfo
from robot.gemini.protos.base_pb2 import *
from google.protobuf.text_format import Merge


def pytest_funcarg__html_config(request):
    return html_config(
        name="geminicl",
        description="""Smoke test. Starts castor and pollux, makes geminicl requests from
                    http://wiki.yandex-team.ru/robot/newDesign/dups/userguide/geminicl""",
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


def test_weak(gemini, html):
    html.test(
        name="Weak",
        suite="geminicl",
        description="Weak type canonization request for http://lenta.ru/kino/?utm_source=twit"
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
    assert len(pb.Response.MainUrl) == 1, message


def test_weak_text(gemini, html):
    html.test(
        name="Weak",
        suite="geminicl",
        description="Weak type canonization request for http://lenta.ru/kino/?utm_source=twit (--format=text)"
    )
    (out, err, retcode) = gemini.geminicl.request(
        url="http://lenta.ru/kino/?utm_source=twit",
        type="weak",
        format="text"
    )
    assert "http://lenta.ru/kino/?utm_source=twit\thttp://lenta.ru/kino/?utm_source=twit\thttp://lenta.ru/kino/" in out
    assert "Url not found in base." not in out
    assert "Url not found in base." not in err


def test_weak_text_url_not_found(gemini, html):
    html.test(
        name="Weak (--format=text, url is not in base)",
        suite="geminicl",
        description="Weak type canonization request for http://lenta.ru/fake (--format=text, url is not in base)"
    )
    (out, err, retcode) = gemini.geminicl.request(
        url="http://lenta.ru/fake",
        type="weak",
        format="text"
    )
    assert "http://lenta.ru/fake\thttp://lenta.ru/fake\thttp://lenta.ru/fake" in out
    assert "Url not found in base." not in out
    assert "Url not found in base." not in err


def test_search_doc_id(gemini, html):
    html.test(
        name="search_doc_id",
        suite="geminicl",
        description="https://st.yandex-team.ru/GEMINI-60"
    )
    (out, err, retcode) = gemini.geminicl.request(
        url="http://lenta.ru/kino/?utm_source=twit",
        type="search_doc_id",
    )
    pb = TResultInfo()
    Merge(out, pb)
    expected = """
    Response {
      OriginalUrl: "http://lenta.ru/kino/?utm_source=twit"
      CanonizedUrl: "http://lenta.ru/kino/?utm_source=twit"
      MainUrl: "Z94EF4F928318DAC6"
      CanonizationType: SEARCH_DOC_ID
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
    assert pb.Response.MainUrl[0] == "Z94EF4F928318DAC6", message
    assert len(pb.Response.MainUrl) == 1, message

    (out, err, retcode) = gemini.geminicl.request(
        url="http://lenta.ru/fake",
        type="search_doc_id",
    )
    pb = TResultInfo()
    Merge(out, pb)
    expected = """
    Response {
      OriginalUrl: "http://lenta.ru/fake"
      CanonizedUrl: "http://lenta.ru/fake"
      MainUrl: "Z0946CE7C2CD7BB7C"
      CanonizationType: SEARCH_DOC_ID
      Error: URL_NOT_FOUND
    }
    Status: 0
    """
    message = "Wrong response from gemini:\n%s" % expected_received_table(expected, out)
    assert pb.Response.OriginalUrl == "http://lenta.ru/fake", message
    assert pb.Response.CanonizedUrl == "http://lenta.ru/fake", message
    assert pb.Response.MainUrl[0] == "Z0946CE7C2CD7BB7C", message
    assert pb.Response.Error == URL_NOT_FOUND, message
    assert len(pb.Response.MainUrl) == 1, message

    (out, err, retcode) = gemini.geminicl.request(
        url="lenta.ru",
        type="search_doc_id",
    )
    pb = TResultInfo()
    Merge(out, pb)
    expected = """
    Response {
      OriginalUrl: "lenta.ru"
      Error: BAD_URL
    }
    Status: 0
    """
    message = "Wrong response from gemini:\n%s" % expected_received_table(expected, out)
    assert pb.Response.OriginalUrl == "lenta.ru", message
    assert pb.Response.Error == BAD_URL, message
    assert len(pb.Response.MainUrl) == 0, message


def test_weak_text_url_not_found_err(gemini, html):
    html.test(
        name="Weak (--format=text --reveal-url-not-found, not in base)",
        suite="geminicl",
        description="Weak type canonization request for http://lenta.ru/fake (--format=text --reveal-url-not-found, url is not in base)"
    )
    (out, err, retcode) = gemini.geminicl.request(
        "--url=http://lenta.ru/fake",
        "--type=weak",
        "--format=text",
        "--reveal-url-not-found",
    )
    assert "http://lenta.ru/fake\thttp://lenta.ru/fake\thttp://lenta.ru/fake" in err
    assert "Url not found in base." in err

def test_weak_stdin(gemini, html):
    html.test(
        name="Weak (urls from stdin)",
        suite="geminicl",
        description="Weak type canonization request for http://lenta.ru/fake (--format=text --reveal-url-not-found, url is not in base)"
    )
    (out, err, retcode) = gemini.geminicl.request(
        stdin="http://lenta.ru/kino/?utm_source=twit",
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
    assert len(pb.Response.MainUrl) == 1, message

    (out, err, retcode) = gemini.geminicl.request(
        stdin="http://lenta.ru/kino/?utm_source=twit\nhttp://lenta.ru/fake",
    )

    res1, res2 = out.split("\n\n")[:2]

    if "http://lenta.ru/fake" in res1:
        res1, res2 = res2, res1

    pb = TResultInfo()
    Merge(res1, pb)
    message = "Wrong response from gemini:\n%s" % expected_received_table(expected, res1)
    assert pb.Response.OriginalUrl == "http://lenta.ru/kino/?utm_source=twit", message
    assert pb.Response.CanonizedUrl == "http://lenta.ru/kino/?utm_source=twit", message
    assert pb.Response.MainUrl[0] == "http://lenta.ru/kino/", message
    assert len(pb.Response.MainUrl) == 1, message

    pb = TResultInfo()
    Merge(res2, pb)
    expected = """
        Response {
          OriginalUrl: "http://lenta.ru/fake"
          CanonizedUrl: "http://lenta.ru/fake"
          MainUrl: "http://lenta.ru/fake"
          CanonizationType: WEAK
          Error: URL_NOT_FOUND
        }
        Status: 0
        """
    message = "Wrong response from gemini:\n%s" % expected_received_table(expected, res2)
    assert pb.Response.OriginalUrl == "http://lenta.ru/fake", message
    assert pb.Response.CanonizedUrl == "http://lenta.ru/fake", message
    assert pb.Response.MainUrl[0] == "http://lenta.ru/fake", message
    assert pb.Response.Error == URL_NOT_FOUND, message
    assert len(pb.Response.MainUrl) == 1, message





def test_strong(gemini, html):
    html.test(
        name="Strong",
        suite="geminicl",
        description="Strong type canonization request for http://lenta.ru/kino/?utm_source=twit"
    )
    (out, err, retcode) = gemini.geminicl.request(
        url="http://lenta.ru/kino/?utm_source=twit",
        type="strong",
        )
    pb = TResultInfo()
    Merge(out, pb)
    expected = """
        Response {
          OriginalUrl: "http://lenta.ru/kino/?utm_source=twit"
          CanonizedUrl: "http://lenta.ru/kino/?utm_source=twit"
          MainUrl: "http://lenta.ru/kino/"
          CanonizationType: STRONG
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
    assert len(pb.Response.MainUrl) == 1, message


def test_empty(gemini, html):
    html.test(
        name="Empty",
        suite="geminicl",
        description="Empty type canonization request for http://lenta.ru/kino/?utm_source=twit"
    )
    (out, err, retcode) = gemini.geminicl.request(
        url="http://lenta.ru/kino/?utm_source=twit",
        type="empty",
        )
    pb = TResultInfo()
    Merge(out, pb)
    expected = """
        Response {
          OriginalUrl: "http://lenta.ru/kino/?utm_source=twit"
          StorageType: ST_ROBOT
          CanonizationType: EMPTY
        }
        Status: 0
        """
    message = "Wrong response from gemini:\n%s" % expected_received_table(expected, out)
    assert pb.Response.OriginalUrl == "http://lenta.ru/kino/?utm_source=twit", message
    assert pb.Response.CanonizationType == EMPTY
    assert not pb.Response.HasField("CanonizedUrl"), message
    assert len(pb.Response.MainUrl) == 0, message


def test_empty_not_in_base(gemini, html):
    html.test(
        name="Empty",
        suite="geminicl",
        description="Empty type canonization request for http://lenta.ru/not_in_base"
    )
    (out, err, retcode) = gemini.geminicl.request(
        url="http://lenta.ru/not_in_base",
        type="empty",
        )
    pb = TResultInfo()
    Merge(out, pb)
    expected = """
        Response {
          OriginalUrl: "http://lenta.ru/not_in_base"
          StorageType: ST_ROBOT
          CanonizationType: EMPTY
        }
        Status: 0
        """
    message = "Wrong response from gemini:\n%s" % expected_received_table(expected, out)
    assert pb.Response.OriginalUrl == "http://lenta.ru/not_in_base", message
    assert pb.Response.CanonizationType == EMPTY
    assert not pb.Response.HasField("CanonizedUrl"), message
    assert len(pb.Response.MainUrl) == 0, message


def test_mirror(gemini, html):
    html.test(
        name="Mirror",
        suite="geminicl",
        description="Mirror type canonization request for http://yandex.ru/catalog/"
    )
    (out, err, retcode) = gemini.geminicl.request(
        url="http://yandex.ru/catalog/",
        type="mirror",
        )
    pb = TResultInfo()
    Merge(out, pb)
    expected = """
    Response {
     OriginalUrl: "http://yandex.ru/catalog/"
     MainMirror: "http://www.yandex.ru/catalog/"
     CanonizationType: MIRROR
    }
    Status: 0
        """
    message = "Wrong response from gemini:\n%s" % expected_received_table(expected, out)
    assert pb.Response.OriginalUrl == "http://yandex.ru/catalog/", message
    assert pb.Response.MainMirror == "http://www.yandex.ru/catalog/", message


def test_mirror_test(gemini, html):
    html.test(
        name="Mirror Test",
        suite="geminicl",
        description="Mirror type canonization request for http://yandex.ru/catalog/"
    )
    (out, err, retcode) = gemini.geminicl.request(
        url="http://yandex.ru/catalog/",
        type="mirror_test",
        )
    pb = TResultInfo()
    Merge(out, pb)
    expected = """
    Response {
     OriginalUrl: "http://yandex.ru/catalog/"
     MainMirror: "http://www.yandex.ru/catalog/"
     CanonizationType: MIRROR
    }
    Status: 0
        """
    message = "Wrong response from gemini:\n%s" % expected_received_table(expected, out)
    assert pb.Response.OriginalUrl == "http://yandex.ru/catalog/", message
    assert pb.Response.MainMirror == "http://www.yandex.ru/catalog/", message


def test_mirror_new(gemini, html):
    html.test(
        name="Mirror New",
        suite="geminicl",
        description="Mirror type canonization request for http://yandex.ru/catalog/"
    )
    (out, err, retcode) = gemini.geminicl.request(
        url="http://yandex.ru/catalog/",
        type="mirror_new",
        )
    pb = TResultInfo()
    Merge(out, pb)
    expected = """
    Response {
     OriginalUrl: "http://yandex.ru/catalog/"
     MainMirror: "http://www.yandex.ru/catalog/"
     CanonizationType: MIRROR
    }
    Status: 0
        """
    message = "Wrong response from gemini:\n%s" % expected_received_table(expected, out)
    assert pb.Response.OriginalUrl == "http://yandex.ru/catalog/", message
    assert pb.Response.MainMirror == "http://www.yandex.ru/catalog/", message


def test_mirror_group(gemini, html):
    html.test(
        name="MirrorGroup",
        suite="geminicl",
        description="MirrorGroup type canonization request for http://yandex.com.tr"
    )
    (out, err, retcode) = gemini.geminicl.request(
        url="http://yandex.ru",
        type="mirror_group",
        )
    pb = TResultInfo()
    Merge(out, pb)
    expected = """
    Response {
     OriginalUrl: "http://yandex.ru"
     MirrorGroup: "www.yandex.ru"
     MirrorGroup: "yandex.ru"
     MirrorGroup: "xn--d1acpjx3f.xn--p1ai"
     CanonizationType: MIRROR_GROUP
    }
    Status: 0
        """
    message = "Wrong response from gemini:\n%s" % expected_received_table(expected, out)

    mirrors = [
        "www.yandex.ru",
        "yandex.ru",
        "xn--d1acpjx3f.xn--p1ai"
    ]

    assert pb.Response.OriginalUrl == "http://yandex.ru", message
    assert pb.Response.MirrorGroup == mirrors, message


def test_host(gemini, html):
    html.test(
        name="Host",
        suite="geminicl",
        description="Host type canonization request for http://yandex.ru/catalog/"
    )
    (out, err, retcode) = gemini.geminicl.request(
        url="http://yandex.ru/catalog/",
        type="host",
        )
    pb = TResultInfo()
    Merge(out, pb)
    expected = """
    Response {
     OriginalUrl: "http://yandex.ru/catalog/"
     Host: "www.yandex.ru"
     CanonizationType: HOST
    }
    Status: 0
        """

    message = "Wrong response from gemini:\n%s" % expected_received_table(expected, out)
    assert pb.Response.OriginalUrl == "http://yandex.ru/catalog/", message
    assert pb.Response.Host == "www.yandex.ru", message


def test_owner(gemini, html):
    html.test(
        name="Owner",
        suite="geminicl",
        description="Owner type canonization request for http://widgets.yandex.ru/catalog/"
    )
    (out, err, retcode) = gemini.geminicl.request(
        url="http://widgets.yandex.ru/catalog/",
        type="owner",
        )
    pb = TResultInfo()
    Merge(out, pb)
    expected = """
    Response {
     OriginalUrl: "http://widgets.yandex.ru/catalog/"
     Owner: "yandex.ru"
     CanonizationType: OWNER
    }
    Status: 0
        """

    message = "Wrong response from gemini:\n%s" % expected_received_table(expected, out)
    assert pb.Response.OriginalUrl == "http://widgets.yandex.ru/catalog/", message
    assert pb.Response.Owner == "yandex.ru", message

