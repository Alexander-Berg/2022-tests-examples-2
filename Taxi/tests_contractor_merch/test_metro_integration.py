import datetime
import decimal

import pytest
import pytz

from tests_contractor_merch import util


ENDPOINT_GET_METRO_CARD = '/driver/v1/contractor-merch/v1/metro-card'
ENDPOINT_METRO_PURCHASE = '/driver/v1/contractor-merch/v1/purchase'
PARK_ID = 'park_id'
DRIVER_ID = 'driver_id'
HEADERS_GET_METRO_CARD = {
    'X-YaTaxi-Park-Id': PARK_ID,
    'X-YaTaxi-Driver-Profile-Id': DRIVER_ID,
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.50',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
}

HEADERS_METRO_PURCHASE = {'Accept-Language': 'en_GB', **HEADERS_GET_METRO_CARD}

TRANSLATIONS = {
    'error.offer_changed_or_expired.text': {
        'en': 'offer_changed_or_expired-tr',
    },
    'error.metro_price_incorrect.text': {'en': 'incorrect_metro_price'},
}

STQ_TRANSLATIONS = util.STQ_TRANSLATIONS

# Check in service.yaml file
SECRET_KEY = 'KEKING_ONLINE'

DATE_TIME = datetime.datetime(2002, 12, 8, 13, 37, 11, 0, pytz.UTC)
UNIXTIME = str(int(DATE_TIME.timestamp() * 1e6))
DATE_TIME_MOCK = DATE_TIME.strftime('%Y-%m-%dT%H:%M:%S%z')

REQUEST_TO_METRO_GET_CARD = {
    'ops': [
        {
            'type': 'create',
            'obj': 'task',
            'conv_id': 3460,
            'data': {
                'base': 'PProd',
                'phone': '89999999999',
                'email': 'chelovek_pavuk@yandex.ru',
                'birthDate': '10.08.2001',
                'name': 'Питер',
                'surname': 'Паркер',
            },
        },
    ],
}

BARCODE = '(255)4607070057079'


@pytest.mark.now(DATE_TIME_MOCK)
async def test_ok_get_card(
        taxi_contractor_merch,
        mock_driver_profiles,
        mock_personal,
        mock_metro_vouchers,
):
    mock_metro_vouchers.request = REQUEST_TO_METRO_GET_CARD
    mock_metro_vouchers.unixtime = UNIXTIME
    mock_metro_vouchers.secret_key = SECRET_KEY
    mock_metro_vouchers.check_signature = True

    response = await taxi_contractor_merch.get(
        ENDPOINT_GET_METRO_CARD, headers=HEADERS_GET_METRO_CARD,
    )

    assert mock_metro_vouchers.metro_endpoint.times_called == 1

    assert response.status == 200
    assert response.json() == {'barcode': BARCODE}


RESPONSE_FROM_METRO_NOT_FOUND_DISCOUNT_LINK = {'result': 'success'}

RESPONSE_FROM_METRO_RESULT_NOT_SUCCESS = {
    'result': 'failed',
    'barcode': f'{BARCODE}',
}


@pytest.mark.now(DATE_TIME_MOCK)
@pytest.mark.parametrize(
    'response_from_metro',
    [
        RESPONSE_FROM_METRO_NOT_FOUND_DISCOUNT_LINK,
        RESPONSE_FROM_METRO_RESULT_NOT_SUCCESS,
    ],
)
async def test_metro_failures_on_get_card(
        taxi_contractor_merch,
        mock_driver_profiles,
        mock_personal,
        mock_metro_vouchers,
        response_from_metro,
):
    mock_metro_vouchers.response = response_from_metro

    response = await taxi_contractor_merch.get(
        ENDPOINT_GET_METRO_CARD, headers=HEADERS_GET_METRO_CARD,
    )

    assert response.status == 500


@pytest.mark.translations(taximeter_backend_marketplace=STQ_TRANSLATIONS)
@pytest.mark.config(
    CONTRACTOR_MERCH_SUPPORTED_BARCODES={
        'gs1databarexpandedstacked': {
            'render_url_template': (
                'https://gs1databarexpandedstacked?barcode={promocode_number}'
            ),
            'url_text_tanker_key': (
                'notification_v1.success.linear_barcode_url_text'
            ),
        },
    },
)
@pytest.mark.parametrize(
    'full_name_driver_profiles,',
    [
        pytest.param({'full_name': {'last_name': 'Паркер'}}),
        pytest.param({'full_name': {'first_name': 'Питер'}}),
        pytest.param({}),
    ],
)
async def test_metro_get_card_failures_missing_driver_profiles_data(
        taxi_contractor_merch,
        mock_driver_profiles,
        mock_personal,
        mock_metro_vouchers,
        full_name_driver_profiles,
):
    resp_driver_profiles_template = {
        'profiles': [
            {
                'data': {
                    # 'full_name': {
                    #     'first_name': 'Питер',
                    #     'last_name': 'Паркер',
                    # },
                    'license_driver_birth_date': '2001-08-10T00:00:00.000',
                    'license': {'pd_id': 'license_pd_id_private'},
                    'email_pd_ids': [{'pd_id': 'email_pd_id_private'}],
                    'phone_pd_ids': [{'pd_id': 'phone_pd_id_private'}],
                },
            },
        ],
    }

    resp_driver_profiles_template['profiles'][0]['data'].update(
        full_name_driver_profiles,
    )
    mock_driver_profiles.response = resp_driver_profiles_template

    response = await taxi_contractor_merch.get(
        ENDPOINT_GET_METRO_CARD, headers=HEADERS_GET_METRO_CARD,
    )

    assert response.status == 500


async def test_metro_purchase_ok(
        taxi_contractor_merch,
        stq,
        # mocks from driver purchase
        mock_billing_replication,
        mock_driver_tags,
        mock_feeds,
        mock_fleet_parks,
        mock_parks_replica,
):
    idempotency_token = 'aaa'
    offer_id = 'feed-id-1'

    response = await taxi_contractor_merch.post(
        ENDPOINT_METRO_PURCHASE,
        headers={
            'Accept-Language': 'en',
            'X-Idempotency-Token': idempotency_token,
            **HEADERS_METRO_PURCHASE,
        },
        json={'offer_id': offer_id, 'price': '100'},
    )

    assert response.json() == {'purchase_id': idempotency_token}
    assert response.status == 200

    assert stq.contractor_merch_purchase.has_calls
    task = stq.contractor_merch_purchase.next_call()
    assert task['id'] == f'{PARK_ID}_{DRIVER_ID}_{idempotency_token}'
    assert task['args'] == []
    kwargs = task['kwargs']
    assert kwargs['driver_id'] == 'driver_id'
    assert kwargs['park_id'] == 'park_id'
    assert kwargs['feed_id'] == offer_id
    assert kwargs['idempotency_token'] == idempotency_token
    assert kwargs['feed_payload'] == {
        'feeds_admin_id': 'feeds-admin-id-1',
        'category': 'tire',
        'balance_payment': True,
        'title': 'Оплата в Metro',
        'name': 'RRRR',
        'partner': {'name': 'Metro'},
        'meta_info': {
            'display_on_main_screen': True,
            'daily_per_driver_limit': 1,
            'total_per_driver_limit': 2,
            'total_per_unique_driver_limit': 3,
            'metro_price_choice': {
                'max_price': 5000,
                'min_price': 100,
                'step': 100,
            },
            'barcode_params': {
                'is_send_enabled': True,
                'type': 'gs1databarexpandedstacked',
            },
        },
        'imageUrl': 'yandex.ru',
        'categories': ['tire'],
        'actions': [
            {'data': 'https://media.5ka.ru/', 'text': 'Медиа', 'type': 'link'},
        ],
        'place_id': 1,
        'offer_id': 'metric',
    }


@pytest.mark.translations(taximeter_backend_marketplace=TRANSLATIONS)
async def test_metro_purchase_failures(
        taxi_contractor_merch,
        stq,
        # mocks from driver purchase
        mock_billing_replication,
        mock_driver_tags,
        mock_feeds,
        mock_fleet_parks,
        mock_parks_replica,
):
    idempotency_token = 'aaa'
    offer_id = 'feed-id-1'

    response = await taxi_contractor_merch.post(
        ENDPOINT_METRO_PURCHASE,
        headers={
            'Accept-Language': 'en',
            'X-Idempotency-Token': idempotency_token,
            **HEADERS_METRO_PURCHASE,
        },
        json={'offer_id': offer_id, 'price': '120'},
    )

    assert response.json() == {
        'code': '400',
        'message': '400',
        'problem_description': {
            'code': 'metro_price_incorrect',
            'localized_message': 'incorrect_metro_price',
        },
    }
    assert response.status == 400


@pytest.mark.translations(taximeter_backend_marketplace=TRANSLATIONS)
async def test_metro_purchase_failures_price_not_integer(
        taxi_contractor_merch,
        stq,
        # mocks from driver purchase
        mock_billing_replication,
        mock_driver_tags,
        mock_feeds,
        mock_fleet_parks,
        mock_parks_replica,
):
    idempotency_token = 'aaa'
    offer_id = 'feed-id-1'

    response = await taxi_contractor_merch.post(
        ENDPOINT_METRO_PURCHASE,
        headers={
            'Accept-Language': 'en',
            'X-Idempotency-Token': idempotency_token,
            **HEADERS_METRO_PURCHASE,
        },
        json={'offer_id': offer_id, 'price': '120.2452'},
    )

    assert response.json() == {
        'code': '400',
        'message': '400',
        'problem_description': {
            'code': 'metro_price_incorrect',
            'localized_message': 'incorrect_metro_price',
        },
    }
    assert response.status == 400


REQUEST_TO_METRO_PURCHASE = {
    'ops': [
        {
            'type': 'create',
            'obj': 'task',
            'conv_id': 3461,
            'data': {
                'base': 'PProd',
                'phone': '89999999999',
                'email': 'chelovek_pavuk@yandex.ru',
                'limit': '200',
            },
        },
    ],
}


@pytest.mark.translations(taximeter_backend_marketplace=STQ_TRANSLATIONS)
@pytest.mark.config(
    CONTRACTOR_MERCH_SUPPORTED_BARCODES={
        'gs1databarexpandedstacked': {
            'render_url_template': (
                'https://gs1databarexpandedstacked?barcode={promocode_number}'
            ),
            'url_text_tanker_key': (
                'notification_v1.success.linear_barcode_url_text'
            ),
        },
    },
)
async def test_stq_metro_purchase_ok(
        taxi_contractor_merch_monitor,
        stq_runner,
        pgsql,
        # mocks from driver purchase
        mock_fleet_parks,
        mock_driver_tags,
        mock_feeds,
        mock_fleet_transactions_api,
        mock_driver_profiles,
        mock_fleet_antifraud,
        mock_parks_activation,
        mock_personal,
        mock_metro_vouchers,
        mock_parks_replica,
        mock_billing_replication,
        mock_tariffs,
        mock_agglomerations,
        mock_billing_orders,
        mock_driver_wall,
):
    mock_metro_vouchers.request = REQUEST_TO_METRO_PURCHASE
    mock_metro_vouchers.response = {
        'request_proc': 'ok',
        'ops': [
            {
                'proc': 'ok',
                'data': {
                    'discount_link': 'keking_online_discount',
                    'result': 'success',
                    'message': 'new_card',
                },
            },
        ],
    }
    cursor = pgsql['contractor_merch'].cursor()

    await stq_runner.contractor_merch_purchase.call(
        task_id='some_task_id',
        kwargs={
            'driver_id': 'driver1',
            'park_id': 'park_id',
            'feed_id': 'some_id',
            'idempotency_token': 'idemp1',
            'accept_language': 'en_GB',
            'price': '200',
            'price_with_currency': {'value': '200', 'currency': 'RUB'},
            'feed_payload': {
                'category': 'cat',
                'feeds_admin_id': 'feeds-admin-id-1',
                'balance_payment': True,
                'title': 'Оплата в Metro',
                'partner': {'name': 'Metro'},
                'meta_info': {
                    'metro_price_choice': {
                        'max_price': 5000,
                        'min_price': 100,
                        'step': 100,
                    },
                    'barcode_params': {
                        'is_send_enabled': True,
                        'type': 'gs1databarexpandedstacked',
                    },
                },
            },
        },
    )
    assert mock_metro_vouchers.metro_endpoint.times_called == 1
    # assert mock_metro_vouchers.

    vouchers = util.get_vouchers(cursor, with_created_at=False)
    assert len(vouchers) == 1
    # tested in withhold money stq_contractor_merch_purchase
    vouchers[0].pop('promocode_id')  # random generated uuid
    assert vouchers == [
        {
            'id': 'idemp1',
            'park_id': 'park_id',
            'driver_id': 'driver1',
            'idempotency_token': 'idemp1',
            'price': decimal.Decimal('200'),
            'currency': 'RUB',
            'feeds_admin_id': 'feeds-admin-id-1',
            'feed_id': 'some_id',
            'status': 'fulfilled',
            'status_reason': None,
        },
    ]

    # metrics = await taxi_contractor_merch_monitor.get_metrics(
    #     'metro-payments-successful',
    # )
    # assert metrics['metro-payments-successful'] == 1


@pytest.mark.translations(taximeter_backend_marketplace=STQ_TRANSLATIONS)
@pytest.mark.config(
    CONTRACTOR_MERCH_SUPPORTED_BARCODES={
        'gs1databarexpandedstacked': {
            'render_url_template': (
                'https://gs1databarexpandedstacked?barcode={promocode_number}'
            ),
            'url_text_tanker_key': (
                'notification_v1.success.linear_barcode_url_text'
            ),
        },
    },
)
async def test_stq_metro_purchase_failures_metro_request_fail(
        taxi_contractor_merch_monitor,
        stq_runner,
        pgsql,
        # mocks from driver purchase
        mock_fleet_parks,
        mock_driver_tags,
        mock_feeds,
        mock_fleet_transactions_api,
        mock_driver_profiles,
        mock_fleet_antifraud,
        mock_parks_activation,
        mock_personal,
        mock_metro_vouchers,
        mock_parks_replica,
        mock_billing_replication,
        mock_tariffs,
        mock_agglomerations,
        mock_billing_orders,
        mock_driver_wall,
):
    cursor = pgsql['contractor_merch'].cursor()

    mock_metro_vouchers.response = mock_metro_vouchers.response = {
        'request_proc': 'ok',
        'ops': [{'proc': 'error'}],
    }

    await stq_runner.contractor_merch_purchase.call(
        task_id='some_task_id',
        kwargs={
            'driver_id': 'driver1',
            'park_id': 'park_id',
            'feed_id': 'some_id',
            'idempotency_token': 'idemp1',
            'accept_language': 'en_GB',
            'price': '200',
            'price_with_currency': {'value': '200', 'currency': 'RUB'},
            'feed_payload': {
                'category': 'cat',
                'feeds_admin_id': 'feeds-admin-id-1',
                'balance_payment': True,
                'title': 'Оплата в Metro',
                'partner': {'name': 'Metro'},
                'meta_info': {
                    'metro_price_choice': {
                        'max_price': 5000,
                        'min_price': 100,
                        'step': 100,
                    },
                    'barcode_params': {
                        'is_send_enabled': True,
                        'type': 'gs1databarexpandedstacked',
                    },
                },
            },
        },
    )

    vouchers = util.get_vouchers(cursor, with_created_at=False)
    assert vouchers == [
        {
            'id': 'idemp1',
            'park_id': 'park_id',
            'driver_id': 'driver1',
            'idempotency_token': 'idemp1',
            'feeds_admin_id': 'feeds-admin-id-1',
            'feed_id': 'some_id',
            'promocode_id': None,
            'price': decimal.Decimal('200.0000'),
            'currency': 'RUB',
            'status': 'failed',
            'status_reason': 'some_error_occured',
        },
    ]

    metrics_failed_all = await taxi_contractor_merch_monitor.get_metrics(
        'metro-payments-failed-all',
    )
    metrics_failed_request = await taxi_contractor_merch_monitor.get_metrics(
        'metro-payments-failed-on-request',
    )
    assert metrics_failed_all['metro-payments-failed-all'] == 1
    assert metrics_failed_request['metro-payments-failed-on-request'] == 1
