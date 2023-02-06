import pytest


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={
        'remove_pay_type_for_client_setcar': True,
        'enable_driver_profiles_request': True,
    },
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_processings_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'__default__': False},
)
async def test_setcar_hide_pay_type(
        mockserver,
        taxi_driver_orders_builder,
        load_json,
        setcar_create_params,
):
    version = '9.30'
    setcar_push = load_json('setcar_push.json')

    @mockserver.json_handler(
        '/driver-profiles/v1/driver/app/profiles/retrieve',
    )
    def _mock_setcar_data(request):
        return {
            'profiles': [
                {
                    'park_driver_profile_id': 'park1_driver1',
                    'data': {
                        'locale': 'ru',
                        'taximeter_version': version,
                        'taximeter_version_type': '',
                        'taximeter_platform': 'android',
                        'fleet_type': 'taximeter',
                    },
                },
            ],
        }

    response = await taxi_driver_orders_builder.post(**setcar_create_params)
    assert response.status_code == 200
    del setcar_push['pay_type']
    assert response.json()['setcar_push'] == setcar_push


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_processings_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'__default__': False},
)
async def test_setcar_push_new_year_sound(
        mockserver,
        taxi_driver_orders_builder,
        load_json,
        setcar_create_params,
        driver_profile_view,
):
    setcar_push = load_json('setcar_push.json')
    setcar_push['notification']['sound'] = 'new_year_order_sound.wav'
    setcar_push['internal']['title'] = 'Новый заказ'

    @mockserver.json_handler(
        '/driver-profiles/v1/driver/app/profiles/retrieve',
    )
    def _mock_get_driver_app(request):
        return {
            'profiles': [
                {
                    'park_driver_profile_id': 'park1_driver1',
                    'data': {
                        'locale': 'ru',
                        'taximeter_version': '9.50',
                        'taximeter_version_type': '',
                        'taximeter_platform': 'ios',
                        'fleet_type': 'taximeter',
                    },
                },
            ],
        }

    driver_profile_view.set_sound('new_year_order_sound.wav')

    response = await taxi_driver_orders_builder.post(**setcar_create_params)
    assert response.status_code == 200
    assert response.json()['setcar_push'] == setcar_push


DEFAULT_SOUND = 'default.wav'


@pytest.mark.config(SETCAR_SOUND_DEFAULT={'sound': DEFAULT_SOUND})
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_processings_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'__default__': False},
)
@pytest.mark.parametrize(
    'income_order_sound',
    [
        {'status': 500, 'body': {}},
        {'status': 200, 'body': {}},
        {'status': 200, 'body': {'sound': ''}},
    ],
)
async def test_setcar_push_config_default_sound(
        mockserver,
        taxi_driver_orders_builder,
        load_json,
        setcar_create_params,
        income_order_sound,
):
    setcar_push_expected = load_json('setcar_push.json')
    setcar_expected = load_json('setcar.json')
    setcar_push_expected['notification']['sound'] = DEFAULT_SOUND
    setcar_expected['notification']['sound'] = DEFAULT_SOUND

    @mockserver.json_handler(
        '/driver-profile-view/internal/v1/income-order-sounds',
    )
    def _mock_income_order_sounds(request):
        return mockserver.make_response(
            status=income_order_sound['status'],
            json=income_order_sound['body'],
        )

    response = await taxi_driver_orders_builder.post(**setcar_create_params)
    assert response.status_code == 200
    assert response.json()['setcar_push'] == setcar_push_expected
    assert response.json()['setcar'] == setcar_expected
