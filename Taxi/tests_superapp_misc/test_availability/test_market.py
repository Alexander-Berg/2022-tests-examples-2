import pytest

from tests_superapp_misc.test_availability import consts
from tests_superapp_misc.test_availability import helpers


@pytest.mark.translations(
    client_messages={
        'superapp.taxi.service_name': {'ru': 'Taxi'},
        'superapp.eats.service_name': {'ru': 'Eats'},
        'superapp.supermarket.service_name': {'ru': 'Market'},
    },
)
@pytest.mark.experiments3(filename='exp3_superapp_availability.json')
@pytest.mark.parametrize(
    ['experiment_value', 'expected_response'],
    [
        pytest.param(
            {'enabled': True},
            helpers.market_ok_response(is_available=True),
            id='Available',
        ),
        pytest.param(
            {'enabled': False},
            helpers.market_ok_response(is_available=False),
            id='Not available by experiment(superapp_market_availability)',
        ),
        pytest.param(None, helpers.ok_response(), id='No experiment'),
        pytest.param(
            {'enabled': True, 'deathflag': True},
            helpers.market_ok_response(is_available=False, deathflag=True),
            id='deathflag',
        ),
        pytest.param(
            {'enabled': False, 'show_disabled': True},
            helpers.market_ok_response(is_available=False, show_disabled=True),
            id='show_disabled',
        ),
    ],
)
async def test_market_availability(
        taxi_superapp_misc, experiment_value, expected_response, experiments3,
):
    if experiment_value is not None:
        experiments3.add_experiment(
            clauses=[
                {
                    'title': 'main clause',
                    'value': experiment_value,
                    'predicate': {'type': 'true'},
                },
            ],
            name='superapp_market_availability',
            consumers=['superapp-misc/availability'],
            match={'enabled': True, 'predicate': {'type': 'true'}},
        )

    response = await taxi_superapp_misc.post(
        consts.URL, helpers.build_payload(),
    )
    assert response.status_code == 200
    assert response.json() == expected_response
