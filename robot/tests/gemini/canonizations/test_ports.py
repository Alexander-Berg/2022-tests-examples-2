import pytest
from plugins.gemini import *
from common.libs.plugins.reporter import *
from collections import namedtuple


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

    return gemini_config(
        main_url=main_url,
        exec_after=exec_after
    )


def pytest_funcarg__html_config(request):
    return html_config(
        name="ports",
        description=""" """,
        directory="canonizations"
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

    Test = namedtuple("Test", ["id", "request", "response"])
    id = 1
    l_add(Test(
        id=id,
        request="http://yandex.ru:80/",
        response="http://www.yandex.ru/"
    ))
    id += 1

    l_add(Test(
        id=id,
        request="http://yandex.ru/",
        response='http://www.yandex.ru/'
    ))
    id += 1

    l_add(Test(
        id=id,
        request="https://yandex.ru:443/",
        response="https://yandex.ru/"
    ))
    id += 1

    l_add(Test(
        id=id,
        request="https://yandex.ru/",
        response="https://yandex.ru/"
    ))
    id += 1

    l_add(Test(
        id=id,
        request="http://yandex.ru:8080/",
        response="http://yandex.ru:8080/"
    ))
    id += 1

    l_add(Test(
        id=id,
        request="https://yandex.ru:8080/",
        response="https://yandex.ru:8080/"
    ))
    id += 1

    l_add(Test(
        id=id,
        request="https://yandex.ru:80/",
        response="https://yandex.ru:80/"
    ))
    id += 1

    l_add(Test(
        id=id,
        request="http://yandex.ru:443/",
        response="http://yandex.ru:443/"
    ))
    id += 1

    metafunc.parametrize("load_query", l, indirect=True, ids=l_id)


def test_ports_weak(gemini, html, load_query):
    test = load_query
    html.test(
        name="#%2d: " % test.id + test.request,
        suite="Ports.Weak ",
        description="""
            Checks response for %s""" % (
                test.request,
            )
    )
    response = gemini.geminicl.request(
        url=test.request,
        type="weak",
        )[0]

    assert ('CanonizedUrl: "' + test.response + '"') in response

def test_ports_strong(gemini, html, load_query):
    test = load_query
    html.test(
        name="#%2d: " % test.id + test.request,
        suite="Ports.Strong ",
        description="""
            Checks response for %s""" % (
            test.request,
        )
    )
    response = gemini.geminicl.request(
        url=test.request,
        type="strong",
        )[0]

    assert ('CanonizedUrl: "' + test.response + '"') in response
