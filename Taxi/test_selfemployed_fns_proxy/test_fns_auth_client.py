import datetime

import aiohttp.web
import lxml.etree
import pytest

from testsuite.utils import http

from selfemployed_fns_proxy.fns import auth

# pylint: disable=invalid-name
pytestmark = [
    pytest.mark.unmock_fns_auth,
    pytest.mark.parametrize('business_unit', ('taxi', 'test_business_unit')),
]


async def test_authorize_ok(
        web_context, mockserver, load_binary, business_unit,
):
    request_ = _fix_indent(load_binary('request.xml'))
    response = load_binary('ok_response.xml')

    @mockserver.handler('/FnsAuthService')
    async def _handle(request: http.Request):
        assert _fix_indent(request.get_data()) == request_
        return aiohttp.web.Response(
            body=response, content_type='application/xml',
        )

    # pylint: disable=protected-access
    token, expire_utc = await web_context.fns.clients[
        business_unit
    ]._token_cache._auth_client.get_token()

    assert token == 'AUTH_TOKEN'
    assert expire_utc == datetime.datetime(2021, 1, 1, 12)


async def test_authorize_fail(
        web_context, mockserver, load_binary, business_unit,
):
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
        # pylint: disable=protected-access
        await web_context.fns.clients[
            business_unit
        ]._token_cache._auth_client.get_token()

    assert req == request_


def _fix_indent(xml_data: bytes) -> bytes:
    etree = lxml.etree.fromstring(xml_data)
    # default pretty_print=False keeps indents from source
    return lxml.etree.tostring(etree, pretty_print=True)
