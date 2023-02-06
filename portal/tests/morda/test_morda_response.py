# -*- coding: utf-8 -*-
import logging

import allure
import pytest
from hamcrest import equal_to, assert_that

from common.client import MordaClient
from common.geobase import Regions
from common.html import get_page_info
from common.morda import DesktopMain, TouchMain, PdaMain, TelMain, \
    TouchMainWp, TouchMainAll, DesktopYaru, TouchYaru, PdaYaru, DesktopHwLg, DesktopHwBmw, DesktopHwLgV2, DesktopCom, \
    TouchCom, PdaCom, DesktopComTr, TouchComTr, PdaComTr, DesktopHwOp, DesktopHwPh, DesktopComTrAll, DesktopMainAll

logger = logging.getLogger(__name__)


def get_params():
    result = [
        DesktopHwLg(),
        DesktopHwLgV2(),
        DesktopHwBmw(),
        DesktopHwOp(),
        DesktopHwPh()
    ]

    for no_pretix in [True, False]:
        result.append(DesktopYaru(no_prefix=no_pretix))
        result.append(TouchYaru(no_prefix=no_pretix))
        result.append(PdaYaru(no_prefix=no_pretix))
        result.append(DesktopCom(no_prefix=no_pretix))
        result.append(TouchCom(no_prefix=no_pretix))
        result.append(PdaCom(no_prefix=no_pretix))
        result.append(DesktopComTr(region=Regions.ISTANBUL, no_prefix=no_pretix))
        result.append(DesktopComTrAll(region=Regions.ISTANBUL, no_prefix=no_pretix))
        result.append(TouchComTr(region=Regions.ISTANBUL, no_prefix=no_pretix))
        result.append(PdaComTr(region=Regions.ISTANBUL, no_prefix=no_pretix))

    for region in [Regions.MOSCOW, Regions.KYIV, Regions.MINSK, Regions.ASTANA]:
        for no_pretix in [True, False]:
            result.append(DesktopMain(region=region, no_prefix=no_pretix))
            result.append(DesktopMainAll(region=region, no_prefix=no_pretix))
            result.append(TouchMain(region=region, no_prefix=no_pretix))
            result.append(TouchMainWp(region=region, no_prefix=no_pretix))
            result.append(TouchMainAll(region=region, no_prefix=no_pretix))
            result.append(PdaMain(region=region, no_prefix=no_pretix))
            result.append(TelMain(region=region, no_prefix=no_pretix))

    return result


def ids(value):
    return str(value)


@allure.feature('morda')
@allure.story('morda_response')
@pytest.mark.yasm(signal='morda_response_{}_tttt')
@pytest.mark.parametrize('morda', get_params(), ids=ids)
def test_response(morda):
    client = MordaClient(morda)
    result = client.morda().send()
    with allure.step('Check morda response'):
        assert result.is_ok(), 'Failed to get morda'
    if morda.morda_content is not None and morda.get_domain() != 'ua':
        page_info = get_page_info(result.content())

        with allure.step('Check morda content is "{}"'.format(morda.morda_content)):
            assert_that(page_info.get('content'), equal_to(morda.morda_content))
        with allure.step('Check morda domain is "{}"'.format(morda.get_domain())):
            assert_that(page_info.get('domain'), equal_to(morda.get_domain()))
