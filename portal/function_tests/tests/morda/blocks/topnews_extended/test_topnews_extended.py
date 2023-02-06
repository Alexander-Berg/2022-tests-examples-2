# -*- coding: utf-8 -*-
import logging
import allure
import pytest

from common import schema
from common.morda import TouchMain, TouchCom
from common.client import MordaClient
from common.geobase import Regions

logger = logging.getLogger(__name__)

"""
HOME-75127
Проверяет работу блока Новости для Topnews_extended.
"""

AB_FLAGS_TOUCH = 'topnews_extended=1:topnews_from_avocado=0:topnews_extended_from_avocado=0:news_degradation=0'
AB_FLAGS_TOUCH_DEGRADATION = 'topnews_extended=1:topnews_from_avocado=0:topnews_extended_from_avocado=0:news_degradation=1'
AB_FLAGS_TOUCH_PERSONAL_NOT_TOURIST = 'topnews_extended=1:topnews_from_avocado=0:topnews_extended_from_avocado=0:news_degradation=0:tourist_blocks=0:news_tourist_tab=0'
AB_FLAGS_TOUCH_PERSONAL_TOURIST = 'topnews_extended=1:topnews_from_avocado=0:topnews_extended_from_avocado=0:news_degradation=0:tourist_blocks=1:news_tourist_tab=1'
AB_FLAGS_TOUCH_TOURIST = 'topnews_extended=1:topnews_from_avocado=0:topnews_extended_from_avocado=0:news_degradation=0:tourist_blocks=1:news_tourist_tab=1'
AB_FLAGS_TOUCH_OFFICIAL_COMMENTS = 'topnews_extended=1:topnews_from_avocado=0:topnews_extended_from_avocado=0:news_degradation=0:topnews_official_comments=1'
FLAGS_MADM_OPTIONS_MOCK = 'options=disclaimer_disallow_enabled'
AB_FLAGS_TOUCH_IN_GO = 'topnews_extended=1:topnews_from_avocado=1:topnews_extended_from_avocado=1'
AB_FLAGS_TOUCH_TOURIST_IN_GO = 'tourist_blocks=1:news_tourist_tab=1'
AB_FLAGS_SUMMARY = 'topnews_summary=1'
AB_FLAGS_OFFICIAL_COMMENTS = 'topnews_official_comments=1'
FLAG_FORCE_AB_FLAGS_OFFICIAL_COMMENTS_AND_SUMMARY = 'flags=yxnews_tops_export_test_official_comments=1'
FLAG_TOP_NEWS_TIMEOUT = 'TOP_NEWS:::10m'
FLAG_USER_COLDNESS_TIMEOUT = 'TOP_NEWS_USER_COLDNESS:::10m'
FLAG_MADM_ENABLE_DISCLAIMER = 'disable_disclaimer_disallow=0'

SAINT_PETERSBURG_GEO = 2

BLOCK_TOPNEWS_EXTENDED = 'Topnews_extended'
DOMAIN_PREFIX = 'yandex.{domain}/news'
DOMAIN_PREFIX_SPORT = 'yandex.{domain}/sport'

DEFAULT_TOUCH_TABS_NUM_GE = 10
DEFAULT_TOUCH_NEWS_IN_TABS_NUM_GE = 10

YASM_SIGNAL_NAME = 'morda_topnews_{}_tttt'

USER_LOGIN = 'accaunt.testing'
USER_PASSWORD = '7d9-5qP-y5u-sjH'

HTTPMOCK_LOGGED_USER_HOT = 'personal_request_batch:0@personal_data_touch,topnews_user_coldness@user_coldness'
HTTPMOCK_LOGGED_DISCLAIMER_ALLOW = 'topnews@news_with_disclaimer_allowed_hot'

HTTPMOCK_GO_USER_HOT = 'TOP_NEWS_USER_COLDNESS:morda-mocks.wdevx.yandex.ru:80/api/v1/mocks/user_coldness/content:10m'

TOPNEWS_FIELD_SCHEMA_PATH_TEMPLATE = 'schema/cleanvars/topnews/common/topnews-event-{}.json'
TOPNEWS_EXTENDED_FROM_GO_SCHEMA_PATH = 'schema/cleanvars/topnews_extended/touch/topnews_extended_unified.json'
NO_REDIRECT = 'disable_redirect_to_ru_from_russian_geo=1'


@allure.feature('morda', 'topnews_extended', 'function_tests_stable')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME)
class TestTopNewsExtendedTouchMoscow(object):
    def setup_class(self):
        self.is_user_logged = False
        self.data = _fetch_data(TouchMain(region=Regions.MOSCOW), self.is_user_logged,
                                params={'ab_flags': AB_FLAGS_TOUCH, 'content': 'touch'})
        self.block = self.data.get(BLOCK_TOPNEWS_EXTENDED)
        self.href_domain = 'ru'
        self.tabs_num_ge = DEFAULT_TOUCH_TABS_NUM_GE
        self.news_in_tabs_num_ge = DEFAULT_TOUCH_NEWS_IN_TABS_NUM_GE

    @allure.story('block exists')
    def test_topnews_existance(self):
        _test_existance(self)

    @allure.story('dates')
    def test_topnews_date(self):
        _test_date(self)

    @allure.story('block exists')
    def test_topnews_common(self):
        _test_common(self)

    @allure.story('tabs')
    def test_topnews_tabs(self):
        _test_tabs(self)

    @allure.story('href')
    def test_topnews_href(self):
        _test_href(self)

    @allure.story('schema')
    def test_topnews_schema(self):
        schema.validate_schema_by_block(self.block, 'topnews_extended', 'touch')


@allure.feature('morda', 'topnews_extended', 'function_tests_stable')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME)
class TestTopNewsExtendedTouchMinsk(object):
    def setup_class(self):
        self.is_user_logged = False
        self.data = _fetch_data(TouchMain(region=Regions.MINSK), self.is_user_logged,
                                params={'ab_flags': AB_FLAGS_TOUCH, 'madm_options': NO_REDIRECT})
        self.block = self.data.get(BLOCK_TOPNEWS_EXTENDED)
        self.href_domain = 'by'
        self.tabs_num_ge = DEFAULT_TOUCH_TABS_NUM_GE
        self.news_in_tabs_num_ge = DEFAULT_TOUCH_NEWS_IN_TABS_NUM_GE

    @allure.story('block exists')
    def test_topnews_existance(self):
        _test_existance(self)

    @allure.story('block exists')
    def test_topnews_common(self):
        _test_common(self)

    @allure.story('tabs')
    def test_topnews_tabs(self):
        _test_tabs(self)

    @allure.story('href')
    def test_topnews_href(self):
        _test_href(self)

    @allure.story('schema')
    def test_topnews_schema(self):
        schema.validate_schema_by_block(self.block, 'topnews_extended', 'touch')


@allure.feature('morda', 'topnews_extended', 'function_tests_stable')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME)
class TestTopNewsExtendedTouchAstana(object):
    def setup_class(self):
        self.is_user_logged = False
        self.data = _fetch_data(TouchMain(region=Regions.ASTANA), self.is_user_logged,
                                params={'ab_flags': AB_FLAGS_TOUCH, 'madm_options': NO_REDIRECT})
        self.block = self.data.get(BLOCK_TOPNEWS_EXTENDED)
        self.href_domain = 'kz'
        self.tabs_num_ge = DEFAULT_TOUCH_TABS_NUM_GE
        self.news_in_tabs_num_ge = DEFAULT_TOUCH_NEWS_IN_TABS_NUM_GE

    @allure.story('block exists')
    def test_topnews_existance(self):
        _test_existance(self)

    @allure.story('block exists')
    def test_topnews_common(self):
        _test_common(self)

    @allure.story('tabs')
    def test_topnews_tabs(self):
        _test_tabs(self)

    @allure.story('href')
    def test_topnews_href(self):
        _test_href(self)

    @allure.story('schema')
    def test_topnews_schema(self):
        schema.validate_schema_by_block(self.block, 'topnews_extended', 'touch')


@allure.feature('morda', 'topnews_extended', 'function_tests_stable')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME)
class TestTopNewsExtendedTouchMoscowDegradation(object):
    def setup_class(self):
        self.is_user_logged = False
        self.data = _fetch_data(TouchMain(region=Regions.MOSCOW), self.is_user_logged,
                                params={'ab_flags': AB_FLAGS_TOUCH_DEGRADATION})
        self.block = self.data.get(BLOCK_TOPNEWS_EXTENDED)
        self.href_domain = 'ru'
        self.tabs_num_ge = 3
        self.news_in_tabs_num_ge = DEFAULT_TOUCH_NEWS_IN_TABS_NUM_GE

    @allure.story('block exists')
    def test_topnews_existance(self):
        _test_existance(self)

    @allure.story('dates')
    def test_topnews_date(self):
        _test_date(self)

    @allure.story('title')
    def test_topnews_title(self):
        _test_title_degradation(self)

    @allure.story('block exists')
    def test_topnews_common(self):
        _test_common(self)

    @allure.story('block exists')
    def test_topnews_favorite(self):
        _test_favorite_degradation(self)

    @allure.story('tabs')
    def test_topnews_tabs(self):
        _test_tabs_degradation(self)

    @allure.story('href')
    def test_topnews_href(self):
        _test_href(self)

    @allure.story('schema')
    def test_topnews_schema(self):
        schema.validate_schema_by_block(self.block, 'topnews_extended', 'touch')


# HOME-77168
# @allure.feature('morda', 'topnews_extended', 'function_tests_stable')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME)
class TestTopNewsExtendedTouchMoscowPersonalNotTourist(object):
    def setup_class(self):
        self.is_user_logged = True
        self.data = _fetch_data(TouchMain(region=Regions.MOSCOW), self.is_user_logged,
                                params={'ab_flags': AB_FLAGS_TOUCH_PERSONAL_NOT_TOURIST,
                                        'httpmock': HTTPMOCK_LOGGED_USER_HOT,
                                        'content': 'touch', 'cleanvars': 'Topnews', 'geo': SAINT_PETERSBURG_GEO})
        self.block = self.data.get(BLOCK_TOPNEWS_EXTENDED)
        self.href_domain = 'ru'
        self.tabs_num_ge = 3
        self.news_in_tabs_num_ge = DEFAULT_TOUCH_NEWS_IN_TABS_NUM_GE

    @allure.story('block exists')
    def test_topnews_existance(self):
        _test_existance(self)

    @allure.story('common exists')
    def test_topnews_common(self):
        _test_common(self)

    @allure.story('dates')
    def test_topnews_date(self):
        _test_date(self)

    @allure.story('tabs')
    def test_topnews_tabs(self):
        _test_tabs(self)
        _test_tabs_personal(self, 2)

    @allure.story('href')
    def test_topnews_href(self):
        _test_href(self)

    @allure.story('schema')
    def test_topnews_schema(self):
        schema.validate_schema_by_block(self.block, 'topnews_extended', 'touch')


# HOME-77168
# @allure.feature('morda', 'topnews_extended', 'function_tests_stable')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME)
class TestTopNewsExtendedTouchMoscowPersonalTourist(object):
    def setup_class(self):
        self.is_user_logged = True
        self.data = _fetch_data(TouchMain(region=Regions.MOSCOW), self.is_user_logged,
                                params={'ab_flags': AB_FLAGS_TOUCH_PERSONAL_TOURIST,
                                        'httpmock': HTTPMOCK_LOGGED_USER_HOT,
                                        'content': 'touch', 'cleanvars': 'Topnews', 'geo': SAINT_PETERSBURG_GEO})
        self.block = self.data.get(BLOCK_TOPNEWS_EXTENDED)
        self.href_domain = 'ru'
        self.tabs_num_ge = 3
        self.news_in_tabs_num_ge = DEFAULT_TOUCH_NEWS_IN_TABS_NUM_GE

    @allure.story('block exists')
    def test_topnews_existance(self):
        _test_existance(self)

    @allure.story('common exists')
    def test_topnews_common(self):
        _test_common(self)

    @allure.story('dates')
    def test_topnews_date(self):
        _test_date(self)

    @allure.story('tabs')
    def test_topnews_tabs(self):
        _test_tabs(self)
        _test_tabs_personal(self, 3)

    @allure.story('href')
    def test_topnews_href(self):
        _test_href(self)

    @allure.story('schema')
    def test_topnews_schema(self):
        schema.validate_schema_by_block(self.block, 'topnews_extended', 'touch')


# HOME-77168
# @allure.feature('morda', 'topnews_extended', 'function_tests_stable')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME)
class TestTopNewsExtendedTouchMoscowTourist(object):
    def setup_class(self):
        self.is_user_logged = True
        self.data = _fetch_data(TouchMain(region=Regions.MOSCOW), self.is_user_logged,
                                params={'ab_flags': AB_FLAGS_TOUCH_TOURIST, 'httpmock': HTTPMOCK_LOGGED_USER_HOT,
                                        'content': 'touch', 'cleanvars': 'Topnews', 'geo': SAINT_PETERSBURG_GEO,
                                        'madm_options': 'enable_new_tourist_morda=0:new_tourist_morda_testids=0',
                                        'madm_mocks': 'tourist_blocks=tourist_blocks.default'})
        self.block = self.data.get(BLOCK_TOPNEWS_EXTENDED)
        self.href_domain = 'ru'
        self.tabs_num_ge = 3
        self.news_in_tabs_num_ge = DEFAULT_TOUCH_NEWS_IN_TABS_NUM_GE

    @allure.story('block exists')
    def test_topnews_existance(self):
        _test_existance(self)

    @allure.story('common exists')
    def test_topnews_common(self):
        _test_common(self)

    @allure.story('dates')
    def test_topnews_date(self):
        _test_date(self)

    @allure.story('tabs')
    def test_topnews_tabs(self):
        _test_tabs(self)
        _test_tabs_tourist(self, 'Saint_Petersburg', 'Moscow')

    @allure.story('href')
    def test_topnews_href(self):
        _test_href(self)

    @allure.story('schema')
    def test_topnews_schema(self):
        schema.validate_schema_by_block(self.block, 'topnews_extended', 'touch')


@allure.feature('morda', 'topnews_extended', 'function_tests_stable')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME)
class TestTopNewsExtendedTouchMoscowOfficialComments(object):
    def setup_class(self):
        self.is_user_logged = False
        self.data = _fetch_data(TouchMain(region=Regions.MOSCOW), self.is_user_logged,
                                params={'ab_flags': AB_FLAGS_TOUCH_OFFICIAL_COMMENTS, 'content': 'touch',
                                        'cleanvars': 'Topnews',
                                        'new_format': 1, 'official_comments': 1,
                                        'topnews_extra_params': 'flags=yxnews_tops_export_test_official_comments=1'})
        self.block = self.data.get(BLOCK_TOPNEWS_EXTENDED)
        self.href_domain = 'ru'
        self.tabs_num_ge = 3
        self.news_in_tabs_num_ge = DEFAULT_TOUCH_NEWS_IN_TABS_NUM_GE

    @allure.story('block exists')
    def test_topnews_existance(self):
        _test_existance(self)

    @allure.story('block exists')
    def test_topnews_common(self):
        _test_common(self)

    @allure.story('dates')
    def test_topnews_date(self):
        _test_date(self)

    @allure.story('tabs')
    def test_topnews_tabs(self):
        _test_tabs(self)
        _test_tabs_official_comments_exists(self)

    @allure.story('href')
    def test_topnews_href(self):
        _test_href(self)

    @allure.story('schema')
    def test_topnews_schema(self):
        schema.validate_schema_by_block(self.block, 'topnews_extended', 'touch')


@allure.feature('morda', 'topnews_extended', 'function_tests_stable')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME)
class TestTopNewsExtendedTouchMoscowExtraStories(object):
    def setup_class(self):
        self.is_user_logged = False
        self.data = _fetch_data(TouchMain(region=Regions.MOSCOW), self.is_user_logged,
                                params={'ab_flags': AB_FLAGS_TOUCH_OFFICIAL_COMMENTS, 'content': 'touch',
                                        'cleanvars': 'Topnews',
                                        'httpmock': HTTPMOCK_LOGGED_DISCLAIMER_ALLOW})
        self.block = self.data.get(BLOCK_TOPNEWS_EXTENDED)
        self.href_domain = 'ru'
        self.tabs_num_ge = 3
        self.news_in_tabs_num_ge = DEFAULT_TOUCH_NEWS_IN_TABS_NUM_GE

    @allure.story('block exists')
    def test_topnews_existance(self):
        _test_existance(self)

    @allure.story('block exists')
    def test_topnews_common(self):
        _test_common(self)

    @allure.story('dates')
    def test_topnews_date(self):
        _test_date(self)

    @allure.story('tabs')
    def test_topnews_tabs(self):
        _test_tabs(self)
        _test_tabs_extra_stories_exist(self)

    @allure.story('href')
    def test_topnews_href(self):
        _test_href(self)

    @allure.story('schema')
    def test_topnews_schema(self):
        schema.validate_schema_by_block(self.block, 'topnews_extended', 'touch')


# HOME-77168
# @allure.feature('morda', 'topnews_extended', 'function_tests_stable')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME)
class TestTopNewsExtendedTouchMoscowDisclaimerAllowAndFavorites(object):
    def setup_class(self):
        self.is_user_logged = True
        self.data = _fetch_data(TouchMain(region=Regions.MOSCOW), self.is_user_logged,
                                params={'ab_flags': AB_FLAGS_TOUCH, 'content': 'touch', 'cleanvars': 'Topnews',
                                        'httpmock': HTTPMOCK_LOGGED_DISCLAIMER_ALLOW,
                                        'madm_mock': FLAGS_MADM_OPTIONS_MOCK})
        self.block = self.data.get(BLOCK_TOPNEWS_EXTENDED)
        self.href_domain = 'ru'
        self.tabs_num_ge = 3
        self.news_in_tabs_num_ge = DEFAULT_TOUCH_NEWS_IN_TABS_NUM_GE

    @allure.story('block exists')
    def test_topnews_existance(self):
        _test_existance(self)

    @allure.story('block exists')
    def test_topnews_common(self):
        _test_common(self)

    @allure.story('dates')
    def test_topnews_date(self):
        _test_date(self)

    @allure.story('disclaimer allow')
    def test_topnews_disclaimer_allow(self):
        _test_disclaimer_allow(self)

    @allure.story('tabs')
    def test_topnews_tabs(self):
        _test_tabs(self)
        _test_tabs_favorites(self)

    @allure.story('href')
    def test_topnews_href(self):
        _test_href(self)

    @allure.story('schema')
    def test_topnews_schema(self):
        schema.validate_schema_by_block(self.block, 'topnews_extended', 'touch')


# HOME-77168
# @allure.feature('morda', 'topnews_extended', 'function_tests_stable')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME)
class TestTopNewsExtendedTouchMoscowHot(object):
    def setup_class(self):
        self.is_user_logged = True
        self.data = _fetch_data(TouchMain(region=Regions.MOSCOW), self.is_user_logged,
                                params={'ab_flags': AB_FLAGS_TOUCH, 'content': 'touch', 'cleanvars': 'Topnews',
                                        'httpmock': HTTPMOCK_LOGGED_DISCLAIMER_ALLOW})
        self.block = self.data.get(BLOCK_TOPNEWS_EXTENDED)
        self.href_domain = 'ru'
        self.tabs_num_ge = 3
        self.news_in_tabs_num_ge = DEFAULT_TOUCH_NEWS_IN_TABS_NUM_GE

    @allure.story('block exists')
    def test_topnews_existance(self):
        _test_existance(self)

    @allure.story('block exists')
    def test_topnews_common(self):
        _test_common(self)

    @allure.story('dates')
    def test_topnews_date(self):
        _test_date(self)

    @allure.story('tabs')
    def test_topnews_tabs(self):
        _test_tabs(self)
        _test_tabs_is_hot(self)

    @allure.story('href')
    def test_topnews_href(self):
        _test_href(self)

    @allure.story('schema')
    def test_topnews_schema(self):
        schema.validate_schema_by_block(self.block, 'topnews_extended', 'touch')


@allure.feature('morda', 'topnews_extended', 'function_tests_stable')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME)
class TestTopNewsExtendedTouchCom(object):
    def setup_class(self):
        self.is_user_logged = False
        self.data = _fetch_data(TouchCom(), self.is_user_logged, params={'ab_flags': AB_FLAGS_TOUCH})

    @allure.story('block does not exist')
    def test_topnews_existance(self):
        assert not self.data.get(BLOCK_TOPNEWS_EXTENDED), 'Block must not be here'


@allure.feature('morda', 'topnews_extended', 'function_tests_stable')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME)
class TestTopNewsExtendedTouchGoTourist(object):
    def setup_class(self):
        self.is_user_logged = True
        flags = [AB_FLAGS_TOUCH_IN_GO, AB_FLAGS_TOUCH_TOURIST_IN_GO]
        self.data = _fetch_data(TouchMain(region=Regions.MOSCOW), self.is_user_logged,
                                params={'ab_flags': ':'.join(flags),
                                        'cleanvars': 'Topnews', 'geo': SAINT_PETERSBURG_GEO,
                                        'srcrwr': FLAG_TOP_NEWS_TIMEOUT,
                                        'httpmock': HTTPMOCK_LOGGED_USER_HOT,
                                        'madm_options': 'enable_new_tourist_morda=0:new_tourist_morda_testids=0',
                                        'madm_mocks': 'tourist_blocks=tourist_blocks.default',
                                        })
        self.block = self.data.get(BLOCK_TOPNEWS_EXTENDED)

    @allure.story('schema')
    def test_topnews_tourist_schema(self):
        schema.validate_schema(self.block, schema.get_schema_validator(TOPNEWS_EXTENDED_FROM_GO_SCHEMA_PATH))

    @allure.story('tabs')
    def test_topnews_tourist_tabs(self):
        _test_tabs_tourist_new_format(self, 'Saint_Petersburg', 'Moscow')


@allure.feature('morda', 'topnews', 'function_tests_stable')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME)
class TestTopNewsExtendedTouchGoFavorite(object):
    def setup_class(self):
        self.is_user_logged = True
        self.data = _fetch_data(
            TouchMain(region=Regions.MOSCOW), self.is_user_logged,
            params={
                'ab_flags': AB_FLAGS_TOUCH_IN_GO,
                'srcrwr': FLAG_TOP_NEWS_TIMEOUT
            }
        )
        self.block = self.data.get(BLOCK_TOPNEWS_EXTENDED)

    @allure.story('schema')
    def test_topnews_favorite_schema(self):
        schema.validate_schema(self.block, schema.get_schema_validator(TOPNEWS_EXTENDED_FROM_GO_SCHEMA_PATH))


@allure.feature('morda', 'topnews', 'function_tests_stable')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME)
class TestTopNewsExtendedTouchGoPersonalTab(object):
    def setup_class(self):
        self.is_user_logged = True
        self.data = _fetch_data(
            TouchMain(region=Regions.MOSCOW), self.is_user_logged,
            params={
                'ab_flags': AB_FLAGS_TOUCH_IN_GO,
                'srcrwr': HTTPMOCK_GO_USER_HOT,
                'geo': SAINT_PETERSBURG_GEO,
            }
        )
        self.block = self.data.get(BLOCK_TOPNEWS_EXTENDED)

    @allure.story('schema')
    def test_topnews_schema(self):
        schema.validate_schema(self.block, schema.get_schema_validator(TOPNEWS_EXTENDED_FROM_GO_SCHEMA_PATH))

    @allure.story('tabs')
    def test_personal_tab(self):
        _test_personal_tab_go(self)


# ==============================


def _fetch_data(morda, is_user_logged, **kwargs):
    client = MordaClient(morda)
    if is_user_logged:
        passport_host = client.cleanvars(['Mail']).send().json()['Mail']['auth_host']
        for i in range(3):
            login_response = client.login(passport_host, USER_LOGIN, USER_PASSWORD).send()
            if login_response.is_ok():
                break
        with allure.step('Login'):
            assert login_response.is_ok(), 'Failed to login'
    response = client.cleanvars([BLOCK_TOPNEWS_EXTENDED], **kwargs).send()
    with allure.step('Fetch data'):
        assert response.is_ok(), 'Failed to get cleanvars'
    return response.json()


def _test_existance(test_case):
    with allure.step('Test if block exists'):
        assert test_case.data[BLOCK_TOPNEWS_EXTENDED], 'Failed to get block'


def _test_common(test_case):
    with allure.step('Test if block shows'):
        assert test_case.block['show'], 'Show must be 1'


def _test_title_degradation(test_case):
    with allure.step('Test if title is correct in degradation mode'):
        assert test_case.block.get('data'), 'data was not found'
        assert test_case.block.get('data').get('topnews'), 'topnews was not found'
        topnews = test_case.block.get('data').get('topnews')
        assert topnews['title'], 'Title was not found'
        test_case_title = topnews['title'].encode('utf-8')
        want_title = u'Новости'.encode('utf-8')
        assert test_case_title == want_title, 'Incorrect title in degrodation mode'


def _test_date(test_case):
    with allure.step('Test if date ok'):
        assert test_case.block.get('data'), 'data was not found'
        assert test_case.block.get('data').get('topnews'), 'topnews was not found'
        assert test_case.block.get('data').get('topnews').get('BigDay'), 'BigDay was not found'
        assert test_case.block.get('data').get('topnews').get('BigMonth'), 'BigMonth was not found'
        assert test_case.block.get('data').get('topnews').get('BigWday'), 'BigWday was not found'


def _test_tabs(test_case):
    with allure.step('Check tabs'):
        assert test_case.block['data'], 'Failed to get tabs'
        tabs = test_case.block['data'].get('topnews').get('tabs')
        assert len(tabs) >= test_case.tabs_num_ge, (
                'Tabs num: must be more than ' + str(test_case.tabs_num_ge))
        for tab in tabs:
            if tab.get('name') != 'video' and tab.get('name') != 'theme' and tab.get('name') != 'personal':
                assert len(tab.get('news')) >= test_case.news_in_tabs_num_ge, (
                        'News num in tab: must be more than ' + str(test_case.news_in_tabs_num_ge))
            if tab.get('news') != None:
                for story in tab.get('news'):
                    if tab.get('name') != 'personal':
                        assert story.get('i') != None, 'Field i is empty'
                        assert story.get('id') != None, 'Field id is empty'
                        assert story.get('text') != None, 'Field text is empty'
        first_tab = tabs[0]
        assert first_tab.get('default'), 'First tab must have default flag'


def _test_tabs_degradation(test_case):
    with allure.step('Check tabs'):
        topnews = test_case.block.get('data').get('topnews')
        assert topnews['tabs'], 'Failed to get tabs'
        assert len(topnews['tabs']) == 1, 'Tabs num: must be equal to 1 '
        tab = topnews['tabs'][0]
        assert tab.get('statid') == "news.index", 'Incorrect tab type, should be news.index'
        assert len(tab.get('news')) == 5, 'Number of news should be equal to 5'
        for story in tab.get('news'):
            assert story.get('extra_stories') == None, 'Extra stories should not be presented in degradation mode'


def _test_tabs_personal(test_case, personal_tab_id):
    with allure.step('Check tabs'):
        topnews = test_case.block.get('data').get('topnews')
        assert topnews['tabs'], 'Failed to get tabs'
        assert len(topnews['tabs']) >= test_case.tabs_num_ge, (
                'Tabs num: must be more than ' + str(test_case.tabs_num_ge))
        tub_number = 0
        for tab in topnews['tabs']:
            if tab.get('name') == 'personal':
                assert tub_number == personal_tab_id, "Personal tab lays on the wrong position"
            tub_number += 1
        assert topnews['tabs'][personal_tab_id].get('name') == 'personal', 'Personal tab does not exist'
        personal_tab = topnews['tabs'][personal_tab_id]
        assert personal_tab.get('alias') == 'Personal', 'Incorrect alias for a personal tab'
        assert personal_tab.get('statid') == 'news.personal', 'Incorrect statid for a personal tab'
        test_case_title = personal_tab.get('title').encode('utf-8')
        want_title = u'Интересное'.encode('utf-8')
        assert test_case_title == want_title, 'Incorrect title in personal tab'


def _test_personal_tab_go(test_case):
    with allure.step('Check personal tab'):
        topnews = test_case.block.get('data').get('topnews')
        assert topnews['rubrics'], 'Failed to get tabs'
        tab_exists = False
        tab_num = 0
        for tab in topnews['rubrics']:
            if tab.get('alias') == 'Personal':
                tab_exists = True
                break
            tab_num += 1
        assert tab_exists is True, "Personal tab doesn't exist"

        personal_tab = topnews['rubrics'][tab_num]
        assert personal_tab.get('alias') == 'Personal', 'Incorrect alias for a personal tab'
        assert personal_tab.get('theme') == 'personal', 'Incorrect theme for a personal tab'
        assert personal_tab.get('data_url') is not None, 'Required field missing in personal tab: data_url'


def _test_tabs_tourist(test_case, news_region_name, home_region_name):
    with allure.step('Check tabs'):
        topnews = test_case.block.get('data').get('topnews')
        assert topnews['tabs'], 'Failed to get tabs'
        assert len(topnews['tabs']) >= test_case.tabs_num_ge, (
                'Tabs num: must be more than ' + str(test_case.tabs_num_ge))
        news_region_tab = topnews['tabs'][1]
        assert news_region_tab.get('alias') == news_region_name, 'Incorrect alias for news_region tab'
        assert news_region_tab.get('name') == 'region', 'Incorrect name for news_region tab'
        assert news_region_tab.get('statid') == 'news.region', 'Incorrect statid for news_region tab'
        if news_region_name == 'Saint_Petersburg':
            assert news_region_tab.get('geo') == '2', 'Incorrect geo for news_region tab'
            test_news_region_title = news_region_tab.get('title').encode('utf-8')
            want_news_region_title = u'Санкт-Петербург'.encode('utf-8')
            assert test_news_region_title == want_news_region_title, 'Incorrect title for news_region tab'

        home_region_tab = topnews['tabs'][2]
        assert home_region_tab.get('alias') == home_region_name, 'Incorrect alias for home_region tab'
        assert home_region_tab.get('name') == 'home_region', 'Incorrect name for home_region tab'
        assert home_region_tab.get('statid') == 'news.homeregion', 'Incorrect statid for home_region tab'
        if home_region_name == 'Moscow':
            assert home_region_tab.get('geo') == '213', 'Incorrect geo for home_region tab'
            test_home_region_title = home_region_tab.get('title').encode('utf-8')
            want_home_region_title = u'Москва'.encode('utf-8')
            assert test_home_region_title == want_home_region_title, 'Incorrect title for home_region tab'


def _test_tabs_extra_stories_exist(test_case):
    with allure.step('Check tabs'):
        topnews = test_case.block.get('data').get('topnews')
        assert topnews['tabs'], 'Failed to get tabs'
        extra_stories_exist = False
        for tab in topnews['tabs']:
            if tab.get('news') != None:
                for story in tab.get('news'):
                    if story.get('extra_stories') != None:
                        extra_stories_exist = True
        assert extra_stories_exist, 'There were no extra stories'


def _test_tabs_favorites(test_case):
    with allure.step('Check tabs'):
        topnews = test_case.block.get('data').get('topnews')
        assert topnews, 'Failed to get tabs'
        assert len(topnews) >= test_case.tabs_num_ge, (
                'Tabs num: must be more than ' + str(test_case.tabs_num_ge))
        tab = topnews['tabs'][0]
        if tab.get('news') != None:
            for story in tab.get('news'):
                assert story.get('is_favorite'), "Field is_favorite is empty"
                assert story.get('is_favorite') == 1, "Field is_favorite should be equal to 1"


def _test_favorite_degradation(test_case):
    with allure.step('Check favorite url'):
        assert test_case.block.get('data').get('topnews').get(
            'url_setup_favorite') is None, 'url_setup_favorite should be empty in degradation mode'


def _test_disclaimer_allow(test_case):
    with allure.step('disclaimer allow'):
        topnews = test_case.block.get('data').get('topnews')
        assert topnews.get('promo'), 'Disclaimer must be present'


def _test_tabs_official_comments_exists(test_case):
    with allure.step('Check tabs'):
        topnews = test_case.block.get('data').get('topnews')
        assert topnews['tabs'], 'Failed to get tabs'
        official_comments_exist = False
        for tab in topnews['tabs']:
            if tab.get('news') != None:
                for story in tab.get('news'):
                    if story.get('official_comments') != None:
                        official_comments_exist = True
        assert official_comments_exist, 'There were no official comments'


def _test_tabs_is_hot(test_case):
    with allure.step('Check tabs'):
        topnews = test_case.block.get('data').get('topnews')
        assert topnews['tabs'], 'Failed to get tabs'
        hot_news_exist = False
        for tab in topnews['tabs']:
            if tab.get('news') != None:
                for story in tab.get('news'):
                    if story.get('ishot') != None and story.get('ishot') == 1:
                        hot_news_exist = True
        assert hot_news_exist, 'There were no hot news'


def _test_href(test_case):
    with allure.step('Check main href'):
        block = test_case.block['data'].get('topnews')
        domain = test_case.href_domain
        main_href = block.get('href')
        assert main_href.index(DOMAIN_PREFIX.format(domain=domain)), 'Domain must be ' + DOMAIN_PREFIX.format(
            domain=domain)

    with allure.step('Check special href'):
        if 'special' in block:
            special_href = block.get('special').get('href')
            assert (DOMAIN_PREFIX.format(domain=domain) in special_href or DOMAIN_PREFIX_SPORT.format(
                domain=domain) in special_href), \
                'Domain must be ' + DOMAIN_PREFIX.format(domain=domain) + ' or ' + DOMAIN_PREFIX_SPORT.format(
                    domain=domain)

    with allure.step('Check news and tabs href'):
        for tab in block.get('tabs'):
            tab_href = tab.get('href')
            assert tab_href.index(DOMAIN_PREFIX.format(domain=domain)), 'Domain must be ' + DOMAIN_PREFIX.format(
                domain=domain)
            if tab.get('name') != 'video' and tab.get('name') != 'theme':
                for n in tab.get('news'):
                    n_href = n.get('href')
                    assert (DOMAIN_PREFIX.format(domain=domain) in n_href or DOMAIN_PREFIX_SPORT.format(
                        domain=domain) in n_href), \
                        'Domain must be ' + DOMAIN_PREFIX.format(domain=domain) + ' or ' + DOMAIN_PREFIX_SPORT.format(
                            domain=domain)


def _test_tabs_tourist_new_format(test_case, news_region_name, home_region_name):
    with allure.step('Check tabs'):
        topnews = test_case.block.get('data').get('topnews')
        news_region_tab = topnews['rubrics'][1]
        assert news_region_tab.get('alias') == news_region_name, 'Incorrect alias for news_region tab'
        assert news_region_tab.get('theme') == 'region', 'Incorrect name for news_region tab'
        if news_region_name == 'Saint_Petersburg':
            assert news_region_tab.get('id') == SAINT_PETERSBURG_GEO, 'Incorrect geo for news_region tab'

        home_region_tab = topnews['rubrics'][2]
        assert home_region_tab.get('alias') == home_region_name, 'Incorrect alias for home_region tab'
        assert home_region_tab.get('theme') == 'home_region', 'Incorrect name for home_region tab'
        if home_region_name == 'Moscow':
            assert home_region_tab.get('id') == 213, 'Incorrect geo for home_region tab'
