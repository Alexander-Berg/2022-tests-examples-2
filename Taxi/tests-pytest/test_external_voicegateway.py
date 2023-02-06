import datetime

import pytest

from taxi.core import arequests
from taxi.external import voice_gateway


PHONE = '+70000000000'
INTRO = 'intro'
CITY = 'city'
VALID_TOKEN = 'VALID'
GATEWAY_ID = 'test_vgw'
HOST = 'https://vgv'
FWD_ID = 'fwdid' * 8
TALK_ID = 'talk_id'


@pytest.mark.filldb()
@pytest.inline_callbacks
def test_get_talk_list_ok(asyncenv, load, areq_request):
    @areq_request
    def requests_request(method, url, **kwargs):
        auth_header = kwargs.get('headers', {}).get('Authorization')
        if method != arequests.METHOD_GET:
            raise voice_gateway.RequestError('Invalid method')
        if HOST not in url:
            raise voice_gateway.RequestError('Invalid host')
        if auth_header != 'Basic %s' % VALID_TOKEN:
            raise voice_gateway.RequestError('Invalid token')
        data = kwargs['params']
        if not isinstance(data['start_from'], basestring) or not isinstance(
                data['start_to'], basestring,
        ):
            raise voice_gateway.RequestError('Invalid request')

        return areq_request.response(200, body=load('get_talks_ok.json'))

    start = datetime.datetime(2015, 11, 28, 17, 50)
    end = datetime.datetime(2015, 11, 28, 17, 55)
    talks = yield voice_gateway.get_talk_list(
        HOST, VALID_TOKEN, start, end,
    )
    assert len(talks) == 2
    for talk in talks:
        assert 'redirectionid' in talk
        assert 'id' in talk
        assert 'start' in talk
        assert 'length' in talk
        assert 'caller' in talk
        assert 'callee' in talk
        assert len(talk['redirectionid']) >= 32


@pytest.mark.parametrize(
    'token,code_or_exc,response,error',
    [
        # invalid token
        ('invalid token', 403, '', voice_gateway.RequestError),
        # http error
        (VALID_TOKEN, 500, '', voice_gateway.RequestError),
        # http error
        (VALID_TOKEN, 400, '', voice_gateway.RequestError),
        # timeout error
        (VALID_TOKEN, arequests.TimeoutError, '', voice_gateway.RequestError),
        # invalid scheme
        (
            VALID_TOKEN,
            arequests.SchemeNotSupported,
            '',
            voice_gateway.RequestError,
        ),
        # invalid response
        (VALID_TOKEN, 200, '', voice_gateway.InvalidResponseError),
        # invalid json
        (VALID_TOKEN, 200, 'asdf', voice_gateway.InvalidResponseError),
    ],
)
@pytest.mark.filldb()
@pytest.inline_callbacks
def test_get_talk_list_error(
        token, code_or_exc, response, error, asyncenv, areq_request,
):
    @areq_request
    def requests_request(method, url, **kwargs):
        auth_header = kwargs.get('headers', {}).get('Authorization')
        if method != arequests.METHOD_GET:
            raise voice_gateway.RequestError('Invalid method')
        if HOST not in url:
            raise voice_gateway.RequestError('Invalid host')
        if auth_header != 'Basic %s' % VALID_TOKEN:
            raise voice_gateway.RequestError('Invalid token')
        data = kwargs['params']
        if not isinstance(data['start_from'], basestring) or not isinstance(
                data['start_to'], basestring,
        ):
            raise voice_gateway.RequestError('Invalid request')
        if not isinstance(code_or_exc, int):
            raise code_or_exc('Error')
        code = code_or_exc
        return areq_request.response(code, body=response)

    start = datetime.datetime(2015, 11, 28, 17, 50)
    end = datetime.datetime(2015, 11, 28, 17, 55)
    with pytest.raises(error):
        yield voice_gateway.get_talk_list(
            HOST, VALID_TOKEN, start, end,
        )
