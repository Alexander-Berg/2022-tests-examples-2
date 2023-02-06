import string
from plugins.gemini import *
from common.libs.plugins.reporter import *
import pytest
from robot.gemini.protos.castor_pb2 import TResultInfo
from robot.gemini.protos.base_pb2 import *
from google.protobuf.text_format import Merge


def pytest_funcarg__html_config(request):
    return html_config(
        name="multilang",
        description="""Smoke test. Starts castor and pollux, makes geminicl requests from
                    http://wiki.yandex-team.ru/robot/newDesign/dups/userguide/geminicl""",
        directory="multilang"
    )


def pytest_funcarg__gemini_config(request):
    main_url = {
        # default and TUR
        "http://lenta.ru/kino/?utm_source=twit": "http://lenta.ru/kino/",
        "http://lenta.ru/kino/": "http://lenta.ru/kino/",
        "TUR@http://lenta.ru/kino/?utm_source=twit": "TUR@http://lenta.ru/tur/",
        "TUR@http://lenta.ru/tur/": "TUR@http://lenta.ru/tur/",
        "USA@http://lenta.ru/kino/?utm_source=twit": "USA@http://lenta.ru/usa/",

        # UNK and TUR
        "http://www.yandex.ru/catalog/": "http://www.yandex.ru/catalog/",
        "TUR@http://www.yandex.ru/catalog/": "TUR@http://www.yandex.ru/catalog/tur/",

        # TUR only
        "TUR@http://yandex.com.tr/": "TUR@http://www.yandex.com.tr/",
        "TUR@http://www.yandex.com.tr/": "TUR@http://www.yandex.com.tr/",

        # default only
        "http://www.yandex.ru/default/": "http://www.yandex.ru/default/",


        # UNK only
        "http://www.yandex.ru/unk/": "http://www.yandex.ru/unk/",

        # not multilang
        "http://nothing.com/": "http://www.nothing.com/"


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


def test_unk(gemini, html):
    html.test(
        name="UNK",
        suite="multilang",
        description=""
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
      Region: "UNK"
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
    assert pb.Response.IsMultilang, message
    assert pb.Response.Region == "UNK", message
    assert len(pb.Response.MainUrl) == 1, message

def test_rus(gemini, html):
    html.test(
        name="RUS",
        suite="multilang",
        description=""
    )
    (out, err, retcode) = gemini.geminicl.request(
        url="http://lenta.ru/kino/?utm_source=twit",
        type="weak",
        region="RUS"
    )
    pb = TResultInfo()
    Merge(out, pb)
    expected = """
    Response {
      OriginalUrl: "http://lenta.ru/kino/?utm_source=twit"
      CanonizedUrl: "http://lenta.ru/kino/?utm_source=twit"
      MainUrl: "http://lenta.ru/kino/"
      CanonizationType: WEAK
      Region: "RUS"
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
    assert pb.Response.IsMultilang, message
    assert pb.Response.Region == "RUS", message
    assert len(pb.Response.MainUrl) == 1, message


def test_tur(gemini, html):
    html.test(
        name="TUR",
        suite="multilang",
        description=""
    )
    (out, err, retcode) = gemini.geminicl.request(
        url="http://lenta.ru/kino/?utm_source=twit",
        type="weak",
        region="TUR"
    )
    pb = TResultInfo()
    Merge(out, pb)
    expected = """
    Response {
      OriginalUrl: "http://lenta.ru/kino/?utm_source=twit"
      CanonizedUrl: "http://lenta.ru/kino/?utm_source=twit"
      MainUrl: "http://lenta.ru/tur/"
      CanonizationType: WEAK
      Region: "tur"
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
    assert pb.Response.MainUrl[0] == "http://lenta.ru/tur/", message
    assert pb.Response.Region == "TUR", message
    assert pb.Response.IsMultilang, message
    assert len(pb.Response.MainUrl) == 1, message


def test_tur_only(gemini, html):
    html.test(
        name="TUR only in mainurl",
        suite="multilang",
        description=""
    )
    (out, err, retcode) = gemini.geminicl.request(
        url="http://yandex.com.tr/",
        type="weak",
        region="tur"
    )
    pb = TResultInfo()
    Merge(out, pb)
    expected = """
    Response {
      OriginalUrl: "http://yandex.com.tr/"
      CanonizedUrl: "http://yandex.com.tr/"
      MainUrl: "http://www.yandex.com.tr/"
      CanonizationType: WEAK
      Region: "TUR"
      BaseInfo {
        IndexTimestamp: 1364188709
        MirrorsTimestamp: 1363264068
        RflTimestamp: 1363593273
      }
    }
    Status: 0
    """
    message = "Wrong response from gemini:\n%s" % expected_received_table(expected, out)
    assert pb.Response.OriginalUrl == "http://yandex.com.tr/", message
    assert pb.Response.CanonizedUrl == "http://yandex.com.tr/", message
    assert pb.Response.MainUrl[0] == "http://www.yandex.com.tr/", message
    assert pb.Response.Region == "TUR", message
    assert pb.Response.IsMultilang, message
    assert len(pb.Response.MainUrl) == 1, message


def test_no_region_tur(gemini, html):
    html.test(
        name="No --region and TUR only in mainurl",
        suite="multilang",
        description=""
    )
    (out, err, retcode) = gemini.geminicl.request(
        url="http://yandex.com.tr/",
        type="weak",
    )
    pb = TResultInfo()
    Merge(out, pb)
    expected = """
    Response {
      OriginalUrl: "http://yandex.com.tr/"
      CanonizedUrl: "http://yandex.com.tr/"
      MainUrl: "http://yandex.com.tr/"
      IsMultilang: true
      StorageType: ST_ROBOT
      CanonizationType: WEAK
      Region: "UNK"
      Error: URL_NOT_FOUND
    }
    Status: 0
    """
    message = "Wrong response from gemini:\n%s" % expected_received_table(expected, out)
    assert pb.Response.OriginalUrl == "http://yandex.com.tr/", message
    assert pb.Response.CanonizedUrl == "http://yandex.com.tr/", message
    assert pb.Response.MainUrl[0] == "http://yandex.com.tr/", message
    assert pb.Response.Region == "UNK", message
    assert pb.Response.IsMultilang, message
    assert pb.Response.Error == URL_NOT_FOUND, message
    assert len(pb.Response.MainUrl) == 1, message


def test_rus_from_tur(gemini, html):
    html.test(
        name="--region=RUS and TUR only in mainurl",
        suite="multilang",
        description=""
    )
    (out, err, retcode) = gemini.geminicl.request(
        url="http://yandex.com.tr/",
        type="weak",
        region="RUS"
    )
    pb = TResultInfo()
    Merge(out, pb)
    expected = """
    Response {
      OriginalUrl: "http://yandex.com.tr/"
      CanonizedUrl: "http://yandex.com.tr/"
      MainUrl: "http://yandex.com.tr/"
      IsMultilang: true
      StorageType: ST_ROBOT
      CanonizationType: WEAK
      Region: "RUS"
      Error: URL_NOT_FOUND
    }
    Status: 0
    """
    message = "Wrong response from gemini:\n%s" % expected_received_table(expected, out)
    assert pb.Response.OriginalUrl == "http://yandex.com.tr/", message
    assert pb.Response.CanonizedUrl == "http://yandex.com.tr/", message
    assert pb.Response.MainUrl[0] == "http://yandex.com.tr/", message
    assert pb.Response.Region == "RUS", message
    assert pb.Response.IsMultilang, message
    assert pb.Response.Error == URL_NOT_FOUND, message
    assert len(pb.Response.MainUrl) == 1, message


def test_not_multilang(gemini, html):
    html.test(
        name="Not multilang host (not in poly.trie)",
        suite="multilang",
        description=""
    )
    (out, err, retcode) = gemini.geminicl.request(
        url="http://nothing.com/",
        type="weak",
    )
    pb = TResultInfo()
    Merge(out, pb)
    expected = """
    Response {
      OriginalUrl: "http://nothing.com/"
      CanonizedUrl: "http://nothing.com/"
      MainUrl: "http://www.nothing.com/"
      IsMultilang: false
      StorageType: ST_ROBOT
      CanonizationType: WEAK
      Region: "UNK"
      BaseInfo {
        IndexTimestamp: 1399890854
        MirrorsTimestamp: 1399890854
        RflTimestamp: 1413201738
        ImagesIndexTimestamp: 0
        VideoIndexTimestamp: 0
      }
    }
    Status: 0
    """
    message = "Wrong response from gemini:\n%s" % expected_received_table(expected, out)
    assert pb.Response.OriginalUrl == "http://nothing.com/", message
    assert pb.Response.CanonizedUrl == "http://nothing.com/", message
    assert pb.Response.MainUrl[0] == "http://www.nothing.com/", message
    assert pb.Response.Region == "UNK", message
    assert not pb.Response.IsMultilang, message
    assert len(pb.Response.MainUrl) == 1, message


def test_not_multilang_rus(gemini, html):
    html.test(
        name="Not multilang host (not in poly.trie) and --region=RUS",
        suite="multilang",
        description=""
    )
    (out, err, retcode) = gemini.geminicl.request(
        url="http://nothing.com/",
        type="weak",
        region="RUS",
    )
    pb = TResultInfo()
    Merge(out, pb)
    expected = """
    Response {
      OriginalUrl: "http://nothing.com/"
      CanonizedUrl: "http://nothing.com/"
      MainUrl: "http://www.nothing.com/"
      IsMultilang: false
      StorageType: ST_ROBOT
      CanonizationType: WEAK
      Region: "RUS"
      BaseInfo {
        IndexTimestamp: 1399890854
        MirrorsTimestamp: 1399890854
        RflTimestamp: 1413201738
        ImagesIndexTimestamp: 0
        VideoIndexTimestamp: 0
      }
    }
    Status: 0
    """
    message = "Wrong response from gemini:\n%s" % expected_received_table(expected, out)
    assert pb.Response.OriginalUrl == "http://nothing.com/", message
    assert pb.Response.CanonizedUrl == "http://nothing.com/", message
    assert pb.Response.MainUrl[0] == "http://www.nothing.com/", message
    assert pb.Response.Region == "RUS", message
    assert not pb.Response.IsMultilang, message
    assert len(pb.Response.MainUrl) == 1, message


def test_not_multilang_tur(gemini, html):
    html.test(
        name="Not multilang host (not in poly.trie) and --region=TUR",
        suite="multilang",
        description=""
    )
    (out, err, retcode) = gemini.geminicl.request(
        url="http://nothing.com/",
        type="weak",
        region="TUR",
    )
    pb = TResultInfo()
    Merge(out, pb)
    expected = """
    Response {
      OriginalUrl: "http://nothing.com/"
      CanonizedUrl: "http://nothing.com/"
      MainUrl: "http://www.nothing.com/"
      IsMultilang: false
      StorageType: ST_ROBOT
      CanonizationType: WEAK
      Region: "TUR"
      BaseInfo {
        IndexTimestamp: 1399890854
        MirrorsTimestamp: 1399890854
        RflTimestamp: 1413201738
        ImagesIndexTimestamp: 0
        VideoIndexTimestamp: 0
      }
    }
    Status: 0
    """
    message = "Wrong response from gemini:\n%s" % expected_received_table(expected, out)
    assert pb.Response.OriginalUrl == "http://nothing.com/", message
    assert pb.Response.CanonizedUrl == "http://nothing.com/", message
    assert pb.Response.MainUrl[0] == "http://www.nothing.com/", message
    assert pb.Response.Region == "TUR", message
    assert not pb.Response.IsMultilang, message
    assert len(pb.Response.MainUrl) == 1, message


def test_unk_reg_unk(gemini, html):
    html.test(
        name="UNK and TUR (--region=UNK)",
        suite="multilang",
        description=""
    )
    (out, err, retcode) = gemini.geminicl.request(
        url="http://yandex.ru/catalog/",
        type="weak",
        region="UNK",
    )
    pb = TResultInfo()
    Merge(out, pb)
    expected = """
    Response {
      OriginalUrl: "http://yandex.ru/catalog/"
      CanonizedUrl: "http://www.yandex.ru/catalog/"
      MainUrl: "http://www.yandex.ru/catalog/"
      IsMultilang: true
      StorageType: ST_ROBOT
      CanonizationType: WEAK
      Region: "UNK"
      BaseInfo {
        IndexTimestamp: 1399890854
        MirrorsTimestamp: 1399890854
        RflTimestamp: 1413201738
        ImagesIndexTimestamp: 0
        VideoIndexTimestamp: 0
      }
    }
    Status: 0
    """
    message = "Wrong response from gemini:\n%s" % expected_received_table(expected, out)
    assert pb.Response.OriginalUrl == "http://yandex.ru/catalog/", message
    assert pb.Response.CanonizedUrl == "http://www.yandex.ru/catalog/", message
    assert pb.Response.MainUrl[0] == "http://www.yandex.ru/catalog/", message
    assert pb.Response.Region == "UNK", message
    assert pb.Response.IsMultilang, message
    assert len(pb.Response.MainUrl) == 1, message


def test_unk_reg_default(gemini, html):
    html.test(
        name="UNK and TUR (no --region)",
        suite="multilang",
        description=""
    )
    (out, err, retcode) = gemini.geminicl.request(
        url="http://yandex.ru/catalog/",
        type="weak",
        region="UNK",
    )
    pb = TResultInfo()
    Merge(out, pb)
    expected = """
    Response {
      OriginalUrl: "http://yandex.ru/catalog/"
      CanonizedUrl: "http://www.yandex.ru/catalog/"
      MainUrl: "http://www.yandex.ru/catalog/"
      IsMultilang: true
      StorageType: ST_ROBOT
      CanonizationType: WEAK
      Region: "UNK"
      BaseInfo {
        IndexTimestamp: 1399890854
        MirrorsTimestamp: 1399890854
        RflTimestamp: 1413201738
        ImagesIndexTimestamp: 0
        VideoIndexTimestamp: 0
      }
    }
    Status: 0
    """
    message = "Wrong response from gemini:\n%s" % expected_received_table(expected, out)
    assert pb.Response.OriginalUrl == "http://yandex.ru/catalog/", message
    assert pb.Response.CanonizedUrl == "http://www.yandex.ru/catalog/", message
    assert pb.Response.MainUrl[0] == "http://www.yandex.ru/catalog/", message
    assert pb.Response.Region == "UNK", message
    assert pb.Response.IsMultilang, message
    assert len(pb.Response.MainUrl) == 1, message


def test_unk_reg_rus(gemini, html):
    html.test(
        name="UNK and TUR (--region=RUS)",
        suite="multilang",
        description=""
    )
    (out, err, retcode) = gemini.geminicl.request(
        url="http://yandex.ru/catalog/",
        type="weak",
        region="RUS",
    )
    pb = TResultInfo()
    Merge(out, pb)
    expected = """
    Response {
      OriginalUrl: "http://yandex.ru/catalog/"
      CanonizedUrl: "http://www.yandex.ru/catalog/"
      MainUrl: "http://www.yandex.ru/catalog/"
      IsMultilang: true
      StorageType: ST_ROBOT
      CanonizationType: WEAK
      Region: "RUS"
      BaseInfo {
        IndexTimestamp: 1399890854
        MirrorsTimestamp: 1399890854
        RflTimestamp: 1413201738
        ImagesIndexTimestamp: 0
        VideoIndexTimestamp: 0
      }
    }
    Status: 0
    """
    message = "Wrong response from gemini:\n%s" % expected_received_table(expected, out)
    assert pb.Response.OriginalUrl == "http://yandex.ru/catalog/", message
    assert pb.Response.CanonizedUrl == "http://www.yandex.ru/catalog/", message
    assert pb.Response.MainUrl[0] == "http://www.yandex.ru/catalog/", message
    assert pb.Response.Region == "RUS", message
    assert pb.Response.IsMultilang, message
    assert len(pb.Response.MainUrl) == 1, message


def test_unk_reg_tur(gemini, html):
    html.test(
        name="UNK and TUR (--region=TUR)",
        suite="multilang",
        description=""
    )
    (out, err, retcode) = gemini.geminicl.request(
        url="http://www.yandex.ru/catalog/",
        type="weak",
        region="TUR",
    )
    pb = TResultInfo()
    Merge(out, pb)
    expected = """
    Response {
      OriginalUrl: "http://yandex.ru/catalog/"
      CanonizedUrl: "http://www.yandex.ru/catalog/tur/"
      MainUrl: "http://www.yandex.ru/catalog/tur/"
      IsMultilang: true
      StorageType: ST_ROBOT
      CanonizationType: WEAK
      Region: "RUS"
      BaseInfo {
        IndexTimestamp: 1399890854
        MirrorsTimestamp: 1399890854
        RflTimestamp: 1413201738
        ImagesIndexTimestamp: 0
        VideoIndexTimestamp: 0
      }
    }
    Status: 0
    """
    message = "Wrong response from gemini:\n%s" % expected_received_table(expected, out)
    assert pb.Response.OriginalUrl == "http://www.yandex.ru/catalog/", message
    assert pb.Response.CanonizedUrl == "http://www.yandex.ru/catalog/", message
    assert pb.Response.MainUrl[0] == "http://www.yandex.ru/catalog/tur/", message
    assert pb.Response.Region == "TUR", message
    assert pb.Response.IsMultilang, message
    assert len(pb.Response.MainUrl) == 1, message


def test_default_only(gemini, html):
    html.test(
        name="Default only",
        suite="multilang",
        description=""
    )
    (out, err, retcode) = gemini.geminicl.request(
        url="http://www.yandex.ru/default/",
        type="weak",
    )
    pb = TResultInfo()
    Merge(out, pb)
    expected = """
    Response {
      OriginalUrl: "http://yandex.ru/default/"
      CanonizedUrl: "http://www.yandex.ru/default/"
      MainUrl: "http://www.yandex.ru/default/"
      IsMultilang: true
      StorageType: ST_ROBOT
      CanonizationType: WEAK
      Region: "UNK"
      BaseInfo {
        IndexTimestamp: 1399890854
        MirrorsTimestamp: 1399890854
        RflTimestamp: 1413201738
        ImagesIndexTimestamp: 0
        VideoIndexTimestamp: 0
      }
    }
    Status: 0
    """
    message = "Wrong response from gemini:\n%s" % expected_received_table(expected, out)
    assert pb.Response.OriginalUrl == "http://www.yandex.ru/default/", message
    assert pb.Response.CanonizedUrl == "http://www.yandex.ru/default/", message
    assert pb.Response.MainUrl[0] == "http://www.yandex.ru/default/", message
    assert pb.Response.Region == "UNK", message
    assert pb.Response.IsMultilang, message
    assert len(pb.Response.MainUrl) == 1, message

    for reg in "RUS", "UNK":
        (out, err, retcode) = gemini.geminicl.request(
            url="http://www.yandex.ru/default/",
            type="weak",
            region=reg
        )
        pb = TResultInfo()
        Merge(out, pb)
        expected = """
        Response {
          OriginalUrl: "http://yandex.ru/default/"
          CanonizedUrl: "http://www.yandex.ru/default/"
          MainUrl: "http://www.yandex.ru/default/"
          IsMultilang: true
          StorageType: ST_ROBOT
          CanonizationType: WEAK
          Region: "%s"
          BaseInfo {
            IndexTimestamp: 1399890854
            MirrorsTimestamp: 1399890854
            RflTimestamp: 1413201738
            ImagesIndexTimestamp: 0
            VideoIndexTimestamp: 0
          }
        }
        Status: 0
        """ % reg
        message = "Wrong response from gemini:\n%s" % expected_received_table(expected, out)
        assert pb.Response.OriginalUrl == "http://www.yandex.ru/default/", message
        assert pb.Response.CanonizedUrl == "http://www.yandex.ru/default/", message
        assert pb.Response.MainUrl[0] == "http://www.yandex.ru/default/", message
        assert pb.Response.Region == reg, message
        assert pb.Response.IsMultilang, message
        assert len(pb.Response.MainUrl) == 1, message

    (out, err, retcode) = gemini.geminicl.request(
        url="http://www.yandex.ru/default/",
        type="weak",
        region="TUR"
    )
    pb = TResultInfo()
    Merge(out, pb)
    expected = """
    Response {
      OriginalUrl: "http://yandex.ru/default/"
      CanonizedUrl: "http://www.yandex.ru/default/"
      MainUrl: "http://www.yandex.ru/default/"
      IsMultilang: true
      StorageType: ST_ROBOT
      CanonizationType: WEAK
      Region: "TUR"
      Error: URL_NOT_FOUND
    }
    Status: 0
    """
    message = "Wrong response from gemini:\n%s" % expected_received_table(expected, out)
    assert pb.Response.OriginalUrl == "http://www.yandex.ru/default/", message
    assert pb.Response.CanonizedUrl == "http://www.yandex.ru/default/", message
    assert pb.Response.MainUrl[0] == "http://www.yandex.ru/default/", message
    assert pb.Response.Region == "TUR", message
    assert pb.Response.IsMultilang, message
    assert len(pb.Response.MainUrl) == 1, message
    assert pb.Response.Error == URL_NOT_FOUND, message



def test_unk_only(gemini, html):
    html.test(
        name="UNK only",
        suite="multilang",
        description=""
    )
    (out, err, retcode) = gemini.geminicl.request(
        url="http://www.yandex.ru/unk/",
        type="weak",
    )
    pb = TResultInfo()
    Merge(out, pb)
    expected = """
    Response {
      OriginalUrl: "http://yandex.ru/unk/"
      CanonizedUrl: "http://www.yandex.ru/unk/"
      MainUrl: "http://www.yandex.ru/unk/"
      IsMultilang: true
      StorageType: ST_ROBOT
      CanonizationType: WEAK
      Region: "UNK"
      BaseInfo {
        IndexTimestamp: 1399890854
        MirrorsTimestamp: 1399890854
        RflTimestamp: 1413201738
        ImagesIndexTimestamp: 0
        VideoIndexTimestamp: 0
      }
    }
    Status: 0
    """
    message = "Wrong response from gemini:\n%s" % expected_received_table(expected, out)
    assert pb.Response.OriginalUrl == "http://www.yandex.ru/unk/", message
    assert pb.Response.CanonizedUrl == "http://www.yandex.ru/unk/", message
    assert pb.Response.MainUrl[0] == "http://www.yandex.ru/unk/", message
    assert pb.Response.Region == "UNK", message
    assert pb.Response.IsMultilang, message
    assert len(pb.Response.MainUrl) == 1, message

    for reg in "RUS", "UNK":
        (out, err, retcode) = gemini.geminicl.request(
            url="http://www.yandex.ru/unk/",
            type="weak",
            region=reg
        )
        pb = TResultInfo()
        Merge(out, pb)
        expected = """
        Response {
          OriginalUrl: "http://yandex.ru/unk/"
          CanonizedUrl: "http://www.yandex.ru/unk/"
          MainUrl: "http://www.yandex.ru/unk/"
          IsMultilang: true
          StorageType: ST_ROBOT
          CanonizationType: WEAK
          Region: "%s"
          BaseInfo {
            IndexTimestamp: 1399890854
            MirrorsTimestamp: 1399890854
            RflTimestamp: 1413201738
            ImagesIndexTimestamp: 0
            VideoIndexTimestamp: 0
          }
        }
        Status: 0
        """ % reg
        message = "Wrong response from gemini:\n%s" % expected_received_table(expected, out)
        assert pb.Response.OriginalUrl == "http://www.yandex.ru/unk/", message
        assert pb.Response.CanonizedUrl == "http://www.yandex.ru/unk/", message
        assert pb.Response.MainUrl[0] == "http://www.yandex.ru/unk/", message
        assert pb.Response.Region == reg, message
        assert pb.Response.IsMultilang, message
        assert len(pb.Response.MainUrl) == 1, message

    (out, err, retcode) = gemini.geminicl.request(
        url="http://www.yandex.ru/unk/",
        type="weak",
        region="TUR"
    )
    pb = TResultInfo()
    Merge(out, pb)
    expected = """
    Response {
      OriginalUrl: "http://yandex.ru/unk/"
      CanonizedUrl: "http://www.yandex.ru/unk/"
      MainUrl: "http://www.yandex.ru/unk/"
      IsMultilang: true
      StorageType: ST_ROBOT
      CanonizationType: WEAK
      Region: "TUR"
      Error: URL_NOT_FOUND
    }
    Status: 0
    """
    message = "Wrong response from gemini:\n%s" % expected_received_table(expected, out)
    assert pb.Response.OriginalUrl == "http://www.yandex.ru/unk/", message
    assert pb.Response.CanonizedUrl == "http://www.yandex.ru/unk/", message
    assert pb.Response.MainUrl[0] == "http://www.yandex.ru/unk/", message
    assert pb.Response.Region == "TUR", message
    assert pb.Response.IsMultilang, message
    assert len(pb.Response.MainUrl) == 1, message
    assert pb.Response.Error == URL_NOT_FOUND, message


def test_all(gemini, html, narrator):
    html.test(
        name="ALL",
        suite="multilang",
        description=""
    )
    (out, err, retcode) = gemini.geminicl.request(
        url="http://lenta.ru/kino/?utm_source=twit",
        type="weak",
        region="ALL",
    )
    pb = TResultInfo()
    Merge(out, pb)
    expected = """
    Response {
      OriginalUrl: "http://lenta.ru/kino/?utm_source=twit"
      CanonizationType: WEAK
      MainUrlInfo {
        CanonizedUrl: "http://lenta.ru/kino/?utm_source=twit"
        MainUrl: "http://lenta.ru/kino/"
        Region: "RUS"
        IsMultilang: true
        BaseInfo {
          IndexTimestamp: 1399890854
          MirrorsTimestamp: 1399890854
          RflTimestamp: 1413201738
          ImagesIndexTimestamp: 0
          VideoIndexTimestamp: 0
        }
      }
      MainUrlInfo {
        CanonizedUrl: "http://lenta.ru/kino/?utm_source=twit"
        MainUrl: "http://lenta.ru/usa/"
        Region: "USA"
        IsMultilang: true
        BaseInfo {
          IndexTimestamp: 1399890854
          MirrorsTimestamp: 1399890854
          RflTimestamp: 1413201738
          ImagesIndexTimestamp: 0
          VideoIndexTimestamp: 0
        }
      }
      MainUrlInfo {
        CanonizedUrl: "http://lenta.ru/kino/?utm_source=twit"
        MainUrl: "http://lenta.ru/tur/"
        Region: "TUR"
        IsMultilang: true
        BaseInfo {
          IndexTimestamp: 1399890854
          MirrorsTimestamp: 1399890854
          RflTimestamp: 1413201738
          ImagesIndexTimestamp: 0
          VideoIndexTimestamp: 0
        }
      }
    }
    Status: 0
    """
    message = "Wrong response from gemini:\n%s" % expected_received_table(expected, out)
    assert pb.Response.OriginalUrl == "http://lenta.ru/kino/?utm_source=twit", message
    assert len(pb.Response.MainUrl) == 0, message
    assert len(pb.Response.MainUrlInfo) == 3, message
    assert len(pb.Response.MainUrlInfo) == 3, message
    assert pb.Response.MainUrlInfo[0].MainUrl == "http://lenta.ru/kino/", message
    assert pb.Response.MainUrlInfo[1].MainUrl == "http://lenta.ru/usa/", message
    assert pb.Response.MainUrlInfo[2].MainUrl == "http://lenta.ru/tur/", message
    assert pb.Response.MainUrlInfo[0].Region == "RUS", message
    assert pb.Response.MainUrlInfo[1].Region == "USA", message
    assert pb.Response.MainUrlInfo[2].Region == "TUR", message
    for i in range(3):
        assert pb.Response.MainUrlInfo[i].CanonizedUrl == "http://lenta.ru/kino/?utm_source=twit", message
        assert pb.Response.MainUrlInfo[i].HasField("BaseInfo")
        assert pb.Response.MainUrlInfo[i].IsMultilang



def test_all_not_multilang(gemini, html, narrator):
    html.test(
        name="ALL (not multilang)",
        suite="multilang",
        description=""
    )
    (out, err, retcode) = gemini.geminicl.request(
        url="http://nothing.com/",
        type="weak",
        region="ALL",
    )
    pb = TResultInfo()
    Merge(out, pb)
    expected = """
    Response {
      OriginalUrl: "http://nothing.com/"
      CanonizationType: WEAK
      MainUrlInfo {
        CanonizedUrl: "http://nothing.com/"
        MainUrl: "http://www.nothing.com/"
        Region: "UNK"
        IsMultilang: false
        Replica: 1
        BaseInfo {
          IndexTimestamp: 1399890854
          MirrorsTimestamp: 1399890854
          RflTimestamp: 1413201738
          ImagesIndexTimestamp: 0
          VideoIndexTimestamp: 0
        }
      }
    }
    Status: 0
    """
    message = "Wrong response from gemini:\n%s" % expected_received_table(expected, out)
    assert pb.Response.OriginalUrl == "http://nothing.com/", message
    assert len(pb.Response.MainUrlInfo) == 1, message
    assert not pb.Response.MainUrlInfo[0].IsMultilang, message
    assert pb.Response.MainUrlInfo[0].CanonizedUrl == "http://nothing.com/", message
    assert len(pb.Response.MainUrl) == 0, message
    assert pb.Response.MainUrlInfo[0].MainUrl == "http://www.nothing.com/", message
    assert pb.Response.MainUrlInfo[0].Region == "UNK", message


def test_not_multilang_def_region(gemini, html):
    html.test(
        name="Not multilang host (not in poly.trie)",
        suite="multilang",
        description=""
    )
    (out, err, retcode) = gemini.geminicl.request(
        "--with-default-region",
        url="http://nothing.com/",
        type="weak",
    )
    pb = TResultInfo()
    Merge(out, pb)
    expected = """
    Response {
      OriginalUrl: "http://nothing.com/"
      CanonizedUrl: "http://nothing.com/"
      MainUrl: "http://www.nothing.com/"
      IsMultilang: false
      StorageType: ST_ROBOT
      CanonizationType: WEAK
      Region: "UNK"
      BaseInfo {
        IndexTimestamp: 1399890854
        MirrorsTimestamp: 1399890854
        RflTimestamp: 1413201738
        ImagesIndexTimestamp: 0
        VideoIndexTimestamp: 0
      }
    }
    Status: 0
    """
    message = "Wrong response from gemini:\n%s" % expected_received_table(expected, out)
    assert pb.Response.OriginalUrl == "http://nothing.com/", message
    assert pb.Response.CanonizedUrl == "http://nothing.com/", message
    assert pb.Response.MainUrl[0] == "http://www.nothing.com/", message
    assert pb.Response.Region == "UNK", message
    assert not pb.Response.IsMultilang, message
    assert len(pb.Response.MainUrl) == 1, message




def test_unk_only_def_region(gemini, html):
    html.test(
        name="UNK only (--with-default-region)",
        suite="multilang",
        description=""
    )
    (out, err, retcode) = gemini.geminicl.request(
        "--with-default-region",
        url="http://www.yandex.ru/unk/",
        type="weak",
    )
    pb = TResultInfo()
    Merge(out, pb)
    expected = """
    Response {
      OriginalUrl: "http://yandex.ru/unk/"
      CanonizedUrl: "http://www.yandex.ru/unk/"
      MainUrl: "http://www.yandex.ru/unk/"
      IsMultilang: true
      StorageType: ST_ROBOT
      CanonizationType: WEAK
      Region: "UNK"
      BaseInfo {
        IndexTimestamp: 1399890854
        MirrorsTimestamp: 1399890854
        RflTimestamp: 1413201738
        ImagesIndexTimestamp: 0
        VideoIndexTimestamp: 0
      }
    }
    Status: 0
    """
    message = "Wrong response from gemini:\n%s" % expected_received_table(expected, out)
    assert pb.Response.OriginalUrl == "http://www.yandex.ru/unk/", message
    assert pb.Response.CanonizedUrl == "http://www.yandex.ru/unk/", message
    assert pb.Response.MainUrl[0] == "http://www.yandex.ru/unk/", message
    assert pb.Response.Region == "UNK", message
    assert pb.Response.IsMultilang, message
    assert len(pb.Response.MainUrl) == 1, message

    for reg in "RUS", "UNK":
        (out, err, retcode) = gemini.geminicl.request(
            "--with-default-region",
            url="http://www.yandex.ru/unk/",
            type="weak",
            region=reg
        )
        pb = TResultInfo()
        Merge(out, pb)
        expected = """
        Response {
          OriginalUrl: "http://yandex.ru/unk/"
          CanonizedUrl: "http://www.yandex.ru/unk/"
          MainUrl: "http://www.yandex.ru/unk/"
          IsMultilang: true
          StorageType: ST_ROBOT
          CanonizationType: WEAK
          Region: "%s"
          BaseInfo {
            IndexTimestamp: 1399890854
            MirrorsTimestamp: 1399890854
            RflTimestamp: 1413201738
            ImagesIndexTimestamp: 0
            VideoIndexTimestamp: 0
          }
        }
        Status: 0
        """ % reg
        message = "Wrong response from gemini:\n%s" % expected_received_table(expected, out)
        assert pb.Response.OriginalUrl == "http://www.yandex.ru/unk/", message
        assert pb.Response.CanonizedUrl == "http://www.yandex.ru/unk/", message
        assert pb.Response.MainUrl[0] == "http://www.yandex.ru/unk/", message
        assert pb.Response.Region == reg, message
        assert pb.Response.IsMultilang, message
        assert len(pb.Response.MainUrl) == 1, message

    (out, err, retcode) = gemini.geminicl.request(
        "--with-default-region",
        url="http://www.yandex.ru/unk/",
        type="weak",
        region="TUR"
    )
    pb = TResultInfo()
    Merge(out, pb)
    expected = """
    Response {
      OriginalUrl: "http://yandex.ru/unk/"
      CanonizedUrl: "http://www.yandex.ru/unk/"
      MainUrl: "http://www.yandex.ru/unk/"
      IsMultilang: true
      StorageType: ST_ROBOT
      CanonizationType: WEAK
      Region: "UNK"
      BaseInfo {
        IndexTimestamp: 1399890854
        MirrorsTimestamp: 1399890854
        RflTimestamp: 1413201738
        ImagesIndexTimestamp: 0
        VideoIndexTimestamp: 0
      }
    }
    Status: 0
    """
    message = "Wrong response from gemini:\n%s" % expected_received_table(expected, out)
    assert pb.Response.OriginalUrl == "http://www.yandex.ru/unk/", message
    assert pb.Response.CanonizedUrl == "http://www.yandex.ru/unk/", message
    assert pb.Response.MainUrl[0] == "http://www.yandex.ru/unk/", message
    assert pb.Response.Region == "UNK", message
    assert pb.Response.IsMultilang, message
    assert len(pb.Response.MainUrl) == 1, message


def test_no_region_tur_def_region(gemini, html):
    html.test(
        name="No --region and TUR only in mainurl (--with-default-region)",
        suite="multilang",
        description=""
    )
    (out, err, retcode) = gemini.geminicl.request(
        "--with-default-region",
        url="http://yandex.com.tr/",
        region="USA",
        type="weak",
    )
    pb = TResultInfo()
    Merge(out, pb)
    expected = """
    Response {
      OriginalUrl: "http://yandex.com.tr/"
      CanonizedUrl: "http://yandex.com.tr/"
      MainUrl: "http://yandex.com.tr/"
      IsMultilang: true
      StorageType: ST_ROBOT
      CanonizationType: WEAK
      Region: "USA"
      Error: URL_NOT_FOUND
    }
    Status: 0
    """
    message = "Wrong response from gemini:\n%s" % expected_received_table(expected, out)
    assert pb.Response.OriginalUrl == "http://yandex.com.tr/", message
    assert pb.Response.CanonizedUrl == "http://yandex.com.tr/", message
    assert pb.Response.MainUrl[0] == "http://yandex.com.tr/", message
    assert pb.Response.Region == "USA", message
    assert pb.Response.IsMultilang, message
    assert pb.Response.Error == URL_NOT_FOUND, message
    assert len(pb.Response.MainUrl) == 1, message


def test_multilang_mirrors(gemini, html):
    html.test(
        name="Mirror with region=ALL",
        suite="multilang",
        description=""
    )
    (out, err, retcode) = gemini.geminicl.request(
        url="http://yandex.ru/",
        region="ALL",
        type="mirror",
    )
    pb = TResultInfo()
    Merge(out, pb)
    expected = """Response {
      OriginalUrl: "http://yandex.ru/"
      CanonizationType: MIRROR
      MainMirrorInfo {
        MainMirror: "http://www.yandex.ru/"
        Region: "RUS"
        IsMultilang: true
      }
      MainMirrorInfo {
        MainMirror: "http://yandex.ru/"
        Region: "DEU"
        IsMultilang: true
      }
      MainMirrorInfo {
        MainMirror: "http://yandex.ru/"
        Region: "USA"
        IsMultilang: true
      }
      MainMirrorInfo {
        MainMirror: "http://yandex.ru/"
        Region: "TUR"
        IsMultilang: true
      }
    }
    Status: 0"""
    message = "Wrong response from gemini:\n%s" % expected_received_table(expected, out)
    assert pb.Response.OriginalUrl == "http://yandex.ru/"
    assert len(pb.Response.MainMirrorInfo) == 4

    assert pb.Response.MainMirrorInfo[0].MainMirror == "http://www.yandex.ru/", message
    assert pb.Response.MainMirrorInfo[0].Region == "RUS", message
    assert pb.Response.MainMirrorInfo[0].IsMultilang, message

    assert pb.Response.MainMirrorInfo[1].MainMirror == "http://yandex.ru/", message
    assert pb.Response.MainMirrorInfo[1].Region == "DEU", message
    assert pb.Response.MainMirrorInfo[1].IsMultilang, message

    assert pb.Response.MainMirrorInfo[2].MainMirror == "http://yandex.ru/", message
    assert pb.Response.MainMirrorInfo[2].Region == "USA", message
    assert pb.Response.MainMirrorInfo[2].IsMultilang, message

    assert pb.Response.MainMirrorInfo[3].MainMirror == "http://yandex.ru/", message
    assert pb.Response.MainMirrorInfo[3].Region == "TUR", message
    assert pb.Response.MainMirrorInfo[3].IsMultilang, message


def test_multilang_mirrors_not_multilang(gemini, html):
    html.test(
        name="Mirror with region=ALL (not multilang host)",
        suite="multilang",
        description=""
    )
    (out, err, retcode) = gemini.geminicl.request(
        url="http://google.com/",
        region="ALL",
        type="mirror",
    )
    pb = TResultInfo()
    Merge(out, pb)
    expected = """Response {
      OriginalUrl: "http://google.com/"
      CanonizationType: MIRROR
      MainMirrorInfo {
        MainMirror: "http://google.com/"
        Region: "RUS"
        IsMultilang: false
      }
      MainMirrorInfo {
        MainMirror: "http://google.com/"
        Region: "DEU"
        IsMultilang: false
      }
      MainMirrorInfo {
        MainMirror: "http://google.com/"
        Region: "USA"
        IsMultilang: false
      }
      MainMirrorInfo {
        MainMirror: "http://google.com/"
        Region: "TUR"
        IsMultilang: false
      }
    }
    Status: 0"""
    message = "Wrong response from gemini:\n%s" % expected_received_table(expected, out)
    assert pb.Response.OriginalUrl == "http://google.com/"
    assert len(pb.Response.MainMirrorInfo) == 4

    assert pb.Response.MainMirrorInfo[0].MainMirror == "http://google.com/", message
    assert pb.Response.MainMirrorInfo[0].Region == "RUS", message
    assert not pb.Response.MainMirrorInfo[0].IsMultilang, message

    assert pb.Response.MainMirrorInfo[1].MainMirror == "http://google.com/", message
    assert pb.Response.MainMirrorInfo[1].Region == "DEU", message
    assert not pb.Response.MainMirrorInfo[1].IsMultilang, message

    assert pb.Response.MainMirrorInfo[2].MainMirror == "http://google.com/", message
    assert pb.Response.MainMirrorInfo[2].Region == "USA", message
    assert not pb.Response.MainMirrorInfo[2].IsMultilang, message

    assert pb.Response.MainMirrorInfo[3].MainMirror == "http://google.com/", message
    assert pb.Response.MainMirrorInfo[3].Region == "TUR", message
    assert not pb.Response.MainMirrorInfo[3].IsMultilang, message
