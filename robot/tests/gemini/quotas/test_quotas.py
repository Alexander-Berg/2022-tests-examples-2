from plugins.gemini import *
from common.libs.plugins.reporter import *
from helpers import *
from cgi import escape
from robot.gemini.protos.castor_pb2 import TResultInfo
from robot.gemini.protos.base_pb2 import QUOTA_EXCEEDED


def pytest_funcarg__html_config(request):
    return html_config(
        name="test_quotas",
        description="",
        directory="quotas"
    )


def pytest_funcarg__gemini_config(request):
    main_url = {
        "http://lenta.ru/kino/?utm_source=twit": "http://lenta.ru/kino/",
        "http://lenta.ru/kino/": "http://lenta.ru/kino/",
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

    return gemini_config(
        main_url,
        exec_after=exec_after,
    )


def test_users(gemini, html, narrator):
    quotas = """
        <ipset name="all">
           <ip name="*"/>
        </ipset>

        <source name="test">
           <requesttype name="GetMain" second="5" minute="5">
             <ipset name="all"/>
           </requesttype>
        </source>"""

    html.test(
        name="Users",
        suite="quotas",
        description="""squota.gemini.xml: <pre>%s</pre>
        Checks that user "test" can make requests and any other user can not.""" % escape(quotas)
    )

    o = open(get_quotas_file(gemini), "w")
    print >> o, quotas
    o.close()
    narrator.pause(10)

    make_requests_and_check(gemini, "test", 1)

    make_request_no_source(gemini)
    make_request_no_source(gemini, "any")
    make_request_no_source(gemini, "fake")


def test_seconds(gemini, html, narrator):
    quotas = """
        <ipset name="all">
           <ip name="*"/>
        </ipset>

        <source name="testseconds">
           <requesttype name="GetMain" second="5">
             <ipset name="all"/>
           </requesttype>
        </source>"""

    html.test(
        name="RPS",
        suite="quotas",
        description="""squota.gemini.xml: <pre>%s</pre>
        Checks that user "testseconds" can make 5 requests per second.""" % escape(quotas)
    )

    o = open(get_quotas_file(gemini), "w")
    print >> o, quotas
    o.close()
    narrator.pause(10)

    out, _, _ = gemini.geminicl.request(
        "--retry-count=1",
        "--urls-file=/dev/stdin",
        user="testseconds",
        stdin="http://lenta.ru/kino/?utm_source=twit\n" * 6,
        type="weak",
    )

    out = out.split("\n\n")[:-1]

    result_ok = 0
    result_no_quota = 0

    for text in out:
        pb = TResultInfo()
        Merge(text, pb)
        if pb.Response.HasField("Error") and pb.Response.Error == QUOTA_EXCEEDED:
            result_no_quota += 1
        elif pb.Response.MainUrl[0] == "http://lenta.ru/kino/":
            result_ok += 1
    assert result_ok + result_no_quota == 6, "Wrong gemini response: \n" + out


def test_second(gemini, html, narrator):
    quotas = """
        <ipset name="all">
           <ip name="*"/>
        </ipset>

        <source name="testsecond">
           <requesttype name="GetMain" second="5" minute="5">
             <ipset name="all"/>
           </requesttype>
        </source>"""

    html.test(
        name="Second",
        suite="quotas",
        description="""squota.gemini.xml: <pre>%s</pre>
        Checks that user "testsecond" can make 5 requests and can not make one more (in one second).""" % escape(quotas)
    )

    o = open(get_quotas_file(gemini), "w")
    print >> o, quotas
    o.close()
    narrator.pause(10)

    make_requests_and_check(gemini, "testsecond", 5)
    make_request_quota_exceeded(gemini, "testsecond")


def test_minute(gemini, html, narrator):
    quotas = """
        <ipset name="all">
           <ip name="*"/>
        </ipset>

        <source name="testminute">
           <requesttype name="GetMain" second="5" minute="5">
             <ipset name="all"/>
           </requesttype>
        </source>"""

    html.test(
        name="Minute",
        suite="quotas",
        description="""squota.gemini.xml: <pre>%s</pre>
        Checks that user "testminute" can make 5 requests and can not make one more
        (2 seconds pause between requests).""" % escape(quotas)
    )

    o = open(get_quotas_file(gemini), "w")
    print >> o, quotas
    o.close()
    narrator.pause(10)

    for i in xrange(5):
        make_requests_and_check(gemini, "testminute", 1)
        narrator.pause(2)
    make_request_quota_exceeded(gemini, "testminute")


def test_hour(gemini, html, narrator):
    quotas = """
        <ipset name="all">
           <ip name="*"/>
        </ipset>

        <source name="testhour">
           <requesttype name="GetMain" second="5" minute="5" hour="5">
             <ipset name="all"/>
           </requesttype>
        </source>"""

    html.test(
        name="Hour",
        suite="quotas",
        description="""squota.gemini.xml: <pre>%s</pre>
        Checks that user "testhour" can make 5 requests and can not make one more.""" % escape(quotas)
    )

    o = open(get_quotas_file(gemini), "w")
    print >> o, quotas
    o.close()
    narrator.pause(10)

    make_requests_and_check(gemini, "testhour", 5)
    make_request_quota_exceeded(gemini, "testhour")


def test_day(gemini, html, narrator):
    quotas = """
        <ipset name="all">
           <ip name="*"/>
        </ipset>

        <source name="testday">
           <requesttype name="GetMain" second="5" minute="5" hour="5" day="5">
             <ipset name="all"/>
           </requesttype>
        </source>"""

    html.test(
        name="Day",
        suite="quotas",
        description="""squota.gemini.xml: <pre>%s</pre>
        Checks that user "testday" can make 5 requests and can not make one more.""" % escape(quotas)
    )

    o = open(get_quotas_file(gemini), "w")
    print >> o, quotas
    o.close()
    narrator.pause(10)

    make_requests_and_check(gemini, "testday", 5)
    make_request_quota_exceeded(gemini, "testday")


def test_two_users(gemini, html, narrator):
    quotas = """
        <ipset name="all">
           <ip name="*"/>
        </ipset>

        <source name="test1">
           <requesttype name="GetMain" second="5" minute="5">
             <ipset name="all"/>
           </requesttype>
        </source>

        <source name="test2">
           <requesttype name="GetMain" second="5" minute="5">
             <ipset name="all"/>
           </requesttype>
        </source>"""

    html.test(
        name="Two Users",
        suite="quotas",
        description="""squota.gemini.xml: <pre>%s</pre>
        Checks that users "test1" and "test2" can make 5 requests and can not make one more.""" % escape(quotas)
    )

    o = open(get_quotas_file(gemini), "w")
    print >> o, quotas
    o.close()
    narrator.pause(10)

    make_requests_and_check(gemini, "test1", 5)
    make_request_quota_exceeded(gemini, "test1")

    make_requests_and_check(gemini, "test2", 5)
    make_request_quota_exceeded(gemini, "test2")
