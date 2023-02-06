from tests_grocery_marketing import common
from tests_grocery_marketing import models


async def test_basic(taxi_grocery_marketing, pgsql, grocery_depots):
    depot_id = '40562'
    lat = 59.91
    lon = 30.37
    location = [lon, lat]

    grocery_depots.add_depot(depot_test_id=1, legacy_depot_id=depot_id)

    response = await taxi_grocery_marketing.post(
        '/lavka/v1/marketing/v1/coming-soon/subscribe',
        json={
            'position': {'location': location, 'depot_id': depot_id},
            'subscribe': True,
        },
        headers=common.DEFAULT_USER_HEADERS,
    )

    assert response.status_code == 200

    subscription = models.ComingSoonSubscription.fetch(
        pgsql, common.SESSION, lat, lon,
    )

    assert subscription.session == common.SESSION
    assert not subscription.notified
    assert subscription.subscribe
    assert subscription.yandex_uid == common.YANDEX_UID

    current_yandex_uid = 'some_new_yandex_uid'
    current_session = 'some_new_sessison'

    response = await taxi_grocery_marketing.post(
        '/internal/v1/marketing/v1/coming-soon/update-subscription',
        json={
            'old_yandex_uids': ['some_yandex_uid', common.YANDEX_UID],
            'old_sessions': [common.SESSION, 'some_session'],
            'current_yandex_uid': current_yandex_uid,
            'current_session': current_session,
        },
        headers=common.DEFAULT_USER_HEADERS,
    )

    assert response.status_code == 200

    old_subscription = models.ComingSoonSubscription.fetch(
        pgsql, common.SESSION, lat, lon,
    )

    current_subscription = models.ComingSoonSubscription.fetch(
        pgsql, current_session, lat, lon,
    )

    assert old_subscription.session == common.SESSION
    assert not old_subscription.notified
    assert old_subscription.subscribe
    assert old_subscription.yandex_uid == common.YANDEX_UID

    assert current_subscription.session == current_session
    assert not current_subscription.notified
    assert current_subscription.subscribe
    assert current_subscription.yandex_uid == current_yandex_uid
