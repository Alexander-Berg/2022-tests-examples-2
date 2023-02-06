import datetime

import pytest


def check_response_status_code(
        taxi_antifraud, request_params, expected_status_code,
):
    response = taxi_antifraud.post(
        'v1/subventions/change_billing_status', json=request_params,
    )

    assert response.status_code == expected_status_code


def check_collection_content(collection, request_params, expected_content):
    actual = collection.find(
        {
            'billing_id': request_params['billing_id'],
            'statuses.antifraud_id': request_params['antifraud_id'],
        },
    )
    assert [
        {
            'billing_id': record['billing_id'],
            'billing_request': record['billing_request'],
            'statuses': record['statuses'],
            'subvention_type': record['subvention_type'],
            'updated': record['updated'],
        }
        for record in actual
    ] == expected_content


@pytest.mark.config(
    AFS_CHANGE_BILLING_STATUS_RESTRICT_NON_POSITIVE_SUBVENTIONS_BLOCKS=True,
)
@pytest.mark.parametrize(
    'request_params,expected_status_code,'
    'expected_db_records,expected_db_records_only_blocked',
    [
        (
            {
                'billing_id': 'doc_id/1681221250040',
                'antifraud_id': 'b29a1cfc9deccb6454db7d0800efc3ae',
                'action': 'pay',
            },
            200,
            [
                {
                    'billing_id': 'doc_id/1681221250040',
                    'billing_request': {
                        'order': {
                            'city': 'Воронеж',
                            'due': '2020-02-20T21:04:00.000000+00:00',
                            'license': '3613635396',
                            'order_id': '9cc637e0414f37c59b6dc7f6379f557e',
                            'time_zone': 'Europe/Moscow',
                            'zone': 'voronezh',
                        },
                        'subvention': {'amount': '100.0'},
                    },
                    'statuses': [
                        {
                            'antifraud_id': 'b29a1cfc9deccb6454db7d0800efc3ae',
                            'created': datetime.datetime(2019, 1, 9, 22, 0),
                            'payment_status': 'block',
                        },
                        {
                            'antifraud_id': 'b29a1cfc9deccb6454db7d0800efc3ae',
                            'created': datetime.datetime(2020, 4, 1, 22, 0),
                            'payment_status': 'pay',
                        },
                    ],
                    'subvention_type': 'order',
                    'updated': datetime.datetime(2020, 4, 1, 22, 0),
                },
            ],
            [
                {
                    'billing_id': 'doc_id/1681221250040',
                    'billing_request': {
                        'order': {
                            'city': 'Воронеж',
                            'due': '2020-02-20T21:04:00.000000+00:00',
                            'license': '3613635396',
                            'order_id': '9cc637e0414f37c59b6dc7f6379f557e',
                            'time_zone': 'Europe/Moscow',
                            'zone': 'voronezh',
                        },
                        'subvention': {'amount': '100.0'},
                    },
                    'statuses': [
                        {
                            'antifraud_id': 'b29a1cfc9deccb6454db7d0800efc3ae',
                            'created': datetime.datetime(2019, 1, 9, 22, 0),
                            'payment_status': 'block',
                        },
                        {
                            'antifraud_id': 'b29a1cfc9deccb6454db7d0800efc3ae',
                            'created': datetime.datetime(2020, 4, 1, 22, 0),
                            'payment_status': 'pay',
                        },
                    ],
                    'subvention_type': 'order',
                    'updated': datetime.datetime(2020, 4, 1, 22, 0),
                },
            ],
        ),
        (
            {
                'billing_id': 'doc_id/1681221250040_only_in_blocked',
                'antifraud_id': 'b29a1cfc9deccb_only_in_blocked',
                'action': 'pay',
            },
            200,
            [],
            [
                {
                    'billing_id': 'doc_id/1681221250040_only_in_blocked',
                    'billing_request': {
                        'order': {
                            'city': 'Воронеж',
                            'due': '2020-02-20T21:04:00.000000+00:00',
                            'license': '3613635396',
                            'order_id': '9cc637e0414f37c59b6dc7f6379f557e',
                            'time_zone': 'Europe/Moscow',
                            'zone': 'voronezh',
                        },
                        'subvention': {'amount': '100.0'},
                    },
                    'statuses': [
                        {
                            'antifraud_id': 'b29a1cfc9deccb_only_in_blocked',
                            'created': datetime.datetime(2019, 1, 9, 22, 0),
                            'payment_status': 'block',
                        },
                        {
                            'antifraud_id': 'b29a1cfc9deccb_only_in_blocked',
                            'created': datetime.datetime(2020, 4, 1, 22, 0),
                            'payment_status': 'pay',
                        },
                    ],
                    'subvention_type': 'order',
                    'updated': datetime.datetime(2020, 4, 1, 22, 0),
                },
            ],
        ),
        (
            {
                'billing_id': 'doc_id/1681221250040_only_in_usual',
                'antifraud_id': 'b29a1cfc9deccb_only_in_usual',
                'action': 'pay',
            },
            200,
            [
                {
                    'billing_id': 'doc_id/1681221250040_only_in_usual',
                    'billing_request': {
                        'order': {
                            'city': 'Воронеж',
                            'due': '2020-02-20T21:04:00.000000+00:00',
                            'license': '3613635396',
                            'order_id': '9cc637e0414f37c59b6dc7f6379f557e',
                            'time_zone': 'Europe/Moscow',
                            'zone': 'voronezh',
                        },
                        'subvention': {'amount': '100.0'},
                    },
                    'statuses': [
                        {
                            'antifraud_id': 'b29a1cfc9deccb_only_in_usual',
                            'created': datetime.datetime(2019, 1, 9, 22, 0),
                            'payment_status': 'pay',
                        },
                        {
                            'antifraud_id': 'b29a1cfc9deccb_only_in_usual',
                            'created': datetime.datetime(2020, 4, 1, 22, 0),
                            'payment_status': 'pay',
                        },
                    ],
                    'subvention_type': 'order',
                    'updated': datetime.datetime(2020, 4, 1, 22, 0),
                },
            ],
            [],
        ),
        (
            {
                'billing_id': 'doc_id/1681221250040_nonexistent',
                'antifraud_id': 'b29a1cfc9deccb6454db7d0800efc3ae_nonexistent',
                'action': 'pay',
            },
            200,
            [],
            [],
        ),
        (
            {
                'billing_id': 'doc_id/1681221250040',
                'antifraud_id': 'b29a1cfc9deccb6454db7d0800efc3ae',
                'subvention_type': 'order',
                'rule_id': 'collusion',
                'billing_request': {
                    'order_id': '905e68c7f949114a9b80b2397616d751',
                    'subvention': {'amount': '100.0'},
                },
                'action': 'block',
            },
            200,
            [
                {
                    'billing_id': 'doc_id/1681221250040',
                    'billing_request': {
                        'order': {
                            'city': 'Воронеж',
                            'due': '2020-02-20T21:04:00.000000+00:00',
                            'license': '3613635396',
                            'order_id': '9cc637e0414f37c59b6dc7f6379f557e',
                            'time_zone': 'Europe/Moscow',
                            'zone': 'voronezh',
                        },
                        'subvention': {'amount': '100.0'},
                    },
                    'statuses': [
                        {
                            'antifraud_id': 'b29a1cfc9deccb6454db7d0800efc3ae',
                            'created': datetime.datetime(2019, 1, 9, 22, 0),
                            'payment_status': 'block',
                        },
                        {
                            'additional_params': {'rule_id': 'collusion'},
                            'antifraud_id': 'b29a1cfc9deccb6454db7d0800efc3ae',
                            'created': datetime.datetime(2020, 4, 1, 22, 0),
                            'payment_status': 'block',
                        },
                    ],
                    'subvention_type': 'order',
                    'updated': datetime.datetime(2020, 4, 1, 22, 0),
                },
            ],
            [
                {
                    'billing_id': 'doc_id/1681221250040',
                    'billing_request': {
                        'order': {
                            'city': 'Воронеж',
                            'due': '2020-02-20T21:04:00.000000+00:00',
                            'license': '3613635396',
                            'order_id': '9cc637e0414f37c59b6dc7f6379f557e',
                            'time_zone': 'Europe/Moscow',
                            'zone': 'voronezh',
                        },
                        'subvention': {'amount': '100.0'},
                    },
                    'statuses': [
                        {
                            'antifraud_id': 'b29a1cfc9deccb6454db7d0800efc3ae',
                            'created': datetime.datetime(2019, 1, 9, 22, 0),
                            'payment_status': 'block',
                        },
                        {
                            'additional_params': {'rule_id': 'collusion'},
                            'antifraud_id': 'b29a1cfc9deccb6454db7d0800efc3ae',
                            'created': datetime.datetime(2020, 4, 1, 22, 0),
                            'payment_status': 'block',
                        },
                    ],
                    'subvention_type': 'order',
                    'updated': datetime.datetime(2020, 4, 1, 22, 0),
                },
            ],
        ),
        (
            {
                'billing_id': 'doc_id/1681221250040_only_in_usual',
                'antifraud_id': 'b29a1cfc9deccb_only_in_usual',
                'subvention_type': 'order',
                'rule_id': 'collusion',
                'billing_request': {
                    'order': {
                        'city': 'Воронеж',
                        'due': '2020-02-20T21:04:00.000000+00:00',
                        'license': '3613635396',
                        'order_id': '9cc637e0414f37c59b6dc7f6379f557e',
                        'time_zone': 'Europe/Moscow',
                        'zone': 'voronezh',
                    },
                    'subvention': {'amount': '100.0'},
                },
                'action': 'block',
            },
            200,
            [
                {
                    'billing_id': 'doc_id/1681221250040_only_in_usual',
                    'billing_request': {
                        'order': {
                            'city': 'Воронеж',
                            'due': '2020-02-20T21:04:00.000000+00:00',
                            'license': '3613635396',
                            'order_id': '9cc637e0414f37c59b6dc7f6379f557e',
                            'time_zone': 'Europe/Moscow',
                            'zone': 'voronezh',
                        },
                        'subvention': {'amount': '100.0'},
                    },
                    'statuses': [
                        {
                            'antifraud_id': 'b29a1cfc9deccb_only_in_usual',
                            'created': datetime.datetime(2019, 1, 9, 22, 0),
                            'payment_status': 'pay',
                        },
                        {
                            'additional_params': {'rule_id': 'collusion'},
                            'antifraud_id': 'b29a1cfc9deccb_only_in_usual',
                            'created': datetime.datetime(2020, 4, 1, 22, 0),
                            'payment_status': 'block',
                        },
                    ],
                    'subvention_type': 'order',
                    'updated': datetime.datetime(2020, 4, 1, 22, 0),
                },
            ],
            [
                {
                    'billing_id': 'doc_id/1681221250040_only_in_usual',
                    'billing_request': {
                        'order': {
                            'city': 'Воронеж',
                            'due': '2020-02-20T21:04:00.000000+00:00',
                            'license': '3613635396',
                            'order_id': '9cc637e0414f37c59b6dc7f6379f557e',
                            'time_zone': 'Europe/Moscow',
                            'zone': 'voronezh',
                        },
                        'subvention': {'amount': '100.0'},
                    },
                    'statuses': [
                        {
                            'additional_params': {'rule_id': 'collusion'},
                            'antifraud_id': 'b29a1cfc9deccb_only_in_usual',
                            'created': datetime.datetime(2020, 4, 1, 22, 0),
                            'payment_status': 'block',
                        },
                    ],
                    'subvention_type': 'order',
                    'updated': datetime.datetime(2020, 4, 1, 22, 0),
                },
            ],
        ),
        (
            {
                'billing_id': 'doc_id/1681221250040_zero_amount',
                'antifraud_id': 'b29a1cfc9deccb_zero_amount',
                'subvention_type': 'order',
                'rule_id': 'some_rule_id',
                'billing_request': {
                    'order_id': '905e68c7f949114a9b80b2397616d751',
                    'subvention': {'amount': '0.0'},
                },
                'action': 'block',
            },
            200,
            [
                {
                    'billing_id': 'doc_id/1681221250040_zero_amount',
                    'billing_request': {
                        'order': {
                            'city': 'Воронеж',
                            'due': '2020-02-20T21:04:00.000000+00:00',
                            'license': '3613635396',
                            'order_id': '9cc637e0414f37c59b6dc7f6379f557e',
                            'time_zone': 'Europe/Moscow',
                            'zone': 'voronezh',
                        },
                        'subvention': {'amount': '0.0'},
                    },
                    'statuses': [
                        {
                            'antifraud_id': 'b29a1cfc9deccb_zero_amount',
                            'created': datetime.datetime(2019, 1, 9, 22, 0),
                            'payment_status': 'pay',
                        },
                    ],
                    'subvention_type': 'order',
                    'updated': datetime.datetime(2019, 1, 9, 22, 0),
                },
            ],
            [],
        ),
        (
            {
                'billing_id': 'doc_id/1681221250040_negative_amount',
                'antifraud_id': 'b29a1cfc9deccb_negative_amount',
                'subvention_type': 'order',
                'rule_id': 'some_rule_id',
                'billing_request': {
                    'order_id': '905e68c7f949114a9b80b2397616d751',
                    'subvention': {'amount': '-100.0'},
                },
                'action': 'block',
            },
            200,
            [
                {
                    'billing_id': 'doc_id/1681221250040_negative_amount',
                    'billing_request': {
                        'order': {
                            'city': 'Воронеж',
                            'due': '2020-02-20T21:04:00.000000+00:00',
                            'license': '3613635396',
                            'order_id': '9cc637e0414f37c59b6dc7f6379f557e',
                            'time_zone': 'Europe/Moscow',
                            'zone': 'voronezh',
                        },
                        'subvention': {'amount': '-100.0'},
                    },
                    'statuses': [
                        {
                            'antifraud_id': 'b29a1cfc9deccb_negative_amount',
                            'created': datetime.datetime(2019, 1, 9, 22, 0),
                            'payment_status': 'pay',
                        },
                    ],
                    'subvention_type': 'order',
                    'updated': datetime.datetime(2019, 1, 9, 22, 0),
                },
            ],
            [],
        ),
    ],
)
@pytest.mark.now('2020-04-01T22:00:00+0000')
def test_subventions_change_billing_status(
        taxi_antifraud,
        mockserver,
        db,
        request_params,
        expected_status_code,
        expected_db_records,
        expected_db_records_only_blocked,
):
    @mockserver.json_handler('/billing_orders/v1/antifraud')
    def mock_billing(request):
        return {'doc': {'id': 1001}}

    check_response_status_code(
        taxi_antifraud, request_params, expected_status_code,
    )

    check_collection_content(
        db.antifraud_subventions_check_status,
        request_params,
        expected_db_records,
    )

    check_collection_content(
        db.antifraud_subventions_check_status_only_blocked,
        request_params,
        expected_db_records_only_blocked,
    )


def test_subventions_change_billing_status_500(taxi_antifraud, mockserver):
    @mockserver.json_handler('/billing_orders/v1/antifraud')
    def mock_billing(request):
        return mockserver.make_response('BadRequest', status=400)

    check_response_status_code(
        taxi_antifraud,
        {
            'billing_id': 'doc_id/1681221250040',
            'antifraud_id': 'b29a1cfc9deccb6454db7d0800efc3ae',
            'action': 'pay',
        },
        500,
    )


@pytest.mark.parametrize(
    'request_params,expected_status_code',
    [
        (
            {
                'billing_id': 'doc_id/1681221250040',
                'antifraud_id': 'b29a1cfc9deccb6454db7d0800efc3ae',
                'action': 'delay',
            },
            501,
        ),
    ],
)
def test_subventions_change_billing_status_not_implemented(
        taxi_antifraud, request_params, expected_status_code,
):
    check_response_status_code(
        taxi_antifraud, request_params, expected_status_code,
    )


@pytest.mark.parametrize(
    'request_params,expected_status_code',
    [
        (
            {
                'antifraud_id': 'b29a1cfc9deccb6454db7d0800efc3ae',
                'action': 'pay',
            },
            400,
        ),
        ({'billing_id': 'doc_id/1681221250040', 'action': 'pay'}, 400),
        (
            {
                'billing_id': 'doc_id/1681221250040',
                'antifraud_id': 'b29a1cfc9deccb6454db7d0800efc3ae',
            },
            400,
        ),
        (
            {
                'billing_id': 'doc_id/1681221250040',
                'antifraud_id': 'b29a1cfc9deccb6454db7d0800efc3ae',
                'action': 'ksdfjh',
            },
            400,
        ),
        (
            {
                'billing_id': 'doc_id/1681221250040',
                'antifraud_id': 'b29a1cfc9deccb6454db7d0800efc3ae',
                'subvention_type': 'order',
                'rule_id': 'collusion',
                'action': 'block',
            },
            400,
        ),
        (
            {
                'billing_id': 'doc_id/1681221250040',
                'antifraud_id': 'b29a1cfc9deccb6454db7d0800efc3ae',
                'subvention_type': 'order',
                'billing_request': {
                    'order_id': '905e68c7f949114a9b80b2397616d751',
                },
                'action': 'block',
            },
            400,
        ),
        (
            {
                'billing_id': 'doc_id/1681221250040',
                'antifraud_id': 'b29a1cfc9deccb6454db7d0800efc3ae',
                'rule_id': 'collusion',
                'billing_request': {
                    'order_id': '905e68c7f949114a9b80b2397616d751',
                },
                'action': 'block',
            },
            400,
        ),
    ],
)
def test_subventions_change_billing_status_bad_request(
        taxi_antifraud, request_params, expected_status_code,
):
    check_response_status_code(
        taxi_antifraud, request_params, expected_status_code,
    )
