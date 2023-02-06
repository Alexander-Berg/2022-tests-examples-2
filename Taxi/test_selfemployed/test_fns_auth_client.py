import datetime

import aiohttp.web
import lxml.etree
import pytest

from testsuite.utils import http

from selfemployed.fns import auth


async def test_authorize_ok(se_web_context, mockserver, load_binary):
    request_ = _fix_indent(load_binary('request.xml'))
    response = load_binary('ok_response.xml')

    @mockserver.handler('/FnsAuthService')
    async def _handle(request: http.Request):
        assert _fix_indent(request.get_data()) == request_
        return aiohttp.web.Response(
            body=response, content_type='application/xml',
        )

    token, expire_utc = await se_web_context.auth_fns.get_token()
    assert token == 'AUTH_TOKEN'
    assert expire_utc == datetime.datetime(2021, 1, 1, 12)


async def test_authorize_fail(se_web_context, mockserver, load_binary):
    request_ = _fix_indent(load_binary('request.xml'))
    response = load_binary('bad_response.xml')

    req = None

    @mockserver.handler('/FnsAuthService')
    async def _handle(request: http.Request):
        nonlocal req
        # assert _fix_indent(request.get_data()) == request_
        req = _fix_indent(request.get_data())
        return aiohttp.web.Response(
            body=response, content_type='application/xml',
        )

    with pytest.raises(auth.AuthFail):
        await se_web_context.auth_fns.get_token()

    assert req == request_


def _fix_indent(xml_data: bytes) -> bytes:
    etree = lxml.etree.fromstring(xml_data)
    # default pretty_print=False keeps indents from source
    return lxml.etree.tostring(etree, pretty_print=True)
