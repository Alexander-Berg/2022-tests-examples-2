import os
from robot.gemini.protos.castor_pb2 import TResultInfo
from google.protobuf.text_format import Merge
from common.libs.plugins.reporter import expected_received_table

repl = lambda s: s.replace(" ", "").replace("\n", "").replace("\t", "")

def make_request(gemini, user=None):
    if user is not None:
        out, _, _ = gemini.geminicl.request(
            "--retry-count=1",
            user=user,
            url="http://lenta.ru/kino/?utm_source=twit",
            type="weak",
            )
    else:
        out, _, _ = gemini.geminicl.request(
            "--retry-count=1",
            url="http://lenta.ru/kino/?utm_source=twit",
            type="weak",
            )
    pb = TResultInfo()
    Merge(out, pb)
    return pb, out


def make_requests_and_check(gemini, user, times):
    for _ in xrange(times):
        pb, out = make_request(gemini, user)
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


def make_request_no_source(gemini, user=None):
    pb, out = make_request(gemini, user)
    expected = """
        Response {
         OriginalUrl: "http://lenta.ru/kino/?utm_source=twit"
         Error: QUOTA_EXCEEDED
         ErrorMessage: "no source in the config"
        }
        Status: 0
        """
    message = "Wrong response from gemini:\n%s" % expected_received_table(expected, out)
    assert repl(expected) == repl(out), message


def make_request_quota_exceeded(gemini, user=None):
    pb, out = make_request(gemini, user)
    expected = """
        Response {
         OriginalUrl: "http://lenta.ru/kino/?utm_source=twit"
         Error: QUOTA_EXCEEDED
         ErrorMessage: "Request type quota is exceeded"
        }
        Status: 0
        """
    message = "Wrong response from gemini:\n%s" % expected_received_table(expected, out)
    assert repl(expected) == repl(out), message

get_quotas_file = lambda gemini: os.path.join(
    gemini.homeDir,
    "config",
    "squota.gemini.xml"
)
