import json

import pytest

from tests_driver_fix import common
from testsuite.utils import ordered_object

MODE_INFO_RESPONSE = {
    'mode': {
        'name': 'driver_fix',
        'started_at': '2019-01-01T08:00:00+0300',
        'features': [
            {
                'name': 'driver_fix',
                'settings': {
                    'rule_id': 'subvention_rule_id',
                    'shift_close_time': '00:00:00+03:00',
                },
            },
            {'name': 'tags'},
        ],
    },
}

HEADERS = common.DEFAULT_HEADERS_FROM_DRIVER_AUTHPROXY.copy()
HEADERS.update({'Accept-Language': 'ru'})


VEHICLE_BINDING = {
    'profiles': [
        {
            'park_driver_profile_id': 'dbid_uuid',
            'data': {'car_id': 'vehicle1'},
        },
    ],
}


@pytest.mark.parametrize(
    'dont_filter,show_additional,show_end,'
    'bs_response,bd_response,expected,expected_group_ids',
    [
        (
            False,
            False,
            False,
            'bs_response.json',
            None,
            'expected_response.json',
            ['group_id/3d8eb989-b2d5-487a-b86a-6ee7eabc8c15'],
        ),
        (
            False,
            False,
            True,
            'bs_response.json',
            None,
            'expected_response_with_end.json',
            ['group_id/3d8eb989-b2d5-487a-b86a-6ee7eabc8c15'],
        ),
        (
            True,
            False,
            False,
            'bs_response.json',
            None,
            'expected_response.json',
            ['group_id/3d8eb989-b2d5-487a-b86a-6ee7eabc8c15'],
        ),
        (
            False,
            False,
            False,
            'bs_response.json',
            'bd_response_invalid_rule.json',
            'expected_response.json',
            ['group_id/3d8eb989-b2d5-487a-b86a-6ee7eabc8c15'],
        ),
        (
            False,
            False,
            False,
            'bs_response.json',
            'bd_response_1_complete.json',
            'expected_response_1_complete.json',
            ['group_id/3d8eb989-b2d5-487a-b86a-6ee7eabc8c15'],
        ),
        (
            False,
            False,
            False,
            'bs_response.json',
            'bd_response_fully_complete.json',
            'expected_response_fully_complete.json',
            ['group_id/3d8eb989-b2d5-487a-b86a-6ee7eabc8c15'],
        ),
        (
            False,
            False,
            False,
            'bs_response.json',
            'bd_response_incomplete.json',
            'expected_response_incomplete.json',
            ['group_id/3d8eb989-b2d5-487a-b86a-6ee7eabc8c15'],
        ),
        (
            False,
            False,
            False,
            'bs_response_full.json',
            'bd_response_full.json',
            'expected_response_full.json',
            [
                'group_id/ffac87b9-34f6-4f1f-9c2f-c21d5c1993c1',
                'group_id/79eaf36c-7076-4648-af71-79aa4babb5a5',
                'group_id/3d8eb989-b2d5-487a-b86a-6ee7eabc8c15',
                'group_id/6305e49a-e498-4328-bd48-bbcbcfd0f6e9',
            ],
        ),
        (
            False,
            False,
            False,
            'bs_response_currency.json',
            'bd_response_1_complete.json',
            'expected_response_currency.json',
            ['group_id/3d8eb989-b2d5-487a-b86a-6ee7eabc8c15'],
        ),
        (False, False, False, 'bs_response_filter.json', None, None, []),
        (
            True,
            False,
            False,
            'bs_response_filter.json',
            None,
            'expected_response_non_filtered.json',
            [],
        ),
        (
            True,
            True,
            False,
            'bs_response_different_options.json',
            None,
            'expected_response_different_options.json',
            [],
        ),
    ],
)
@pytest.mark.config(
    DRIVER_FIX_USE_TAXIMETER_GEOPOINT_AS_FALLBACK=True,
    DRIVER_FIX_STATUS_PANEL_ITEMS=['subventions'],
    RULES_SELECT_WRAPPER_CACHE_SETTINGS={
        '__default__': {
            'expiration_time_seconds': 180,
            'max_size': 5000,
            'time_tolerance_seconds': 60,
            'merge_add_subventions': True,
        },
    },
    CURRENCY_FORMATTING_RULES={
        'RUB': {'__default__': 2, 'driver-fix': 0},
        '__default__': {'__default__': 2, 'driver-fix': 1},
    },
)
@pytest.mark.now('2019-01-01T12:00:00+0300')  # Tuesday
async def test_do_x_get_y(
        load_json,
        taxi_driver_fix,
        activity,
        vehicles,
        driver_tags_mocks,
        mockserver,
        mock_offer_requirements,
        mock_driver_mode_index,
        taxi_config,
        unique_drivers,
        dont_filter,
        show_additional,
        show_end,
        bs_response,
        bd_response,
        expected,
        expected_group_ids,
):
    taxi_config.set(
        DRIVER_FIX_SUBVENTIONS_SETTINGS={
            'disable_filtering': dont_filter,
            'show_additional_requirements': show_additional,
            'show_rule_end': show_end,
        },
    )

    mock_offer_requirements.init(
        common.PROFILES_DEFAULT_VALUE,
        common.DCB_DEFAULT_VALUE,
        common.PAYMENT_TYPES_DEFAULT_VALUES,
        common.NEARESTZONE_DEFAULT_VALUE,
        None,
        {
            'driver_fix': [common.DEFAULT_DRIVER_FIX_RULE],
            'goal': load_json(bs_response),
        },
        load_json(bd_response) if bd_response else None,
    )

    mock_offer_requirements.profiles_value['classes'] = ['econom', 'business']
    mock_offer_requirements.profiles_value['position'] = [0, 0]
    mock_offer_requirements.set_position_fallback([37.63361316, 55.75419758])
    driver_tags_mocks.set_tags_info('dbid', 'uuid', ['non_virtual_tag'])

    @mockserver.json_handler('/driver-mode-subscription/v1/mode/info')
    def _dms_mode_info(request):
        return MODE_INFO_RESPONSE

    mock_driver_mode_index.set_virtual_tags(['virtual_tag_1', 'virtual_tag_2'])

    @mockserver.json_handler('/driver-metrics-storage/v2/event/new')
    async def _event_new(request):
        return {}

    @mockserver.json_handler('/billing_subventions/v1/virtual_by_driver')
    async def _get_by_driver(request):
        return {'subventions': []}

    unique_drivers.add_driver('dbid', 'uuid', 'very_unique_id')
    if show_additional:
        activity.add_driver('very_unique_id', 88.0)
        vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
        vehicles.set_cars_list_response(load_json('parks_cars_list.json'))

    response = await taxi_driver_fix.get(
        'v1/view/status',
        params={
            'tz': 'Europe/Moscow',
            'park_id': 'dbid',
            'lon': 37.63361316,
            'lat': 55.75419758,
        },
        headers=HEADERS,
    )

    assert response.status_code == 200

    assert len(mock_offer_requirements.rules_select_call_params) == 2

    if expected_group_ids:
        assert mock_offer_requirements.by_driver_calls == 1
        ordered_object.assert_eq(
            json.loads(mock_offer_requirements.by_driver_call_params[0]),
            {
                'subvention_rule_ids': expected_group_ids,
                'time': '2019-01-01T09:00:00+00:00',
                'unique_driver_id': 'very_unique_id',
            },
            ['subvention_rule_ids'],
        )

    print(mock_offer_requirements.rules_select_call_params)
    expected_request = {
        'is_personal': False,
        'limit': 1000,
        'profile_tags': ['non_virtual_tag', 'virtual_tag_1', 'virtual_tag_2'],
        'order_tariff_classes': ['business', 'econom'],
        'status': 'enabled',
        'tariff_zone': 'moscow',
        'time_range': {
            'start': '2019-01-01T09:00:00+00:00',
            'end': '2019-01-01T09:00:00.001+00:00',
        },
        'types': ['goal'],
    }
    assert expected_request in mock_offer_requirements.rules_select_call_params

    if expected:
        ordered_object.assert_eq(
            load_json(expected), response.json()['panel_body'], ['items'],
        )
    else:
        assert {'items': []} == response.json()['panel_body']
