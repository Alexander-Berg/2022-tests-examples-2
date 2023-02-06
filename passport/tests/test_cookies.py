# -*- coding: utf-8 -*-
from passport.backend.core.cookies.utils.utils import parse_cookie


def test_cookie_parse_passp_24271():
    expected = {
        'yabs-frequency': 'true',
        'mda': '0',
    }

    actual = parse_cookie("yabs-frequency=true; ; ; ; mda=0;")
    assert actual == dict({'': ''}, **expected)

    actual = parse_cookie("yabs-frequency=true; mda=0;")
    assert actual == expected

    actual = parse_cookie("yabs-frequency=true; ; ; ; mda=0; ; ; ; ")
    assert actual == dict({'': ''}, **expected)

    actual = parse_cookie(" ; ; ; ; ; ; yabs-frequency=true; ; ; ; mda=0;")
    assert actual == dict({'': ''}, **expected)

    actual = parse_cookie("yabs-frequency=true;  = 1; mda=0")
    assert actual == dict({'': '1'}, **expected)

    actual = parse_cookie("yabs-frequency=true; 1 = ; mda=0")
    assert actual == dict({'1': ''}, **expected)

    actual = parse_cookie("yabs-frequency=true; 1 ; mda=0")
    assert actual == dict({'1': ''}, **expected)

    actual = parse_cookie("yabs-frequency=true; 1; mda=0")
    assert actual == dict({'1': ''}, **expected)


def test_cookies():
    actual = parse_cookie('dismiss-top=6; CP=null*; PHPSESSID=0a539d42abc001cdc762809248d4beed; a=42; b="\\\";"')
    expected = {
        'CP': u'null*',
        'PHPSESSID': u'0a539d42abc001cdc762809248d4beed',
        'a': u'42',
        'dismiss-top': u'6',
        'b': u'\";'
    }
    assert actual == expected

    actual = parse_cookie('fo234{=bar; blub=Blah')
    expected = {'fo234{': u'bar', 'blub': u'Blah'}
    assert actual == expected

    # PASSP-12573
    actual = parse_cookie(u'a=b; foo=бар; c=d'.encode('utf-8'))
    expected = {'foo': u'бар', 'a': 'b', 'c': 'd'}
    assert actual == expected


# отсюда взят пример: https://github.com/pallets/werkzeug/commit/d4087a3072c8387d2d4dd57f988d051a2e202b25
def test_bad_cookies():
    actual = parse_cookie('first=IamTheFirst ; a=1; oops ; a=2 ;second = andMeTwo;', cls=list)
    expected = [
        ('first', u'IamTheFirst'),
        ('a', u'1'),
        ('oops', u''),
        ('a', u'2'),
        ('second', u'andMeTwo'),
    ]
    expected.reverse()
    assert actual == expected
