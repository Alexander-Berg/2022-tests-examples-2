# pylint: disable=too-many-lines
import pytest


@pytest.mark.now('2019-11-11T12:00:00+0')
@pytest.mark.pgsql('persey_payments', files=['simple.sql'])
@pytest.mark.parametrize(
    [
        'order_id',
        'yandex_uid',
        'expected_zone_name',
        'stq_kwargs',
        'expected_invoice_create_request',
        'expected_invoice_update_request',
        'expected_ride_subs',
        'expected_events',
        'expected_donations',
        'zalogin_resp',
        'zalogin_no_uid',
        'invoice_retrieved',
        'invoice_started',
        'stq_delay',
        'stq_rescheduled',
        'zalogin_called',
        'expected_paid_orders',
    ],
    [
        (
            'order777',
            'phonish_uid',
            'moscow',
            {
                'order_id': 'order777',
                'user_id': 'some_taxi_user_id',
                'phone_id': {'$oid': 'af35af35af35af35af35af35'},
                'application': 'android',
                'nearest_zone': 'moscow',
                'user_uid': 'phonish_uid',
                'payment_tech_type': 'card',
                'payment_method_id': 'card-x66dd38a35cca9fd90a1bcaf6',
                'payment_billing_id': '',
                'account_type': 'phonish',
                'user_ip': '127.0.0.1',
                'user_locale': 'ru',
                'created_at': '2020-07-01T00:00:00+0000',
            },
            'expected_invoice_create_request_phonish.json',
            'expected_invoice_update_request.json',
            'expected_ride_subs_phonish.json',
            'expected_events_phonish.json',
            [
                (
                    'friends',
                    'phonish_uid',
                    '5',
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    1,
                    'yataxi',
                    'order777',
                    'started',
                ),
            ],
            None,
            False,
            1,
            1,
            None,
            0,
            0,
            [['order777', '5.0000']],
        ),
        (
            'order777',
            'portal_uid',
            'moscow',
            {
                'order_id': 'order777',
                'user_id': 'some_taxi_user_id',
                'phone_id': {'$oid': 'cccccccccccccccccccccccc'},
                'application': 'android',
                'nearest_zone': 'moscow',
                'user_uid': 'portal_uid',
                'payment_tech_type': 'card',
                'payment_method_id': 'card-x66dd38a35cca9fd90a1bcaf6',
                'payment_billing_id': 'x66dd38a35cca9fd90a1bcaf6',
                'account_type': 'portal',
                'user_ip': '127.0.0.1',
                'user_locale': 'ru',
                'created_at': '2020-07-01T00:00:00+0000',
            },
            'expected_invoice_create_request_portal.json',
            'expected_invoice_update_request.json',
            'expected_ride_subs_portal.json',
            'expected_events_portal.json',
            [
                (
                    'friends',
                    'portal_uid',
                    '5',
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    3,
                    'yataxi',
                    'order777',
                    'started',
                ),
            ],
            'zalogin_resp_portal.json',
            False,
            1,
            1,
            None,
            0,
            1,
            [['order777', '5.0000']],
        ),
        (
            'need_accept',
            'phonish_uid',
            'moscow',
            {
                'order_id': 'need_accept',
                'user_id': 'some_taxi_user_id',
                'phone_id': {'$oid': 'af35af35af35af35af35af35'},
                'application': 'android',
                'nearest_zone': 'moscow',
                'user_uid': 'phonish_uid',
                'payment_tech_type': 'card',
                'payment_method_id': 'card-x66dd38a35cca9fd90a1bcaf6',
                'payment_billing_id': 'x66dd38a35cca9fd90a1bcaf6',
                'account_type': 'phonish',
                'user_ip': '127.0.0.1',
                'user_locale': 'ru',
                'created_at': '2020-07-01T00:00:00+0000',
            },
            None,
            None,
            'expected_ride_subs_phonish.json',
            'expected_events_phonish.json',
            [],
            None,
            False,
            0,
            0,
            600,
            1,
            0,
            [],
        ),
        (
            'need_disp_accept',
            'phonish_uid',
            'moscow',
            {
                'order_id': 'need_disp_accept',
                'user_id': 'some_taxi_user_id',
                'phone_id': {'$oid': 'af35af35af35af35af35af35'},
                'application': 'android',
                'nearest_zone': 'moscow',
                'user_uid': 'phonish_uid',
                'payment_tech_type': 'card',
                'payment_method_id': 'card-x66dd38a35cca9fd90a1bcaf6',
                'payment_billing_id': 'x66dd38a35cca9fd90a1bcaf6',
                'account_type': 'phonish',
                'user_ip': '127.0.0.1',
                'user_locale': 'ru',
                'created_at': '2020-07-01T00:00:00+0000',
            },
            None,
            None,
            'expected_ride_subs_phonish.json',
            'expected_events_phonish.json',
            [],
            None,
            False,
            0,
            0,
            600,
            1,
            0,
            [],
        ),
        (
            'order777',
            'no_ride_subs',
            'moscow',
            {
                'order_id': 'order777',
                'user_id': 'some_taxi_user_id',
                'phone_id': {'$oid': 'af35af35af35af35af35af35'},
                'application': 'android',
                'nearest_zone': 'moscow',
                'user_uid': 'no_ride_subs',
                'payment_tech_type': 'card',
                'payment_method_id': 'card-x66dd38a35cca9fd90a1bcaf6',
                'payment_billing_id': 'x66dd38a35cca9fd90a1bcaf6',
                'account_type': 'phonish',
                'user_ip': '127.0.0.1',
                'user_locale': 'ru',
                'created_at': '2020-07-01T00:00:00+0000',
            },
            None,
            None,
            'expected_ride_subs_phonish.json',
            'expected_events_phonish.json',
            [],
            None,
            False,
            0,
            0,
            None,
            0,
            0,
            [],
        ),
        (
            'order777',
            'phonish_uid',
            'baku',
            {
                'order_id': 'order777',
                'user_id': 'some_taxi_user_id',
                'phone_id': {'$oid': 'af35af35af35af35af35af35'},
                'application': 'android',
                'nearest_zone': 'baku',
                'user_uid': 'phonish_uid',
                'payment_tech_type': 'card',
                'payment_method_id': 'card-x66dd38a35cca9fd90a1bcaf6',
                'payment_billing_id': 'x66dd38a35cca9fd90a1bcaf6',
                'account_type': 'phonish',
                'user_ip': '127.0.0.1',
                'user_locale': 'ru',
                'created_at': '2020-07-01T00:00:00+0000',
            },
            None,
            None,
            'expected_ride_subs_phonish.json',
            'expected_events_empty.json',
            [],
            None,
            False,
            0,
            0,
            None,
            0,
            0,
            [],
        ),
        (
            'order777',
            'phonish_uid',
            'elbashy',
            {
                'order_id': 'order777',
                'user_id': 'some_taxi_user_id',
                'phone_id': {'$oid': 'af35af35af35af35af35af35'},
                'application': 'android',
                'nearest_zone': 'elbashy',
                'user_uid': 'phonish_uid',
                'payment_tech_type': 'card',
                'payment_method_id': 'card-x66dd38a35cca9fd90a1bcaf6',
                'payment_billing_id': 'x66dd38a35cca9fd90a1bcaf6',
                'account_type': 'phonish',
                'user_ip': '127.0.0.1',
                'user_locale': 'ru',
                'created_at': '2020-07-01T00:00:00+0000',
            },
            None,
            None,
            'expected_ride_subs_phonish.json',
            'expected_events_empty.json',
            [],
            None,
            False,
            0,
            0,
            None,
            0,
            0,
            [],
        ),
        (
            'order777',
            'portal_uid',
            'moscow',
            {
                'order_id': 'order777',
                'user_id': 'some_taxi_user_id',
                'phone_id': {'$oid': 'cccccccccccccccccccccccc'},
                'application': 'android',
                'nearest_zone': 'moscow',
                'user_uid': 'portal_uid',
                'payment_tech_type': 'card',
                'payment_method_id': 'card-x66dd38a35cca9fd90a1bcaf6',
                'payment_billing_id': 'x66dd38a35cca9fd90a1bcaf6',
                'account_type': 'portal',
                'user_ip': '127.0.0.1',
                'user_locale': 'ru',
                'created_at': '2020-07-01T00:00:00+0000',
            },
            None,
            None,
            'expected_ride_subs_phonish.json',
            'expected_events_empty.json',
            [],
            None,
            True,
            0,
            0,
            None,
            0,
            1,
            [],
        ),
        (
            'order777',
            'portal_with_subs_uid',
            'moscow',
            {
                'order_id': 'order777',
                'user_id': 'some_taxi_user_id',
                'phone_id': {'$oid': 'cccccccccccccccccccccccc'},
                'application': 'android',
                'nearest_zone': 'moscow',
                'user_uid': 'portal_with_subs_uid',
                'payment_tech_type': 'card',
                'payment_method_id': 'card-x66dd38a35cca9fd90a1bcaf6',
                'payment_billing_id': 'x66dd38a35cca9fd90a1bcaf6',
                'account_type': 'portal',
                'user_ip': '127.0.0.1',
                'user_locale': 'ru',
                'created_at': '2020-07-01T00:00:00+0000',
            },
            'expected_invoice_create_request_no_uid_portal_with_subs.json',
            'expected_invoice_update_request.json',
            'expected_ride_subs_phonish.json',
            'expected_events_empty.json',
            [
                (
                    'friends',
                    'portal_with_subs_uid',
                    '5',
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    2,
                    'yataxi',
                    'order777',
                    'started',
                ),
            ],
            None,
            True,
            1,
            1,
            None,
            0,
            1,
            [['order777', '5.0000']],
        ),
        (
            'order777',
            'phonish_uid',
            'moscow',
            {
                'order_id': 'order777',
                'user_id': 'some_taxi_user_id',
                'phone_id': {'$oid': 'af35af35af35af35af35af35'},
                'application': 'android',
                'nearest_zone': 'moscow',
                'user_uid': 'phonish_uid',
                'payment_tech_type': 'card',
                'payment_method_id': 'card-x66dd38a35cca9fd90a1bcaf6',
                'payment_billing_id': 'x66dd38a35cca9fd90a1bcaf6',
                'account_type': None,
                'user_ip': '127.0.0.1',
                'user_locale': 'ru',
                'created_at': '2020-07-01T00:00:00+0000',
            },
            'expected_invoice_create_request_phonish.json',
            'expected_invoice_update_request.json',
            'expected_ride_subs_phonish.json',
            'expected_events_phonish.json',
            [
                (
                    'friends',
                    'phonish_uid',
                    '5',
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    1,
                    'yataxi',
                    'order777',
                    'started',
                ),
            ],
            None,
            True,
            1,
            1,
            None,
            0,
            1,
            [['order777', '5.0000']],
        ),
        (
            'order777',
            'no_ride_subs',
            'moscow',
            {
                'order_id': 'order777',
                'user_id': 'some_taxi_user_id',
                'phone_id': {'$oid': 'af35af35af35af35af35af35'},
                'application': 'android',
                'nearest_zone': 'moscow',
                'user_uid': 'no_ride_subs',
                'payment_tech_type': 'card',
                'payment_method_id': 'card-x66dd38a35cca9fd90a1bcaf6',
                'payment_billing_id': 'x66dd38a35cca9fd90a1bcaf6',
                'account_type': None,
                'user_ip': '127.0.0.1',
                'user_locale': 'ru',
                'created_at': '2020-07-01T00:00:00+0000',
            },
            None,
            None,
            'expected_ride_subs_phonish.json',
            'expected_events_phonish.json',
            [],
            None,
            True,
            0,
            0,
            None,
            0,
            1,
            [],
        ),
        (
            'not_finish_handled',
            'phonish_uid',
            'moscow',
            {
                'order_id': 'not_finish_handled',
                'user_id': 'some_taxi_user_id',
                'phone_id': {'$oid': 'af35af35af35af35af35af35'},
                'application': 'android',
                'nearest_zone': 'moscow',
                'user_uid': 'phonish_uid',
                'payment_tech_type': 'card',
                'payment_method_id': 'card-x66dd38a35cca9fd90a1bcaf6',
                'payment_billing_id': 'x66dd38a35cca9fd90a1bcaf6',
                'account_type': 'phonish',
                'user_ip': '127.0.0.1',
                'user_locale': 'ru',
                'created_at': '2019-11-11T11:00:00+0000',
            },
            None,
            None,
            'expected_ride_subs_phonish.json',
            'expected_events_phonish.json',
            [],
            None,
            False,
            0,
            0,
            30,
            1,
            0,
            [],
        ),
        (
            'not_finish_handled',
            'phonish_uid',
            'moscow',
            {
                'order_id': 'not_finish_handled',
                'user_id': 'some_taxi_user_id',
                'phone_id': {'$oid': 'af35af35af35af35af35af35'},
                'application': 'android',
                'nearest_zone': 'moscow',
                'user_uid': 'phonish_uid',
                'payment_tech_type': 'card',
                'payment_method_id': 'card-x66dd38a35cca9fd90a1bcaf6',
                'payment_billing_id': 'x66dd38a35cca9fd90a1bcaf6',
                'account_type': 'phonish',
                'user_ip': '127.0.0.1',
                'user_locale': 'ru',
                'created_at': '2019-11-11T10:59:59+0000',
            },
            None,
            None,
            'expected_ride_subs_phonish.json',
            'expected_events_phonish.json',
            [],
            None,
            False,
            0,
            0,
            None,
            0,
            0,
            [],
        ),
        (
            'nonexistent',
            'phonish_uid',
            'moscow',
            {
                'order_id': 'nonexistent',
                'user_id': 'some_taxi_user_id',
                'phone_id': {'$oid': 'af35af35af35af35af35af35'},
                'application': 'android',
                'nearest_zone': 'moscow',
                'user_uid': 'phonish_uid',
                'payment_tech_type': 'card',
                'payment_method_id': 'card-x66dd38a35cca9fd90a1bcaf6',
                'payment_billing_id': 'x66dd38a35cca9fd90a1bcaf6',
                'account_type': 'phonish',
                'user_ip': '127.0.0.1',
                'user_locale': 'ru',
                'created_at': '2019-11-11T13:00:00+0000',
            },
            None,
            None,
            'expected_ride_subs_phonish.json',
            'expected_events_phonish.json',
            [],
            None,
            False,
            0,
            0,
            None,
            0,
            0,
            [],
        ),
        pytest.param(
            'order777',
            'phonish_uid',
            'moscow',
            {
                'order_id': 'order777',
                'user_id': 'some_taxi_user_id',
                'phone_id': {'$oid': 'af35af35af35af35af35af35'},
                'application': 'android',
                'nearest_zone': 'moscow',
                'user_uid': 'phonish_uid',
                'payment_tech_type': 'card',
                'payment_method_id': 'card-x66dd38a35cca9fd90a1bcaf6',
                'payment_billing_id': 'x66dd38a35cca9fd90a1bcaf6',
                'account_type': 'phonish',
                'user_ip': '127.0.0.1',
                'user_locale': 'ru',
                'created_at': '2020-07-01T00:00:00+0000',
            },
            None,
            None,
            'expected_ride_subs_phonish.json',
            'expected_events_phonish.json',
            [
                (
                    'friends',
                    'portal_uid',
                    '5',
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    1,
                    'yataxi',
                    'order777',
                    'finished',
                ),
            ],
            None,
            False,
            1,
            0,
            None,
            0,
            0,
            [],
            marks=pytest.mark.pgsql(
                'persey_payments', files=['donation_conflict.sql'],
            ),
        ),
        (
            'order777',
            'phonish_uid',
            'moscow',
            {
                'order_id': 'order777',
                'user_id': 'some_taxi_user_id',
                'phone_id': {'$oid': 'af35af35af35af35af35af35'},
                'application': 'android',
                'nearest_zone': 'moscow',
                'user_uid': 'phonish_uid',
                'payment_tech_type': 'applepay',
                'payment_method_id': 'applepay_token_12345678',
                'payment_billing_id': '',
                'account_type': 'phonish',
                'user_ip': '127.0.0.1',
                'user_locale': 'ru',
                'created_at': '2020-07-01T00:00:00+0000',
            },
            'expected_invoice_create_request_phonish.json',
            'expected_invoice_update_request.json',
            'expected_ride_subs_phonish.json',
            'expected_events_phonish.json',
            [],
            None,
            False,
            0,
            0,
            None,
            0,
            0,
            [],
        ),
        pytest.param(
            'order777',
            'phonish_uid',
            'moscow',
            {
                'order_id': 'order777',
                'user_id': 'some_taxi_user_id',
                'phone_id': {'$oid': 'af35af35af35af35af35af35'},
                'application': 'android',
                'nearest_zone': 'moscow',
                'user_uid': 'phonish_uid',
                'payment_tech_type': 'applepay',
                'payment_method_id': 'applepay_token_12345678',
                'payment_billing_id': '',
                'account_type': 'phonish',
                'user_ip': '127.0.0.1',
                'user_locale': 'ru',
                'created_at': '2020-07-01T00:00:00+0000',
            },
            'expected_invoice_create_request_agent.json',
            'expected_invoice_update_request_agent.json',
            'expected_ride_subs_phonish.json',
            'expected_events_phonish.json',
            [
                (
                    'friends',
                    'phonish_uid',
                    '5',
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    1,
                    'yataxi',
                    'order777',
                    'started',
                ),
            ],
            None,
            False,
            1,
            1,
            None,
            0,
            0,
            [['order777', '5.0000']],
            marks=pytest.mark.config(
                PERSEY_PAYMENTS_TAXI_AGENT={
                    'terminal': {'applepay': 'taxi'},
                    'settings': {
                        'service': 's',
                        'billing_service': 'bs',
                        'pass_params': {
                            'terminal_route_data': {'description': 'taxi'},
                        },
                        'product_id': 'p_id',
                        'item_id': 'i_id',
                        'fiscal_receipt_info_title': 'frit',
                    },
                },
            ),
        ),
        pytest.param(
            'order777',
            'phonish_uid',
            'moscow',
            {
                'order_id': 'order777',
                'user_id': 'some_taxi_user_id',
                'phone_id': {'$oid': 'af35af35af35af35af35af35'},
                'application': 'android',
                'nearest_zone': 'moscow',
                'user_uid': 'phonish_uid',
                'payment_tech_type': 'applepay',
                'payment_method_id': 'applepay_token_12345678',
                'payment_billing_id': '',
                'account_type': 'phonish',
                'user_ip': '127.0.0.1',
                'user_locale': 'ru',
                'created_at': '2020-07-01T00:00:00+0000',
            },
            'expected_invoice_create_request_agent.json',
            'expected_invoice_update_request_agent.json',
            'expected_ride_subs_phonish.json',
            'expected_events_phonish.json',
            [
                (
                    'friends',
                    'phonish_uid',
                    '5',
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    1,
                    'yataxi',
                    'order777',
                    'started',
                ),
            ],
            None,
            False,
            1,
            1,
            None,
            0,
            0,
            [['order777', '5.0000']],
            marks=[
                pytest.mark.config(
                    PERSEY_PAYMENTS_TAXI_AGENT={
                        'terminal': {'applepay': 'from_experiment'},
                        'settings': {
                            'service': 's',
                            'billing_service': 'bs',
                            'pass_params': {
                                'terminal_route_data': {'description': 'taxi'},
                            },
                            'product_id': 'p_id',
                            'item_id': 'i_id',
                            'fiscal_receipt_info_title': 'frit',
                        },
                    },
                ),
                pytest.mark.client_experiments3(
                    consumer='persey-payments/ride_subs',
                    experiment_name='persey_payments_taxi_terminal',
                    args=[
                        {
                            'name': 'yandex_uid',
                            'type': 'string',
                            'value': 'phonish_uid',
                        },
                        {
                            'name': 'phone_id',
                            'type': 'string',
                            'value': 'af35af35af35af35af35af35',
                        },
                        {
                            'name': 'application',
                            'type': 'string',
                            'value': 'android',
                        },
                        {'name': 'brand', 'type': 'string', 'value': 'yataxi'},
                    ],
                    value={'terminal': {'card': 'nko', 'applepay': 'taxi'}},
                ),
            ],
        ),
        pytest.param(
            'order777',
            'phonish_uid',
            'moscow',
            {
                'order_id': 'order777',
                'user_id': 'some_taxi_user_id',
                'phone_id': {'$oid': 'af35af35af35af35af35af35'},
                'application': 'android',
                'nearest_zone': 'moscow',
                'user_uid': 'phonish_uid',
                'payment_tech_type': 'card',
                'payment_method_id': 'card-x66dd38a35cca9fd90a1bcaf6',
                'payment_billing_id': '',
                'account_type': 'phonish',
                'user_ip': '127.0.0.1',
                'user_locale': 'ru',
                'created_at': '2020-07-01T00:00:00+0000',
            },
            'expected_invoice_create_request_phonish.json',
            'expected_invoice_update_request.json',
            'expected_ride_subs_phonish.json',
            'expected_events_phonish.json',
            [
                (
                    'friends',
                    'phonish_uid',
                    '5',
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    1,
                    'yataxi',
                    'order777',
                    'started',
                ),
            ],
            None,
            False,
            1,
            1,
            None,
            0,
            0,
            [['order777', '5.0000']],
            marks=[
                pytest.mark.config(
                    PERSEY_PAYMENTS_TAXI_AGENT={
                        'terminal': {'card': 'from_experiment'},
                        'settings': {
                            'service': 's',
                            'billing_service': 'bs',
                            'pass_params': {
                                'terminal_route_data': {'description': 'taxi'},
                            },
                            'product_id': 'p_id',
                            'item_id': 'i_id',
                            'fiscal_receipt_info_title': 'frit',
                        },
                    },
                ),
                pytest.mark.client_experiments3(
                    consumer='persey-payments/ride_subs',
                    experiment_name='persey_payments_taxi_terminal',
                    args=[
                        {
                            'name': 'yandex_uid',
                            'type': 'string',
                            'value': 'phonish_uid',
                        },
                        {
                            'name': 'phone_id',
                            'type': 'string',
                            'value': 'af35af35af35af35af35af35',
                        },
                        {
                            'name': 'application',
                            'type': 'string',
                            'value': 'android',
                        },
                        {'name': 'brand', 'type': 'string', 'value': 'yataxi'},
                    ],
                    value={'terminal': {'card': 'nko', 'applepay': 'taxi'}},
                ),
            ],
        ),
        pytest.param(
            'order777',
            'phonish_uid',
            'moscow',
            {
                'order_id': 'order777',
                'user_id': 'some_taxi_user_id',
                'phone_id': {'$oid': 'af35af35af35af35af35af35'},
                'application': 'android',
                'nearest_zone': 'moscow',
                'user_uid': 'phonish_uid',
                'payment_tech_type': 'applepay',
                'payment_method_id': 'applepay_token_12345678',
                'payment_billing_id': '',
                'account_type': 'phonish',
                'user_ip': '127.0.0.1',
                'user_locale': 'ru',
                'created_at': '2020-07-01T00:00:00+0000',
            },
            'expected_invoice_create_request_agent.json',
            'expected_invoice_update_request_agent.json',
            'expected_ride_subs_phonish.json',
            'expected_events_phonish.json',
            [],
            None,
            False,
            0,
            0,
            None,
            0,
            0,
            [],
            marks=[
                pytest.mark.config(
                    PERSEY_PAYMENTS_TAXI_AGENT={
                        'terminal': {'applepay': 'from_experiment'},
                        'settings': {
                            'service': 's',
                            'billing_service': 'bs',
                            'pass_params': {
                                'terminal_route_data': {'description': 'taxi'},
                            },
                            'product_id': 'p_id',
                            'item_id': 'i_id',
                            'fiscal_receipt_info_title': 'frit',
                        },
                    },
                ),
                pytest.mark.client_experiments3(
                    consumer='persey-payments/ride_subs',
                    experiment_name='persey_payments_taxi_terminal',
                    args=[
                        {
                            'name': 'yandex_uid',
                            'type': 'string',
                            'value': 'phonish_uid',
                        },
                        {
                            'name': 'phone_id',
                            'type': 'string',
                            'value': 'af35af35af35af35af35af35',
                        },
                        {
                            'name': 'application',
                            'type': 'string',
                            'value': 'android',
                        },
                        {'name': 'brand', 'type': 'string', 'value': 'yataxi'},
                    ],
                    value={},
                ),
            ],
        ),
        pytest.param(
            'order777',
            'phonish_uid',
            'moscow',
            {
                'order_id': 'order777',
                'user_id': 'some_taxi_user_id',
                'phone_id': {'$oid': 'af35af35af35af35af35af35'},
                'application': 'android',
                'nearest_zone': 'moscow',
                'user_uid': 'phonish_uid',
                'payment_tech_type': 'applepay',
                'payment_method_id': 'applepay_token_12345678',
                'payment_billing_id': '',
                'account_type': 'phonish',
                'user_ip': '127.0.0.1',
                'user_locale': 'ru',
                'created_at': '2020-07-01T00:00:00+0000',
            },
            'expected_invoice_create_request_agent.json',
            'expected_invoice_update_request_agent.json',
            'expected_ride_subs_phonish.json',
            'expected_events_phonish.json',
            [],
            None,
            False,
            0,
            0,
            None,
            0,
            0,
            [],
            marks=[
                pytest.mark.config(
                    PERSEY_PAYMENTS_TAXI_AGENT={
                        'terminal': {'applepay': 'from_experiment'},
                        'settings': {
                            'service': 's',
                            'billing_service': 'bs',
                            'pass_params': {
                                'terminal_route_data': {'description': 'taxi'},
                            },
                            'product_id': 'p_id',
                            'item_id': 'i_id',
                            'fiscal_receipt_info_title': 'frit',
                        },
                    },
                ),
            ],
        ),
    ],
)
async def test_simple(
        mockserver,
        pgsql,
        load_json,
        stq_runner,
        get_ride_subs,
        check_ride_subs_events,
        get_ride_subs_cache,
        get_donations,
        mock_invoice_create,
        mock_invoice_update,
        mock_invoice_retrieve,
        mock_stq_reschedule,
        mock_zalogin,
        mock_tariffs,
        order_id,
        yandex_uid,
        expected_zone_name,
        stq_kwargs,
        expected_invoice_create_request,
        expected_invoice_update_request,
        expected_ride_subs,
        expected_events,
        expected_donations,
        zalogin_resp,
        zalogin_no_uid,
        invoice_retrieved,
        invoice_started,
        stq_delay,
        stq_rescheduled,
        zalogin_called,
        expected_paid_orders,
):
    invoice_create_mock = mock_invoice_create(expected_invoice_create_request)
    invoice_update_mock = mock_invoice_update(expected_invoice_update_request)
    invoice_retrieve_mock = mock_invoice_retrieve(
        order_id, 'invoice_retrieve_resp.json',
    )
    stq_reschedule = mock_stq_reschedule(
        'persey_payments_ride_subs', stq_delay,
    )
    zalogin_mock = mock_zalogin(yandex_uid, zalogin_resp, zalogin_no_uid)
    tariffs_mock = mock_tariffs(expected_zone_name)

    await stq_runner.persey_payments_ride_subs.call(
        task_id='1', args=[], kwargs=stq_kwargs,
    )

    assert invoice_retrieve_mock.times_called == invoice_retrieved
    assert invoice_create_mock.times_called == invoice_started
    assert invoice_update_mock.times_called == invoice_started
    assert stq_reschedule.times_called == stq_rescheduled
    assert zalogin_mock.times_called == zalogin_called
    assert tariffs_mock.times_called == 1
    assert get_ride_subs() == load_json(expected_ride_subs)
    check_ride_subs_events(expected_events)
    assert get_ride_subs_cache()['paid_order'] == expected_paid_orders
    assert get_donations() == expected_donations
