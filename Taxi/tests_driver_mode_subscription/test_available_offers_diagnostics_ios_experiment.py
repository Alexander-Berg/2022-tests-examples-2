import datetime as dt
import enum
from typing import List
from typing import Optional

import pytest
import pytz

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import offer_templates
from tests_driver_mode_subscription import scenario

_TIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
'2019-05-01T05:00:00+00:00'
_NOW = dt.datetime(2020, 5, 5, 15, 15, 5, 0, tzinfo=pytz.utc)


class DriverProfileResponseType(enum.Enum):
    ALL_OK = 'ALL_OK'
    NO_PLATFORM = 'NO_PLATFORM'
    NO_VERSION = 'NO_VERSION'
    NO_PLATFORM_AND_VERSION = 'NO_PLATFORM_AND_VERSION'
    NO_PROFILE_DATA = 'NO_PROFILE_DATA'
    NO_PROFILE = 'NO_PROFILE'
    ERROR = 'ERROR'


class TaximeterPlatform(enum.Enum):
    IOS = 'ios'
    ANDROID = 'android'


_VERSION_562 = '8.80 (562)'
_VERSION_600 = '9.72 (600)'


def _mock_driver_profiles(
        mockserver,
        result_type: DriverProfileResponseType,
        platform: TaximeterPlatform,
        version: str,
):
    @mockserver.json_handler(
        '/driver-profiles/v1/driver/app/profiles/retrieve',
    )
    def handler(request):
        if result_type == DriverProfileResponseType.NO_PROFILE_DATA:
            return {'profiles': [{'park_driver_profile_id': 'dbid_uuid'}]}
        if result_type == DriverProfileResponseType.NO_PLATFORM:
            return {
                'profiles': [
                    {
                        'data': {'taximeter_version': version},
                        'park_driver_profile_id': 'dbid_uuid',
                    },
                ],
            }
        if result_type == DriverProfileResponseType.NO_VERSION:
            return {
                'profiles': [
                    {
                        'data': {'taximeter_platform': platform.value},
                        'park_driver_profile_id': 'dbid_uuid',
                    },
                ],
            }
        if result_type == DriverProfileResponseType.NO_PLATFORM_AND_VERSION:
            return {
                'profiles': [
                    {'data': {}, 'park_driver_profile_id': 'dbid_uuid'},
                ],
            }
        if result_type == DriverProfileResponseType.NO_PROFILE:
            return {'profiles': []}
        if result_type == DriverProfileResponseType.ERROR:
            return mockserver.make_response(status=500)

        return {
            'profiles': [
                {
                    'park_driver_profile_id': 'dbid_uuid',
                    'data': {
                        'taximeter_platform': platform.value,
                        'taximeter_version': version,
                    },
                },
            ],
        }

    return handler


def _mock_services(
        mockserver,
        mocked_time,
        dbid_uuid: str,
        udid: Optional[str],
        position: Optional[common.Position],
        tags: List[str],
        app_profiles_response_type: DriverProfileResponseType,
        platform: TaximeterPlatform,
        version: str,
):
    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        return common.mode_history_response(request, 'orders', mocked_time)

    @mockserver.json_handler('/driver-fix/v1/view/offer')
    async def _mock_view_offer(request):
        return {
            'offers': [
                {
                    'offer_card': {
                        'title': 'За время',
                        'subtitle': 'Доступен до 2 декабря',
                        'description': 'Заработок зависит от времени работы',
                        'is_new': True,
                        'enabled': True,
                    },
                    'settings': {
                        'rule_id': 'id_rule1',
                        'shift_close_time': '00:01',
                    },
                    'offer_screen': {
                        'items': [
                            {'type': 'text', 'text': 'Подробности правила 1.'},
                        ],
                    },
                    'memo_screen': {
                        'items': [{'type': 'text', 'text': 'Memo правила 1'}],
                    },
                },
            ],
        }

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    def _v1_uniques(request):
        if udid:
            return {
                'uniques': [
                    {
                        'park_driver_profile_id': dbid_uuid,
                        'data': {'unique_driver_id': udid},
                    },
                ],
            }
        return {'uniques': []}

    @mockserver.json_handler('/driver-tags/v1/drivers/match/profile')
    def _match_profile(request):
        return {'tags': tags}

    scenario.Scene.mock_driver_trackstory(mockserver, position)

    _mock_driver_profiles(
        mockserver, app_profiles_response_type, platform, version,
    )


@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=(
        offer_templates.DEFAULT_OFFER_TEMPLATES
    ),
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS=(
        offer_templates.DEFAULT_MODE_TEMPLATE_RELATIONS
    ),
)
@pytest.mark.mode_rules(
    rules=mode_rules.patched(patches=[mode_rules.Patch('custom_orders')]),
)
@pytest.mark.now(_NOW.strftime(_TIME_FORMAT))
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.experiments3(filename='available_offers_ios_display_modes.json')
@pytest.mark.parametrize(
    'dbid_uuid, udid, position, tags, app_profiles_response_type, platform,'
    'version, expected_displayed_modes',
    [
        pytest.param(
            'dbid_uuid',
            'udid',
            scenario.SPB_POSITION,
            [],
            DriverProfileResponseType.ALL_OK,
            TaximeterPlatform.IOS,
            _VERSION_562,
            [],
            id='empty_set',
        ),
        pytest.param(
            'dbid_uuid',
            'udid1',
            scenario.SPB_POSITION,
            [],
            DriverProfileResponseType.ALL_OK,
            TaximeterPlatform.IOS,
            _VERSION_562,
            ['orders', 'custom_orders'],
            id='match_udid',
        ),
        pytest.param(
            'dbid_uuid',
            None,
            scenario.SPB_POSITION,
            [],
            DriverProfileResponseType.ALL_OK,
            TaximeterPlatform.IOS,
            _VERSION_562,
            [],
            id='no_udid',
        ),
        pytest.param(
            'dbid1_uuid1',
            'udid',
            scenario.SPB_POSITION,
            [],
            DriverProfileResponseType.ALL_OK,
            TaximeterPlatform.IOS,
            _VERSION_562,
            ['orders', 'custom_orders', 'driver_fix'],
            id='match_dbid_uuid',
        ),
        pytest.param(
            'dbid_uuid',
            'udid',
            scenario.SPB_POSITION,
            [
                'loginef_driver',
                'discount_1000_2020_04_01_loginef_test_effdev_1040_tmp',
            ],
            DriverProfileResponseType.ALL_OK,
            TaximeterPlatform.IOS,
            _VERSION_562,
            ['orders', 'custom_orders', 'driver_fix'],
            id='match_tags',
        ),
        pytest.param(
            'dbid_uuid',
            'udid',
            scenario.SPB_POSITION,
            [],
            DriverProfileResponseType.ALL_OK,
            TaximeterPlatform.IOS,
            _VERSION_600,
            ['orders', 'custom_orders', 'driver_fix'],
            id='match_version',
        ),
        pytest.param(
            'dbid_uuid',
            'udid',
            scenario.MOSCOW_POSITION,
            [],
            DriverProfileResponseType.ALL_OK,
            TaximeterPlatform.IOS,
            _VERSION_562,
            ['orders', 'custom_orders', 'driver_fix'],
            id='match_geonodes',
        ),
        pytest.param(
            'dbid_uuid',
            'udid',
            scenario.SPB_POSITION,
            [],
            DriverProfileResponseType.ALL_OK,
            TaximeterPlatform.ANDROID,
            _VERSION_562,
            ['orders', 'custom_orders', 'driver_fix'],
            id='android',
        ),
        pytest.param(
            'dbid_uuid',
            'udid',
            scenario.SPB_POSITION,
            [],
            DriverProfileResponseType.NO_PLATFORM,
            TaximeterPlatform.IOS,
            _VERSION_562,
            ['orders', 'custom_orders', 'driver_fix'],
            id='empty_platform',
        ),
        pytest.param(
            'dbid_uuid',
            'udid',
            scenario.SPB_POSITION,
            [],
            DriverProfileResponseType.NO_VERSION,
            TaximeterPlatform.IOS,
            _VERSION_562,
            ['orders', 'custom_orders', 'driver_fix'],
            id='empty_version',
        ),
        pytest.param(
            'dbid_uuid',
            'udid',
            scenario.SPB_POSITION,
            [],
            DriverProfileResponseType.NO_PLATFORM_AND_VERSION,
            TaximeterPlatform.IOS,
            _VERSION_562,
            ['orders', 'custom_orders', 'driver_fix'],
            id='empty_taximeter_info',
        ),
        pytest.param(
            'dbid_uuid',
            'udid',
            scenario.SPB_POSITION,
            [],
            DriverProfileResponseType.NO_PROFILE_DATA,
            TaximeterPlatform.IOS,
            _VERSION_562,
            ['orders', 'custom_orders', 'driver_fix'],
            id='empty_profile',
        ),
        pytest.param(
            'dbid_uuid',
            'udid',
            scenario.SPB_POSITION,
            [],
            DriverProfileResponseType.NO_PROFILE,
            TaximeterPlatform.IOS,
            _VERSION_562,
            ['orders', 'custom_orders', 'driver_fix'],
            id='no_profile',
        ),
        pytest.param(
            'dbid_uuid',
            'udid',
            scenario.SPB_POSITION,
            [],
            DriverProfileResponseType.ERROR,
            TaximeterPlatform.IOS,
            _VERSION_562,
            ['orders', 'custom_orders', 'driver_fix'],
            id='profile_fetch_error',
        ),
        pytest.param(
            'dbid_uuid',
            'udid',
            None,
            [],
            DriverProfileResponseType.ALL_OK,
            TaximeterPlatform.IOS,
            _VERSION_562,
            [],
            id='no_position',
        ),
    ],
)
async def test_diagnostics_ios_experiment(
        taxi_driver_mode_subscription,
        mockserver,
        mocked_time,
        mode_rules_data,
        mode_geography_defaults,
        dbid_uuid: str,
        udid: Optional[str],
        position: Optional[common.Position],
        tags: List[str],
        app_profiles_response_type: DriverProfileResponseType,
        platform: TaximeterPlatform,
        version: str,
        expected_displayed_modes: List[str],
):
    mode_geography_defaults.set_all_modes_available()
    _mock_services(
        mockserver,
        mocked_time,
        dbid_uuid,
        udid,
        position,
        tags,
        app_profiles_response_type,
        platform,
        version,
    )

    response = await common.available_offers_diagnostics(
        taxi_driver_mode_subscription,
        dbid_uuid.split('_')[0],
        dbid_uuid.split('_')[1],
    )

    displayed_modes = [
        x['mode_id']
        for x in response['driver_modes']
        if x['display']['is_displayed']
    ]
    assert sorted(displayed_modes) == sorted(expected_displayed_modes)
