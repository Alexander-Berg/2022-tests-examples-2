import pytest

import testsuite


def find_action(json, action_type):
    for action in json['current_point']['actions']:
        if action['type'] == action_type:
            return action
    return None


SUPPORT_ACTION_SETTINGS = pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_orders_support_action_settings',
    consumers=['cargo-orders/support-action-settings'],
    default_value={'show_phone': True},
)


@pytest.mark.now('2021-11-01T13:30:00+0000')
@pytest.mark.config(
    CARGO_SUPPORT_PHONES={
        'rus': {
            'cities': {
                'moscow': {
                    'phone': '+79123456789',
                    'formatted_phone': '+7 (912) 345 67 89',
                    'working_time': {'from': '09:00', 'to': '21:00'},
                },
            },
            'default_callback': ['test'],
        },
    },
)
@SUPPORT_ACTION_SETTINGS
async def test_happy_path(
        taxi_cargo_orders,
        mock_waybill_info,
        get_driver_cargo_state,
        default_order_id,
        my_waybill_info,
        mock_driver_tags_v1_match_profile,
):
    response = await get_driver_cargo_state(default_order_id)
    assert response.status_code == 200

    support_action = find_action(response.json(), 'support')
    assert support_action == {'type': 'support', 'phone': '+79123456789'}


@pytest.mark.config(CARGO_SUPPORT_PHONES={})
@SUPPORT_ACTION_SETTINGS
async def test_no_country(
        taxi_cargo_orders,
        mock_waybill_info,
        get_driver_cargo_state,
        default_order_id,
        my_waybill_info,
        mock_driver_tags_v1_match_profile,
):
    response = await get_driver_cargo_state(default_order_id)
    assert response.status_code == 200
    assert find_action(response.json(), 'support') is None


@pytest.mark.config(
    CARGO_SUPPORT_PHONES={'rus': {'cities': {}, 'default_callback': ['test']}},
)
@SUPPORT_ACTION_SETTINGS
async def test_no_city(
        taxi_cargo_orders,
        mock_waybill_info,
        get_driver_cargo_state,
        default_order_id,
        my_waybill_info,
        mock_driver_tags_v1_match_profile,
):
    response = await get_driver_cargo_state(default_order_id)
    assert response.status_code == 200
    assert find_action(response.json(), 'support') is None


@pytest.mark.config(
    CARGO_SUPPORT_PHONES={
        'rus': {
            'cities': {
                'moscow': {
                    'phone': '+79123456789',
                    'formatted_phone': '+7 (912) 345 67 89',
                },
            },
            'default_callback': ['test'],
        },
    },
)
@SUPPORT_ACTION_SETTINGS
async def test_no_working_hours(
        taxi_cargo_orders,
        mock_waybill_info,
        get_driver_cargo_state,
        default_order_id,
        my_waybill_info,
        mock_driver_tags_v1_match_profile,
):
    response = await get_driver_cargo_state(default_order_id)
    assert response.status_code == 200
    assert find_action(response.json(), 'support') is None


@pytest.mark.now('2021-11-01T13:30:00+0000')  # 16:30 in Msc
@pytest.mark.parametrize(
    ('from_', 'to_'),
    [
        pytest.param('18:00', '21:00', id='Hours before'),
        pytest.param('16:40', '21:00', id='Minutes before'),
        pytest.param('09:00', '12:00', id='Hours after'),
        pytest.param('16:40', '16:20', id='Minutes after'),
    ],
)
@SUPPORT_ACTION_SETTINGS
async def test_out_of_working_time(
        taxi_config,
        taxi_cargo_orders,
        mock_waybill_info,
        get_driver_cargo_state,
        default_order_id,
        my_waybill_info,
        mock_driver_tags_v1_match_profile,
        from_,
        to_,
):

    taxi_config.set(
        CARGO_SUPPORT_PHONES={
            'rus': {
                'cities': {
                    'moscow': {
                        'phone': '+79123456789',
                        'formatted_phone': '+7 (912) 345 67 89',
                        'working_time': {'from': from_, 'to': to_},
                    },
                },
                'default_callback': ['test'],
            },
        },
    )
    await taxi_cargo_orders.invalidate_caches()

    response = await get_driver_cargo_state(default_order_id)
    assert response.status_code == 200
    assert find_action(response.json(), 'support') is None


@pytest.mark.parametrize(
    ('time_of_day', 'is_valid'),
    [
        ('', False),
        (':', False),
        ('0:00', True),
        ('0:000', False),
        (':00', False),
        ('4:60', False),
        ('17:a', False),
        ('12:5', True),
    ],
)
async def test_time_of_day_pattern(
        taxi_cargo_orders, taxi_config, time_of_day, is_valid,
):
    try:
        taxi_config.set(
            CARGO_SUPPORT_PHONES={
                'rus': {
                    'cities': {
                        'moscow': {
                            'phone': '',
                            'formatted_phone': '',
                            'working_time': {
                                'from': time_of_day,
                                'to': '21:00',
                            },
                        },
                    },
                    'default_callback': [],
                },
            },
        )
        await taxi_cargo_orders.invalidate_caches()
        assert is_valid
    except testsuite.utils.http.HttpResponseError:
        assert not is_valid
