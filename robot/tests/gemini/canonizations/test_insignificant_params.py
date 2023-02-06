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
        name="insignificant_params",
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

    params_any_val = [
        "s_id",
        "ses",
        "session",
        "sessid",
        "sess",
        "no_cache",
        "nocache",
        "expandsection",
        "rnd",
        "test",
        "staz",
        "tophits",
        "kk",
        "href",
        "thsh",
        "reid",
        "pairslogin",
        "cart_id",
        "back_url",
        "referer",
        "redirect",
        "href"
    ]
    id = 1
    url = "http://yandex.ru/"
    main_url = "http://www.yandex.ru/"
    for param in params_any_val:
        l_add(Test(
            id=id,
            request=url + "?" + param + "=asd123",
            response=main_url
        ))
        id += 1
        l_add(Test(
            id=id,
            request=url + "?" + param,
            response=main_url
        ))
        id += 1

    l_add(Test(
        id=id,
        request=url + "?" + params_any_val[0] + "=val321&" + params_any_val[0] + "=asd321",
        response=main_url
    ))
    id += 1

    l_add(Test(
        id=id,
        request=url + "?" + params_any_val[0] + "&" + params_any_val[0],
        response=main_url
    ))
    id += 1

    l_add(Test(
        id=id,
        request=url + "?" + params_any_val[0] + "=" + params_any_val[0] + "=qwerty",
        response=main_url
    ))
    id += 1

    l_add(Test(
        id=id,
        request=url + "?" + params_any_val[1] + "=asd&nonfake=qwerty",
        response=main_url + "?nonfake=qwerty"
    ))
    id += 1

    l_add(Test(
        id=id,
        request=url + "?nonfake=qwerty&" + params_any_val[1] + "=asd",
        response=main_url + "?nonfake=qwerty"
    ))
    id += 1

    l_add(Test(
        id=id,
        request=url + "?" + params_any_val[1].upper(),
        response=main_url
    ))
    id += 1

    l_add(Test(
        id=id,
        request=url + "?" + "&".join(params_any_val),
        response=main_url
    ))
    id += 1

    l_add(Test(
        id=id,
        request=url + "?" + "&".join((param + "=qwe" for param in params_any_val)),
        response=main_url
    ))
    id += 1

    l_add(Test(
        id=id,
        request=url + "?sid=87bd3f60-9eff-11df-953d-0019b9f99000",
        response=main_url
    ))
    id += 1

    metafunc.parametrize("load_query", l, indirect=True, ids=l_id)


def test_insignificant_params_weak(gemini, html, load_query):
    test = load_query
    html.test(
        name="#%2d: " % test.id + test.request,
        suite="InsignificantParams.Weak ",
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


def test_insignificant_params_strong(gemini, html, load_query):
    test = load_query
    html.test(
        name="#%2d: " % test.id + test.request,
        suite="InsignificantParams.Strong ",
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
