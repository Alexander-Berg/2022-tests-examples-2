import pytest

from tests_superapp_misc.test_availability import consts
from tests_superapp_misc.test_availability import helpers

CLIENT_MESSAGES_TRANSLATIONS = {
    'superapp.taxi.service_name': {'ru': 'Taxi'},
    'superapp.eats.service_name': {'ru': 'Eats'},
    'superapp.grocery.service_name': {'ru': 'Grocery'},
    'superapp.drive.service_name': {'ru': 'Drive'},
    'superapp.masstransit.service_name': {'ru': 'Masstransit'},
    'superapp.delivery.service_name': {'ru': 'Delivery'},
    'superapp.restaurants.service_name': {'ru': 'Restaurants'},
}

FALLBACK_NAME = 'superapp-misc.restaurants.fallback'


@pytest.mark.experiments3(filename='exp3_superapp_availability.json')
@pytest.mark.translations(client_messages=CLIENT_MESSAGES_TRANSLATIONS)
@pytest.mark.parametrize('fallback_fired', [True, False])
@pytest.mark.parametrize(
    'available, deathflag, expected_available',
    [(True, False, True), (False, False, False), (True, True, False)],
)
async def test_restaurants_availability(
        taxi_superapp_misc,
        add_experiment,
        statistics,
        deathflag,
        available,
        expected_available,
        fallback_fired,
):
    add_experiment(
        name='superapp_restaurants_availability',
        value={
            'deathflag': deathflag,
            'enabled': available,
            'show_disabled': False,
        },
    )
    request = helpers.build_payload()

    if fallback_fired:
        statistics.fallbacks = [FALLBACK_NAME]
        await taxi_superapp_misc.invalidate_caches()

    response = await taxi_superapp_misc.post(
        consts.URL, request, headers={'X-YaTaxi-UserId': 'user_id'},
    )
    assert response.status_code == 200
    restaurants_mode = helpers.build_mode(
        'restaurants',
        available=expected_available and not fallback_fired,
        deathflag=deathflag,
        show_disabled=False,
    )
    assert restaurants_mode in response.json()['modes']
