# -*- coding: utf-8 -*-
import allure
import pytest
import re

from common.client import MordaClient
from common.geobase import Regions
from common.morda import Morda
from hamcrest import equal_to

DOMAIN = 'yandex.ru'
URL_FROM = Morda.get_origin()
REGIONS = {
    Regions.MINSK: '.by',
    Regions.KYIV: '.ua',
    Regions.ASTANA: '.kz',
}


@allure.step('Check correct redirect')
def check_redirect(res, url_to):
    assert res.is_ok(equal_to(302)), 'Expect redirect status, got {}'.format(
        res.response.status_code)
    location = res.response.headers['Location']
    assert location.startswith(
        url_to), 'Expect location starts with {}, got {}'.format(url_to, location)


@allure.feature('national redirects')
@allure.story('redirects')
@pytest.mark.parametrize('region', REGIONS)
def test_redirect_from_ru(region):
    url_to = re.sub(r'\.ru$', REGIONS[region], URL_FROM)
    client = MordaClient()
    client.set_cookie_yandex_gid(region, '.{}'.format(DOMAIN))
    response = client.request(url=URL_FROM, allow_redirects=False).send()
    check_redirect(response, url_to)


def test_expected_origin():
    assert URL_FROM.endswith(DOMAIN)
