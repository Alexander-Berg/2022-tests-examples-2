import pytest
from plugins.gemini import *
from common.libs.plugins.reporter import *
from collections import namedtuple


def remove_original_url(s):
    res = ""
    for line in s.split("\n"):
        if not line.lstrip().startswith("OriginalUrl:"):
            res += line + "\n"
    return res


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
        name="schemes",
        description=""" """,
        directory="parser"
    )


def pytest_funcarg__load_query(request):
    return request.param

l = []
l_id = []


def l_add(test):
    l.append(test)
    l_id.append("%2d" % test.id)


# test factory ******************************************************
def pytest_generate_tests(metafunc):

    global l
    global l_id
    l=[]
    l_id=[]

    Test = namedtuple("Test", ["id", "scheme", "result"])
    good_schemes = ["http://", "https://"]
    id = 1
    for scheme in good_schemes:
        l_add(Test(id, scheme, 0))
        id += 1

    bad_schemes = [
        "", ":", "://",
        "http:", "http:/", "http/", "http//",
        "https:", "https:/", "https/", "https//",
        "ht://", "htp://", "file:///"
    ]

    for scheme in bad_schemes:
        l_add(Test(id, scheme, 1))
        id += 1

    metafunc.parametrize("load_query", l, indirect=True, ids=l_id)


def test_schemes(gemini, html, load_query):
    test = load_query
    html.test(
        name="#%2d: " % test.id + test.scheme,
        suite="Schemes",
        description="""
            Checks response for %syandex.ru (%s)""" % (
            test.scheme,
            "bad" if test.result else "good"
        )
    )
    response = gemini.geminicl.request(
        url=test.scheme + "yandex.ru/",
    )[0]
    if test.result:
        assert "BAD_URL" in response, "Wrong response:\n\n" + response
    else:
        assert "BAD_URL" not in response, "Wrong response:\n\n" + response
