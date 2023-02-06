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
        name="remove_default",
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

def pytest_funcarg__load_query1(request):
    return request.param

l1 = []
l_id1 = []


def l_add1(test):
    l1.append(test)
    l_id1.append("%2d" % test.id)


# test factory ******************************************************
def pytest_generate_tests(metafunc):

    global l
    global l_id
    l=[]
    l_id=[]

    Test = namedtuple("Test", ["id", "request", "response"])

    defaults = [
        "index.html",
        "index.htm",
        "index.php",
        "index.php3",
        "index.php4",
        "default.asp",
        "default.aspx",
        ]
    url = "http://yandex.ru/"
    main_url = "http://www.yandex.ru/"
    url_path = "http://yandex.ru/path/"
    main_url_path = "http://www.yandex.ru/path"
    id = 1
    for default in defaults:
        l_add(Test(
            id=id,
            request=url + default,
            response=main_url
        ))
        id += 1

    for default in defaults:
        l_add(Test(
            id=id,
            request=url_path + default,
            response=main_url_path
        ))
        id += 1

    l_add(Test(
        id=id,
        request=url + "?param=" + defaults[0],
        response=main_url + "?param=" + defaults[0]
    ))
    id += 1

    l_add(Test(
        id=id,
        request=url + "?param=" + defaults[1],
        response=main_url + "?param=" + defaults[1]
    ))
    id += 1

    l_add(Test(
        id=id,
        request=url + defaults[0] + "?param=" + defaults[0],
        response=main_url + "?param=" + defaults[0]
    ))
    id += 1

    l_add(Test(
        id=id,
        request=url + defaults[1] + "?param=" + defaults[1],
        response=main_url + "?param=" + defaults[1]
    ))
    id += 1

    l_add(Test(
        id=id,
        request=url + defaults[0] + "/",
        response=main_url + defaults[0]
    ))
    id += 1

    l_add(Test(
        id=id,
        request=url + defaults[1] + "/",
        response=main_url + defaults[1]
    ))
    id += 1

    l_add(Test(
        id=id,
        request="http://index.php.ru/",
        response="http://index.php.ru/"
    ))
    id += 1

    l_add(Test(
        id=id,
        request=url + "php3",
        response=main_url + "php3"
    ))
    id += 1

    l_add(Test(
        id=id,
        request=url_path + "html",
        response=main_url_path + "/html"
    ))
    id += 1

    l_add(Test(
        id=id,
        request=url_path + "aspx/",
        response=main_url_path + "/aspx"
    ))
    id += 1

    replacements = {
        "php3": "php",
        "php4": "php",
        "php5": "php5",
        "aspx": "asp",
        "html": "htm"
    }

    for replacement in replacements:
        l_add(Test(
            id=id,
            request=url_path + "test." + replacement,
            response=main_url_path + "/test." + replacements[replacement]
        ))
        id += 1


    metafunc.parametrize("load_query", l, indirect=True, ids=l_id)


def test_remove_defaults(gemini, html, load_query):
    test = load_query
    html.test(
        name="#%2d: " % test.id + test.request,
        suite="Remove index.html and others ",
        description="""
            Checks response for %s""" % (
            test.request,
        )
    )
    response = gemini.geminicl.request(
        url=test.request,
        type="strong",
        )[0]

    assert ('CanonizedUrl: "' + test.response + '"') in response, "Wrong response: \n\n" + response + \
                                                             "\n\nExpected: \n\n MainUrl: " + test.response
