# -*- coding: utf-8 -*-
from __future__ import print_function
import logging
import allure
import pytest
from common.client import MordaClient
from common.geobase import Regions
from common.cookies.y import CookieYp
from common.morda import DesktopMain, TouchMain, PdaMain, DesktopCom, \
    TouchCom, PdaCom, DesktopComTr, TouchComTr, PdaComTr

logger = logging.getLogger(__name__)


def get_mordas():
    result = [
        DesktopCom(),
        TouchCom(),
        PdaCom(),
        DesktopComTr(region=Regions.ISTANBUL),
        TouchComTr(region=Regions.ISTANBUL),
        PdaComTr(region=Regions.ISTANBUL),
        # DesktopYaru(),
        # TouchYaru(),
        # PdaYaru(),
        # DesktopHwLg(),
        # DesktopHwLgV2(),
        # DesktopHwBmw(),
        # DesktopHwOp(),
        # DesktopHwPh(),
        # DesktopComTrAll(region=Regions.ISTANBUL),
    ]

    for region in [Regions.MOSCOW, Regions.KYIV, Regions.MINSK, Regions.ASTANA]:
        result.append(DesktopMain(region=region))
        result.append(TouchMain(region=region))
        result.append(PdaMain(region=region))
        # result.append(DesktopMainAll(region=region))
        # result.append(TouchMainWp(region=region))
        # result.append(TouchMainAll(region=region))
        # result.append(TelMain(region=region))

    return result


def ids(value):
    return str(value)


CLID_PARAM = 'clid'
CLH = 'clh'
TEST_CLID = '123456'
TEST_CLID_2 = '654321'
TEST_CLID_WITH_HYPHEN = '123-456'

COOKIE_YP_YGU_VALUE = '1571409796.ygu.0'


@allure.feature('morda')
@allure.story('clid')
@pytest.mark.parametrize('morda', get_mordas(), ids=ids)
def test_clid(morda):
    client = MordaClient(morda)

    req = client.morda()
    client.set_cookie_yp(COOKIE_YP_YGU_VALUE)

    req.params[CLID_PARAM] = TEST_CLID
    result = req.send()

    with allure.step('Check morda response'):
        assert result.is_ok(), 'Failed to get morda'

    cookieparser = CookieYp(client.get_cookie_yp())
    cookieparser.test_block(CLH, TEST_CLID)


@allure.feature('morda')
@allure.story('clid')
@pytest.mark.parametrize('morda', get_mordas(), ids=ids)
def test_clid_hyphen(morda):
    client = MordaClient(morda)

    req = client.morda()
    client.set_cookie_yp(COOKIE_YP_YGU_VALUE)

    req.params[CLID_PARAM] = TEST_CLID_WITH_HYPHEN
    result = req.send()

    with allure.step('Check morda response'):
        assert result.is_ok(), 'Failed to get morda'

    cookieparser = CookieYp(client.get_cookie_yp())
    cookieparser.test_block(CLH, TEST_CLID_WITH_HYPHEN)


@allure.feature('morda')
@allure.story('clid')
@pytest.mark.parametrize('morda', get_mordas(), ids=ids)
def test_clid_overwrite(morda):
    client = MordaClient(morda)

    req = client.morda()
    client.set_cookie_yp(COOKIE_YP_YGU_VALUE)

    req.params[CLID_PARAM] = TEST_CLID
    req.send()

    req2 = client.morda()
    req2.params[CLID_PARAM] = TEST_CLID_2
    result = req2.send()

    with allure.step('Check morda response'):
        assert result.is_ok(), 'Failed to get morda'

    cookieparser = CookieYp(client.get_cookie_yp())
    cookieparser.test_block(CLH, TEST_CLID_2)
