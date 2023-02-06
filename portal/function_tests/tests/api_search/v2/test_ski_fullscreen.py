# -*- coding: utf-8 -*-
import logging

import allure
import pytest

from common import env
from common.client import MordaClient
import common.utils

logger = logging.getLogger(__name__)

ALL_PARAMS = {
    'iphone': {
        'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 YaBrowser/19.5.2.38.10 YaApp_iOS/96.00 Safari/604.1 SA/3',
        'afisha_version': '3',
        'app_build_number': '882',
        'app_id': 'ru.yandex.mobile.dev',
        'app_platform': 'iphone',
        'app_version': '96000000',
        'app_version_name': '96.00',
        'book_reader': '1',
        'country_init': 'RU',
        'debug_panel_on': '1',
        'dialog_onboarding_shows_count': '1',
        'did': '35CA3657-9F89-4F96-8F02-207A9E6DDFE7',
        'div_bs': '1',
        'divkit_version': '2.3.0',
        'div_profile': '1',
        'dp': '3.0',
        'informersCard': '2',
        'lang': 'ru-RU',
        'location_accuracy': '5.000000',
        'location_recency': '213',
        'manufacturer': 'Apple',
        'messengerInProfile': '1',
        'model': 'x86_64',
        'morda_ng': '1',
        'nav_board_promo': '1',
        'new_nav_panel': '1',
        'os_version': '15.2',
        'poiy': '1462',
        'processAssist': '1',
        'service_extensions': 'repetition_bropp',
        'size': '1170%2C2532',
    },
    'android': {
        'user_agent': 'Mozilla/5.0 (Linux; arm; Android 8.1.0; A60) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.174 BroPP/1.0 SA/3 Mobile Safari/537.36 YandexSearch/22.16.1',
        'afisha_version': '3',
        'api_key': '45de325a-08de-435d-bcc3-1ebf6e0ae41b',
        'app_build_number': '220106011',
        'app_id': 'ru.yandex.searchplugin',
        'app_platform': 'android',
        'app_version': '22010601',
        'app_version_name': '22.16',
        'book_reader': '1',
        'bropp': '1',
        'bs_promo': '1',
        'cellid': '250%2C20%2C182671%2C13808%2C0',
        'country_init': 'ru',
        'dialog_onboarding_shows_count': '1',
        'did': '3865c0a92cdcda8b8ba35bf47a15b305',
        'div_bs': '1',
        'divkit_version': '2.3',
        'div_profile': '1',
        'dp': '1.5',
        'gaid': '7c68eb90-0af7-4432-857a-645348b88966',
        'informersCard': '2',
        'installed_launchers': '-1',
        'lang': 'ru-RU',
        'locationPermission': 'true',
        'manufacturer': 'Blackview',
        'model': 'A60',
        'morda_ng': '1',
        'n21_alice_fab': '0',
        'n21_bs_redesign': '0',
        'n21_no_bs_close': '0',
        'nav_board_promo': '1',
        'navigation_2021': '1',
        'new_nav_panel': '1',
        'os_version': '8.1.0',
        'poiy': '750',
        'recents': 'video2%2Cimages%2Cwhocalls%2Cmaps%2Cmusic',
        'search_tab_lister': 'local-template_morda',
        'size': '600%2C1208',
        'with_palette': '0',
        'yuid': '4672709161645105606',
        'zen_extensions': 'true',
        'zen_pages': '1'
    }
}

@pytest.mark.ticket('HOME-77163')
#@allure.feature('function_tests_stable')
@pytest.mark.parametrize('platform', ('android', 'iphone'))
@pytest.mark.parametrize(('lat', 'lon', 'is_tourist', 'fullscreen'), (
    # координаты красной поляны, турист
    (43.668791, 40.258294, 1, True),
    # координаты далекие от поляны, турист
    (55.668791, 37.258294, 1, False),
    # координаты красной поляны, пользователь не турист
    (43.668791, 40.258294, 0, False),
    # координаты далекие от поляны, не турист
    (55.668791, 37.258294, 1, False),
))

def test_ski_fullscreen(platform, lat, lon, is_tourist, fullscreen):
    params = ALL_PARAMS[platform]
    params['cleanvars'] = 1
    params['madm_mocks'] = 'yabs_flags=yabs_flags:welcome_tab=welcome_tab:tourist_blocks=tourist_blocks.default'
    params['lat']= lat
    params['lon']= lon
    params['madm_options'] = 'enable_new_tourist_morda=0:new_tourist_morda_testids=0:set_is_tourist_laas={}'.format(is_tourist)

    if fullscreen:
        params['httpmock'] = 'yabs@bk_answer_tourist'
    else:
        params['httpmock'] = 'yabs@empty_dict'

    client   = MordaClient(env=env.morda_env())
    response = client.api_search_2(**params).send()
    assert response.is_ok(), 'Failed to get api-search response'

    json_data  = response.json()
    common.utils.check_madm_error(json_data)

    if fullscreen:
        assert 'welcome_tab' in json_data
        assert json_data['welcome_tab']['url'] == 'yellowskin://?fullscreenHiddenBnt=true&fullscreenMode=fullscreen&url=https%3A%2F%2Fyandex.ru%2Fpromo%2Fsearchapp%2Fski_fullscreen%2Fski_resorts'
    else:
        'welcome_tab' not in json_data
