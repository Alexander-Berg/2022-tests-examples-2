import collections

import pytest


_REQUEST = {
    'card': {'bin': 'bin'},
    'order_id': 'order_id',
    'payment': {'method': 'payment_method', 'type': 'personal_wallet'},
    'platform': 'android',
    'request_id': 'request_id',
    'service_id': 124,
    'user_agent': 'user_agent',
    'transaction': {
        'amount_by_type': {
            'ride': '500.100',
            'tips': '900.2',
            'cashback': '100.3',
        },
        'currency': 'RUB',
    },
    'user': {
        'id': 'user_id',
        'ip': '127.0.0.1',
        'passport_uid': 'passport_uid',
    },
    'login_id': 'login_id',
    'billing_service': 'billing_service',
    'created': '2020-02-11T14:15:21+03:00',
    'personal_phone_id': 'personal_phone_id',
    'external_user_info': {'origin': 'origin', 'user_id': 'user_id'},
    'products': {'product1': 'product_value1', 'product2': 'product_value2'},
    'transactions_scope': 'taxi',
    'payload': {
        'field1': 'value1',
        'field2': ['value2'],
        'field3': {'field4': 'value4'},
    },
}


@pytest.fixture(name='rt_xaron_service')
def _rt_xaron_service(mockserver):
    @mockserver.json_handler('rt-xaron/')
    def _handle(request):
        expected_request_json = {
            'params': {'service': 'rtxaron'},
            'currency': 'RUB',
            'user_id': 'user_id',
            'payment_type': 'personal_wallet',
            'user_uid': 'passport_uid',
            'order_id': 'order_id',
            'user_personal_phone_id': 'personal_phone_id',
            'request_ip': '127.0.0.1',
            'user_agent': 'user_agent',
            'user_fixed_price': 142.3,
            'billing_currency_rate': 'test_billing_contract_currency_rate',
            'updated': 1614328156.789,
            'plan_transporting_distance_m': 2005.123,
            'source_geopoint': [123.123, 234.234],
            'cost': 678.901,
            'status_updated': 1614328156.956,
            'request_classes': [
                'test_request_class1',
                'test_request_class2',
                'test_request_class3',
            ],
            'driver_fixed_price': 132.35,
            'tips_value': 847.123,
            'rating_value': 5.2,
            'source_country': 'test_request_source_country',
            'nz': 'test_nz',
            'tips_type': 'test_creditcard_tips_type',
            'order_application': 'test_statistics_application',
            'plan_transporting_time_sec': 125.256,
            'performer_tariff_class': 'test_performer_tariff_class',
            'status': 'test_status',
            'db_id': 'test_performer_db_id',
            'driver_license_personal_id': (
                'test_performer_driver_license_personal_id'
            ),
            'user_locale': 'test_user_locale',
            'taxi_status': 'test_taxi_status',
            'user_device_id': 'test_device_id',
            'driver_position': [3.3, 3.3],
            'calc_method': 'test_driver_cost_calc_method',
            'created': 1614328156.639,
            'driver_uuid': 'test_performer_uuid',
            'destinations_geopoint': [[1.1, 2.2], [3.3, 4.4], [5.5, 6.6]],
            'main_card_payment_id': 'test_payment_tech_main_card_payment_id',
            'alias': 'test_performer_taxi_alias_id',
            'user_phone_id': '3db2856b7974b5db628e79a1',
            'driver_clid': 'test_performer_clid',
        }

        assert request.json == expected_request_json

        return {
            'id': 1,
            'result': [
                {'name': 'rt_xaron_rule_true', 'value': True},
                {'name': 'rt_xaron_rule_false', 'value': False},
            ],
        }


def _make_experiment():
    return {
        'name': 'uafs_js_rules_enabled',
        'match': {
            'consumers': [{'name': 'uafs_js_rule'}],
            'predicate': {'type': 'true'},
            'enabled': True,
        },
        'clauses': [
            {
                'predicate': {
                    'init': {
                        'arg_name': 'rule_type',
                        'arg_type': 'string',
                        'value': 'payment',
                    },
                    'type': 'eq',
                },
                'value': {'enabled': True},
            },
        ],
    }


@pytest.mark.parametrize(
    'req,exp',
    [
        (
            _REQUEST,
            {
                'card': {'bin': 'bin'},
                'order_id': 'order_id',
                'payment': {
                    'method': 'payment_method',
                    'type': 'personal_wallet',
                },
                'platform': 'android',
                'request_id': 'request_id',
                'service_id': 124,
                'user_agent': 'user_agent',
                'transaction': {
                    'amount_by_type': {
                        'ride': 500.100,
                        'tips': 900.2,
                        'cashback': 100.3,
                    },
                    'currency': 'RUB',
                },
                'user': {
                    'id': 'user_id',
                    'ip': '127.0.0.1',
                    'passport_uid': 'passport_uid',
                },
                'login_id': 'login_id',
                'billing_service': 'billing_service',
                'created': '2020-02-11T11:15:21.000Z',
                'personal_phone_id': 'personal_phone_id',
                'external_user_info': {
                    'origin': 'origin',
                    'user_id': 'user_id',
                },
                'products': {
                    'product1': 'product_value1',
                    'product2': 'product_value2',
                },
                'transactions_scope': 'taxi',
                'payload': {
                    'field1': 'value1',
                    'field2': ['value2'],
                    'field3': {'field4': 'value4'},
                },
                'auto_entity_map': {},
            },
        ),
        (
            {
                'payment': {'type': 'card', 'method': 'card-x7601'},
                'request_id': 'beeb766b52bc40aa82f6974fad329942',
                'service_id': 124,
                'transaction': {
                    'amount_by_type': {'ride': '118'},
                    'currency': 'RUB',
                },
                'user': {
                    'ip': '2a02:6b8:0:232c:896d:4a46:a4a5:eeb0',
                    'passport_uid': '4003555591',
                },
                'order_id': '5b11f2652cdf46f0a29300bede641e9b',
            },
            {
                'order_id': '5b11f2652cdf46f0a29300bede641e9b',
                'payment': {'method': 'card-x7601', 'type': 'card'},
                'request_id': 'beeb766b52bc40aa82f6974fad329942',
                'service_id': 124,
                'transaction': {
                    'amount_by_type': {'ride': 118},
                    'currency': 'RUB',
                },
                'user': {
                    'ip': '2a02:6b8:0:232c:896d:4a46:a4a5:eeb0',
                    'passport_uid': '4003555591',
                },
                'auto_entity_map': {},
            },
        ),
        (
            {
                'payment': {'type': 'yandex_card', 'method': 'yandex_card_id'},
                'request_id': 'beeb766b52bc40aa82f6974fad329942',
                'service_id': 124,
                'transaction': {
                    'amount_by_type': {'ride': '118'},
                    'currency': 'RUB',
                },
                'user': {
                    'ip': '2a02:6b8:0:232c:896d:4a46:a4a5:eeb0',
                    'passport_uid': '4003555591',
                },
                'order_id': '5b11f2652cdf46f0a29300bede641e9b',
            },
            {
                'order_id': '5b11f2652cdf46f0a29300bede641e9b',
                'payment': {'method': 'yandex_card_id', 'type': 'yandex_card'},
                'request_id': 'beeb766b52bc40aa82f6974fad329942',
                'service_id': 124,
                'transaction': {
                    'amount_by_type': {'ride': 118},
                    'currency': 'RUB',
                },
                'user': {
                    'ip': '2a02:6b8:0:232c:896d:4a46:a4a5:eeb0',
                    'passport_uid': '4003555591',
                },
                'auto_entity_map': {},
            },
        ),
        (
            {
                'payment': {'type': 'sbp', 'method': 'sbp_qr'},
                'request_id': 'beeb766b52bc40aa82f6974fad329942',
                'service_id': 124,
                'transaction': {
                    'amount_by_type': {'ride': '118'},
                    'currency': 'RUB',
                },
                'user': {
                    'ip': '2a02:6b8:0:232c:896d:4a46:a4a5:eeb0',
                    'passport_uid': '4003555591',
                },
                'order_id': '5b11f2652cdf46f0a29300bede641e9b',
            },
            {
                'order_id': '5b11f2652cdf46f0a29300bede641e9b',
                'payment': {'type': 'sbp', 'method': 'sbp_qr'},
                'request_id': 'beeb766b52bc40aa82f6974fad329942',
                'service_id': 124,
                'transaction': {
                    'amount_by_type': {'ride': 118},
                    'currency': 'RUB',
                },
                'user': {
                    'ip': '2a02:6b8:0:232c:896d:4a46:a4a5:eeb0',
                    'passport_uid': '4003555591',
                },
                'auto_entity_map': {},
            },
        ),
    ],
)
@pytest.mark.experiments3(**_make_experiment())
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='uafs_js_rules_exp_exec_payment_to_skip_or_not_to_skip',
    consumers=['uafs/js_rules_exp_exec'],
    clauses=[],
    default_value={'rules': ['test_not_skipped_rule1']},
)
@pytest.mark.config(UAFS_JS_RULES_EXP_EXEC_ENABLED=['test_skipped_rule1'])
async def test_base(taxi_uantifraud, testpoint, req, exp):
    triggered_rules = collections.defaultdict(int)
    skipped_rules = collections.defaultdict(int)

    @testpoint('script_compile_failed')
    def script_compile_failed_tp(_):
        pass

    @testpoint('script_run_failed')
    def script_run_failed_tp(_):
        pass

    @testpoint('rule_exec_failed')
    def rule_exec_failed_tp(_):
        pass

    @testpoint('rule_exec_triggered')
    def rule_exec_triggered_tp(args):  # pylint: disable=W0612
        triggered_rules[args['rule_id']] += 1

    @testpoint('rule_exec_disabled_by_exps')
    def rule_exec_disabled_by_exps_tp(args):  # pylint: disable=W0612
        skipped_rules[args['rule_id']] += 1

    @testpoint('test_args')
    def test_args_tp(data):
        assert data == exp
        return {'status': 'block'}

    async def _test():
        resp = await taxi_uantifraud.post('/v1/payment/check', json=req)
        assert resp.status_code == 200
        assert resp.json() == {'status': 'block'}

        await test_args_tp.wait_call()

        assert not script_compile_failed_tp.has_calls
        assert not script_run_failed_tp.has_calls
        assert not rule_exec_failed_tp.has_calls

    for _ in range(10):
        await _test()
        await taxi_uantifraud.invalidate_caches()

    for _ in range(10):
        await _test()

    assert triggered_rules == {'test_rule1': 20, 'test_not_skipped_rule1': 20}
    assert skipped_rules == {'test_skipped_rule1': 20}


@pytest.mark.experiments3(**_make_experiment())
async def test_auto_entity_map(taxi_uantifraud, testpoint):
    @testpoint('script_compile_failed')
    def script_compile_failed_tp(_):
        pass

    @testpoint('script_run_failed')
    def script_run_failed_tp(_):
        pass

    @testpoint('rule_exec_failed')
    def rule_exec_failed_tp(_):
        pass

    async def _test():
        resp = await taxi_uantifraud.post('/v1/payment/check', json=_REQUEST)
        assert resp.status_code == 200
        assert resp.json() == {'status': 'allow'}

        assert not script_compile_failed_tp.has_calls
        assert not script_run_failed_tp.has_calls
        assert not rule_exec_failed_tp.has_calls

    for _ in range(10):
        await _test()
        await taxi_uantifraud.invalidate_caches()

    for _ in range(10):
        await _test()


@pytest.mark.parametrize(
    'req,exp',
    [
        (
            {
                'card': {'bin': 'bin'},
                'order_id': 'order_id',
                'payment': {
                    'method': 'payment_method',
                    'type': 'personal_wallet',
                },
                'platform': 'android',
                'request_id': 'request_id',
                'service_id': 124,
                'user_agent': 'user_agent',
                'transaction': {
                    'amount_by_type': {
                        'ride': '500.100',
                        'tips': '900.2',
                        'cashback': '100.3',
                    },
                    'currency': 'RUB',
                },
                'user': {
                    'id': 'user_id',
                    'ip': '127.0.0.1',
                    'passport_uid': 'passport_uid',
                },
                'login_id': 'login_id',
                'billing_service': 'billing_service',
                'created': '2020-02-11T14:15:21.123456+03:00',
                'personal_phone_id': 'personal_phone_id',
                'external_user_info': {
                    'origin': 'origin',
                    'user_id': 'user_id',
                },
                'products': {
                    'product1': 'product_value1',
                    'product2': 'product_value2',
                },
                'transactions_scope': 'taxi',
                'payload': {
                    'order_city': 'test_city',
                    'main_card_persistent_id': (
                        'test_payment_tech_main_card_persistent_id'
                    ),
                    'performer_driver_id': (
                        'test_performer_clid_test_performer_uuid'
                    ),
                    'sum_to_pay_tips': 123.456,
                    'sum_to_pay_ride': 234.567,
                    'plan_order_cost': 132.354,
                    'request_destinations_count': 3,
                    'travel_time_s': 12300.123,
                    'travel_distance_m': 3123.123,
                    'uid_creation_dt': '2021-02-26T08:28:21+0000',
                    'car_number': 'test_performer_car_number',
                    'user_phone_id': '3db2856b7974b5db628e79a1',
                    'user_fixed_price': 142.3,
                    'billing_currency_rate': (
                        'test_billing_contract_currency_rate'
                    ),
                    'updated': 1614328156.789,
                    'plan_transporting_distance_m': 2005.123,
                    'source_geopoint': [123.123, 234.234],
                    'order_cost': 678.901,
                    'status_updated': 1614328156.956,
                    'driver_fixed_price': 132.35,
                    'request_classes': [
                        'test_request_class1',
                        'test_request_class2',
                        'test_request_class3',
                    ],
                    'tips_value': 847.123,
                    'rating_value': 5.2,
                    'source_country': 'test_request_source_country',
                    'nearest_zone': 'test_nz',
                    'tips_type': 'test_creditcard_tips_type',
                    'application': 'test_statistics_application',
                    'plan_transporting_time_s': 125.256,
                    'order_tariff': 'test_performer_tariff_class',
                    'status': 'test_status',
                    'performer_db_id': 'test_performer_db_id',
                    'driver_license_personal_id': (
                        'test_performer_driver_license_personal_id'
                    ),
                    'user_locale': 'test_user_locale',
                    'taxi_status': 'test_taxi_status',
                    'device_id': 'test_device_id',
                    'driver_position': [3.3, 3.3],
                    'driver_cost_calc_method': 'test_driver_cost_calc_method',
                    'created': 1614328156.639,
                    'performer_uuid': 'test_performer_uuid',
                    'request_destinations_geopoints': [
                        [1.1, 2.2],
                        [3.3, 4.4],
                        [5.5, 6.6],
                    ],
                    'main_card_payment_id': (
                        'test_payment_tech_main_card_payment_id'
                    ),
                    'alias_id': 'test_performer_taxi_alias_id',
                    'performer_clid': 'test_performer_clid',
                },
            },
            {
                'card': {'bin': 'bin'},
                'order_id': 'order_id',
                'payment': {
                    'method': 'payment_method',
                    'type': 'personal_wallet',
                },
                'platform': 'android',
                'request_id': 'request_id',
                'service_id': 124,
                'user_agent': 'user_agent',
                'transaction': {
                    'amount_by_type': {
                        'ride': 500.100,
                        'tips': 900.2,
                        'cashback': 100.3,
                    },
                    'currency': 'RUB',
                },
                'user': {
                    'id': 'user_id',
                    'ip': '127.0.0.1',
                    'passport_uid': 'passport_uid',
                },
                'login_id': 'login_id',
                'billing_service': 'billing_service',
                'created': '2020-02-11T11:15:21.123Z',
                'personal_phone_id': 'personal_phone_id',
                'external_user_info': {
                    'origin': 'origin',
                    'user_id': 'user_id',
                },
                'products': {
                    'product1': 'product_value1',
                    'product2': 'product_value2',
                },
                'transactions_scope': 'taxi',
                'rt_xaron': ['rt_xaron_rule_true'],
                'payload': {
                    'order_city': 'test_city',
                    'main_card_persistent_id': (
                        'test_payment_tech_main_card_persistent_id'
                    ),
                    'performer_driver_id': (
                        'test_performer_clid_test_performer_uuid'
                    ),
                    'sum_to_pay_tips': 123.456,
                    'sum_to_pay_ride': 234.567,
                    'plan_order_cost': 132.354,
                    'request_destinations_count': 3,
                    'travel_time_s': 12300.123,
                    'travel_distance_m': 3123.123,
                    'uid_creation_dt': '2021-02-26T08:28:21+0000',
                    'car_number': 'test_performer_car_number',
                    'user_phone_id': '3db2856b7974b5db628e79a1',
                    'user_fixed_price': 142.3,
                    'billing_currency_rate': (
                        'test_billing_contract_currency_rate'
                    ),
                    'updated': 1614328156.789,
                    'plan_transporting_distance_m': 2005.123,
                    'source_geopoint': [123.123, 234.234],
                    'order_cost': 678.901,
                    'status_updated': 1614328156.956,
                    'driver_fixed_price': 132.35,
                    'request_classes': [
                        'test_request_class1',
                        'test_request_class2',
                        'test_request_class3',
                    ],
                    'tips_value': 847.123,
                    'rating_value': 5.2,
                    'source_country': 'test_request_source_country',
                    'nearest_zone': 'test_nz',
                    'tips_type': 'test_creditcard_tips_type',
                    'application': 'test_statistics_application',
                    'plan_transporting_time_s': 125.256,
                    'order_tariff': 'test_performer_tariff_class',
                    'status': 'test_status',
                    'performer_db_id': 'test_performer_db_id',
                    'driver_license_personal_id': (
                        'test_performer_driver_license_personal_id'
                    ),
                    'user_locale': 'test_user_locale',
                    'taxi_status': 'test_taxi_status',
                    'device_id': 'test_device_id',
                    'driver_position': [3.3, 3.3],
                    'driver_cost_calc_method': 'test_driver_cost_calc_method',
                    'created': 1614328156.639,
                    'performer_uuid': 'test_performer_uuid',
                    'request_destinations_geopoints': [
                        [1.1, 2.2],
                        [3.3, 4.4],
                        [5.5, 6.6],
                    ],
                    'main_card_payment_id': (
                        'test_payment_tech_main_card_payment_id'
                    ),
                    'alias_id': 'test_performer_taxi_alias_id',
                    'performer_clid': 'test_performer_clid',
                },
                'auto_entity_map': {},
            },
        ),
    ],
)
@pytest.mark.experiments3(**_make_experiment())
@pytest.mark.config(UAFS_PAYMENT_RT_XARON_ENABLED=True)
async def test_rt_xaron(
        taxi_uantifraud, testpoint, req, exp, rt_xaron_service,
):
    @testpoint('script_compile_failed')
    def script_compile_failed_tp(_):
        pass

    @testpoint('script_run_failed')
    def script_run_failed_tp(_):
        pass

    @testpoint('rule_exec_failed')
    def rule_exec_failed_tp(_):
        pass

    @testpoint('test_args')
    def test_args_tp(data):
        assert data == exp
        return {'status': 'block'}

    async def _test():
        resp = await taxi_uantifraud.post('/v1/payment/check', json=req)
        assert resp.status_code == 200
        assert resp.json() == {'status': 'block'}

        await test_args_tp.wait_call()

        assert not script_compile_failed_tp.has_calls
        assert not script_run_failed_tp.has_calls
        assert not rule_exec_failed_tp.has_calls

    for _ in range(10):
        await _test()
        await taxi_uantifraud.invalidate_caches()

    for _ in range(10):
        await _test()
