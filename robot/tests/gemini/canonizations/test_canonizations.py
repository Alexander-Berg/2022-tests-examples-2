import string
from plugins.gemini import *
from common.libs.plugins.reporter import *
import pytest
from robot.gemini.protos.castor_pb2 import TResultInfo
from google.protobuf.text_format import Merge



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

        # time.sleep(1000)

    return gemini_config(
        main_url=main_url,
        exec_after=exec_after
    )


def pytest_funcarg__html_config(request):
    return html_config(
        name="canonizations",
        description="""Cases for all types canonizations""",
        directory="canonizations"
    )


def remove_whitespaces(s):
    for c in string.whitespace:
        s = s.replace(c, "")
    return s


def remove_original_url(s):
    res = ""
    for line in s.split("\n"):
        if not line.lstrip().startswith("OriginalUrl:") and not line.lstrip().startswith("MainUrl:"):
            res += line + "\n"
    return res


class WeakAndStrong:
    def test_cyrillic_path(self, gemini, html):
        wiki_yandex = 'http://ru.wikipedia.org/wiki/\xd0\xaf\xd0\xbd\xd0\xb4\xd0\xb5\xd0\xba\xd1\x81'
        president_rf_news = 'http://\xd0\xbf\xd1\x80\xd0\xb5\xd0\xb7\xd0\xb8\xd0\xb4\xd0\xb5\xd0\xbd\xd1\x82.' \
                            '\xd1\x80\xd1\x84/\xd0\xbd\xd0\xbe\xd0\xb2\xd0\xbe\xd1\x81\xd1\x82\xd0\xb8'
        html.test(
            name="Cyrillic Path",
            suite="Canonizations." + self.type,
            description="""
            <li>Checks response for %s</li>
            <li>Checks response for %s</li>""" % (
                wiki_yandex,
                president_rf_news
            )
        )
        response = gemini.geminicl.request(
            url=wiki_yandex,
            type=self.type
        )[0]
        assert 'CanonizedUrl: "http://ru.wikipedia.org/wiki/%D0%AF%D0%BD%D0%B4%D0%B5%D0%BA%D1%81"' in response

        response = gemini.geminicl.request(
            url=president_rf_news,
            type=self.type
        )[0]
        assert 'CanonizedUrl: "http://xn--d1abbgf6aiiy.xn--p1ai/%D0%BD%D0%BE%D0%B2%D0%BE%D1%81%D1%82%D0%B8"' in response

class TestWeak(WeakAndStrong):

    type = "weak"

    def test_case_sensitivity(self, gemini, html):
        html.test(
            name="Case Sensitivity",
            suite="Canonizations." + self.type,
            description="""
            <li>Checks that responses for http://yandex.ru/yandsearch and http://YANDEX.ru/yandsearch are similar</li>
            <li>Checks that responses for http://yandex.ru/yandsearch and http://YANDEX.ru/yANDsearch differ</li>"""
        )
        response_yandex = gemini.geminicl.request(
            url="http://yandex.ru/yandsearch",
            type=self.type
        )[0]
        response_YANDEX = gemini.geminicl.request(
            url="http://YANDEX.ru/yandsearch",
            type=self.type
        )[0]
        assert remove_original_url(response_yandex) == remove_original_url(response_YANDEX)

        response_yandex = gemini.geminicl.request(
            url="http://yandex.ru/yandsearch",
            type=self.type
        )[0]
        response_YANDEX = gemini.geminicl.request(
            url="http://YANDEX.ru/yANDsearch",
            type=self.type
        )[0]
        assert remove_original_url(response_yandex) != remove_original_url(response_YANDEX)

    def test_cyrillic_host(self, gemini, html):
        # yandex.rf in cyrillic
        host_yandex_rf = "\xd1\x8f\xd0\xbd\xd0\xb4\xd0\xb5\xd0\xba\xd1\x81.\xd1\x80\xd1\x84"

        host_bad = "\xd1\x8b\xd0\xb2\xd0\xb0\xd0\xbe\xd1\x8b\xd0\xb0\xd0\xb4.\xd1\x80\xd1\x84"

        html.test(
            name="Case Cyrillic Host",
            suite="Canonizations." + self.type,
            description="""<li>Checks response for http://%s/</li>
            <li>Checks response for http://%s/</li>""" % (host_yandex_rf, host_bad)
        )
        response = gemini.geminicl.request(
            url="http://%s/" % host_yandex_rf,
            type=self.type
        )[0]
        assert 'CanonizedUrl: "http://www.yandex.ru/"' in response

        response = gemini.geminicl.request(
            url="http://%s/" % host_bad,
            type=self.type
        )[0]
        assert 'CanonizedUrl: "http://xn--80aaek2c4dd.xn--p1ai/"' in response

    def test_hash_in_url(self, gemini, html):
        html.test(
            name="Hash in Url",
            suite="Canonizations." + self.type,
            description="""<li>Checks response for http://twitter.com/test#top</li>
            <li>Checks response for http://twitter.com/test#!top</li>
            <li>Checks response for http://twitter.com/test#t!op</li>"""
        )
        response = gemini.geminicl.request(
            url="http://twitter.com/test#top",
            type=self.type
        )[0]
        assert 'CanonizedUrl: "http://twitter.com/test"' in response
        response = gemini.geminicl.request(
            url="http://twitter.com/test#!top",
            type=self.type
        )[0]
        assert 'CanonizedUrl: "http://twitter.com/test?_escaped_fragment_=top' in response
        response = gemini.geminicl.request(
            url="http://twitter.com/test#t!op",
            type=self.type
        )[0]
        assert 'CanonizedUrl: "http://twitter.com/test"' in response


class TestStrong(WeakAndStrong):

    type = "strong"

    def test_case_sensitivity(self, gemini, html):
        html.test(
            name="Case Sensitivity",
            suite="Canonizations." + self.type,
            description="""
            <li>Checks that responses for http://yandex.ru/yandsearch and http://YANDEX.ru/yandsearch are similar</li>
            <li>Checks that responses for http://yandex.ru/yandsearch and http://YANDEX.ru/yANDsearch differ</li>"""
        )
        response_yandex = gemini.geminicl.request(
            url="http://yandex.ru/yandsearch",
            type=self.type
        )[0]
        response_YANDEX = gemini.geminicl.request(
            url="http://YANDEX.ru/yandsearch",
            type=self.type
        )[0]
        assert remove_original_url(response_yandex) == remove_original_url(response_YANDEX), \
            expected_received_table(response_YANDEX, response_yandex, "YANDEX", "yandex")

        response_yandex = gemini.geminicl.request(
            url="http://yandex.ru/yandsearch",
            type=self.type
        )[0]
        response_YANDEX = gemini.geminicl.request(
            url="http://YANDEX.ru/yANDsearch",
            type=self.type
        )[0]
        assert remove_original_url(response_yandex) == remove_original_url(response_YANDEX), \
            expected_received_table(response_YANDEX, response_yandex, "YANDEX", "yandex")


    def test_cyrillic_host(self, gemini, html):
        # yandex.rf in cyrillic
        host_yandex_rf = "\xd1\x8f\xd0\xbd\xd0\xb4\xd0\xb5\xd0\xba\xd1\x81.\xd1\x80\xd1\x84"

        host_bad = "\xd1\x8b\xd0\xb2\xd0\xb0\xd0\xbe\xd1\x8b\xd0\xb0\xd0\xb4.\xd1\x80\xd1\x84"

        html.test(
            name="Case Cyrillic Host",
            suite="Canonizations." + self.type,
            description="""<li>Checks response for http://%s/</li>
            <li>Checks response for http://%s/</li>""" % (host_yandex_rf, host_bad)
        )
        response = gemini.geminicl.request(
            url="http://%s/" % host_yandex_rf,
            type=self.type
        )[0]
        assert 'CanonizedUrl: "http://www.yandex.ru/"' in response

        response = gemini.geminicl.request(
            url="http://%s/" % host_bad,
            type=self.type
        )[0]
        assert 'CanonizedUrl: "http://xn--80aaek2c4dd.xn--p1ai/"' in response

    def test_hash_in_url(self, gemini, html):
        html.test(
            name="Hash in Url",
            suite="Canonizations." + self.type,
            description="""<li>Checks response for http://twitter.com/test#top</li>
            <li>Checks response for http://twitter.com/test#!top</li>
            <li>Checks response for http://twitter.com/test#t!op</li>"""
        )
        response = gemini.geminicl.request(
            url="http://twitter.com/test#top",
            type=self.type
        )[0]
        assert 'CanonizedUrl: "http://twitter.com/test"' in response
        response = gemini.geminicl.request(
            url="http://twitter.com/test#!top",
            type=self.type
        )[0]
        assert 'CanonizedUrl: "http://twitter.com/test?_escaped_fragment_=top' in response
        response = gemini.geminicl.request(
            url="http://twitter.com/test#t!op",
            type=self.type
        )[0]
        assert 'CanonizedUrl: "http://twitter.com/test"' in response
