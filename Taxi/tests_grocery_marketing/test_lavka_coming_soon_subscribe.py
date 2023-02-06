import pytest

from tests_grocery_marketing import common
from tests_grocery_marketing import models


DEPOT_ID = '40562'


@pytest.mark.parametrize(
    'phone_number, phone_normalized, personal_phone_id, times_called',
    [
        pytest.param(
            '8(999)123-42-12',
            '+79991234212',
            'personal-phone-id-123',
            1,
            id='with phone',
        ),
        pytest.param(None, None, None, 0, id='without phone'),
    ],
)
@pytest.mark.parametrize(
    'subscribe',
    (
        pytest.param(True, id='subscribed'),
        pytest.param(False, id='not subscribed'),
    ),
)
@pytest.mark.parametrize(
    'depot_id,depot_not_found',
    (
        pytest.param(None, False, id='without depot but with overlord'),
        pytest.param(None, True, id='without depot and overlord'),
        pytest.param(DEPOT_ID, False, id='with depot'),
    ),
)
async def test_basic(
        taxi_grocery_marketing,
        pgsql,
        grocery_depots,
        subscribe,
        personal,
        phone_number,
        phone_normalized,
        personal_phone_id,
        times_called,
        depot_id,
        depot_not_found,
):
    region_id = 2

    depot = grocery_depots.add_depot(depot_test_id=1, legacy_depot_id=DEPOT_ID)
    personal.check_request(
        phone=phone_normalized, personal_phone_id=personal_phone_id,
    )

    if depot_not_found:
        lat = 59.91
        lon = 30.37
    else:
        lat = depot.location['lat']
        lon = depot.location['lon']

    location = [lon, lat]

    response = await taxi_grocery_marketing.post(
        '/lavka/v1/marketing/v1/coming-soon/subscribe',
        json={
            'position': {'location': location, 'depot_id': depot_id},
            'subscribe': subscribe,
            'phone_number': phone_number,
        },
        headers=common.DEFAULT_USER_HEADERS,
    )

    assert response.status_code == 200

    assert personal.times_phones_store_called() == times_called

    subscription = models.ComingSoonSubscription.fetch(
        pgsql, common.SESSION, lat, lon,
    )

    assert subscription.session == common.SESSION
    assert not subscription.notified
    assert subscription.subscribe == subscribe
    assert subscription.yandex_uid == common.YANDEX_UID
    assert subscription.raw_auth_context is not None
    assert subscription.personal_phone_id == personal_phone_id
    if depot_not_found:
        assert subscription.region_id == region_id
        assert not subscription.depot_id_subscribed
    else:
        assert subscription.depot_id_subscribed == DEPOT_ID
