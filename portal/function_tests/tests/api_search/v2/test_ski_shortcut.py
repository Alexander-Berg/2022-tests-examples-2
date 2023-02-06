# -*- coding: utf-8 -*-
import logging

import allure
import pytest

from common import env
from common.client import MordaClient
import common.utils

logger = logging.getLogger(__name__)

ALL_PARAMS = {
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
    'div_profile': '1',
    'divkit_version': '2.3.0',
    'dp': '3.0',
    'informersCard': '2',
    'lang': 'ru-RU',
    'manufacturer': 'Apple',
    'messengerInProfile': '1',
    'model': 'x86_64',
    'morda_ng': '1',
    'nav_board_promo': '1',
    'new_nav_panel': '1',
    'os_version': '15.2',
    'poiy': '1462',
    'service_extensions': 'repetition_bropp',
    'size': '1170,2532',
    'location_accuracy': '5.000000',
    'location_recency': '104565',
    'cleanvars': '1',
    'processAssist': 1,
    'madm_mocks': 'shortcuts_settings_v2=shortcuts_settings_v2_mock_2'
}

@pytest.mark.xfail(reason='ski shortcut is turned off', strict=True)
@pytest.mark.ticket('HOME-77164')
@allure.feature('function_tests_stable')
@pytest.mark.parametrize(('recents', 'lat', 'lon', 'is_tourist', 'first_shortcut'), (
    # координаты красной поляны. горнолыжка на первом месте
    (None,                        43.668791, 40.258294, 1, True),
    # координаты красной поляны и параметр recents=ski_krasnaya-polyana-meta. горнолыжка остается на первом месте
    ('ski_krasnaya-polyana-meta', 43.668791, 40.258294, 1, True),
    # координаты далекие от поляны и параметр recents=ski_krasnaya-polyana-meta. горнолыжка должна уйти в рисенты
    ('ski_krasnaya-polyana-meta', 55.668791, 37.258294, 1, False),
    # координаты красной поляны, пользователь не турист. Горнолыжка не на первом месте
    (None, 43.668791, 40.258294, 0, False),
    # координаты красной поляны, пользователь не турист и параметр recents=ski_krasnaya-polyana-meta. Горнолыжка не на первом месте
    ('ski_krasnaya-polyana-meta', 43.668791, 40.258294, 0, False),
))
def test_ski_shortcut_first(recents, lat, lon, is_tourist, first_shortcut):
    params = ALL_PARAMS
    params['lat']= lat
    params['lon']= lon
    params['madm_options'] = 'enable_new_tourist_morda=0:new_tourist_morda_testids=0:ski_shortcut_not_tourist_order=999:set_is_tourist_laas={}'.format(is_tourist)

    if recents is not None:
        params['recents'] = recents

    client   = MordaClient(env=env.morda_env())
    response = client.api_search_2(**params).send()
    assert response.is_ok(), 'Failed to get api-search response'

    json_data  = response.json()
    common.utils.check_madm_error(json_data)

    shortcuts = json_data['raw_data']['alerts']['alerts']['informers']['cards'][0]['data']['shortcuts']
    if first_shortcut:
        assert  shortcuts[0]['type'] == 'ski_krasnaya-polyana-meta'
    else:
        # позиция рисентов задается в экспорте shortcuts_settings_v2, ищем записи с type=recent, в поле order позиция
        # количество шорткатов перед рисентами, тоже не постоянное, поэтому мокаем экспорт shortcuts_settings_v2
        for i in range(0,3):
            assert shortcuts[i]['type'] != 'ski_krasnaya-polyana-meta', "shortcuts[{}]['type']={}".format(i, shortcuts[i]['type'])
        assert shortcuts[-1]['type'] == 'ski_krasnaya-polyana-meta'
