import typing

import pytest

from eats_integration_proxy.internal import entities
from eats_integration_proxy.internal import proxy

PARTNER = entities.Partner(
    id=0,
    brand_id='',
    slug='',
    protocol='http',
    host='host',
    port=80,
    login='test_login',
    password='test_password',
    token='test_token',
)


def render(content: typing.Any) -> typing.Any:
    return proxy.render_template(content, PARTNER)


async def test_render_template_str():
    assert render('{{ LOGIN }}') == 'test_login'
    assert render('{{ PASSWORD}}') == 'test_password'
    assert render('{{TOKEN}}') == 'test_token'
    assert render('{{LOGIN}} {{PASSWORD}}') == 'test_login test_password'

    with pytest.raises(proxy.IncorrectTemplate):
        render('{{ UNKNOWN }}')
    with pytest.raises(proxy.IncorrectTemplate):
        render('{{ login }}')


async def test_render_template_dict():
    assert render({'login': '{{ LOGIN }}'}) == {'login': 'test_login'}
    assert render({'{{PASSWORD}}': 100}) == {'test_password': 100}
    assert render({'q': {'w': '{{TOKEN}}'}}) == {'q': {'w': 'test_token'}}


async def test_render_template_list():
    assert render(['qwe', '{{LOGIN}}']) == ['qwe', 'test_login']
    assert render([{'{{LOGIN}}': '{{PASSWORD}}'}]) == [
        {'test_login': 'test_password'},
    ]
