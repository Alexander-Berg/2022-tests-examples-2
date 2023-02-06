# -*- coding: utf-8 -*-
import logging
import allure
import pytest

from common import schema
from common.morda import DesktopMain, TouchMain
from common.client import MordaClient
from common.geobase import Regions

logger = logging.getLogger(__name__)

BLOCK = 'UserProfile'
YASM_SIGNAL_NAME = 'morda_user_profile_{}_tttt'

AB_FLAGS_TOUCH = 'touch_redesign_new=1'
AB_FLAGS_DESKTOP = 'new_profile_big=1'

MADM_PROFILE_MOCK = 'profile=profile_touch_big_searchapp_mock'
HTTP_MOCK_MARKET_CART = 'market_cart@func_tests_market_cart'
HTTP_MOCK_TRUST_API = 'trust_api@func_tests_trust_api'

USER_LOGIN = 'accaunt.testing'
USER_PASSWORD = '7d9-5qP-y5u-sjH'


@allure.feature('morda', 'user_profile', 'function_tests_stable')
@allure.testcase('https://testpalm.yandex-team.ru/testcase/home_all-1097')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME)
class TesterUserProfileDesktopMoscow(object):
    def setup_class(self):
        self.data = _fetch_data(DesktopMain(region=Regions.MOSCOW), params={
            'ab_flags': AB_FLAGS_DESKTOP,
            'madm_mocks': MADM_PROFILE_MOCK,
        })
        self.block = self.data.get(BLOCK)
        self.href_domain = 'ru'

    @allure.story('block exists')
    def test_existance(self):
        _test_existance(self)

    @allure.story('block show')
    def test_common(self):
        _test_common(self)

    @allure.story('login section')
    def test_section(self):
        _test_section_existance(self, 'login')

    @allure.story('menu item mail')
    def test_menu_mail(self):
        _test_menu_mail(self)

    @allure.story('schema')
    def test_schema(self):
        schema.validate_schema_by_block(self.block, 'user_profile', 'desktop')


# HOME-77168
# @allure.feature('morda', 'user_profile', 'function_tests_stable')
# @allure.testcase('https://testpalm.yandex-team.ru/testcase/home_all-1097')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME)
class TesterUserProfileDesktopMoscowLogin(object):
    def setup_class(self):
        self.data = _fetch_data_login(DesktopMain(region=Regions.MOSCOW), params={
            'ab_flags': AB_FLAGS_DESKTOP,
            'madm_mocks': MADM_PROFILE_MOCK,
            'httpmock': ','.join([HTTP_MOCK_TRUST_API, HTTP_MOCK_MARKET_CART]),
        })
        self.block = self.data.get(BLOCK)
        self.href_domain = 'ru'

    @allure.story('block exists')
    def test_existance(self):
        _test_existance(self)

    @allure.story('block show')
    def test_common(self):
        _test_common(self)

    @allure.story('auth section')
    def test_section(self):
        _test_section_existance(self, 'auth')

    @allure.story('menu item plus')
    def test_menu_plus(self):
        _test_menu_plus(self)

    @allure.story('menu item market')
    def test_menu_market(self):
        _test_menu_market_cart(self)

    @allure.story('schema')
    def test_schema(self):
        schema.validate_schema_by_block(self.block, 'user_profile', 'desktop')


@allure.feature('morda', 'user_profile', 'function_tests_stable')
@allure.testcase('https://testpalm.yandex-team.ru/testcase/home_all-1098')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME)
class TestUserProfileTouchMoscow(object):
    def setup_class(self):
        self.data = _fetch_data(TouchMain(region=Regions.MOSCOW), params={
            'ab_flags': AB_FLAGS_TOUCH,
            'madm_mocks': MADM_PROFILE_MOCK,
        })
        self.block = self.data.get(BLOCK)
        self.href_domain = 'ru'

    @allure.story('block exists')
    def test_existance(self):
        _test_existance(self)

    @allure.story('block show')
    def test_common(self):
        _test_common(self)

    @allure.story('login section')
    def test_section(self):
        _test_section_existance(self, 'login')

    @allure.story('schema')
    def test_schema(self):
        schema.validate_schema_by_block(self.block, 'user_profile', 'touch')


# HOME-77168
# @allure.feature('morda', 'user_profile', 'function_tests_stable')
# @allure.testcase('https://testpalm.yandex-team.ru/testcase/home_all-1098')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME)
class TestUserProfileTouchMoscowLogin(object):
    def setup_class(self):
        self.data = _fetch_data_login(TouchMain(region=Regions.MOSCOW), params={
            'ab_flags': AB_FLAGS_TOUCH,
            'madm_mocks': MADM_PROFILE_MOCK,
            'httpmock': HTTP_MOCK_TRUST_API,
        })
        self.block = self.data.get(BLOCK)
        self.href_domain = 'ru'

    @allure.story('block exists')
    def test_existance(self):
        _test_existance(self)

    @allure.story('block show')
    def test_common(self):
        _test_common(self)

    @allure.story('auth section')
    def test_section(self):
        _test_section_existance(self, 'auth')

    @allure.story('schema')
    def test_schema(self):
        schema.validate_schema_by_block(self.block, 'user_profile', 'touch')


# ==============================


def _fetch_data(morda, **kwargs):
    client = MordaClient(morda)
    response = client.cleanvars([BLOCK], **kwargs).send()
    with allure.step('Fetch data'):
        assert response.is_ok(), 'Failed to get cleanvars'

    res = response.json()
    assert res.get('madm_mock_error') is None, res.get('madm_mock_error')
    return res


def _fetch_data_login(morda, **kwargs):
    client = MordaClient(morda)
    passport_host = client.cleanvars(['Mail']).send().json()['Mail']['auth_host']
    login_response = client.login(passport_host, USER_LOGIN, USER_PASSWORD).send()
    with allure.step('Login'):
        assert login_response.is_ok(), 'Failed to login'
    response = client.cleanvars([BLOCK], **kwargs).send()
    with allure.step('Fetch data'):
        assert response.is_ok(), 'Failed to get cleanvars'
    client.logout(passport_host)

    res = response.json()
    assert res.get('madm_mock_error') is None, res.get('madm_mock_error')
    return res


def _test_existance(test_case):
    with allure.step('Test if block exists'):
        assert test_case.data[BLOCK], 'Failed to get block'


def _test_common(test_case):
    with allure.step('Test if block shows'):
        assert test_case.block['show'], 'Show must be 1'


def _test_section_existance(test_case, section_name):
    with allure.step('Test if section exists'):
        assert test_case.block[section_name], 'Section ' + section_name + ' must exists'


def _test_menu_plus(test_case):
    with allure.step('Test if section exists'):
        assert test_case.block['menu'], 'Section menu must exists'
    _test_menu_item(test_case, 'plus', 'plus', '4200')


def _test_menu_market_cart(test_case):
    with allure.step('Test if section exists'):
        assert test_case.block['menu'], 'Section menu must exists'
    _test_menu_item(test_case, 'market', 'count', u'11 000 ₽')


def _test_menu_mail(test_case):
    with allure.step('Test if section exists'):
        assert test_case.block['menu'], 'Section menu must exists'
    _test_menu_item(test_case, 'create_mail')


def _test_menu_item(test_case, menu_item_id, counter_type=None, counter_value=None):
    with allure.step('Test if menu item ' + menu_item_id + ' exists'):
        item = {}
        for menu_item in test_case.block['menu']:
            if menu_item['id'] == menu_item_id:
                item = menu_item
        assert item, 'Menu item "' + menu_item_id + '" must exists'
    if counter_type and len(counter_type) > 0:
        with allure.step('Test ' + menu_item_id + ' counter'):
            assert item['counter']['type'] == counter_type, \
                menu_item_id + ' counter has incorrect type, expected "' + counter_type + '"'
            assert item['counter']['value'] == counter_value, \
                menu_item_id + ' counter has incorrect value, expected "' + counter_value + '"'
