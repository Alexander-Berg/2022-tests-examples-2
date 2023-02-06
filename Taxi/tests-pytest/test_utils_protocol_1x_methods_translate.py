import pytest

from utils.protocol_1x.methods import translate

import mocks


@pytest.mark.filldb(_fill=False)
@pytest.mark.translations([
    ('t', 'k', 'ru', 'value_ru'),
    ('t', 'k', 'en', 'value_en'),
])
@pytest.mark.asyncenv('blocking')
@pytest.mark.parametrize('args,code,response', [
    ({'keyset': ['t'], 'key': ['k'], 'lang': ['ru']}, 200, 'value_ru'),
    ({'keyset': ['t'], 'key': ['k'], 'lang': ['en']}, 200, 'value_en'),
    ({'keyset': ['z'], 'key': ['k'], 'lang': ['ru']}, 406, 'unknown keyset'),
    ({'keyset': ['__getattr__'], 'key': ['k'], 'lang': ['ru']}, 406,
     'wrong keyset __getattr__'),
    ({'keyset': ['t'], 'key': ['z'], 'lang': ['ru']}, 406,
     'translation not found'),
    ({'keyset': ['t'], 'key': ['k'], 'lang': ['u']}, 406,
     'translation not found'),
    ({'keyset': ['a', 'b'], 'k': ['key'], 'lang': ['ru']}, 400,
     'keyset must be only one'),
    ({'keyset': ['a', 'b'], 'k': ['key'], 'lang': ['ru']}, 400,
     'keyset must be only one'),
    ({'keyset': ['t'], 'key': ['a', 'b'], 'lang': ['ru']}, 400,
     'key must be only one'),
    ({'keyset': ['t'], 'key': ['k'], 'lang': ['a', 'b']}, 400,
     'lang must be only one'),
    ({'key': ['k'], 'lang': ['a', 'b']}, 400, 'keyset is missing in request'),
    ({'keyset': ['t'], 'lang': ['ru']}, 400, 'key is missing in request'),
    ({'keyset': ['t'], 'key': ['k']}, 400, 'lang is missing in request'),
])
def test_translate(args, code, response):
    method = translate.Method()
    request = mocks.FakeRequest()
    request.args = args
    result = method.render_GET(request)
    assert request.headers['Content-Type'] == 'text/plain; charset=utf-8'
    assert result == response
    assert request.response_code == code
