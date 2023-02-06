# flake8: noqa
# pylint: disable=import-error,wildcard-import

from eats_restapp_places_plugins.generated_tests import *

# Feel free to provide your custom implementation to override generated tests.
import json
import pytest

ZERO_METRIC = {
    'update_address_rate_by_place': {'avg': 0, 'max': 0, 'min': 0},
    'update_address_rate_by_user': {'avg': 0, 'max': 0, 'min': 0},
    'update_comments_rate_by_place': {'avg': 0, 'max': 0, 'min': 0},
    'update_comments_rate_by_user': {'avg': 0, 'max': 0, 'min': 0},
    'update_emails_rate_by_place': {'avg': 0, 'max': 0, 'min': 0},
    'update_emails_rate_by_user': {'avg': 0, 'max': 0, 'min': 0},
    'update_name_rate_by_place': {'avg': 0, 'max': 0, 'min': 0},
    'update_name_rate_by_user': {'avg': 0, 'max': 0, 'min': 0},
    'update_payment_methods_rate_by_place': {'avg': 0, 'max': 0, 'min': 0},
    'update_payment_methods_rate_by_user': {'avg': 0, 'max': 0, 'min': 0},
    'update_phones_rate_by_place': {'avg': 0, 'max': 0, 'min': 0},
    'update_phones_rate_by_user': {'avg': 0, 'max': 0, 'min': 0},
    'update_rate_by_place': {'avg': 0, 'max': 0, 'min': 0},
    'update_rate_by_user': {'avg': 0, 'max': 0, 'min': 0},
}

START_GLOBAL_METRIC = {
    'place_update_address_rate': 5,
    'place_update_comments_rate': 5,
    'place_update_emails_rate': 5,
    'place_update_name_rate': 5,
    'place_update_payment_methods_rate': 5,
    'place_update_phones_rate': 5,
    'place_update_rate': 30,
}

UPDATE_GLOBAL_METRIC = {
    'place_update_address_rate': 6,
    'place_update_comments_rate': 6,
    'place_update_emails_rate': 6,
    'place_update_name_rate': 6,
    'place_update_payment_methods_rate': 6,
    'place_update_phones_rate': 6,
    'place_update_rate': 36,
}

UPDATE_GLOBAL_METRIC_AFTER_BEL = {
    'place_update_address_rate': 7,
    'place_update_comments_rate': 7,
    'place_update_emails_rate': 7,
    'place_update_name_rate': 7,
    'place_update_payment_methods_rate': 7,
    'place_update_phones_rate': 7,
    'place_update_rate': 42,
}


async def request_proxy_update_schedule(
        taxi_eats_restapp_places, data, patner_id,
):
    url = '/4.0/restapp-front/places/v1/update-schedule'

    headers = {
        'X-YaEda-PartnerId': str(patner_id),
        'Content-type': 'application/json',
    }
    extra = {'headers': headers}

    return await taxi_eats_restapp_places.post(
        url, data=json.dumps(data), **extra,
    )


async def test_update_schedule(
        taxi_eats_restapp_places,
        mock_authorizer_allowed,
        mock_eats_core,
        mock_restapp_authorizer,
):
    data = {
        'intervals': [{'day': 1, 'from': 480, 'to': 960}],
        'place_ids': [41, 43],
    }
    partner_id = 1
    response = await request_proxy_update_schedule(
        taxi_eats_restapp_places, data, partner_id,
    )
    assert response.status_code == 204


async def test_wrong_places_update_schedule(
        taxi_eats_restapp_places,
        mock_authorizer_allowed,
        mock_eats_core,
        mock_restapp_authorizer_403,
):
    data = {
        'intervals': [{'day': 1, 'from': 480, 'to': 960}],
        'place_ids': [41, 44],
    }
    partner_id = 1
    response = await request_proxy_update_schedule(
        taxi_eats_restapp_places, data, partner_id,
    )
    assert response.status_code == 403
    assert response.json()['code'] == '403'
    assert (
        response.json()['message']
        == 'Error: no access to the place or no permissions'
    )


async def test_wrong_params_update_schedule(
        taxi_eats_restapp_places, mock_authorizer_allowed, mock_eats_core,
):
    data = {
        'intervals': [{'day': 145, 'from': 480, 'to': 960}],
        'place_ids': [41, 43],
    }
    partner_id = 1
    response = await request_proxy_update_schedule(
        taxi_eats_restapp_places, data, partner_id,
    )
    assert response.status_code == 400


async def test_core_500_update_schedule(
        taxi_eats_restapp_places,
        mock_authorizer_allowed,
        mock_eats_core_500,
        mock_restapp_authorizer,
):
    data = {
        'intervals': [{'day': 1, 'from': 480, 'to': 960}],
        'place_ids': [41, 43],
    }
    partner_id = 1
    response = await request_proxy_update_schedule(
        taxi_eats_restapp_places, data, partner_id,
    )
    assert response.status_code == 500
    assert response.json()['code'] == '500'
    assert response.json()['message'] == 'Internal Server Error'


async def test_core_404_update_schedule(
        taxi_eats_restapp_places,
        mock_authorizer_allowed,
        mock_eats_core_404,
        mock_restapp_authorizer,
):
    data = {
        'intervals': [{'day': 1, 'from': 480, 'to': 960}],
        'place_ids': [41, 43],
    }
    partner_id = 1
    response = await request_proxy_update_schedule(
        taxi_eats_restapp_places, data, partner_id,
    )
    assert response.status_code == 404
    assert response.json()['code'] == '404'
    assert response.json()['message'] == 'places not found'


async def test_authorizer_error_update_schedule(
        taxi_eats_restapp_places,
        mock_eats_core,
        mock_authorizer_500,
        mock_restapp_authorizer_400,
):
    data = {
        'intervals': [{'day': 1, 'from': 480, 'to': 960}],
        'place_ids': [41, 43],
    }
    partner_id = 1
    response = await request_proxy_update_schedule(
        taxi_eats_restapp_places, data, partner_id,
    )
    assert response.status_code == 400
    assert response.json()['code'] == '400'
    assert response.json()['message'] == 'Error: unable to authorize'


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


async def test_empty_update(
        taxi_eats_restapp_places,
        taxi_eats_restapp_places_monitor,
        get_count_by_place,
        get_count_by_partner,
        mock_authorizer_allowed,
        mock_eats_core_update_201,
        mock_restapp_authorizer,
):
    data = {}
    partner_id = 1
    place_id = 42
    response = await request_proxy_update(
        taxi_eats_restapp_places, data, partner_id, place_id,
    )

    rates_by_place = get_count_by_place(place_id)
    assert rates_by_place[1] == 0
    assert rates_by_place[2] == 0
    assert rates_by_place[3] == 0
    assert rates_by_place[4] == 0
    assert rates_by_place[5] == 0
    assert rates_by_place[6] == 0

    rates_by_partner = get_count_by_partner(partner_id)
    assert rates_by_partner[1] == 0
    assert rates_by_partner[2] == 0
    assert rates_by_partner[3] == 0
    assert rates_by_partner[4] == 0
    assert rates_by_partner[5] == 0
    assert rates_by_partner[6] == 0

    assert response.status_code == 201

    await taxi_eats_restapp_places.run_periodic_task('update_rates_task')

    metrics = await taxi_eats_restapp_places_monitor.get_metrics()

    assert metrics['update-rates-avg-statistics'] == ZERO_METRIC
    assert metrics['update-rates-global-statistics'] == START_GLOBAL_METRIC


async def test_authorizer_error_update(
        taxi_eats_restapp_places,
        taxi_eats_restapp_places_monitor,
        get_count_by_place,
        get_count_by_partner,
        mock_authorizer_500,
        mock_eats_core_update_201,
        mock_restapp_authorizer_400,
):
    data = {}
    partner_id = 1
    place_id = 42
    response = await request_proxy_update(
        taxi_eats_restapp_places, data, partner_id, place_id,
    )
    rates_by_place = get_count_by_place(place_id)
    assert rates_by_place is None

    rates_by_partner = get_count_by_partner(partner_id)
    assert rates_by_partner is None

    assert response.status_code == 400
    assert response.json()['message'] == 'Error: unable to authorize'

    await taxi_eats_restapp_places.run_periodic_task('update_rates_task')

    metrics = await taxi_eats_restapp_places_monitor.get_metrics()

    assert metrics['update-rates-avg-statistics'] == ZERO_METRIC
    assert metrics['update-rates-global-statistics'] == START_GLOBAL_METRIC


async def test_wrong_place_update(
        taxi_eats_restapp_places,
        taxi_eats_restapp_places_monitor,
        get_count_by_place,
        get_count_by_partner,
        mock_authorizer_allowed,
        mock_eats_core_update_201,
        mock_restapp_authorizer_403,
):
    data = {}
    partner_id = 1
    place_id = 45
    response = await request_proxy_update(
        taxi_eats_restapp_places, data, partner_id, place_id,
    )
    rates_by_place = get_count_by_place(place_id)
    assert rates_by_place is None

    rates_by_partner = get_count_by_partner(partner_id)
    assert rates_by_partner is None

    assert response.status_code == 403
    assert response.json()['code'] == '403'
    assert (
        response.json()['message']
        == 'Error: no access to the place or no permissions'
    )

    await taxi_eats_restapp_places.run_periodic_task('update_rates_task')

    metrics = await taxi_eats_restapp_places_monitor.get_metrics()

    assert metrics['update-rates-avg-statistics'] == ZERO_METRIC
    assert metrics['update-rates-global-statistics'] == START_GLOBAL_METRIC


async def test_update(
        taxi_eats_restapp_places,
        taxi_eats_restapp_places_monitor,
        get_count_by_place,
        get_count_by_partner,
        mock_authorizer_allowed,
        mock_eats_core_update_201_data,
        mock_restapp_authorizer,
):
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

    rates_by_place = get_count_by_place(place_id)
    assert rates_by_place[1] == 1
    assert rates_by_place[2] == 1
    assert rates_by_place[3] == 1
    assert rates_by_place[4] == 1
    assert rates_by_place[5] == 1
    assert rates_by_place[6] == 1

    rates_by_partner = get_count_by_partner(partner_id)
    assert rates_by_partner[1] == 1
    assert rates_by_partner[2] == 1
    assert rates_by_partner[3] == 1
    assert rates_by_partner[4] == 1
    assert rates_by_partner[5] == 1
    assert rates_by_partner[6] == 1

    assert response.status_code == 201

    await taxi_eats_restapp_places.run_periodic_task('update_rates_task')

    metrics = await taxi_eats_restapp_places_monitor.get_metrics()

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
    assert metrics['update-rates-global-statistics'] == UPDATE_GLOBAL_METRIC


async def test_update_belarus_phone(
        taxi_eats_restapp_places,
        mock_authorizer_allowed,
        mock_eats_core_update_201_bel,
        mock_restapp_authorizer,
):
    data = {
        'name': 'place-name',
        'address': {'city': 'Минск', 'address': 'Максима Богдановича 16'},
        'phones': [{'type': 'official', 'number': '+375291234567'}],
        'emails': [{'type': 'main', 'address': 'admin@admin.com'}],
        'payment_methods': ['cash', 'card'],
        'comments': [{'type': 'client', 'text': 'its good'}],
    }
    partner_id = 1
    place_id = 42

    await request_proxy_update(
        taxi_eats_restapp_places, data, partner_id, place_id,
    )


async def test_wrong_value_update(
        taxi_eats_restapp_places,
        taxi_eats_restapp_places_monitor,
        get_count_by_place,
        get_count_by_partner,
        mock_authorizer_allowed,
        mock_eats_core_update_201,
):
    data = {'phones': [{'type': 'not_official', 'number': '+78005553535'}]}
    partner_id = 1
    place_id = 42
    response = await request_proxy_update(
        taxi_eats_restapp_places, data, partner_id, place_id,
    )
    rates_by_place = get_count_by_place(place_id)
    assert rates_by_place is None

    rates_by_partner = get_count_by_partner(partner_id)
    assert rates_by_partner is None

    assert response.status_code == 400
    assert response.json()['code'] == '400'

    await taxi_eats_restapp_places.run_periodic_task('update_rates_task')

    metrics = await taxi_eats_restapp_places_monitor.get_metrics()

    assert metrics['update-rates-avg-statistics'] == ZERO_METRIC
    assert (
        metrics['update-rates-global-statistics']
        == UPDATE_GLOBAL_METRIC_AFTER_BEL
    )


async def test_core_404_update(
        taxi_eats_restapp_places,
        taxi_eats_restapp_places_monitor,
        get_count_by_place,
        get_count_by_partner,
        mock_authorizer_allowed,
        mock_eats_core_update_404,
        mock_restapp_authorizer,
):
    data = {}
    partner_id = 1
    place_id = 42
    response = await request_proxy_update(
        taxi_eats_restapp_places, data, partner_id, place_id,
    )
    rates_by_place = get_count_by_place(place_id)
    assert rates_by_place is None

    rates_by_partner = get_count_by_partner(partner_id)
    assert rates_by_partner is None

    assert response.status_code == 404
    assert response.json()['code'] == '404'
    assert response.json()['message'] == 'Ресторан не найден'

    await taxi_eats_restapp_places.run_periodic_task('update_rates_task')

    metrics = await taxi_eats_restapp_places_monitor.get_metrics()

    assert metrics['update-rates-avg-statistics'] == ZERO_METRIC
    assert (
        metrics['update-rates-global-statistics']
        == UPDATE_GLOBAL_METRIC_AFTER_BEL
    )


async def test_core_400_update(
        taxi_eats_restapp_places,
        taxi_eats_restapp_places_monitor,
        get_count_by_place,
        get_count_by_partner,
        mock_authorizer_allowed,
        mock_eats_core_update_400,
        mock_restapp_authorizer,
):
    data = {}
    partner_id = 1
    place_id = 42
    response = await request_proxy_update(
        taxi_eats_restapp_places, data, partner_id, place_id,
    )
    rates_by_place = get_count_by_place(place_id)
    assert rates_by_place is None

    rates_by_partner = get_count_by_partner(partner_id)
    assert rates_by_partner is None

    assert response.status_code == 400
    assert response.json()['code'] == '400'
    assert response.json()['details']['errors'][0]['name'] == 'address'
    assert (
        response.json()['details']['errors'][0]['error']
        == 'адрес не существует'
    )

    await taxi_eats_restapp_places.run_periodic_task('update_rates_task')

    metrics = await taxi_eats_restapp_places_monitor.get_metrics()

    assert metrics['update-rates-avg-statistics'] == ZERO_METRIC
    assert (
        metrics['update-rates-global-statistics']
        == UPDATE_GLOBAL_METRIC_AFTER_BEL
    )


async def test_core_validation_400_update(
        taxi_eats_restapp_places,
        taxi_eats_restapp_places_monitor,
        get_count_by_place,
        get_count_by_partner,
        mock_authorizer_allowed,
        mock_eats_core_update400invald,
        mock_restapp_authorizer,
):
    data = {}
    partner_id = 1
    place_id = 43
    response = await request_proxy_update(
        taxi_eats_restapp_places, data, partner_id, place_id,
    )
    rates_by_place = get_count_by_place(place_id)
    assert rates_by_place is None

    rates_by_partner = get_count_by_partner(partner_id)
    assert rates_by_partner is None

    assert response.status_code == 400
    assert response.json()['message'] == 'Request format is invalid'

    await taxi_eats_restapp_places.run_periodic_task('update_rates_task')

    metrics = await taxi_eats_restapp_places_monitor.get_metrics()

    assert metrics['update-rates-avg-statistics'] == ZERO_METRIC
    assert (
        metrics['update-rates-global-statistics']
        == UPDATE_GLOBAL_METRIC_AFTER_BEL
    )


async def request_proxy_service_schedule(
        taxi_eats_restapp_places, patner_id, place_id,
):
    url = '/4.0/restapp-front/places/v1/service-schedule?place_id={}'.format(
        place_id,
    )

    headers = {
        'X-YaEda-PartnerId': str(patner_id),
        'Content-type': 'application/json',
        'placeId': str(place_id),
    }
    extra = {'headers': headers}

    return await taxi_eats_restapp_places.get(url, **extra)


async def test_service_schedule(
        taxi_eats_restapp_places,
        mock_authorizer_allowed,
        mock_eats_service_schedule,
):
    place_id = 42
    partner_id = 1
    response = await request_proxy_service_schedule(
        taxi_eats_restapp_places, partner_id, place_id,
    )
    assert response.status_code == 200

    assert len(response.json()['default']) == 1
    assert response.json()['default'][0]['day'] == 1
    assert response.json()['default'][0]['from'] == 480
    assert response.json()['default'][0]['to'] == 540

    assert len(response.json()['redefined']) == 1
    assert response.json()['redefined'][0]['date'] == '2020-09-24'
    assert response.json()['redefined'][0]['from'] == 480
    assert response.json()['redefined'][0]['to'] == 960


async def test_service_schedule_400(
        taxi_eats_restapp_places,
        mock_authorizer_400,
        mock_eats_service_schedule,
):
    place_id = 'Nan'
    partner_id = 1
    response = await request_proxy_service_schedule(
        taxi_eats_restapp_places, partner_id, place_id,
    )
    assert response.status_code == 400


async def test_service_schedule_403(
        taxi_eats_restapp_places,
        mock_authorizer_forbidden,
        mock_eats_service_schedule,
):
    place_id = 47
    partner_id = 1
    response = await request_proxy_service_schedule(
        taxi_eats_restapp_places, partner_id, place_id,
    )
    assert response.status_code == 403


async def test_service_schedule_404(
        taxi_eats_restapp_places,
        mock_authorizer_allowed,
        mock_eats_service_schedule,
):
    place_id = 43
    partner_id = 1
    response = await request_proxy_service_schedule(
        taxi_eats_restapp_places, partner_id, place_id,
    )
    assert response.status_code == 404


async def request_get_redefined_schedule(
        taxi_eats_restapp_places, patner_id, place_id,
):
    url = (
        '/4.0/restapp-front/places/v1/schedule-redefined-dates?place_id={}'.format(
            place_id,
        )
    )

    headers = {
        'X-YaEda-PartnerId': str(patner_id),
        'Content-type': 'application/json',
        'placeId': str(place_id),
    }
    extra = {'headers': headers}

    return await taxi_eats_restapp_places.get(url, **extra)


async def test_get_redefined_schedule(
        taxi_eats_restapp_places,
        mock_authorizer_allowed,
        mock_eats_redefined_schedule,
):
    place_id = 42
    partner_id = 1
    response = await request_get_redefined_schedule(
        taxi_eats_restapp_places, partner_id, place_id,
    )
    assert response.status_code == 200

    assert len(response.json()['payload']) == 1
    assert response.json()['payload'][0]['date'] == '2020-09-24'
    assert response.json()['payload'][0]['from'] == 480
    assert response.json()['payload'][0]['to'] == 960


async def test_get_redefined_schedule_400(
        taxi_eats_restapp_places,
        mock_authorizer_allowed,
        mock_eats_redefined_schedule,
):
    place_id = 'Nan'
    partner_id = 1
    response = await request_get_redefined_schedule(
        taxi_eats_restapp_places, partner_id, place_id,
    )
    assert response.status_code == 400


async def test_get_redefined_schedule_403(
        taxi_eats_restapp_places,
        mock_authorizer_forbidden,
        mock_eats_redefined_schedule,
):
    place_id = 47
    partner_id = 1
    response = await request_get_redefined_schedule(
        taxi_eats_restapp_places, partner_id, place_id,
    )
    assert response.status_code == 403


async def test_get_redefined_schedule_404(
        taxi_eats_restapp_places,
        mock_authorizer_allowed,
        mock_eats_redefined_schedule,
):
    place_id = 43
    partner_id = 1
    response = await request_get_redefined_schedule(
        taxi_eats_restapp_places, partner_id, place_id,
    )
    assert response.status_code == 404


async def request_proxy_update_redefined(
        taxi_eats_restapp_places, data, patner_id, place_id,
):
    url = (
        '/4.0/restapp-front/places/v1/schedule-redefined-dates?place_id={}'.format(
            place_id,
        )
    )

    headers = {
        'X-YaEda-PartnerId': str(patner_id),
        'Content-type': 'application/json',
    }
    extra = {'headers': headers}

    return await taxi_eats_restapp_places.post(
        url, data=json.dumps(data), **extra,
    )


async def test_update_redefined_schedule(
        taxi_eats_restapp_places,
        mock_authorizer_allowed,
        mock_eats_redefined_update,
):
    data = {'intervals': [{'date': '2020-09-24', 'from': 480, 'to': 960}]}
    partner_id = 1
    place_id = 43
    response = await request_proxy_update_redefined(
        taxi_eats_restapp_places, data, partner_id, place_id,
    )
    assert response.status_code == 204


async def test_wrong_place_update_redefined(
        taxi_eats_restapp_places,
        mock_authorizer_forbidden,
        mock_eats_redefined_update,
):
    data = {'intervals': [{'date': '2020-09-24', 'from': 480, 'to': 960}]}
    partner_id = 1
    place_id = 44
    response = await request_proxy_update_redefined(
        taxi_eats_restapp_places, data, partner_id, place_id,
    )
    assert response.status_code == 403
    assert response.json()['code'] == '403'


async def test_wrong_params_update_redefined(
        taxi_eats_restapp_places,
        mock_authorizer_allowed,
        mock_eats_redefined_update,
):
    data = {'intervals': [{'date': '2020-09-42', 'from': 480, 'to': 960}]}
    partner_id = 1
    place_id = 'Nan'
    response = await request_proxy_update_redefined(
        taxi_eats_restapp_places, data, partner_id, place_id,
    )
    assert response.status_code == 400


async def test_core_500_update_redefined(
        taxi_eats_restapp_places,
        mock_authorizer_allowed,
        mock_eats_redefined_update_500,
):
    data = {'intervals': [{'date': '2020-09-24', 'from': 480, 'to': 960}]}
    partner_id = 1
    place_id = 43
    response = await request_proxy_update_redefined(
        taxi_eats_restapp_places, data, partner_id, place_id,
    )
    assert response.status_code == 500
    assert response.json()['code'] == '500'
    assert response.json()['message'] == 'Internal Server Error'


async def test_core_404_update_redefined(
        taxi_eats_restapp_places,
        mock_authorizer_allowed,
        mock_eats_redefined_update_404,
):
    data = {'intervals': [{'date': '2020-09-24', 'from': 480, 'to': 960}]}
    partner_id = 1
    place_id = 43
    response = await request_proxy_update_redefined(
        taxi_eats_restapp_places, data, partner_id, place_id,
    )
    assert response.status_code == 404
    assert response.json()['code'] == '404'
    assert response.json()['message'] == 'place id=43 not found'


async def test_vendor_error_update_redefined(
        taxi_eats_restapp_places,
        mock_authorizer_500,
        mock_eats_redefined_update,
):
    data = {'intervals': [{'date': '2020-09-24', 'from': 480, 'to': 960}]}
    partner_id = 1
    place_id = 43
    response = await request_proxy_update_redefined(
        taxi_eats_restapp_places, data, partner_id, place_id,
    )
    assert response.status_code == 500
    assert response.json()['code'] == '500'
    assert response.json()['message'] == 'Internal Server Error'


async def test_vendor_400_update_redefined(
        taxi_eats_restapp_places,
        mock_authorizer_400,
        mock_eats_redefined_update,
):
    data = {'intervals': [{'date': '2020-09-24', 'from': 480, 'to': 960}]}
    partner_id = 1
    place_id = 43
    response = await request_proxy_update_redefined(
        taxi_eats_restapp_places, data, partner_id, place_id,
    )
    assert response.status_code == 400
    assert response.json()['code'] == '400'
    assert response.json()['message'] == 'Пользователь не найден'


async def request_proxy_get_vat_list(taxi_eats_restapp_places, country):
    url = '/4.0/restapp-front/places/v1/vat-list?country={}'.format(country)

    headers = {'Content-type': 'application/json'}
    extra = {'headers': headers}

    return await taxi_eats_restapp_places.get(url, **extra)


@pytest.mark.config(
    EATS_RESTAPP_PLACES_CLIENT_VAT_LIST=[
        {
            'country': 'RUS',
            'values': [
                {'value': 10, 'description': '10%'},
                {'value': 20, 'description': '20%'},
            ],
        },
    ],
)
async def test_get_vat_list(
        taxi_eats_restapp_places, mock_authorizer_allowed, taxi_config,
):
    country = 'RUS'

    response = await request_proxy_get_vat_list(
        taxi_eats_restapp_places, country,
    )

    assert response.status_code == 200
    assert len(response.json()['values']) == 2
    assert response.json()['values'][0]['value'] == 10
    assert response.json()['values'][0]['description'] == '10%'
    assert response.json()['values'][1]['value'] == 20
    assert response.json()['values'][1]['description'] == '20%'


async def test_get_vat_list_404(
        taxi_eats_restapp_places, mock_authorizer_allowed,
):
    country = 'RUS'
    response = await request_proxy_get_vat_list(
        taxi_eats_restapp_places, country,
    )
    assert response.status_code == 404
    assert response.json()['code'] == '404'


async def request_proxy_get_schedule(
        taxi_eats_restapp_places, partner_id, place_id,
):
    url = '/4.0/restapp-front/places/v1/schedule?place_id={}'.format(place_id)

    headers = {
        'X-YaEda-PartnerId': str(partner_id),
        'Content-type': 'application/json',
    }
    extra = {'headers': headers}

    return await taxi_eats_restapp_places.get(url, **extra)


async def test_get_schedule(
        taxi_eats_restapp_places,
        mock_authorizer_allowed,
        mock_eats_get_schedule,
):
    partner_id = 1
    place_id = 43

    response = await request_proxy_get_schedule(
        taxi_eats_restapp_places, partner_id, place_id,
    )

    assert response.status_code == 200
    assert len(response.json()['intervals']) == 1
    assert response.json()['intervals'][0]['day'] == 1
    assert response.json()['intervals'][0]['from'] == 480
    assert response.json()['intervals'][0]['to'] == 540


async def test_get_schedule_400(
        taxi_eats_restapp_places,
        mock_authorizer_allowed,
        mock_eats_get_schedule,
):
    partner_id = 1
    place_id = 'Nan'

    response = await request_proxy_get_schedule(
        taxi_eats_restapp_places, partner_id, place_id,
    )

    assert response.status_code == 400
    assert response.json()['code'] == '400'


async def test_get_schedule_403(
        taxi_eats_restapp_places,
        mock_authorizer_forbidden,
        mock_eats_get_schedule,
):
    partner_id = 1
    place_id = 45

    response = await request_proxy_get_schedule(
        taxi_eats_restapp_places, partner_id, place_id,
    )

    assert response.status_code == 403
    assert response.json()['code'] == '403'


async def test_get_schedule_404(
        taxi_eats_restapp_places,
        mock_authorizer_allowed,
        mock_eats_get_schedule_404,
):
    partner_id = 1
    place_id = 42

    response = await request_proxy_get_schedule(
        taxi_eats_restapp_places, partner_id, place_id,
    )

    assert response.status_code == 404
    assert response.json()['code'] == '404'
