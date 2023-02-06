import pytest

_AUTH_HEADERS = {'X-Yandex-UID': 'yandex_uid'}
_REQUEST = {
    'scooter_number': 'scooter_number1',
    'payment_method': 'payment_method1',
    'user_position': {'lat': 1.2, 'lon': 3.4},
    'scooter_position': {'lat': 5.6, 'lon': 7.8},
    'card_id': 'card_id1',
    'card_mask': 'card_mask1',
    'device_id': 'device_id1',
    'phone_verified': 'phone_verified1',
}


def _make_experiment(uid):
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
                        'predicates': [
                            {
                                'init': {
                                    'arg_name': 'rule_type',
                                    'arg_type': 'string',
                                    'value': 'user_scooters_scoring',
                                },
                                'type': 'eq',
                            },
                            {
                                'init': {
                                    'arg_name': 'uuid',
                                    'arg_type': 'string',
                                    'value': uid,
                                },
                                'type': 'eq',
                            },
                        ],
                    },
                    'type': 'all_of',
                },
                'value': {'enabled': True},
            },
        ],
    }


async def _test_base(taxi_uantifraud):
    response = await taxi_uantifraud.post(
        'v1/user/scooters_scoring', json=_REQUEST, headers=_AUTH_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {'deposit': 0}


async def test_base1(taxi_uantifraud):
    await _test_base(taxi_uantifraud)


@pytest.mark.experiments3(**_make_experiment(_AUTH_HEADERS['X-Yandex-UID']))
async def test_base2(taxi_uantifraud):
    await _test_base(taxi_uantifraud)


@pytest.mark.experiments3(**_make_experiment(_AUTH_HEADERS['X-Yandex-UID']))
async def test_args(taxi_uantifraud, testpoint):
    response = {'deposit': 666}

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
        assert data == {
            'auth_context': {
                'app_vars': {
                    'app_brand': '',
                    'app_build': '',
                    'app_name': '',
                    'app_ver': '',
                    'app_ver1': '',
                    'app_ver2': '',
                    'app_ver3': '',
                    'platform_ver1': '',
                    'platform_ver2': '',
                    'platform_ver3': '',
                },
                'flags': {
                    'has_lite': False,
                    'has_neophonish': False,
                    'has_pdd': False,
                    'has_phonish': False,
                    'has_plus_cashback': False,
                    'has_portal': False,
                    'has_social': False,
                    'has_ya_plus': False,
                    'is_portal': False,
                    'no_login': False,
                    'phone_confirm_required': False,
                },
                'is_authorized': True,
                'locale': '',
                'login_id': '',
                'personal_data': {
                    'eats_id': '',
                    'email_id': '',
                    'phone_id': '',
                },
                'remote_ip': '',
                'yandex_login': '',
                'yandex_taxi_userid': '',
                'yandex_uid': 'yandex_uid',
            },
            'auto_entity_map': {},
            'card_id': 'card_id1',
            'card_mask': 'card_mask1',
            'device_id': 'device_id1',
            'payment_method': 'payment_method1',
            'phone_verified': 'phone_verified1',
            'scooter_number': 'scooter_number1',
            'scooter_position': {'lat': 5.6, 'lon': 7.8},
            'user_position': {'lat': 1.2, 'lon': 3.4},
        }
        return response

    resp = await taxi_uantifraud.post(
        'v1/user/scooters_scoring', json=_REQUEST, headers=_AUTH_HEADERS,
    )

    assert resp.status_code == 200
    assert resp.json() == response

    assert await test_args_tp.wait_call()

    assert not script_compile_failed_tp.has_calls
    assert not script_run_failed_tp.has_calls
    assert not rule_exec_failed_tp.has_calls


@pytest.mark.experiments3(**_make_experiment(_AUTH_HEADERS['X-Yandex-UID']))
async def test_select_max_deposit(taxi_uantifraud, testpoint):
    rules_triggered = []
    test_rules_triggered = []

    rules_passed = []
    test_rules_passed = []

    @testpoint('rule_exec_triggered')
    def rule_exec_triggered_tp(rule):
        (
            test_rules_triggered if rule['test_mode'] else rules_triggered
        ).append(rule['rule_id'])

    @testpoint('rule_exec_passed')
    def rule_exec_passed_tp(rule):
        (test_rules_passed if rule['test_mode'] else rules_passed).append(
            rule['rule_id'],
        )

    @testpoint('script_compile_failed')
    def script_compile_failed_tp(_):
        pass

    @testpoint('script_run_failed')
    def script_run_failed_tp(_):
        pass

    @testpoint('rule_exec_failed')
    def rule_exec_failed_tp(_):
        pass

    resp = await taxi_uantifraud.post(
        'v1/user/scooters_scoring', json=_REQUEST, headers=_AUTH_HEADERS,
    )

    assert resp.status_code == 200
    assert resp.json() == {'deposit': 4}

    assert not script_compile_failed_tp.has_calls
    assert not script_run_failed_tp.has_calls
    assert not rule_exec_failed_tp.has_calls

    assert rule_exec_triggered_tp.has_calls
    assert rule_exec_passed_tp.has_calls

    assert rules_triggered == [
        'test_rule4',
        'test_rule3',
        'test_rule2',
        'test_rule1',
    ]
    assert test_rules_triggered == ['test_rule5']

    assert rules_passed == ['test_rule6']
    assert test_rules_passed == ['test_rule7']
