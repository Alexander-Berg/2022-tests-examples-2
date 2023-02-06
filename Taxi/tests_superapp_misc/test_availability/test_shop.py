import pytest

from tests_superapp_misc.test_availability import consts
from tests_superapp_misc.test_availability import helpers


@consts.USE_CATLOG_STORAGE
@pytest.mark.translations(
    client_messages={
        'superapp.taxi.service_name': {'ru': 'Taxi'},
        'superapp.shop.service_name': {'ru': 'Shop'},
    },
)
@pytest.mark.experiments3(filename='exp3_superapp_availability.json')
@pytest.mark.parametrize(
    'available, available_exp, deathflag_exp, expected_available',
    [
        pytest.param(True, True, False, True, id='Available'),
        pytest.param(
            False,
            True,
            False,
            False,
            id='Not available by eda-catalog availability: False',
        ),
        pytest.param(
            True,
            False,
            False,
            False,
            id='Not available by experiment(superapp_shop_availability)',
        ),
        pytest.param(
            True,
            True,
            True,
            False,
            id='Not available by deathflag(superapp_deathflag_shop)',
        ),
    ],
)
async def test_shop_availability(
        taxi_superapp_misc,
        taxi_config,
        available,
        available_exp,
        deathflag_exp,
        expected_available,
        experiments3,
        mockserver,
):
    eda_availability_called = False

    @mockserver.json_handler(consts.EDA_STORAGE_AVAILBILITY)
    def _eda_availability(request):
        nonlocal eda_availability_called
        eda_availability_called = True
        return {
            'payload': {
                'services': [
                    {
                        'type': 'shop',
                        'isAvailable': available,
                        'isExist': True,
                    },
                ],
            },
        }

    experiments3.add_experiment(
        clauses=[
            {
                'title': 'main clause',
                'value': helpers.build_exp_value(
                    used_services={'shop': available_exp},
                    deathflag=deathflag_exp,
                ),
                'predicate': {'type': 'true'},
            },
        ],
        name='superapp_availability',
        consumers=['superapp-misc/availability'],
        match={'enabled': True, 'predicate': {'type': 'true'}},
    )

    response = await taxi_superapp_misc.post(
        consts.URL, helpers.build_payload(send_services=False),
    )
    assert response.status_code == 200
    assert eda_availability_called
    assert response.json() == {
        'modes': [
            {
                'mode': 'taxi',
                'parameters': {'available': True, 'product_tag': 'taxi'},
            },
            {
                'mode': 'shop',
                'parameters': {
                    'available': expected_available,
                    'deathflag': deathflag_exp,
                    'product_tag': 'shop',
                },
            },
        ],
        'products': [
            {'service': 'taxi', 'tag': 'taxi', 'title': 'Taxi'},
            {'service': 'shop', 'tag': 'shop', 'title': 'Shop'},
        ],
        'typed_experiments': {'items': [], 'version': -1},
        'zone_name': 'moscow',
    }


@consts.USE_CATLOG_STORAGE
@pytest.mark.translations(
    client_messages={
        'superapp.taxi.service_name': {'ru': 'Taxi'},
        'superapp.shop.service_name': {'ru': 'Shop'},
    },
)
@pytest.mark.experiments3(filename='exp3_superapp_availability.json')
@pytest.mark.parametrize(
    'exp_multipoint, expected_availability, expected_mock_calls',
    [
        pytest.param(
            True,
            True,
            3,
            id='Available only on waypoint, exp ON, available: true',
        ),
        pytest.param(
            False,
            False,
            1,
            id='Available only on waypoint, exp OFF, available: false',
        ),
        pytest.param(
            None,
            False,
            1,
            id='Available only on waypoint, exp is empty, available: false',
        ),
    ],
)
async def test_shop_multipoint_availability(
        taxi_superapp_misc,
        taxi_config,
        experiments3,
        mockserver,
        exp_multipoint,
        expected_availability,
        expected_mock_calls,
):
    @mockserver.json_handler(consts.EDA_STORAGE_AVAILBILITY)
    def _eda_availability(request):
        available = helpers.is_equal_position(
            request.query, consts.ADDITIONAL_POSITION,
        )
        return {
            'payload': {
                'services': [
                    {
                        'type': 'shop',
                        'isAvailable': available,
                        'isExist': True,
                    },
                ],
            },
        }

    experiments3.add_experiment(
        clauses=[
            {
                'title': 'main clause',
                'value': helpers.build_exp_value(
                    used_services={'shop': True}, deathflag=False,
                ),
                'predicate': {'type': 'true'},
            },
        ],
        name='superapp_availability',
        consumers=['superapp-misc/availability'],
        match={'enabled': True, 'predicate': {'type': 'true'}},
    )
    if exp_multipoint is not None:
        helpers.add_exp_multipoint(experiments3, exp_multipoint)

    response = await taxi_superapp_misc.post(
        consts.URL,
        helpers.build_payload(
            send_services=False, state=helpers.build_state(),
        ),
    )
    assert response.status_code == 200
    assert _eda_availability.times_called == expected_mock_calls
    assert response.json() == {
        'modes': [
            {
                'mode': 'taxi',
                'parameters': {'available': True, 'product_tag': 'taxi'},
            },
            {
                'mode': 'shop',
                'parameters': {
                    'available': expected_availability,
                    'deathflag': False,
                    'product_tag': 'shop',
                },
            },
        ],
        'products': [
            {'service': 'taxi', 'tag': 'taxi', 'title': 'Taxi'},
            {'service': 'shop', 'tag': 'shop', 'title': 'Shop'},
        ],
        'typed_experiments': {'items': [], 'version': -1},
        'zone_name': 'moscow',
    }
