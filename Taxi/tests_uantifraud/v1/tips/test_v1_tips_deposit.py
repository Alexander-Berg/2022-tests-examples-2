import pytest

_REQUEST = {
    'id': 'id1',
    'recipient_id': 'recipient_id1',
    'recipient_id_b2p': 'recipient_id_b2p1',
    'is_guest_commission': True,
    'alias': 'alias1',
    'guest_amount': '100.500',
    'fee': 'fee1',
    'payment_type': 'payment_type1',
    'recipient_type': 'recipient_type1',
    'date_reg': '2020-01-01T10:00:00+03:00',
    'is_admin_reg': False,
    'is_free_procent': True,
    'trans_guest': True,
    'trans_guest_block': False,
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
                        'predicates': [
                            {
                                'init': {
                                    'arg_name': 'rule_type',
                                    'arg_type': 'string',
                                    'value': 'tips_deposit',
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
    response = await taxi_uantifraud.post('/v1/tips/deposit', json=_REQUEST)
    assert response.status_code == 200
    assert response.json() == {'status': 'allow'}


async def test_base_wo_exp(taxi_uantifraud):
    await _test_base(taxi_uantifraud)


@pytest.mark.experiments3(**_make_experiment())
async def test_base_with_exp(taxi_uantifraud):
    await _test_base(taxi_uantifraud)


@pytest.mark.experiments3(**_make_experiment())
async def test_args(taxi_uantifraud, testpoint):
    @testpoint('test_args')
    def test_args_tp(data):
        assert data == {**_REQUEST, **{'auto_entity_map': {}}}
        return {'status': 'block_account'}

    response = await taxi_uantifraud.post('/v1/tips/deposit', json=_REQUEST)

    assert response.status_code == 200
    assert response.json() == {'status': 'block_account'}

    assert await test_args_tp.wait_call()


@pytest.mark.experiments3(**_make_experiment())
async def test_priority(taxi_uantifraud, testpoint):
    rules_triggered = []
    rules_passed = []

    @testpoint('rule_exec_triggered')
    def rule_exec_triggered_tp(rule):  # pylint: disable=W0612
        rules_triggered.append(rule['rule_id'])

    @testpoint('rule_exec_passed')
    def rule_exec_passed_tp(rule):  # pylint: disable=W0612
        rules_passed.append(rule['rule_id'])

    response = await taxi_uantifraud.post('/v1/tips/deposit', json=_REQUEST)

    assert response.status_code == 200
    assert response.json() == {'status': 'block_account'}

    assert rules_triggered == [
        'test_tips_deposit_block_topup',
        'test_tips_deposit_block_account',
    ]
    assert rules_passed == ['test_tips_deposit_allow']
