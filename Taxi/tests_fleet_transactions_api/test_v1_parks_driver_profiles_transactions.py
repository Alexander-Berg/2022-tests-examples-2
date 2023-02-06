# encoding=utf-8
import base64
import hashlib
import json

import dateutil
import pytest

from tests_fleet_transactions_api import utils


BILLING_ORDERS_MOCK_URL = '/billing-orders/v1/process_event'
BILLING_REPORTS_MOCK_URL = '/billing-reports/v2/docs/select'
BILLING_REPORTS_BALANCES_MOCK_URL = '/billing-reports/v1/balances/select'

EVENT_AT = '2019-09-05T07:27:00+00:00'
EVENT_AT_NOW = '2020-02-26T08:37:00+00:00'
DESCRIPTION = 'текстовое описание платежа'
IDEMPOTENCY_TOKEN = '2ed3c756698311ecb9d9acde48001122'
IDEMPOTENCY_HEADERS = {'X-Idempotency-Token': IDEMPOTENCY_TOKEN}
ENDPOINTS = [
    (
        'v1/parks/driver-profiles/transactions/by-fleet-api',
        {**utils.FLEET_API_HEADERS, **IDEMPOTENCY_HEADERS},
        {
            'identity': 'fleet-api',
            'client_id': utils.FLEET_API_CLIENT_ID,
            'key_id': utils.FLEET_API_KEY_ID,
        },
    ),
    (
        'v1/parks/driver-profiles/transactions/by-platform',
        {**utils.PLATFORM_HEADERS, **IDEMPOTENCY_HEADERS},
        {
            'identity': 'platform',
            'tvm_service_name': utils.MOCK_TVM_SERVICE_NAME,
        },
    ),
    (
        'v1/parks/driver-profiles/transactions/by-user',
        {**utils.DISPATCHER_HEADERS, **IDEMPOTENCY_HEADERS},
        {
            'identity': 'dispatcher',
            'passport_uid': utils.DISPATCHER_PASSPORT_UID,
            'dispatcher_id': 'ant123',
            'dispatcher_name': 'Anton Todua',
        },
    ),
    (
        'v1/parks/driver-profiles/transactions/by-user',
        {**utils.TECH_SUPPORT_HEADERS, **IDEMPOTENCY_HEADERS},
        {
            'identity': 'tech-support',
            'passport_uid': utils.TECH_SUPPORT_PASSPORT_UID,
        },
    ),
]

OK_BILLING_ORDERS_RESPONSE = {'doc': {'id': 111222333444}}


def make_request(
        category_id='manual',
        park_id='7ad35b',
        driver_profile_id='9c5e35',
        amount='12345.789',
        description=DESCRIPTION,
        balance_min=None,
):
    return {
        'event_at': EVENT_AT,
        'park_id': park_id,
        'driver_profile_id': driver_profile_id,
        'category_id': category_id,
        'amount': amount,
        'description': description,
        'condition': (
            {'balance_min': balance_min} if balance_min is not None else None
        ),
    }


def make_response_created_by(created_by):
    result = created_by.copy()
    if result['identity'] == 'platform':
        result.pop('tvm_service_name')
    elif result['identity'] == 'tech-support':
        result.pop('passport_uid')
    return result


def make_response(category_id, created_by, event_at, description=DESCRIPTION):
    return {
        'event_at': event_at,
        'park_id': '7ad35b',
        'driver_profile_id': '9c5e35',
        'category_id': category_id,
        'amount': '12345.7890',
        'currency_code': 'RUB',
        'description': description,
        'created_by': make_response_created_by(created_by),
    }


def make_orders_request(
        agreement, sub_account, created_by, event_at, description=DESCRIPTION,
):
    def base64_encode(data):
        return base64.b64encode(data).decode('utf-8').rstrip('=')

    obj_id = 'taxi/taximeter/payment/7ad35b/9c5e35/' + base64_encode(
        IDEMPOTENCY_TOKEN.encode('utf-8'),
    )
    transaction_id = (
        hashlib.blake2b(obj_id.encode('utf-8'), digest_size=16).digest().hex()
    )
    return {
        'external_obj_id': obj_id,
        'external_event_ref': obj_id,
        'event_at': event_at,
        'kind': 'taximeter_payment',
        'data': {
            'driver': {'db_id': '7ad35b', 'driver_uuid': '9c5e35'},
            'payment_info': {
                'transaction_id': transaction_id,
                'agreement': agreement,
                'sub_account': sub_account,
                'currency': 'RUB',
                'amount': '12345.7890',
                'reason': '',
                'description': description,
                'service_id': 'fleet-transactions-api',
            },
            'fleet_transactions_api_info': {'created_by': created_by},
        },
    }


def dump_ongoing_transactions(pgsql):
    with pgsql['fleet_transactions_api'].cursor() as cursor:
        cursor.execute(
            f"""
            SELECT
                park_id,
                driver_profile_id,
                topic,
                event_at
            FROM fleet_transactions_api.ongoing_transactions
            """,
        )
        return {(row[0], row[1], row[2]): row[3] for row in cursor.fetchall()}


OK_PARAMS = [
    ('manual', 'taxi/park_services', 'arbitrary/other'),
    ('partner_service_manual_2', 'taxi/park_services', 'external/2'),
]


@pytest.mark.config(TVM_ENABLED=True, TVM_USER_TICKETS_ENABLED=True)
@pytest.mark.tvm2_ticket(
    {111: utils.MOCK_SERVICE_TICKET, 2002228: utils.ORDERS_SERVICE_TICKET},
)
@pytest.mark.parametrize('endpoint_url, headers, created_by', ENDPOINTS)
@pytest.mark.parametrize('category_id, agreement, sub_account', OK_PARAMS)
@pytest.mark.now(EVENT_AT_NOW)
async def test_ok(
        taxi_fleet_transactions_api,
        mockserver,
        mock_fleet_parks_list,
        dispatcher_access_control,
        driver_profiles,
        endpoint_url,
        headers,
        created_by,
        category_id,
        agreement,
        sub_account,
        pgsql,
):
    @mockserver.json_handler(BILLING_ORDERS_MOCK_URL)
    async def mock_orders(request):
        request.get_data()
        return OK_BILLING_ORDERS_RESPONSE

    @mockserver.json_handler(BILLING_REPORTS_MOCK_URL)
    async def _mock_reports(request):
        request.get_data()
        return {
            'docs': [
                {
                    'doc_id': 111222333000,
                    'event_at': '2020-02-26T08:37:00+00:00',
                    'topic': (
                        'taxi/taximeter/payment/7ad35b/9c5e35/'
                        'OTIxM2VhNjA2OTdiMTFlYzhkYTQ1MjU0MDAxMjM0NTY'
                    ),
                    'status': 'created',
                },
            ],
            'cursor': 'cursor',
        }

    response = await taxi_fleet_transactions_api.post(
        endpoint_url, headers=headers, json=make_request(category_id),
    )

    event_at = EVENT_AT if endpoint_url.endswith('platform') else EVENT_AT_NOW

    assert response.status_code == 200, response.text
    assert response.json() == make_response(category_id, created_by, event_at)

    assert mock_fleet_parks_list.mock_parks_list.times_called == 1
    assert mock_orders.times_called == 1
    billing_request = mock_orders.next_call()['request']
    assert billing_request.method == 'POST'
    assert billing_request.headers.get('X-Ya-Service-Ticket') is not None
    assert json.loads(billing_request.get_data()) == make_orders_request(
        agreement, sub_account, created_by, event_at,
    )


@pytest.mark.parametrize('endpoint_url, headers, created_by', ENDPOINTS)
async def test_park_not_found(
        taxi_fleet_transactions_api,
        mock_fleet_parks_list,
        dispatcher_access_control,
        driver_profiles,
        endpoint_url,
        headers,
        created_by,
        pgsql,
        mockserver,
):
    response = await taxi_fleet_transactions_api.post(
        endpoint_url,
        headers=headers,
        json=make_request(park_id='nonexistent'),
    )

    @mockserver.json_handler(BILLING_REPORTS_MOCK_URL)
    async def _mock_reports(request):
        request.get_data()
        return {
            'docs': [
                {
                    'doc_id': 111222333000,
                    'event_at': '2020-02-26T08:37:00+00:00',
                    'topic': (
                        'taxi/taximeter/payment/7ad35b/9c5e35/'
                        'OTIxM2VhNjA2OTdiMTFlYzhkYTQ1MjU0MDAxMjM0NTY'
                    ),
                    'status': 'created',
                },
            ],
            'cursor': 'cursor',
        }

    assert response.status_code == 400, response.text
    assert response.json() == {
        'code': 'park_not_found',
        'message': 'park with id `nonexistent` not found',
    }

    assert mock_fleet_parks_list.mock_parks_list.times_called == 1


@pytest.mark.parametrize('endpoint_url, headers, created_by', ENDPOINTS)
@pytest.mark.parametrize(
    'park_id',
    ['godfather', 'avengers'],  # empty currency code, country not found
)
async def test_no_currency_code(
        taxi_fleet_transactions_api,
        mockserver,
        mock_fleet_parks_list,
        dispatcher_access_control,
        driver_profiles,
        park_id,
        endpoint_url,
        headers,
        created_by,
):
    @mockserver.json_handler(BILLING_ORDERS_MOCK_URL)
    async def mock_orders(request):
        request.get_data()
        return {}

    response = await taxi_fleet_transactions_api.post(
        endpoint_url, headers=headers, json=make_request(park_id=park_id),
    )

    assert response.status_code == 500, response.text
    assert mock_fleet_parks_list.mock_parks_list.times_called == 1
    assert mock_orders.times_called == 0


@pytest.mark.parametrize('endpoint_url, headers, created_by', ENDPOINTS)
@pytest.mark.config(FLEET_TRANSACTIONS_API_GROUPS=[])
async def test_incorrect_config(
        taxi_fleet_transactions_api,
        mock_fleet_parks_list,
        dispatcher_access_control,
        driver_profiles,
        endpoint_url,
        headers,
        created_by,
):
    response = await taxi_fleet_transactions_api.post(
        endpoint_url, headers=headers, json=make_request(),
    )
    assert response.status_code == 500, response.text


@pytest.mark.parametrize('endpoint_url, headers, created_by', ENDPOINTS)
async def test_driver_profile_not_found(
        taxi_fleet_transactions_api,
        mock_fleet_parks_list,
        dispatcher_access_control,
        driver_profiles,
        endpoint_url,
        headers,
        created_by,
):
    response = await taxi_fleet_transactions_api.post(
        endpoint_url,
        headers=headers,
        json=make_request(driver_profile_id='not_a_driver_id'),
    )

    assert response.status_code == 400, response.text
    assert response.json() == {
        'code': 'driver_profile_not_found',
        'message': 'driver profile with id `not_a_driver_id` was not found',
    }


@pytest.mark.parametrize('endpoint_url, headers, created_by', ENDPOINTS)
async def test_driver_profiles_error(
        taxi_fleet_transactions_api,
        mock_fleet_parks_list,
        dispatcher_access_control,
        mockserver,
        endpoint_url,
        headers,
        created_by,
):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    async def mock_driver_profiles(request):
        request.get_data()
        return []

    response = await taxi_fleet_transactions_api.post(
        endpoint_url, headers=headers, json=make_request(),
    )

    assert response.status_code == 500, response.text
    assert mock_driver_profiles.times_called == 1


@pytest.mark.parametrize('endpoint_url, headers, created_by', ENDPOINTS)
async def test_amount_too_big(
        taxi_fleet_transactions_api, endpoint_url, headers, created_by,
):
    response = await taxi_fleet_transactions_api.post(
        endpoint_url,
        headers=headers,
        json=make_request(amount='1000000000.0001'),
    )

    assert response.status_code == 400, response.text
    assert response.json() == {
        'code': 'too_big_amount',
        'message': 'too big amount',
    }


@pytest.mark.parametrize('endpoint_url, headers, created_by', ENDPOINTS)
async def test_description_too_long(
        taxi_fleet_transactions_api, endpoint_url, headers, created_by,
):
    response = await taxi_fleet_transactions_api.post(
        endpoint_url,
        headers=headers,
        json=make_request(description='я' * 1001),
    )

    assert response.status_code == 400, response.text


@pytest.mark.config(TVM_ENABLED=True, TVM_USER_TICKETS_ENABLED=True)
@pytest.mark.parametrize('endpoint_url, headers, created_by', ENDPOINTS)
async def test_status_code_429(
        taxi_fleet_transactions_api,
        mockserver,
        mock_fleet_parks_list,
        dispatcher_access_control,
        driver_profiles,
        endpoint_url,
        headers,
        created_by,
        testpoint,
):
    @mockserver.json_handler(BILLING_ORDERS_MOCK_URL)
    async def mock_orders(request):
        return mockserver.make_response(status=429)

    @mockserver.json_handler(BILLING_REPORTS_MOCK_URL)
    async def _mock_reports(request):
        request.get_data()
        return {
            'docs': [
                {
                    'doc_id': 111222333000,
                    'event_at': '2020-02-26T08:37:00+00:00',
                    'topic': (
                        'taxi/taximeter/payment/7ad35b/9c5e35/'
                        'OTIxM2VhNjA2OTdiMTFlYzhkYTQ1MjU0MDAxMjM0NTY'
                    ),
                    'status': 'created',
                },
            ],
            'cursor': 'cursor',
        }

    response = await taxi_fleet_transactions_api.post(
        endpoint_url, headers=headers, json=make_request(OK_PARAMS[0][0]),
    )

    assert response.status_code == 429, response.text
    assert mock_orders.has_calls


@pytest.mark.config(TVM_ENABLED=True, TVM_USER_TICKETS_ENABLED=True)
@pytest.mark.parametrize('endpoint_url, headers, created_by', ENDPOINTS)
@pytest.mark.parametrize('category_id, agreement, sub_account', OK_PARAMS)
@pytest.mark.now(EVENT_AT_NOW)
async def test_status_code_429_ongoing(
        taxi_fleet_transactions_api,
        mockserver,
        mock_fleet_parks_list,
        dispatcher_access_control,
        driver_profiles,
        endpoint_url,
        headers,
        created_by,
        category_id,
        agreement,
        sub_account,
        pgsql,
):
    @mockserver.json_handler(BILLING_REPORTS_MOCK_URL)
    async def mock_reports(request):
        data = json.loads(request.get_data())
        if data['topic'] == 'some_topic':
            return {
                'docs': [
                    {
                        'doc_id': 111222333000,
                        'event_at': '2020-02-26T08:37:00+00:00',
                        'topic': 'some_topic',
                        'status': 'created',
                    },
                ],
                'cursor': 'cursor',
            }
        return {'docs': [], 'cursor': 'cursor'}

    response = await taxi_fleet_transactions_api.post(
        endpoint_url,
        headers=headers,
        json=make_request(category_id, balance_min='0'),
    )

    assert response.status_code == 429, response.text

    assert mock_fleet_parks_list.mock_parks_list.times_called == 1
    assert mock_reports.times_called == 2
    reports_request = mock_reports.next_call()['request']
    assert reports_request.method == 'POST'
    assert reports_request.headers.get('X-Ya-Service-Ticket') is not None
    assert json.loads(reports_request.get_data()) == {
        'begin_time': '2020-02-25T08:37:00+00:00',
        'end_time': '2020-02-26T08:37:00+00:00',
        'limit': 1,
        'projection': ['status'],
        'topic': 'some_topic',
    }
    reports_request = mock_reports.next_call()['request']
    assert reports_request.method == 'POST'
    assert reports_request.headers.get('X-Ya-Service-Ticket') is not None
    assert json.loads(reports_request.get_data()) == {
        'begin_time': '2020-02-25T08:37:00+00:00',
        'end_time': '2020-02-26T08:37:00+00:00',
        'limit': 1,
        'projection': ['status'],
        'topic': (
            'taxi/taximeter/payment/7ad35b/9c5e35/'
            'MmVkM2M3NTY2OTgzMTFlY2I5ZDlhY2RlNDgwMDExMjI'
        ),
    }

    assert dump_ongoing_transactions(pgsql) == {
        ('7ad35b', '9c5e35', 'some_topic'): dateutil.parser.parse(
            '2020-02-26T08:37:00+00:00',
        ),
    }


@pytest.mark.config(TVM_ENABLED=True, TVM_USER_TICKETS_ENABLED=True)
@pytest.mark.parametrize('endpoint_url, headers, created_by', ENDPOINTS)
@pytest.mark.parametrize('category_id, agreement, sub_account', OK_PARAMS)
@pytest.mark.now(EVENT_AT_NOW)
async def test_status_code_409(
        taxi_fleet_transactions_api,
        mockserver,
        mock_fleet_parks_list,
        dispatcher_access_control,
        driver_profiles,
        endpoint_url,
        headers,
        created_by,
        category_id,
        agreement,
        sub_account,
        pgsql,
        load_json,
):
    @mockserver.json_handler(BILLING_REPORTS_MOCK_URL)
    async def mock_reports(request):
        data = json.loads(request.get_data())
        if data['topic'] == 'some_topic':
            return {
                'docs': [
                    {
                        'doc_id': 111222333000,
                        'event_at': '2020-02-26T08:37:00+00:00',
                        'topic': 'some_topic',
                        'status': 'complete',
                    },
                ],
                'cursor': 'cursor',
            }
        return {'docs': [], 'cursor': 'cursor'}

    @mockserver.json_handler(BILLING_REPORTS_BALANCES_MOCK_URL)
    async def _mock_billing_reports(request):
        request.get_data()
        return load_json('mock_response.json')

    response = await taxi_fleet_transactions_api.post(
        endpoint_url,
        headers=headers,
        json=make_request(category_id, balance_min='5100'),
    )

    assert response.status_code == 409, response.text

    assert mock_fleet_parks_list.mock_parks_list.times_called == 1
    assert mock_reports.times_called == 2
    reports_request = mock_reports.next_call()['request']
    assert reports_request.method == 'POST'
    assert reports_request.headers.get('X-Ya-Service-Ticket') is not None
    assert json.loads(reports_request.get_data()) == {
        'begin_time': '2020-02-25T08:37:00+00:00',
        'end_time': '2020-02-26T08:37:00+00:00',
        'limit': 1,
        'projection': ['status'],
        'topic': 'some_topic',
    }
    reports_request = mock_reports.next_call()['request']
    assert reports_request.method == 'POST'
    assert reports_request.headers.get('X-Ya-Service-Ticket') is not None
    assert json.loads(reports_request.get_data()) == {
        'begin_time': '2020-02-25T08:37:00+00:00',
        'end_time': '2020-02-26T08:37:00+00:00',
        'limit': 1,
        'projection': ['status'],
        'topic': (
            'taxi/taximeter/payment/7ad35b/9c5e35/'
            'MmVkM2M3NTY2OTgzMTFlY2I5ZDlhY2RlNDgwMDExMjI'
        ),
    }

    assert dump_ongoing_transactions(pgsql) == {}


@pytest.mark.pgsql(
    'fleet_transactions_api',
    queries=[
        """
        INSERT INTO fleet_transactions_api.ongoing_transactions VALUES (
            '7ad35b',
            '9c5e35',
            'taxi/taximeter/payment/7ad35b/9c5e35/'
            'MmVkM2M3NTY2OTgzMTFlY2I5ZDlhY2RlNDgwMDExMjI',
            '2020-02-26T08:37:00+00:00'
        ), (
            '7ad35b',
            '9c5e35',
            'some_topic',
            '2020-02-26T08:37:00+00:00'
        )
        """,
    ],
)
@pytest.mark.config(TVM_ENABLED=True, TVM_USER_TICKETS_ENABLED=True)
@pytest.mark.parametrize('endpoint_url, headers, created_by', ENDPOINTS)
@pytest.mark.parametrize('category_id, agreement, sub_account', OK_PARAMS)
@pytest.mark.now(EVENT_AT_NOW)
async def test_status_code_200_ongoing_idempotency(
        taxi_fleet_transactions_api,
        mockserver,
        mock_fleet_parks_list,
        dispatcher_access_control,
        driver_profiles,
        endpoint_url,
        headers,
        created_by,
        category_id,
        agreement,
        sub_account,
        pgsql,
):
    @mockserver.json_handler(BILLING_REPORTS_MOCK_URL)
    async def _mock_reports(request):
        data = json.loads(request.get_data())
        if data['topic'] == 'some_topic':
            return {
                'docs': [
                    {
                        'doc_id': 111222333000,
                        'event_at': '2020-02-26T08:37:00+00:00',
                        'topic': 'some_topic',
                        'status': 'created',
                    },
                ],
                'cursor': 'cursor',
            }
        if data['topic'] == (
                'taxi/taximeter/payment/7ad35b/9c5e35/'
                'MmVkM2M3NTY2OTgzMTFlY2I5ZDlhY2RlNDgwMDExMjI'
        ):
            return {
                'docs': [
                    {
                        'doc_id': 111222333000,
                        'event_at': '2020-02-26T08:37:00+00:00',
                        'topic': (
                            'taxi/taximeter/payment/7ad35b/9c5e35/'
                            'MmVkM2M3NTY2OTgzMTFlY2I5ZDlhY2RlNDgwMDExMjI'
                        ),
                        'status': 'complete',
                    },
                ],
                'cursor': 'cursor',
            }
        return {'docs': [], 'cursor': 'cursor'}

    response = await taxi_fleet_transactions_api.post(
        endpoint_url,
        headers=headers,
        json=make_request(category_id, balance_min='0'),
    )

    assert response.status_code == 200, response.text

    assert mock_fleet_parks_list.mock_parks_list.times_called == 1

    assert dump_ongoing_transactions(pgsql) == {
        ('7ad35b', '9c5e35', 'some_topic'): dateutil.parser.parse(
            '2020-02-26T08:37:00+00:00',
        ),
    }


@pytest.mark.pgsql(
    'fleet_transactions_api',
    queries=[
        """
        INSERT INTO fleet_transactions_api.ongoing_transactions VALUES (
            '7ad35b',
            '9c5e35',
            'taxi/taximeter/payment/7ad35b/9c5e35/'
            'MmVkM2M3NTY2OTgzMTFlY2I5ZDlhY2RlNDgwMDExMjI',
            '2020-02-26T08:37:00+00:00'
        ), (
            '7ad35b',
            '9c5e35',
            'some_topic',
            '2020-02-26T08:37:00+00:00'
        )
        """,
    ],
)
@pytest.mark.config(TVM_ENABLED=True, TVM_USER_TICKETS_ENABLED=True)
@pytest.mark.parametrize('endpoint_url, headers, created_by', ENDPOINTS)
@pytest.mark.parametrize('category_id, agreement, sub_account', OK_PARAMS)
@pytest.mark.now(EVENT_AT_NOW)
async def test_status_code_200_conflict_idempotency(
        taxi_fleet_transactions_api,
        mockserver,
        mock_fleet_parks_list,
        dispatcher_access_control,
        driver_profiles,
        endpoint_url,
        headers,
        created_by,
        category_id,
        agreement,
        sub_account,
        pgsql,
        load_json,
):
    @mockserver.json_handler(BILLING_REPORTS_MOCK_URL)
    async def _mock_reports(request):
        data = json.loads(request.get_data())
        if data['topic'] == 'some_topic':
            return {
                'docs': [
                    {
                        'doc_id': 111222333000,
                        'event_at': '2020-02-26T08:37:00+00:00',
                        'topic': 'some_topic',
                        'status': 'complete',
                    },
                ],
                'cursor': 'cursor',
            }
        if data['topic'] == (
                'taxi/taximeter/payment/7ad35b/9c5e35/'
                'MmVkM2M3NTY2OTgzMTFlY2I5ZDlhY2RlNDgwMDExMjI'
        ):
            return {
                'docs': [
                    {
                        'doc_id': 111222333000,
                        'event_at': '2020-02-26T08:37:00+00:00',
                        'topic': (
                            'taxi/taximeter/payment/7ad35b/9c5e35/'
                            'MmVkM2M3NTY2OTgzMTFlY2I5ZDlhY2RlNDgwMDExMjI'
                        ),
                        'status': 'complete',
                    },
                ],
                'cursor': 'cursor',
            }
        return {'docs': [], 'cursor': 'cursor'}

    @mockserver.json_handler(BILLING_REPORTS_BALANCES_MOCK_URL)
    async def _mock_billing_reports(request):
        request.get_data()
        return load_json('mock_response.json')

    response = await taxi_fleet_transactions_api.post(
        endpoint_url,
        headers=headers,
        json=make_request(category_id, balance_min='5100'),
    )

    assert response.status_code == 200, response.text

    assert mock_fleet_parks_list.mock_parks_list.times_called == 1
    assert dump_ongoing_transactions(pgsql) == {}


@pytest.mark.pgsql(
    'fleet_transactions_api',
    queries=[
        """
        INSERT INTO fleet_transactions_api.ongoing_transactions VALUES (
            '7ad35b',
            '9c5e35',
            'taxi/taximeter/payment/7ad35b/9c5e35/'
            'MmVkM2M3NTY2OTgzMTFlY2I5ZDlhY2RlNDgwMDExMjI',
            '2020-02-26T08:37:00+00:00'
        ), (
            '7ad35b',
            '9c5e35',
            'some_topic',
            '2020-02-26T08:37:00+00:00'
        )
        """,
    ],
)
@pytest.mark.config(TVM_ENABLED=True, TVM_USER_TICKETS_ENABLED=True)
@pytest.mark.parametrize('endpoint_url, headers, created_by', ENDPOINTS)
@pytest.mark.parametrize('category_id, agreement, sub_account', OK_PARAMS)
@pytest.mark.now(EVENT_AT_NOW)
async def test_status_code_429_ongoing_recent(
        taxi_fleet_transactions_api,
        mockserver,
        mock_fleet_parks_list,
        dispatcher_access_control,
        driver_profiles,
        endpoint_url,
        headers,
        created_by,
        category_id,
        agreement,
        sub_account,
        pgsql,
        load_json,
):
    @mockserver.json_handler(BILLING_REPORTS_MOCK_URL)
    async def _mock_reports(request):
        data = json.loads(request.get_data())
        if data['topic'] == 'some_topic':
            return {
                'docs': [
                    {
                        'doc_id': 111222333000,
                        'event_at': '2020-02-26T08:37:00+00:00',
                        'topic': 'some_topic',
                        'status': 'complete',
                    },
                ],
                'cursor': 'cursor',
            }
        return {'docs': [], 'cursor': 'cursor'}

    response = await taxi_fleet_transactions_api.post(
        endpoint_url,
        headers=headers,
        json=make_request(category_id, balance_min='0'),
    )

    assert response.status_code == 429, response.text

    assert mock_fleet_parks_list.mock_parks_list.times_called == 1

    assert dump_ongoing_transactions(pgsql) == {
        (
            '7ad35b',
            '9c5e35',
            'taxi/taximeter/payment/7ad35b/9c5e35/'
            'MmVkM2M3NTY2OTgzMTFlY2I5ZDlhY2RlNDgwMDExMjI',
        ): dateutil.parser.parse('2020-02-26T08:37:00+00:00'),
    }


@pytest.mark.pgsql(
    'fleet_transactions_api',
    queries=[
        """
        INSERT INTO fleet_transactions_api.ongoing_transactions VALUES (
            '7ad35b',
            '9c5e35',
            'taxi/taximeter/payment/7ad35b/9c5e35/'
            'MmVkM2M3NTY2OTgzMTFlY2I5ZDlhY2RlNDgwMDExMjI',
            '2020-02-26T08:36:00+00:00'
        )
        """,
        """
        INSERT INTO fleet_transactions_api.park_transaction_categories VALUES
        (
            'park_id_test',
            1, -- category index in park
            'Штрафы',
            'abcd1234cdef5678',
            TRUE,
            current_timestamp,
            current_timestamp
        ),
        (
            'park_id_test',
            2, -- category index in park
            'по Расписанию',
            'zyx9876543210cba',
            FALSE,
            current_timestamp,
            current_timestamp
        ),
        (
            '7ad35b',
            1, -- category index in park
            'Барщина',
            'abcd1234cdef5678',
            FALSE,
            current_timestamp,
            current_timestamp
        ),
        (
            '7ad35b',
            2, -- category index in park
            'Оброк',
            'zyx9876543210cba',
            TRUE,
            current_timestamp,
            current_timestamp
        );
        """,
    ],
)
@pytest.mark.config(TVM_ENABLED=True, TVM_USER_TICKETS_ENABLED=True)
@pytest.mark.tvm2_ticket(
    {111: utils.MOCK_SERVICE_TICKET, 2002228: utils.ORDERS_SERVICE_TICKET},
)
@pytest.mark.parametrize('endpoint_url, headers, created_by', ENDPOINTS)
@pytest.mark.parametrize('category_id, agreement, sub_account', OK_PARAMS)
@pytest.mark.now(EVENT_AT_NOW)
async def test_status_code_200_ongoing_missing(
        taxi_fleet_transactions_api,
        mockserver,
        mock_fleet_parks_list,
        dispatcher_access_control,
        driver_profiles,
        endpoint_url,
        headers,
        created_by,
        category_id,
        agreement,
        sub_account,
        pgsql,
        load_json,
):
    @mockserver.json_handler(BILLING_ORDERS_MOCK_URL)
    async def mock_orders(request):
        request.get_data()
        return OK_BILLING_ORDERS_RESPONSE

    @mockserver.json_handler(BILLING_REPORTS_MOCK_URL)
    async def _mock_reports(request):
        request.get_data()
        return {
            'docs': [
                {
                    'doc_id': 111222333000,
                    'event_at': '2020-02-26T08:37:00+00:00',
                    'topic': (
                        'taxi/taximeter/payment/7ad35b/9c5e35/'
                        'OTIxM2VhNjA2OTdiMTFlYzhkYTQ1MjU0MDAxMjM0NTY'
                    ),
                    'status': 'created',
                },
            ],
            'cursor': 'cursor',
        }

    response = await taxi_fleet_transactions_api.post(
        endpoint_url, headers=headers, json=make_request(category_id),
    )

    event_at = EVENT_AT if endpoint_url.endswith('platform') else EVENT_AT_NOW

    assert response.status_code == 200, response.text
    assert response.json() == make_response(category_id, created_by, event_at)

    assert mock_fleet_parks_list.mock_parks_list.times_called == 1
    assert mock_orders.times_called == 1
    billing_request = mock_orders.next_call()['request']
    assert billing_request.method == 'POST'
    assert billing_request.headers.get('X-Ya-Service-Ticket') is not None
    assert json.loads(billing_request.get_data()) == make_orders_request(
        agreement, sub_account, created_by, event_at,
    )
