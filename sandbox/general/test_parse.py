# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import pytest
import yatest.common
from sandbox.projects.geosuggest.response.parse import response_as_object


def read_file(name):
    with open(yatest.common.source_path(os.path.join('sandbox/projects/geosuggest/response/ut/examples', name))) as fd:
        return fd.read()


def test_suggest_geo_v1_js():
    obj = response_as_object(read_file('suggest-geo-v1.js'))
    assert obj[0] == 'Россия, Москва, Троицк, микрорайон к'
    assert obj[1][0][0] == 'maps'


def test_suggest_geo_v9_json():
    obj = response_as_object(read_file('suggest-geo-v9.json'))

    assert obj['part'] == 'шекснинская 16'
    assert obj['results'][0]['title']['text'] == 'Шекснинская улица, 16'

    assert obj['suggest_reqid'] == 'not involved in diff'
    assert obj['results'][0]['log_id']['suggest_reqid'] == 'not involved in diff'
    assert obj['results'][0]['log_id']['server_reqid'] == 'not involved in diff'


def test_suggest_geo_v5_json():
    obj = response_as_object(read_file('suggest-geo-v5.json'))
    assert obj[0] == 'лесна'
    assert obj[1][0][3]['hl'][0][1] == 5


def test_suggest_geo_mobile():
    obj = response_as_object(read_file('suggest-geo-mobile.xml'))
    assert obj['suggest']['item'][0]['@lat'] == '56.8506'
    assert obj['suggest']['item'][0]['display']['t'] == 'Совхозная улица, 1А, Ижевск, Удмуртская Республика, Россия'


def test_suggest_geo_mobile_v3():
    obj = response_as_object(read_file('suggest-geo-mobile-v3.bin'))
    assert 'reqid' not in obj
    assert obj['item'][0]['search_text'] == 'Россия, Санкт-Петербург, Пушкин'
    assert obj['item'][0]['distance']['value'] == 51037.61509995184
    assert obj['item'][0]['type'] == 'TOPONYM'


def test_suggest_geo_mobile_v4_bin():
    obj = response_as_object(read_file('suggest-geo-mobile-v4.bin'))
    assert obj['reqid'] == 'not involved in diff'
    assert obj['item'][0]['title']['text'] == 'сбербанк россии, банкоматы'
    assert obj['item'][0]['log_id'] == {
        'suggest_reqid': 'not involved in diff',
        'user_params': {
            'request': 'С',
            'll': '37.525410,55.531601',
            'spn': '0.00703812,0.00703812',
            'ull': '37.525410,55.532299',
            'lang': 'ru'
        },
        'prefixtop': True,
        'type': 'query',
        'text': 'сбербанк россии, банкоматы'
    }


def test_v0():
    tokens = ['{}'.format(x) for x in range(100)]
    line = '\t'.join(tokens)

    obj = response_as_object((line + '\n').encode('utf-8'))
    assert isinstance(obj, list)
    assert len(obj) == 1
    assert obj[0] == line

    obj = response_as_object((line + '\n' + line).encode('utf-8'))
    assert isinstance(obj, list)
    assert obj == [line, line]

    with pytest.raises(ValueError):
        response_as_object((line + '\n' + 'aba\tcaba').encode('utf-8'))


def test_strange():
    obj = response_as_object(b'')
    assert isinstance(obj, list)
    assert obj == []

    for strange_input in [b'\x00\x01\x02', b'aba caba']:
        with pytest.raises(ValueError):
            response_as_object(strange_input)
