# -*- coding: utf-8 -*-
import logging
import allure
import pytest

from common import schema
from common.morda import DesktopMain, DesktopCom, DesktopComTr, TouchMain, TouchCom, TouchComTr
from common.client import MordaClient
from common.geobase import Regions
from common.blocks import existance, fetch_data, check_show, count_elements, absence
from common.blocks import fetch_data

logger = logging.getLogger(__name__)

"""
HOME-37220
Проверяет работу блока Новости
Бывший mordabackend/topnews/TopnewsBlockTest.java
"""

AB_FLAGS_TOUCH = 'topnews_extended=0:topnews_from_avocado=0:topnews_extended_from_avocado=0:news_degradation=0'
AB_FLAGS_TOUCH_DEGRADATION = 'topnews_extended=0:topnews_from_avocado=0:topnews_extended_from_avocado=0:news_degradation=1'
AB_FLAGS_TOUCH_OFFICIAL_COMMENTS = 'topnews_extended=0:topnews_from_avocado=0:topnews_extended_from_avocado=0:news_degradation=0:topnews_official_comments=1'
AB_FLAGS_TOUCH_SUMMARY = 'topnews_extended=0:topnews_from_avocado=0:topnews_extended_from_avocado=0:news_degradation=0:topnews_summary=1'
AB_FLAGS_TOUCH_TOURIST = 'topnews_extended=0:topnews_from_avocado=0:topnews_extended_from_avocado=0:news_degradation=0:tourist_blocks=1:news_tourist_tab=1'
AB_FLAGS_TOUCH_PERSONAL_TOURIST = 'topnews_extended=0:topnews_from_avocado=0:topnews_extended_from_avocado=0:news_degradation=0:tourist_blocks=1:news_tourist_tab=1'
AB_FLAGS_TOUCH_PERSONAL_NOT_TOURIST = 'topnews_extended=0:topnews_from_avocado=0:topnews_extended_from_avocado=0:news_degradation=0:tourist_blocks=0:news_tourist_tab=0'
FLAGS_MADM_OPTIONS_MOCK = 'options=disclaimer_disallow_enabled'
AB_FLAGS_DESKTOP_MORE_NEWS = 'more_news=1:zen_desktop_redesign2=1'
AB_FLAGS_DESKTOP_NEWS_DEGRADATION = 'news_degradation=1'
AB_FLAGS_DESKTOP_NEWS_FROM_GO = 'topnews_from_avocado:news_degradation=0:topnews_full=0'

DESKTOP_MOCK_USER_COLDNESS = 'topnews_user_coldness@user_coldness'
DESKTOP_NEWS_RESPONSE_MOCK = 'topnews@news_with_disclaimer_allowed_hot'

AB_FLAGS_SUMMARY = 'topnews_summary=1'
AB_FLAGS_OFFICIAL_COMMENTS = 'topnews_official_comments=1'
FLAG_FORCE_AB_FLAGS_OFFICIAL_COMMENTS_AND_SUMMARY = 'flags=yxnews_tops_export_test_official_comments=1'
BLOCK = 'Topnews'
URI_TEMPLATE_NEWS = 'yandex.{domain}/news'
URI_TEMPLATE_SPORT = 'yandex.{domain}/sport'

DEFAULT_DESKTOP_TABS_NUM_GE = 2
DEFAULT_DESKTOP_NEWS_IN_TABS_NUM_GE = 5

DEFAULT_TOUCH_TABS_NUM_GE = 10
DEFAULT_TOUCH_NEWS_IN_TABS_NUM_GE = 10

TOUCH_NEWS_NUM_DEGRADATION = 5

MORE_NEWS_DESKTOP_NEWS_IN_TABS_NUM_GE = 15

DEGRADATION_DESKTOP_TABS_NUM_GE = 1
DEGRADATION_DESKTOP_NEWS_IN_TABS_NUM_GE = 5

YASM_SIGNAL_NAME_TEMPLATE = 'morda_topnews_{}_tttt'

USER_LOGIN = 'accaunt.testing'
USER_PASSWORD = '7d9-5qP-y5u-sjH'

HTTPMOCK_LOGGED_USER_HOT = 'personal_request_batch:0@personal_data_touch,topnews_user_coldness@user_coldness'
HTTPMOCK_LOGGED_DISCLAIMER_ALLOW = 'topnews@news_with_disclaimer_allowed_hot'
NO_REDIRECT = 'disable_redirect_to_ru_from_russian_geo=1'

TOPNEWS_FROM_GO_SCHEMA_PATH = 'schema/cleanvars/topnews/unified/topnews-unified.json'

FLAG_TOPNEWS_TIMEOUT = 'TOP_NEWS:::10m'


@allure.feature('morda', 'topnews', 'function_tests_stable')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME_TEMPLATE)
class TestTopNewsDesktopMoscow(object):
    def setup_class(self):
        self.is_user_logged = False
        self.data = _fetch_data(DesktopMain(region=Regions.MOSCOW), self.is_user_logged)
        self.block = self.data.get(BLOCK)
        self.href_domain = 'ru'
        self.tabs_num_ge = DEFAULT_DESKTOP_TABS_NUM_GE
        self.news_in_tabs_num_ge = DEFAULT_DESKTOP_NEWS_IN_TABS_NUM_GE

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

    @allure.story('href')
    def test_topnews_href(self):
        _test_href(self)

    @allure.story('schema')
    def test_topnews_schema(self):
        schema.validate_schema_by_block(self.block, 'topnews', 'desktop')


@allure.feature('morda', 'topnews', 'function_tests_stable')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME_TEMPLATE)
class TestTopNewsDesktopMinsk(object):
    def setup_class(self):
        self.is_user_logged = False
        self.data = _fetch_data(DesktopMain(region=Regions.MINSK), self.is_user_logged, params={'madm_options': NO_REDIRECT})
        self.block = self.data.get(BLOCK)
        self.href_domain = 'by'
        self.tabs_num_ge = DEFAULT_DESKTOP_TABS_NUM_GE
        self.news_in_tabs_num_ge = DEFAULT_DESKTOP_NEWS_IN_TABS_NUM_GE

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

    @allure.story('href')
    def test_topnews_href(self):
        _test_href(self)

    @allure.story('schema')
    def test_topnews_schema(self):
        schema.validate_schema_by_block(self.block, 'topnews', 'desktop')


@allure.feature('morda', 'topnews', 'function_tests_stable')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME_TEMPLATE)
class TestTopNewsDesktopAstana(object):
    def setup_class(self):
        self.is_user_logged = False
        self.data = _fetch_data(DesktopMain(region=Regions.ASTANA), self.is_user_logged, params={'madm_options': NO_REDIRECT})
        self.block = self.data.get(BLOCK)
        self.href_domain = 'kz'
        self.tabs_num_ge = DEFAULT_DESKTOP_TABS_NUM_GE
        self.news_in_tabs_num_ge = DEFAULT_DESKTOP_NEWS_IN_TABS_NUM_GE

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

    @allure.story('href')
    def test_topnews_href(self):
        _test_href(self)

    @allure.story('schema')
    def test_topnews_schema(self):
        schema.validate_schema_by_block(self.block, 'topnews', 'desktop')


@allure.feature('morda', 'topnews', 'function_tests_stable')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME_TEMPLATE)
class TestTopNewsDesktopCom(object):
    def setup_class(self):
        self.is_user_logged = False
        self.data = _fetch_data(DesktopCom(), self.is_user_logged)

    @allure.story('block does not exist')
    def test_topnews_existance(self):
        assert not self.data.get(BLOCK), 'Block must not be here'


@allure.feature('morda', 'topnews', 'function_tests_stable')
class TestTopNewsDesktopComTr(object):
    def setup_class(cls):
        data = fetch_data(DesktopComTr(), [BLOCK], cgi_params={'madm_options': NO_REDIRECT})
        cls.block = data.get(BLOCK)

    @allure.story('block exists')
    def test_topnews_absence(self):
        absence(self.block)


@allure.feature('morda', 'topnews', 'function_tests_stable')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME_TEMPLATE)
class TestTopNewsDesktopMoscowMoreNews(object):
    def setup_class(self):
        self.is_user_logged = False
        self.data = _fetch_data(DesktopMain(region=Regions.MOSCOW), self.is_user_logged, params={'ab_flags':AB_FLAGS_DESKTOP_MORE_NEWS})
        self.block = self.data.get(BLOCK)
        self.href_domain = 'ru'
        self.tabs_num_ge = DEFAULT_DESKTOP_TABS_NUM_GE
        self.news_in_tabs_num_ge = MORE_NEWS_DESKTOP_NEWS_IN_TABS_NUM_GE

    @allure.story('block exists')
    def test_topnews_common(self):
        _test_common(self)

    @allure.story('tabs')
    def test_topnews_tabs(self):
        _test_tabs(self)


#HOME-77168
#@allure.feature('morda', 'topnews', 'function_tests_stable')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME_TEMPLATE)
class TestTopNewsDesktopMoscowDegradation(object):
    def setup_class(self):
        self.is_user_logged = True
        self.data = _fetch_data(DesktopMain(region=Regions.MOSCOW), self.is_user_logged, params={'ab_flags':AB_FLAGS_DESKTOP_NEWS_DEGRADATION})
        self.block = self.data.get(BLOCK)
        self.href_domain = 'ru'
        self.tabs_num_ge = DEGRADATION_DESKTOP_TABS_NUM_GE
        self.news_in_tabs_num_ge = DEGRADATION_DESKTOP_NEWS_IN_TABS_NUM_GE

    @allure.story('block exists')
    def test_topnews_existance(self):
        _test_existance(self)

    @allure.story('block exists')
    def test_topnews_common(self):
        _test_common(self)

    @allure.story('tabs')
    def test_topnews_tabs(self):
        _test_tabs_degradation(self)

    @allure.story('no extra stories')
    def test_topnews_no_extra_stories(self):
        _test_field_in_stories(self, 'extra_stories', False)

    @allure.story('schema')
    def test_topnews_schema(self):
        schema.validate_schema_by_block(self.block, 'topnews', 'desktop')


@allure.feature('morda', 'topnews', 'function_tests_stable')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME_TEMPLATE)
class TestTopNewsDesktopMoscowExtraStories(object):
    def setup_class(self):
        self.is_user_logged = False
        self.data = _fetch_data(DesktopMain(region=Regions.MOSCOW), self.is_user_logged, params = {'httpmock':DESKTOP_NEWS_RESPONSE_MOCK})
        self.block = self.data.get(BLOCK)
        self.href_domain = 'ru'
        self.tabs_num_ge = DEFAULT_DESKTOP_TABS_NUM_GE
        self.news_in_tabs_num_ge = DEFAULT_DESKTOP_NEWS_IN_TABS_NUM_GE

    @allure.story('block exists')
    def test_topnews_existance(self):
        _test_existance(self)

    @allure.story('schema')
    def test_topnews_schema(self):
        schema.validate_schema_by_block(self.block, 'topnews', 'desktop')

    @allure.story('extra stories')
    def test_topnews_extra_stories(self):
        _test_field_in_stories(self, 'extra_stories')


#HOME-77168
#@allure.feature('morda', 'topnews', 'function_test_stable')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME_TEMPLATE)
class TestTopNewsDesktopMoscowFavorite(object):
    def setup_class(self):
        self.is_user_logged = True
        self.data = _fetch_data(DesktopMain(region=Regions.MOSCOW), self.is_user_logged,\
         params = {'httpmock':DESKTOP_NEWS_RESPONSE_MOCK})
        self.block = self.data.get(BLOCK)
        self.href_domain = 'ru'
        self.tabs_num_ge = DEFAULT_DESKTOP_TABS_NUM_GE
        self.news_in_tabs_num_ge = DEFAULT_DESKTOP_NEWS_IN_TABS_NUM_GE

    @allure.story('block exists')
    def test_topnews_existance(self):
        _test_existance(self)

    @allure.story('schema')
    def test_topnews_schema(self):
        schema.validate_schema_by_block(self.block, 'topnews', 'desktop')

    @allure.story('topnews request')
    def test_topnews_data_url(self):
        _test_favorite_news_data_url(self)

    @allure.story('is_favorite flag')
    def test_topnews_favorite_flag_existance(self):
        _test_field_in_stories(self, 'is_favorite')
        _test_field_value_in_stories(self, 'is_favorite', 1)


#HOME-77168
#@allure.feature('morda', 'topnews', 'function_tests_stable')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME_TEMPLATE)
class TestTopNewsDesktopMoscowPersonalTab(object):
    def setup_class(self):
        self.is_user_logged = True
        self.data = _fetch_data(DesktopMain(region=Regions.MOSCOW), self.is_user_logged, params={'httpmock':DESKTOP_MOCK_USER_COLDNESS})
        self.block = self.data.get(BLOCK)
        self.href_domain = 'ru'
        self.tabs_num_ge = 3
        self.news_in_tabs_num_ge = DEFAULT_DESKTOP_NEWS_IN_TABS_NUM_GE

    @allure.story('block extists')
    def test_existance(self):
        _test_existance(self)

    @allure.story('tabs')
    def test_topnews_tabs(self):
        _test_tabs(self)

    @allure.story('schema')
    def test_topnews_schema(self):
        schema.validate_schema_by_block(self.block, 'topnews', 'desktop')

    @allure.story('personal tab exists')
    def test_personal_tab_existance(self):
        _test_personal_tab_existance(self)

@allure.feature('morda', 'topnews', 'function_tests_stable')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME_TEMPLATE)
class TestTopNewsDesktopMoscowHotNews(object):
    def setup_class(self):
        self.is_user_logged = False
        self.data = _fetch_data(DesktopMain(region=Regions.MOSCOW), self.is_user_logged, params = {'httpmock' : DESKTOP_NEWS_RESPONSE_MOCK})
        self.block = self.data.get(BLOCK)
        self.href_domain = 'ru'
        self.tabs_num_ge = DEFAULT_DESKTOP_TABS_NUM_GE
        self.news_in_tabs_num_ge = DEFAULT_DESKTOP_NEWS_IN_TABS_NUM_GE

    @allure.story('block exists')
    def test_topnews_existance(self):
        _test_existance(self)


    @allure.story('schema')
    def test_topnews_schema(self):
        schema.validate_schema_by_block(self.block, 'topnews', 'desktop')


    @allure.story('hot news')
    def test_topnews_hot_news(self):
        _test_field_in_stories(self, 'ishot')
        _test_field_value_in_stories(self, 'ishot', 1)


#HOME-77168
#@allure.feature('morda', 'topnews', 'function_tests_stable')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME_TEMPLATE)
class TestTopnewsDesktopMoscowDisclaimer(object):
    def setup_class(self):
        self.is_user_logged = True
        self.data = _fetch_data(DesktopMain(region=Regions.MOSCOW), self.is_user_logged, params={'httpmock':DESKTOP_NEWS_RESPONSE_MOCK,\
            'madm_mock' : FLAGS_MADM_OPTIONS_MOCK})
        self.block = self.data.get(BLOCK)
        self.href_domain = 'ru'
        self.tabs_num_ge = DEFAULT_DESKTOP_TABS_NUM_GE
        self.news_in_tabs_num_ge = DEFAULT_DESKTOP_NEWS_IN_TABS_NUM_GE

    @allure.story('block exists')
    def test_topnews_existance(self):
        assert self.data.get('madm_mock_error') is None, 'MADM mock error: {}'.format(self.data.get('madm_mock_error'))
        _test_existance(self)

    @allure.story('schema')
    def test_topnews_schema(self):
        schema.validate_schema_by_block(self.block, 'topnews', 'desktop')

    @allure.story('disclaimer exists')
    def test_topnews_disclaimer(self):
        _test_disclaimer_existance(self)


@allure.feature('morda', 'topnews', 'function_tests_stable')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME_TEMPLATE)
class TestTopNewsDesktopMoscowOfficialComments(object):
    def setup_class(self):
        self.is_user_logged = False
        self.data = _fetch_data(
            DesktopMain(region=Regions.MOSCOW), self.is_user_logged,
            params={
                'ab_flags': AB_FLAGS_OFFICIAL_COMMENTS,
                'topnews_extra_params': FLAG_FORCE_AB_FLAGS_OFFICIAL_COMMENTS_AND_SUMMARY
            }
        )
        self.block = self.data.get(BLOCK)

    @allure.story('block exists')
    def test_topnews_common(self):
        _test_common(self)

    @allure.story('official comments exists')
    def test_topnews_official_comments_exist(self):
        _test_official_comments(self)

    @allure.story('schema')
    def test_topnews_schema(self):
        schema.validate_schema_by_block(self.block, 'topnews', 'desktop')


@allure.feature('morda', 'topnews', 'function_tests_stable')
@allure.testcase('https://testpalm.yandex-team.ru/testcase/home_all-1092')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME_TEMPLATE)
class TestTopNewsDesktopMoscowSummary(object):
    def setup_class(self):
        self.is_user_logged = False
        self.data = _fetch_data(
            DesktopMain(region=Regions.MOSCOW), self.is_user_logged,
            params={
                'ab_flags': AB_FLAGS_SUMMARY,
                'topnews_extra_params': FLAG_FORCE_AB_FLAGS_OFFICIAL_COMMENTS_AND_SUMMARY
            }
        )
        self.block = self.data.get(BLOCK)

    @allure.story('block exists')
    def test_topnews_common(self):
        _test_common(self)

    # HOME-77180
    #@allure.story('summary exists')
    #def test_topnews_summary_exist(self):
    #    _test_summary(self)

    @allure.story('schema')
    def test_topnews_schema(self):
        schema.validate_schema_by_block(self.block, 'topnews', 'desktop')


@allure.feature('morda', 'topnews', 'function_tests_stable')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME_TEMPLATE)
class TestTopNewsTouchMoscow(object):
    def setup_class(self):
        self.is_user_logged = False
        self.data = _fetch_data(TouchMain(region=Regions.MOSCOW), self.is_user_logged, params={'ab_flags':AB_FLAGS_TOUCH})
        self.block = self.data.get(BLOCK)
        self.href_domain = 'ru'
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

    @allure.story('dates')
    def test_topnews_date(self):
        _test_date(self)

    @allure.story('href')
    def test_topnews_href(self):
        _test_href(self)

    @allure.story('schema')
    def test_topnews_schema(self):
        schema.validate_schema_by_block(self.block, 'topnews', 'touch')


@allure.feature('morda', 'topnews', 'function_tests_stable')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME_TEMPLATE)
class TestTopNewsTouchMinsk(object):
    def setup_class(self):
        self.is_user_logged = False
        self.data = _fetch_data(TouchMain(region=Regions.MINSK,
            params={'ab_flags':AB_FLAGS_TOUCH, 'madm_options': NO_REDIRECT}), self.is_user_logged)
        self.block = self.data.get(BLOCK)
        self.href_domain = 'by'
        self.tabs_num_ge = DEFAULT_TOUCH_TABS_NUM_GE
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

    @allure.story('href')
    def test_topnews_href(self):
        _test_href(self)

    @allure.story('schema')
    def test_topnews_schema(self):
        schema.validate_schema_by_block(self.block, 'topnews', 'touch')


@allure.feature('morda', 'topnews', 'function_tests_stable')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME_TEMPLATE)
class TestTopNewsTouchAstana(object):
    def setup_class(self):
        self.is_user_logged = False
        self.data = _fetch_data(TouchMain(region=Regions.ASTANA), self.is_user_logged,
            params={'ab_flags':AB_FLAGS_TOUCH, 'madm_options': NO_REDIRECT})
        self.block = self.data.get(BLOCK)
        self.href_domain = 'kz'
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

    @allure.story('href')
    def test_topnews_href(self):
        _test_href(self)

    @allure.story('schema')
    def test_topnews_schema(self):
        schema.validate_schema_by_block(self.block, 'topnews', 'touch')


# Topnews при деградации: HOME-64708
@allure.feature('morda', 'topnews', 'function_tests_stable')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME_TEMPLATE)
class TestTopNewsTouchMoscowDegradation(object):
    def setup_class(self):
        self.is_user_logged = False
        self.data = _fetch_data(TouchMain(region=Regions.MOSCOW), self.is_user_logged, params={'ab_flags':AB_FLAGS_TOUCH_DEGRADATION})
        self.block = self.data.get(BLOCK)
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
        schema.validate_schema_by_block(self.block, 'topnews', 'touch')


#HOME-77168
#@allure.feature('morda', 'topnews', 'function_tests_stable')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME_TEMPLATE)
class TestTopNewsTouchMoscowPersonalNotTourist(object):
    def setup_class(self):
        self.is_user_logged = True
        self.data = _fetch_data(TouchMain(region=Regions.MOSCOW), self.is_user_logged,
        params={'ab_flags':AB_FLAGS_TOUCH_PERSONAL_NOT_TOURIST, 'httpmock': HTTPMOCK_LOGGED_USER_HOT,
        'content': 'touch', 'cleanvars': 'Topnews', 'geo': 2})
        self.block = self.data.get(BLOCK)
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
        schema.validate_schema_by_block(self.block, 'topnews', 'touch')


#HOME-77168
#@allure.feature('morda', 'topnews', 'function_tests_stable')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME_TEMPLATE)
class TestTopNewsTouchMoscowPersonalTourist(object):
    def setup_class(self):
        self.is_user_logged = True
        self.data = _fetch_data(TouchMain(region=Regions.MOSCOW), self.is_user_logged,
        params={'ab_flags':AB_FLAGS_TOUCH_PERSONAL_TOURIST, 'httpmock': HTTPMOCK_LOGGED_USER_HOT,
        'content': 'touch', 'cleanvars': 'Topnews', 'geo': 2})
        self.block = self.data.get(BLOCK)
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
        schema.validate_schema_by_block(self.block, 'topnews', 'touch')


#HOME-77168
#@allure.feature('morda', 'topnews', 'function_tests_stable')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME_TEMPLATE)
class TestTopNewsTouchMoscowTourist(object):
    def setup_class(self):
        self.is_user_logged = True
        self.data = _fetch_data(TouchMain(region=Regions.MOSCOW), self.is_user_logged,
        params={'ab_flags':AB_FLAGS_TOUCH_TOURIST, 'httpmock': HTTPMOCK_LOGGED_USER_HOT,
        'content': 'touch', 'cleanvars': 'Topnews', 'geo': 2, 'madm_options': 'enable_new_tourist_morda=0:new_tourist_morda_testids=0',
        'madm_mocks': 'tourist_blocks=tourist_blocks.default'})
        self.block = self.data.get(BLOCK)
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
        schema.validate_schema_by_block(self.block, 'topnews', 'touch')


@allure.feature('morda', 'topnews', 'function_tests_stable')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME_TEMPLATE)
class TestTopNewsTouchMoscowExtraStories(object):
    def setup_class(self):
        self.is_user_logged = False
        self.data = _fetch_data(TouchMain(region=Regions.MOSCOW), self.is_user_logged,
        params={'ab_flags':AB_FLAGS_TOUCH_OFFICIAL_COMMENTS, 'content': 'touch', 'cleanvars': 'Topnews',
        'httpmock': HTTPMOCK_LOGGED_DISCLAIMER_ALLOW})
        self.block = self.data.get(BLOCK)
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
        schema.validate_schema_by_block(self.block, 'topnews', 'touch')


#HOME-77168
#@allure.feature('morda', 'topnews', 'function_tests_stable')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME_TEMPLATE)
class TestTopNewsTouchMoscowDisclaimerAllowAndFavorites(object):
    def setup_class(self):
        self.is_user_logged = True
        self.data = _fetch_data(TouchMain(region=Regions.MOSCOW), self.is_user_logged,
        params={'ab_flags':AB_FLAGS_TOUCH, 'content': 'touch', 'cleanvars': 'Topnews',
        'httpmock': HTTPMOCK_LOGGED_DISCLAIMER_ALLOW, 'madm_mock' : FLAGS_MADM_OPTIONS_MOCK})
        self.block = self.data.get(BLOCK)
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
        schema.validate_schema_by_block(self.block, 'topnews', 'touch')


#HOME-77168
#@allure.feature('morda', 'topnews', 'function_tests_stable')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME_TEMPLATE)
class TestTopNewsTouchMoscowHot(object):
    def setup_class(self):
        self.is_user_logged = True
        self.data = _fetch_data(TouchMain(region=Regions.MOSCOW), self.is_user_logged,
        params={'ab_flags':AB_FLAGS_TOUCH, 'content': 'touch', 'cleanvars': 'Topnews',
        'httpmock': HTTPMOCK_LOGGED_DISCLAIMER_ALLOW})
        self.block = self.data.get(BLOCK)
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
        schema.validate_schema_by_block(self.block, 'topnews', 'touch')


@allure.feature('morda', 'topnews', 'function_tests_stable')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME_TEMPLATE)
class TestTopNewsTouchCom(object):
    def setup_class(self):
        self.is_user_logged = False
        self.data = _fetch_data(TouchCom(), self.is_user_logged,
            params={'ab_flags':AB_FLAGS_TOUCH, 'madm_options': NO_REDIRECT})

    @allure.story('block does not exist')
    def test_topnews_existance(self):
        assert not self.data.get(BLOCK), 'Block must not be here'


@allure.feature('morda', 'topnews', 'function_tests_stable')
class TestTopNewsTouchComTr(object):
    def setup_class(cls):
        data = fetch_data(TouchComTr(), [BLOCK], cgi_params={'madm_options': NO_REDIRECT})
        cls.block = data.get(BLOCK)

    @allure.story('block exists')
    def test_topnews_absence(self):
        absence(self.block)


@allure.feature('morda', 'topnews', 'function_tests_stable')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME_TEMPLATE)
class TestTopNewsTouchMoscowOfficialComments(object):
    def setup_class(self):
        flags = [AB_FLAGS_OFFICIAL_COMMENTS, AB_FLAGS_TOUCH]
        self.is_user_logged = False
        self.data = _fetch_data(
            TouchMain(region=Regions.MOSCOW), self.is_user_logged,
            params={
                'ab_flags': ':'.join(flags),
                'topnews_extra_params': FLAG_FORCE_AB_FLAGS_OFFICIAL_COMMENTS_AND_SUMMARY
            }
        )
        self.block = self.data.get(BLOCK)

    @allure.story('block exists')
    def test_topnews_common(self):
        _test_common(self)

    @allure.story('official_comments')
    def test_topnews_official_comments_exist(self):
        _test_official_comments(self)

    @allure.story('schema')
    def test_topnews_schema(self):
        schema.validate_schema_by_block(self.block, 'topnews', 'touch')


@allure.feature('morda', 'topnews', 'function_tests_stable')
@pytest.mark.yasm(signal=YASM_SIGNAL_NAME_TEMPLATE)
class TestTopNewsTouchMoscowSummary(object):
    def setup_class(self):
        self.is_user_logged = False
        flags = [AB_FLAGS_SUMMARY, AB_FLAGS_TOUCH]
        self.data = _fetch_data(
            TouchMain(region=Regions.MOSCOW), self.is_user_logged,
            params={
                'ab_flags': ':'.join(flags),
                'topnews_extra_params': FLAG_FORCE_AB_FLAGS_OFFICIAL_COMMENTS_AND_SUMMARY
            }
        )
        self.block = self.data.get(BLOCK)

    @allure.story('block exists')
    def test_topnews_common(self):
        _test_common(self)

    # HOME-77180
    #@allure.story('summary exists')
    #def test_topnews_summary_exist(self):
    #    _test_summary(self)

    @allure.story('schema')
    def test_topnews_schema(self):
        schema.validate_schema_by_block(self.block, 'topnews', 'touch')


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

    response = client.cleanvars([BLOCK], **kwargs).send()
    with allure.step('Fetch data'):
        assert response.is_ok(), 'Failed to get cleanvars'
    return response.json()


def _test_existance(test_case):
    with allure.step('Test if block exists'):
        assert test_case.data[BLOCK], 'Failed to get block'


def _test_title_degradation(test_case):
    with allure.step('Test if title is correct in degradation mode'):
        assert test_case.block['title'], 'Title was not found'
        test_case_title = test_case.block['title'].encode('utf-8')
        want_title = u'Новости'.encode('utf-8')
        assert test_case_title == want_title, 'Incorrect title in degrodation mode'


def _test_common(test_case):
    with allure.step('Test if block shows'):
        assert test_case.block['show'], 'Show must be 1'


def _test_date(test_case):
    with allure.step('Test if date ok'):
        assert test_case.block['BigDay'], 'BigDay was not found'
        assert test_case.block['BigMonth'], 'BigMonth was not found'
        assert test_case.block['BigWday'], 'BigWday was not found'


def _test_disclaimer_allow(test_case):
    with allure.step('disclaimer allow'):
        assert test_case.block.get('promo'), 'Disclaimer must be present'


def _test_tabs(test_case):
    with allure.step('Check tabs'):
        assert test_case.block['tabs'], 'Failed to get tabs'
        assert len(test_case.block['tabs']) >= test_case.tabs_num_ge, (
                'Tabs num: must be more than ' + str(test_case.tabs_num_ge))
        for tab in test_case.block['tabs']:
            if tab.get('name') != 'video' and tab.get('name') != 'theme' and tab.get('name') != 'personal':
                assert len(tab.get('news')) >= test_case.news_in_tabs_num_ge, (
                        'News num in tab: must be more than '+str(test_case.news_in_tabs_num_ge))
            if tab.get('news') != None:
                for story in tab.get('news'):
                    if tab.get('name') != 'personal':
                        assert story.get('i') != None, 'Field i is empty'
                        assert story.get('id') != None, 'Field id is empty'
                        assert story.get('text') != None, 'Field text is empty'
        first_tab = test_case.block['tabs'][0]
        assert first_tab.get('default'), 'First tab must have default flag'


def _test_tabs_degradation(test_case):
    with allure.step('Check tabs for degradation'):
        assert test_case.block['tabs'], 'Failed to get tabs'
        assert len(test_case.block['tabs']) == DEGRADATION_DESKTOP_TABS_NUM_GE,\
            'Tabs num: must be ' + '{}'.format(DEGRADATION_DESKTOP_TABS_NUM_GE)
        assert len(test_case.block['tabs'][0].get('news')) == DEGRADATION_DESKTOP_NEWS_IN_TABS_NUM_GE,\
            'News num in tab: must be ' + '{}'.format(DEGRADATION_DESKTOP_NEWS_IN_TABS_NUM_GE)
        assert test_case.block['tabs'][0].get('default'), 'First tab must have default flag'


def _test_field_in_stories(test_case, field_name, test_presence = True):
    for tab in test_case.block.get('tabs'):
        if tab.get('name') == 'video' or tab.get('name') == 'theme':
            continue
        for n in tab.get('news'):
            if n.get(field_name) is None:
                continue
            if test_presence:
                return
            else:
                assert False, '{} must be absent'.format(field_name)
    if test_presence:
        assert False, '{} must be present'.format(field_name)


def _test_field_value_in_stories(test_case, field_name, value):
    for tab in test_case.block.get('tabs'):
        if tab.get('name') == 'video' or tab.get('name') == 'theme':
            continue
        for n in tab.get('news'):
            if n.get(field_name) is None:
                continue
            assert n.get(field_name) == value, "{} must equal to {}".format(field_name, value)


def _test_favorite_news_data_url(test_case):
    assert test_case.block.get('data_url'), 'Data URL must be present'
    assert test_case.block.get('data_url').index('get_favorites_for'),\
        'Data URL must contain get_favorites_for=UID flag'


def _test_disclaimer_existance(test_case):
    assert test_case.block.get('promo'), 'Disclaimer must be present'


def _test_personal_tab_existance(test_case):
    with allure.step('Check personal tab existance'):
        for tab in test_case.block.get('tabs'):
            if tab.get('alias') == 'Personal':
                return
        assert False, 'Personal tab must exist'


def _test_tabs_favorites(test_case):
    with allure.step('Check tabs'):
        assert test_case.block['tabs'], 'Failed to get tabs'
        assert len(test_case.block['tabs']) >= test_case.tabs_num_ge, (
                'Tabs num: must be more than '+str(test_case.tabs_num_ge))
        tab = test_case.block['tabs'][0]
        if tab.get('news') != None:
            for story in tab.get('news'):
                assert story.get('is_favorite'), "Field is_favorite is empty"
                assert story.get('is_favorite') == 1, "Field is_favorite should be equal to 1"


def _test_tabs_tourist(test_case, news_region_name, home_region_name):
    with allure.step('Check tabs'):
        assert test_case.block['tabs'], 'Failed to get tabs'
        assert len(test_case.block['tabs']) >= test_case.tabs_num_ge, (
                'Tabs num: must be more than '+str(test_case.tabs_num_ge))
        news_region_tab = test_case.block['tabs'][1]
        assert news_region_tab.get('alias') == news_region_name, 'Incorrect alias for news_region tab'
        assert news_region_tab.get('name') == 'region', 'Incorrect name for news_region tab'
        assert news_region_tab.get('statid') == 'news.region', 'Incorrect statid for news_region tab'
        if news_region_name == 'Saint_Petersburg':
            assert news_region_tab.get('geo') == '2', 'Incorrect geo for news_region tab'
            test_news_region_title = news_region_tab.get('title').encode('utf-8')
            want_news_region_title = u'Санкт-Петербург'.encode('utf-8')
            assert test_news_region_title == want_news_region_title, 'Incorrect title for news_region tab'

        home_region_tab = test_case.block['tabs'][2]
        assert home_region_tab.get('alias') == home_region_name, ('Incorrect alias for home_region tab')
        assert home_region_tab.get('name') == 'home_region', 'Incorrect name for home_region tab'
        assert home_region_tab.get('statid') == 'news.homeregion', 'Incorrect statid for home_region tab'
        if home_region_name == 'Moscow':
            assert home_region_tab.get('geo') == '213', 'Incorrect geo for home_region tab'
            test_home_region_title = home_region_tab.get('title').encode('utf-8')
            want_home_region_title = u'Москва'.encode('utf-8')
            assert test_home_region_title == want_home_region_title, 'Incorrect title for home_region tab'


def _test_tabs_personal(test_case, personal_tab_id):
    with allure.step('Check tabs'):
        assert test_case.block['tabs'], 'Failed to get tabs'
        assert len(test_case.block['tabs']) >= test_case.tabs_num_ge, (
                'Tabs num: must be more than '+str(test_case.tabs_num_ge))
        tub_number = 0
        for tab in test_case.block['tabs']:
            if tab.get('name') == 'personal':
                assert tub_number == personal_tab_id, "Personal tab lays on the wrong position"
            tub_number += 1
        assert test_case.block['tabs'][personal_tab_id].get('name') == 'personal', 'Personal tab does not exist'
        personal_tab = test_case.block['tabs'][personal_tab_id]
        assert personal_tab.get('alias') == 'Personal', 'Incorrect alias for a personal tab'
        assert personal_tab.get('statid') == 'news.personal', 'Incorrect statid for a personal tab'
        test_case_title = personal_tab.get('title').encode('utf-8')
        want_title = u'Интересное'.encode('utf-8')
        assert test_case_title == want_title, 'Incorrect title in personal tab'


def _test_tabs_degradation(test_case):
    with allure.step('Check tabs'):
        assert test_case.block['tabs'], 'Failed to get tabs'
        assert len(test_case.block['tabs']) == 1, 'Tabs num: must be equal to 1 '
        tab = test_case.block['tabs'][0]
        assert tab.get('statid') == "news.index", 'Incorrect tab type, should be news.index'
        assert len(tab.get('news')) == 5, 'Number of news should be equal to 5'
        for story in tab.get('news'):
            assert story.get('extra_stories') == None, 'Extra stories should not be presented in degradation mode'


def _test_tabs_official_comments_exists(test_case):
    with allure.step('Check tabs'):
        assert test_case.block['tabs'], 'Failed to get tabs'
        official_comments_exist = False
        for tab in test_case.block['tabs']:
            if tab.get('news') != None:
                for story in tab.get('news'):
                    if story.get('official_comments') != None:
                        official_comments_exist = True
        assert official_comments_exist, 'There were no official comments'

def _test_tabs_extra_stories_exist(test_case):
    with allure.step('Check tabs'):
        assert test_case.block['tabs'], 'Failed to get tabs'
        extra_stories_exist = False
        for tab in test_case.block['tabs']:
            if tab.get('news') != None:
                for story in tab.get('news'):
                    if story.get('extra_stories') != None:
                        extra_stories_exist = True
        assert extra_stories_exist, 'There were no extra stories'


def _test_tabs_is_hot(test_case):
    with allure.step('Check tabs'):
        assert test_case.block['tabs'], 'Failed to get tabs'
        hot_news_exist = False
        for tab in test_case.block['tabs']:
            if tab.get('news') != None:
                for story in tab.get('news'):
                    if story.get('ishot') != None and story.get('ishot') == 1:
                        hot_news_exist = True
        assert hot_news_exist, 'There were no hot news'

def _test_favorite_degradation(test_case):
    with allure.step('Check favorite url'):
        assert test_case.block.get('url_setup_favorite') == None, 'url_setup_favorite should be empty in degradation mode'


def _test_href(test_case):
    with allure.step('Check main href'):
        block = test_case.block
        domain = test_case.href_domain
        main_href = block.get('href')
        assert main_href.index(URI_TEMPLATE_NEWS.format(domain=domain)), 'Domain must be ' + URI_TEMPLATE_NEWS.format(
            domain=domain)

    with allure.step('Check special href'):
        if 'special' in block:
            special_href = block.get('special').get('href')
            assert (URI_TEMPLATE_NEWS.format(domain=domain) in special_href or URI_TEMPLATE_SPORT.format(
                domain=domain) in special_href), \
                'Domain must be ' + URI_TEMPLATE_NEWS.format(domain=domain) + ' or ' + URI_TEMPLATE_SPORT.format(
                    domain=domain)

    with allure.step('Check news and tabs href'):
        for tab in block.get('tabs'):
            tab_href = tab.get('href')
            assert tab_href.index(URI_TEMPLATE_NEWS.format(domain=domain)), 'Domain must be ' + URI_TEMPLATE_NEWS.format(
                domain=domain)
            if tab.get('name') != 'video' and tab.get('name') != 'theme':
                for n in tab.get('news'):
                    n_href = n.get('href')
                    assert (URI_TEMPLATE_NEWS.format(domain=domain) in n_href or URI_TEMPLATE_SPORT.format(
                        domain=domain) in n_href), \
                        'Domain must be ' + URI_TEMPLATE_NEWS.format(domain=domain) + ' or ' + URI_TEMPLATE_SPORT.format(
                            domain=domain)


def _test_official_comments(test_case):
    with allure.step('Check official comments exists'):
        block = test_case.block
        assert block.get('tabs'), 'Failed to get tabs'
        official_comments_exists = False
        for tab in block.get('tabs'):
            for news in tab.get('news'):
                official_comments = news.get('official_comments')
                if official_comments and len(official_comments) > 0:
                    official_comments_exists = True
                    break
            if official_comments_exists:
                break
        assert official_comments_exists, 'Can not find official comments in tabs'


def _test_summary(test_case):
    with allure.step('Check summary exists'):
        block = test_case.block
        assert block.get('tabs'), 'Failed to get tabs'
        summary_exists = False
        for tab in block.get('tabs'):
            for news in tab.get('news'):
                summary = news.get('summary')
                if summary and len(summary) > 0:
                    summary_exists = True
                    break
            if summary_exists:
                break
        assert summary_exists, 'Can not find summary in tabs'
