import copy

import pytest


_REQUEST = {
    'order_id': 'order_id1',
    'user_id': 'user_id1',
    'phone_id': 'phone_id1',
    'device_id': 'device_id1',
    'yandex_uid': 'yandex_uid1',
    'nz': 'nz1',
    'personal_phone_id': 'personal_phone_id1',
}


def _make_experiment(order_id=None):
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
                                    'value': 'payment_type_change_available',
                                },
                                'type': 'eq',
                            },
                            {
                                'init': {
                                    'arg_name': 'uuid',
                                    'arg_type': 'string',
                                    'value': (
                                        order_id
                                        if order_id is not None
                                        else _REQUEST['order_id']
                                    ),
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


@pytest.mark.parametrize(
    'tags_enabled',
    [
        False,
        pytest.param(
            True,
            marks=pytest.mark.config(
                UAFS_PAYMENT_TYPE_CHANGE_ENABLE_TAGS=True,
            ),
        ),
    ],
)
@pytest.mark.experiments3(**_make_experiment())
async def test_base(
        taxi_uantifraud, mongodb, testpoint, mockserver, tags_enabled,
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

    expected_tags = {'tag1': True, 'tag2': True}

    @testpoint('test_args')
    def test_args_tp(data):
        expected_data = copy.deepcopy(_REQUEST)
        expected_data['auto_entity_map'] = {}
        if tags_enabled:
            expected_data['passenger_tags'] = expected_tags

        assert data == expected_data
        return {'status': 'block'}

    @testpoint('pay_type_change_available_store_result_duplicate_error')
    def duplicate_tp(_):
        pass

    @mockserver.json_handler('/passenger-tags/v2/match_single')
    def _handler(request):
        assert tags_enabled
        data = request.json
        assert data == {
            'match': [
                {'type': 'personal_phone_id', 'value': 'personal_phone_id1'},
            ],
        }
        return {'tags': list(expected_tags)}

    async def _make_request():
        resp = await taxi_uantifraud.post(
            '/v1/events/order/draft', json=_REQUEST,
        )
        assert resp.status_code == 200
        assert resp.json() == {}

    def _check_mongo():
        assert (
            mongodb.antifraud_pay_type_change_available_results.find_one(
                {'_id': _REQUEST['order_id']},
            )['result']
            == 'block'
        )

    for _ in range(2):
        await _make_request()

    await duplicate_tp.wait_call()
    await test_args_tp.wait_call()

    assert not script_compile_failed_tp.has_calls
    assert not script_run_failed_tp.has_calls
    assert not rule_exec_failed_tp.has_calls

    _check_mongo()


@pytest.mark.experiments3(**_make_experiment())
async def test_result_not_overrite(taxi_uantifraud, mongodb, testpoint):
    @testpoint('script_compile_failed')
    def script_compile_failed_tp(_):
        pass

    @testpoint('script_run_failed')
    def script_run_failed_tp(_):
        pass

    @testpoint('rule_exec_failed')
    def rule_exec_failed_tp(_):
        pass

    @testpoint('pay_type_change_available_store_result_duplicate_error')
    def duplicate_tp(_):
        pass

    async def _make_request(user_id):
        resp = await taxi_uantifraud.post(
            '/v1/events/order/draft',
            json={**_REQUEST, **{'user_id': user_id}},
        )
        assert resp.status_code == 200
        assert resp.json() == {}

    def _check_mongo():
        assert (
            mongodb.antifraud_pay_type_change_available_results.find_one(
                {'_id': _REQUEST['order_id']},
            )['result']
            == 'allow'
        )

    await _make_request('non_fraud_user_id')
    _check_mongo()

    await _make_request('fraud_user_id')
    _check_mongo()

    await duplicate_tp.wait_call()

    assert not script_compile_failed_tp.has_calls
    assert not script_run_failed_tp.has_calls
    assert not rule_exec_failed_tp.has_calls
