# flake8: noqa
# pylint: disable=import-error,wildcard-import

import json
import pytest


async def request_proxy_update(
        taxi_eats_restapp_places, data, patner_id, place_id,
):
    url = '/4.0/restapp-front/places/v1/update?place_id={}'.format(place_id)

    headers = {
        'X-YaEda-PartnerId': str(patner_id),
        'Content-type': 'application/json',
    }
    extra = {'headers': headers}

    return await taxi_eats_restapp_places.patch(
        url, data=json.dumps(data), **extra,
    )


async def test_multi_update(
        taxi_eats_restapp_places,
        taxi_eats_restapp_places_monitor,
        get_count_by_place,
        get_count_by_partner,
        mocked_time,
        mock_restapp_authorizer,
        mock_eats_core_update_201_data,
        mock_eats_core_update_data_43,
        mock_eats_core_update_data_44,
):
    await taxi_eats_restapp_places.run_periodic_task('update_rates_task')

    data = {
        'name': 'place-name',
        'address': {'city': 'Moscow', 'address': 'Льва Толстого 16'},
        'phones': [{'type': 'official', 'number': '+78005553535'}],
        'emails': [{'type': 'main', 'address': 'admin@admin.com'}],
        'payment_methods': ['cash', 'card'],
        'comments': [{'type': 'client', 'text': 'its good'}],
    }
    partner_id = 1
    place_id = 42

    response = await request_proxy_update(
        taxi_eats_restapp_places, data, partner_id, place_id,
    )

    assert response.status_code == 201

    partner_id = 2
    place_id = 42

    response = await request_proxy_update(
        taxi_eats_restapp_places, data, partner_id, place_id,
    )

    assert response.status_code == 201

    partner_id = 3
    place_id = 43

    response = await request_proxy_update(
        taxi_eats_restapp_places, data, partner_id, place_id,
    )

    assert response.status_code == 201

    partner_id = 3
    place_id = 44

    response = await request_proxy_update(
        taxi_eats_restapp_places, data, partner_id, place_id,
    )

    assert response.status_code == 201

    rates_by_place = get_count_by_place(42)
    assert rates_by_place[1] == 2
    assert rates_by_place[2] == 2
    assert rates_by_place[3] == 2
    assert rates_by_place[4] == 2
    assert rates_by_place[5] == 2
    assert rates_by_place[6] == 2
    rates_by_place = get_count_by_place(43)
    assert rates_by_place[1] == 1
    assert rates_by_place[2] == 1
    assert rates_by_place[3] == 1
    assert rates_by_place[4] == 1
    assert rates_by_place[5] == 1
    assert rates_by_place[6] == 1
    rates_by_place = get_count_by_place(44)
    assert rates_by_place[1] == 1
    assert rates_by_place[2] == 1
    assert rates_by_place[3] == 1
    assert rates_by_place[4] == 1
    assert rates_by_place[5] == 1
    assert rates_by_place[6] == 1

    rates_by_partner = get_count_by_partner(1)
    assert rates_by_partner[1] == 1
    assert rates_by_partner[2] == 1
    assert rates_by_partner[3] == 1
    assert rates_by_partner[4] == 1
    assert rates_by_partner[5] == 1
    assert rates_by_partner[6] == 1
    rates_by_partner = get_count_by_partner(2)
    assert rates_by_partner[1] == 1
    assert rates_by_partner[2] == 1
    assert rates_by_partner[3] == 1
    assert rates_by_partner[4] == 1
    assert rates_by_partner[5] == 1
    assert rates_by_partner[6] == 1
    rates_by_partner = get_count_by_partner(3)
    assert rates_by_partner[1] == 2
    assert rates_by_partner[2] == 2
    assert rates_by_partner[3] == 2
    assert rates_by_partner[4] == 2
    assert rates_by_partner[5] == 2
    assert rates_by_partner[6] == 2

    mocked_time.sleep(86402)
    await taxi_eats_restapp_places.invalidate_caches()

    await taxi_eats_restapp_places.run_periodic_task('update_rates_task')

    metrics = await taxi_eats_restapp_places_monitor.get_metrics()

    assert metrics['update-rates-avg-statistics'] == {
        'update_address_rate_by_place': {'avg': 1, 'max': 2, 'min': 1},
        'update_address_rate_by_user': {'avg': 1, 'max': 2, 'min': 1},
        'update_comments_rate_by_place': {'avg': 1, 'max': 2, 'min': 1},
        'update_comments_rate_by_user': {'avg': 1, 'max': 2, 'min': 1},
        'update_emails_rate_by_place': {'avg': 1, 'max': 2, 'min': 1},
        'update_emails_rate_by_user': {'avg': 1, 'max': 2, 'min': 1},
        'update_name_rate_by_place': {'avg': 1, 'max': 2, 'min': 1},
        'update_name_rate_by_user': {'avg': 1, 'max': 2, 'min': 1},
        'update_payment_methods_rate_by_place': {'avg': 1, 'max': 2, 'min': 1},
        'update_payment_methods_rate_by_user': {'avg': 1, 'max': 2, 'min': 1},
        'update_phones_rate_by_place': {'avg': 1, 'max': 2, 'min': 1},
        'update_phones_rate_by_user': {'avg': 1, 'max': 2, 'min': 1},
        'update_rate_by_place': {'avg': 8, 'max': 12, 'min': 6},
        'update_rate_by_user': {'avg': 8, 'max': 12, 'min': 6},
    }

    assert metrics['update-rates-global-statistics'] == {
        'place_update_address_rate': 4,
        'place_update_comments_rate': 4,
        'place_update_emails_rate': 4,
        'place_update_name_rate': 4,
        'place_update_payment_methods_rate': 4,
        'place_update_phones_rate': 4,
        'place_update_rate': 24,
    }


async def test_multi_update_single_place(
        taxi_eats_restapp_places,
        taxi_eats_restapp_places_monitor,
        get_count_by_place,
        get_count_by_partner,
        mocked_time,
        mock_restapp_authorizer,
        mock_eats_core_update_any_data,
):
    data = {'name': 'place-name'}
    partner_id = 1
    place_id = 42

    response = await request_proxy_update(
        taxi_eats_restapp_places, data, partner_id, place_id,
    )

    assert response.status_code == 201

    data = {'address': {'city': 'Moscow', 'address': 'Льва Толстого 16'}}

    response = await request_proxy_update(
        taxi_eats_restapp_places, data, partner_id, place_id,
    )

    assert response.status_code == 201

    data = {'phones': [{'type': 'official', 'number': '+78005553535'}]}

    response = await request_proxy_update(
        taxi_eats_restapp_places, data, partner_id, place_id,
    )

    assert response.status_code == 201

    data = {'emails': [{'type': 'main', 'address': 'admin@admin.com'}]}

    response = await request_proxy_update(
        taxi_eats_restapp_places, data, partner_id, place_id,
    )

    assert response.status_code == 201

    data = {'payment_methods': ['cash', 'card']}

    response = await request_proxy_update(
        taxi_eats_restapp_places, data, partner_id, place_id,
    )

    assert response.status_code == 201

    data = {'comments': [{'type': 'client', 'text': 'its good'}]}

    response = await request_proxy_update(
        taxi_eats_restapp_places, data, partner_id, place_id,
    )

    assert response.status_code == 201

    rates_by_place = get_count_by_place(42)
    assert rates_by_place[1] == 1
    assert rates_by_place[2] == 1
    assert rates_by_place[3] == 1
    assert rates_by_place[4] == 1
    assert rates_by_place[5] == 1
    assert rates_by_place[6] == 1

    rates_by_partner = get_count_by_partner(1)
    assert rates_by_partner[1] == 1
    assert rates_by_partner[2] == 1
    assert rates_by_partner[3] == 1
    assert rates_by_partner[4] == 1
    assert rates_by_partner[5] == 1
    assert rates_by_partner[6] == 1

    await taxi_eats_restapp_places.run_periodic_task('update_rates_task')

    metrics = await taxi_eats_restapp_places_monitor.get_metrics()

    assert metrics['update-rates-global-statistics'] == {
        'place_update_address_rate': 5,
        'place_update_comments_rate': 5,
        'place_update_emails_rate': 5,
        'place_update_name_rate': 5,
        'place_update_payment_methods_rate': 5,
        'place_update_phones_rate': 5,
        'place_update_rate': 30,
    }

    assert metrics['update-rates-avg-statistics'] == {
        'update_address_rate_by_place': {'avg': 1, 'max': 1, 'min': 1},
        'update_address_rate_by_user': {'avg': 1, 'max': 1, 'min': 1},
        'update_comments_rate_by_place': {'avg': 1, 'max': 1, 'min': 1},
        'update_comments_rate_by_user': {'avg': 1, 'max': 1, 'min': 1},
        'update_emails_rate_by_place': {'avg': 1, 'max': 1, 'min': 1},
        'update_emails_rate_by_user': {'avg': 1, 'max': 1, 'min': 1},
        'update_name_rate_by_place': {'avg': 1, 'max': 1, 'min': 1},
        'update_name_rate_by_user': {'avg': 1, 'max': 1, 'min': 1},
        'update_payment_methods_rate_by_place': {'avg': 1, 'max': 1, 'min': 1},
        'update_payment_methods_rate_by_user': {'avg': 1, 'max': 1, 'min': 1},
        'update_phones_rate_by_place': {'avg': 1, 'max': 1, 'min': 1},
        'update_phones_rate_by_user': {'avg': 1, 'max': 1, 'min': 1},
        'update_rate_by_place': {'avg': 6, 'max': 6, 'min': 6},
        'update_rate_by_user': {'avg': 6, 'max': 6, 'min': 6},
    }
