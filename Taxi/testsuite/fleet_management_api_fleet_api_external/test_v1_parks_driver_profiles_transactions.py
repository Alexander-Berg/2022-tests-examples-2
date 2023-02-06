import json

import pytest

from fleet_management_api import utils
from . import auth

MOCK_BASE_URL = (
    '/taximeter-xservice.taxi.yandex.net/fm-api/driver/transactions'
)
ENDPOINT_BASE_URL = '/v1/parks/driver-profiles/transactions'
X_REAL_IP = '1.2.3.4'

TRANSACTIONS_LIST_TEST_REQUEST = {'query': {'park': {'id': 'xxx'}}, 'limit': 1}

TRANSACTIONS_LIST_INTERNAL_RESPONSE = {
    'transactions': [
        {
            'id': 'aaa',
            'date': '2019-02-07T09:04:14.517+0000',
            'order_id': 'bbb',
            'order_number': 123,
            'balance': 12345.6789,
            'driver_name': 'Anton',
            'driver_signal': 'sig',
            'park_id': 'ccc',
            'driver_id': 'ddd',
            'account_id': 'eee',
            'factor': 'income',
            'amount': 500.73,
            'currency': 'RUB',
            'type': 'payment',
            'group': 'tips',
            'payment_method': 'cash',
            'groups': 'some-groups',
            'service_id': 'opteum',
            'description': '',
            'user_name': 'fleet-api',
            'root_transaction_id': 'fff',
        },
        {
            'id': 'aaa',
            'date': '2019-02-07T09:04:14.517+0000',
            'balance': 12345.6789,
            'park_id': 'ccc',
            'driver_id': 'ddd',
            'account_id': 'eee',
            'factor': 'income',
            'amount': 500.73,
            'currency': 'RUB',
        },
    ],
    'cursor': {
        'older_than': {'date': '2019-02-07T11:04:14.517+0000', 'id': 'ggg'},
    },
}

TRANSACTIONS_LIST_EXTERNAL_RESPONSE = {
    'transactions': [
        {
            'id': 'aaa',
            'date': '2019-02-07T09:04:14.517+0000',
            'order_id': 'bbb',
            'balance_after_commit': '12345.6789',
            'park_id': 'ccc',
            'driver_profile_id': 'ddd',
            'account_id': 'eee',
            'factor': 'income',
            'amount': '500.7300',
            'currency': 'RUB',
            'type': 'payment',
            'group': 'tips',
            'payment_method': 'cash',
            'description': '',
            'root_transaction_id': 'fff',
        },
        {
            'id': 'aaa',
            'date': '2019-02-07T09:04:14.517+0000',
            'balance_after_commit': '12345.6789',
            'park_id': 'ccc',
            'driver_profile_id': 'ddd',
            'account_id': 'eee',
            'factor': 'income',
            'amount': '500.7300',
            'currency': 'RUB',
        },
    ],
    'cursor': {
        'older_than': {'date': '2019-02-07T11:04:14.517+0000', 'id': 'ggg'},
    },
}

AMOUNT_FORMAT_ERROR_TEXT = (
    'amount must be a positive decimal formatted as'
    ' a string with up to 4 significant digits'
    ' in the fractional part'
)


@pytest.mark.parametrize(
    'request_json,internal_request_json',
    [
        (
            {
                'park_id': 'xxx',
                'driver_profile_id': 'yyy',
                'account_id': 'yyy',
                'factor': 'income',
                'amount': '1',
                'currency': 'RUB',
                'type': 'payment',
                'group': 'other',
                'payment_method': 'internal',
                'description': '',
                'root_transaction_id': 'zzz',
            },
            {
                'park_id': 'xxx',
                'driver_id': 'yyy',
                'account_id': 'yyy',
                'factor': 'income',
                'amount': 1,
                'currency': 'RUB',
                'type': 'payment',
                'group': 'other',
                'payment_method': 'internal',
                'description': '',
                'root_transaction_id': 'zzz',
                'user_name': 'fleet-api',
                'service_id': 'anton-todua',
            },
        ),
        (
            {
                'park_id': 'xxx',
                'driver_profile_id': 'yyy',
                'account_id': 'yyy',
                'factor': 'income',
                'amount': '1.2',
                'currency': 'RUB',
            },
            {
                'park_id': 'xxx',
                'driver_id': 'yyy',
                'account_id': 'yyy',
                'factor': 'income',
                'amount': 1.2,
                'currency': 'RUB',
                'user_name': 'fleet-api',
                'service_id': 'anton-todua',
            },
        ),
        (
            {
                'park_id': 'xxx',
                'driver_profile_id': 'yyy',
                'account_id': 'yyy',
                'factor': 'income',
                'amount': '1.23',
                'currency': 'RUB',
                'some_other_field': 'some_other_value',
            },
            {
                'park_id': 'xxx',
                'driver_id': 'yyy',
                'account_id': 'yyy',
                'factor': 'income',
                'amount': 1.23,
                'currency': 'RUB',
                'user_name': 'fleet-api',
                'service_id': 'anton-todua',
            },
        ),
        (
            {
                'park_id': 'xxx',
                'driver_profile_id': 'yyy',
                'account_id': 'yyy',
                'factor': 'income',
                'amount': '1.234',
                'currency': 'RUB',
                'service_id': 'abra',
            },
            {
                'park_id': 'xxx',
                'driver_id': 'yyy',
                'account_id': 'yyy',
                'factor': 'income',
                'amount': 1.234,
                'currency': 'RUB',
                'user_name': 'fleet-api',
                'service_id': 'anton-todua',
            },
        ),
        (
            {
                'park_id': 'xxx',
                'driver_profile_id': 'yyy',
                'account_id': 'yyy',
                'factor': 'income',
                'amount': '1.2345',
                'currency': 'RUB',
                'type': 'payment',
                'group': 'other',
                'payment_method': 'internal',
                'description': '',
                'root_transaction_id': 'zzz',
                'some_other_field': 'some_other_value',
                'service_id': 'abrakadabra',
            },
            {
                'park_id': 'xxx',
                'driver_id': 'yyy',
                'account_id': 'yyy',
                'factor': 'income',
                'amount': 1.2345,
                'currency': 'RUB',
                'type': 'payment',
                'group': 'other',
                'payment_method': 'internal',
                'description': '',
                'root_transaction_id': 'zzz',
                'user_name': 'fleet-api',
                'service_id': 'anton-todua',
            },
        ),
        (
            {
                'park_id': 'xxx',
                'driver_profile_id': 'yyy',
                'account_id': 'yyy',
                'factor': 'income',
                'amount': '1' + '0' * 15 + '.' + '9876',
                'currency': 'RUB',
                'service_id': 'abra',
            },
            {
                'park_id': 'xxx',
                'driver_id': 'yyy',
                'account_id': 'yyy',
                'factor': 'income',
                'amount': 10 ** 15 + 0.9876,
                'currency': 'RUB',
                'user_name': 'fleet-api',
                'service_id': 'anton-todua',
            },
        ),
    ],
)
def test_post_ok(
        taxi_fleet_api_external,
        request_json,
        internal_request_json,
        mockserver,
):
    ok_response = {'status': 'draft'}

    @mockserver.json_handler(MOCK_BASE_URL)
    def mock_callback(request):
        assert request.args.to_dict() == {}
        assert json.loads(request.get_data()) == internal_request_json
        assert request.headers['X-Real-IP'] == X_REAL_IP
        return ok_response

    response = taxi_fleet_api_external.post(
        ENDPOINT_BASE_URL,
        headers=auth.HEADERS,
        data=json.dumps(request_json),
        x_real_ip=X_REAL_IP,
    )

    assert mock_callback.times_called == 1
    assert response.status_code == 200
    assert response.json() == ok_response


@pytest.mark.parametrize(
    'request_json,error_text',
    [
        (
            {
                'driver_profile_id': 'yyy',
                'account_id': 'yyy',
                'factor': 'income',
                'amount': '1.2',
                'currency': 'RUB',
            },
            'park_id must be present',
        ),
        (
            {
                'park_id': 'xxx',
                'account_id': 'yyy',
                'factor': 'income',
                'amount': '1.2',
                'currency': 'RUB',
            },
            'driver_profile_id must be present',
        ),
        (
            {
                'park_id': 'xxx',
                'driver_profile_id': 'yyy',
                'factor': 'income',
                'amount': '1.2',
                'currency': 'RUB',
            },
            'account_id must be present',
        ),
        (
            {
                'park_id': 'xxx',
                'driver_profile_id': 'yyy',
                'account_id': 'yyy',
                'amount': '1.2',
                'currency': 'RUB',
            },
            'factor must be present',
        ),
        (
            {
                'park_id': 'xxx',
                'driver_profile_id': 'yyy',
                'account_id': 'yyy',
                'factor': 'income',
                'currency': 'RUB',
            },
            'amount must be present',
        ),
        (
            {
                'park_id': 'xxx',
                'driver_profile_id': 'yyy',
                'account_id': 'yyy',
                'factor': 'income',
                'amount': '1.2',
            },
            'currency must be present',
        ),
        (
            {
                'park_id': 'xxx',
                'driver_profile_id': 'yyy',
                'account_id': 'yyy',
                'factor': 'income',
                'amount': '.2',
                'currency': 'RUB',
            },
            AMOUNT_FORMAT_ERROR_TEXT,
        ),
        (
            {
                'park_id': 'xxx',
                'driver_profile_id': 'yyy',
                'account_id': 'yyy',
                'factor': 'income',
                'amount': '2.',
                'currency': 'RUB',
            },
            AMOUNT_FORMAT_ERROR_TEXT,
        ),
        (
            {
                'park_id': 'xxx',
                'driver_profile_id': 'yyy',
                'account_id': 'yyy',
                'factor': 'income',
                'amount': '0.12345',
                'currency': 'RUB',
            },
            AMOUNT_FORMAT_ERROR_TEXT,
        ),
        (
            {
                'park_id': 'xxx',
                'driver_profile_id': 'yyy',
                'account_id': 'yyy',
                'factor': 'income',
                'amount': ' 1.2',
                'currency': 'RUB',
            },
            AMOUNT_FORMAT_ERROR_TEXT,
        ),
        (
            {
                'park_id': 'xxx',
                'driver_profile_id': 'yyy',
                'account_id': 'yyy',
                'factor': 'income',
                'amount': '1.2 ',
                'currency': 'RUB',
            },
            AMOUNT_FORMAT_ERROR_TEXT,
        ),
        (
            {
                'park_id': 'xxx',
                'driver_profile_id': 'yyy',
                'account_id': 'yyy',
                'factor': 'income',
                'amount': '0',
                'currency': 'RUB',
            },
            AMOUNT_FORMAT_ERROR_TEXT,
        ),
        (
            {
                'park_id': 'xxx',
                'driver_profile_id': 'yyy',
                'account_id': 'yyy',
                'factor': 'income',
                'amount': '0.0',
                'currency': 'RUB',
            },
            AMOUNT_FORMAT_ERROR_TEXT,
        ),
        (
            {
                'park_id': 'xxx',
                'driver_profile_id': 'yyy',
                'account_id': 'yyy',
                'factor': 'income',
                'amount': '1' * 17,
                'currency': 'RUB',
            },
            AMOUNT_FORMAT_ERROR_TEXT,
        ),
    ],
)
def test_post_bad_request(
        taxi_fleet_api_external, request_json, error_text, mockserver,
):
    @mockserver.json_handler(MOCK_BASE_URL)
    def mock_callback(request):
        return {}

    response = taxi_fleet_api_external.post(
        ENDPOINT_BASE_URL,
        headers=auth.HEADERS,
        data=json.dumps(request_json),
        x_real_ip=X_REAL_IP,
    )

    assert mock_callback.times_called == 0
    assert response.status_code == 400
    assert response.json() == utils.format_error(error_text)


@pytest.mark.parametrize(
    'request_json,internal_request_json',
    [
        (TRANSACTIONS_LIST_TEST_REQUEST, TRANSACTIONS_LIST_TEST_REQUEST),
        (
            {
                'query': {
                    'park': {'id': 'xxx'},
                    'driver_profile': {'id': ['yyy1', 'yyy2', 'yyy3']},
                    'document': {
                        'date_from': '2019-02-05T08:04:14.517+0000',
                        'date_to': '2019-02-06T08:04:14.517+0000',
                        'factor': 'income',
                        'group': 'other',
                        'order_id': 'zzz',
                    },
                },
                'cursor': {
                    'older_than': {
                        'date': '2019-02-05T19:04:14.517+0000',
                        'id': 'vvv',
                    },
                },
                'limit': 1000,
            },
            {
                'query': {
                    'park': {'id': 'xxx'},
                    'driver': {'ids': ['yyy1', 'yyy2', 'yyy3']},
                    'document': {
                        'date_from': '2019-02-05T08:04:14.517+0000',
                        'date_to': '2019-02-06T08:04:14.517+0000',
                        'factor': 'income',
                        'group': 'other',
                        'order_id': 'zzz',
                    },
                },
                'cursor': {
                    'older_than': {
                        'date': '2019-02-05T19:04:14.517+0000',
                        'id': 'vvv',
                    },
                },
                'limit': 1000,
            },
        ),
    ],
)
def test_list_ok(
        taxi_fleet_api_external,
        request_json,
        internal_request_json,
        mockserver,
):
    ok_response = {'transactions': []}

    @mockserver.json_handler(MOCK_BASE_URL + '/list')
    def mock_callback(request):
        assert request.args.to_dict() == {}
        assert json.loads(request.get_data()) == internal_request_json
        assert request.headers['X-Real-IP'] == X_REAL_IP
        return ok_response

    response = taxi_fleet_api_external.post(
        ENDPOINT_BASE_URL + '/list',
        headers=auth.HEADERS,
        data=json.dumps(request_json),
        x_real_ip=X_REAL_IP,
    )

    assert mock_callback.times_called == 1
    assert response.status_code == 200
    assert response.json() == ok_response


def test_list_response_ok(taxi_fleet_api_external, mockserver):
    @mockserver.json_handler(MOCK_BASE_URL + '/list')
    def mock_callback(request):
        assert request.args.to_dict() == {}
        assert json.loads(request.get_data()) == TRANSACTIONS_LIST_TEST_REQUEST
        assert request.headers['X-Real-IP'] == X_REAL_IP
        return TRANSACTIONS_LIST_INTERNAL_RESPONSE

    response = taxi_fleet_api_external.post(
        ENDPOINT_BASE_URL + '/list',
        headers=auth.HEADERS,
        data=json.dumps(TRANSACTIONS_LIST_TEST_REQUEST),
        x_real_ip=X_REAL_IP,
    )

    assert mock_callback.times_called == 1
    assert response.status_code == 200
    assert response.json() == TRANSACTIONS_LIST_EXTERNAL_RESPONSE


@pytest.mark.parametrize(
    'request_json,error_text',
    [
        (
            {
                'query': {
                    'driver_profile': {'id': ['yyy1', 'yyy2', 'yyy3']},
                    'document': {
                        'date_from': '2019-02-05T08:04:14.517+0000',
                        'date_to': '2019-02-06T08:04:14.517+0000',
                        'factor': 'income',
                        'group': 'other',
                        'order_id': 'zzz',
                    },
                },
                'cursor': {
                    'older_than': {
                        'date': '2019-02-05T19:04:14.517+0000',
                        'id': 'vvv',
                    },
                },
                'limit': 1000,
            },
            'query.park must be present',
        ),
        (
            {
                'query': {
                    'park': {'id': 'xxx'},
                    'driver_profile': {'id': 'yyy'},
                },
                'limit': 1000,
            },
            'query.driver_profile.id must be an array',
        ),
        (
            {'query': {'park': {'id': 'xxx'}}, 'cursor': {}, 'limit': 1000},
            'cursor.older_than must be present',
        ),
        (
            {
                'query': {'park': {'id': 'xxx'}},
                'cursor': {'older_than': {'id': 'vvv'}},
                'limit': 1000,
            },
            'cursor.older_than.date must be present',
        ),
        (
            {
                'query': {'park': {'id': 'xxx'}},
                'cursor': {
                    'older_than': {
                        'date': '2019-02-05T19:04:14.517+0000',
                        'id': False,
                    },
                },
                'limit': 1000,
            },
            'cursor.older_than.id '
            'must be a non-empty utf-8 string without BOM',
        ),
    ],
)
def test_list_bad_request(
        taxi_fleet_api_external, request_json, error_text, mockserver,
):
    @mockserver.json_handler(MOCK_BASE_URL + '/list')
    def mock_callback(request):
        return {}

    response = taxi_fleet_api_external.post(
        ENDPOINT_BASE_URL + '/list',
        headers=auth.HEADERS,
        data=json.dumps(request_json),
    )

    assert mock_callback.times_called == 0
    assert response.status_code == 400
    assert response.json() == utils.format_error(error_text)


@pytest.mark.parametrize(
    'internal_response_json',
    [
        (
            {
                'transactions': [
                    {
                        'id': 'aaa',
                        'date': '2019-02-07T09:04:14.517+0000',
                        'balance': 12345.6789,
                        'park_id': 'ccc',
                        'driver_id': 'ddd',
                        'account_id': 'eee',
                        'factor': 'income',
                        'amount': 500.73,
                        'currency': 'RUB',
                    },
                ],
                'cursor': {},
            }
        ),
        (
            {
                'transactions': [
                    {
                        'id': 'aaa',
                        'date': '2019-02-07T09:04:14.517+0000',
                        'balance': 12345.6789,
                        'park_id': 'ccc',
                        'driver_id': 'ddd',
                        'account_id': 'eee',
                        'factor': 'income',
                        'amount': 500.73,
                        'currency': 'RUB',
                    },
                ],
                'cursor': {'older_than': {'id': 'ggg'}},
            }
        ),
        (
            {
                'transactions': [
                    {
                        'date': '2019-02-07T09:04:14.517+0000',
                        'balance': 12345.6789,
                        'park_id': 'ccc',
                        'driver_id': 'ddd',
                        'account_id': 'eee',
                        'factor': 'income',
                        'amount': 500.73,
                        'currency': 'RUB',
                    },
                ],
            }
        ),
        (
            {
                'transactions': [
                    {
                        'id': 'aaa',
                        'balance': 12345.6789,
                        'park_id': 'ccc',
                        'driver_id': 'ddd',
                        'account_id': 'eee',
                        'factor': 'income',
                        'amount': 500.73,
                        'currency': 'RUB',
                    },
                ],
            }
        ),
        (
            {
                'transactions': [
                    {
                        'id': 'aaa',
                        'date': '2019-02-07T09:04:14.517+0000',
                        'park_id': 'ccc',
                        'driver_id': 'ddd',
                        'account_id': 'eee',
                        'factor': 'income',
                        'amount': 500.73,
                        'currency': 'RUB',
                    },
                ],
            }
        ),
        (
            {
                'transactions': [
                    {
                        'id': 'aaa',
                        'date': '2019-02-07T09:04:14.517+0000',
                        'balance': 12345.6789,
                        'driver_id': 'ddd',
                        'account_id': 'eee',
                        'factor': 'income',
                        'amount': 500.73,
                        'currency': 'RUB',
                    },
                ],
            }
        ),
        (
            {
                'transactions': [
                    {
                        'id': 'aaa',
                        'date': '2019-02-07T09:04:14.517+0000',
                        'balance': 12345.6789,
                        'park_id': 'ccc',
                        'account_id': 'eee',
                        'factor': 'income',
                        'amount': 500.73,
                        'currency': 'RUB',
                    },
                ],
            }
        ),
        (
            {
                'transactions': [
                    {
                        'id': 'aaa',
                        'date': '2019-02-07T09:04:14.517+0000',
                        'balance': 12345.6789,
                        'park_id': 'ccc',
                        'driver_id': 'ddd',
                        'factor': 'income',
                        'amount': 500.73,
                        'currency': 'RUB',
                    },
                ],
            }
        ),
        (
            {
                'transactions': [
                    {
                        'id': 'aaa',
                        'date': '2019-02-07T09:04:14.517+0000',
                        'balance': 12345.6789,
                        'park_id': 'ccc',
                        'driver_id': 'ddd',
                        'account_id': 'eee',
                        'amount': 500.73,
                        'currency': 'RUB',
                    },
                ],
            }
        ),
        (
            {
                'transactions': [
                    {
                        'id': 'aaa',
                        'date': '2019-02-07T09:04:14.517+0000',
                        'balance': 12345.6789,
                        'park_id': 'ccc',
                        'driver_id': 'ddd',
                        'account_id': 'eee',
                        'factor': 'income',
                        'currency': 'RUB',
                    },
                ],
            }
        ),
        (
            {
                'transactions': [
                    {
                        'id': 'aaa',
                        'date': '2019-02-07T09:04:14.517+0000',
                        'balance': 12345.6789,
                        'park_id': 'ccc',
                        'driver_id': 'ddd',
                        'account_id': 'eee',
                        'factor': 'income',
                        'amount': 500.73,
                    },
                ],
            }
        ),
        (
            {
                'transactions': [
                    {
                        'id': 'aaa',
                        'date': '2019-02-07T09:04:14.517+0000',
                        'balance': '12345.6789',
                        'park_id': 'ccc',
                        'driver_id': 'ddd',
                        'account_id': 'eee',
                        'factor': 'income',
                        'amount': 500.73,
                        'currency': 'RUB',
                    },
                ],
            }
        ),
        (
            {
                'transactions': [
                    {
                        'id': 'aaa',
                        'date': '2019-02-07T09:04:14.517+0000',
                        'balance': 12345.6789,
                        'park_id': 'ccc',
                        'driver_id': 'ddd',
                        'account_id': 'eee',
                        'factor': 'income',
                        'amount': '500.73',
                        'currency': 'RUB',
                    },
                ],
            }
        ),
    ],
)
def test_list_internal_error(
        taxi_fleet_api_external, internal_response_json, mockserver,
):
    @mockserver.json_handler(MOCK_BASE_URL + '/list')
    def mock_callback(request):
        assert request.args.to_dict() == {}
        assert json.loads(request.get_data()) == TRANSACTIONS_LIST_TEST_REQUEST
        assert request.headers['X-Real-IP'] == X_REAL_IP
        return internal_response_json

    response = taxi_fleet_api_external.post(
        ENDPOINT_BASE_URL + '/list',
        headers=auth.HEADERS,
        data=json.dumps(TRANSACTIONS_LIST_TEST_REQUEST),
        x_real_ip=X_REAL_IP,
    )

    assert mock_callback.times_called == 1
    assert response.status_code == 500
    assert response.json() == utils.INTERNAL_ERROR
