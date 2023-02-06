import pytest

_REQUEST = {
    'id': 'id1',
    'partner_id': 'partner_id1',
    'amount': '100.500',
    'fee': 'fee1',
    'is_blacklist': False,
    'is_one_card': False,
    'is_from_3k_pay': True,
    'exceeded_threshold': True,
    'exceeded_threshold_fresh': False,
    'withdrawal_method': 'withdrawal_method1',
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
                                    'value': 'tips_withdrawal',
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
    response = await taxi_uantifraud.post('/v1/tips/withdrawal', json=_REQUEST)
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
        return {'status': 'block_withdrawal'}

    response = await taxi_uantifraud.post('/v1/tips/withdrawal', json=_REQUEST)

    assert response.status_code == 200
    assert response.json() == {'status': 'block_withdrawal'}

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

    response = await taxi_uantifraud.post('/v1/tips/withdrawal', json=_REQUEST)

    assert response.status_code == 200
    assert response.json() == {'status': 'block_account'}

    assert rules_triggered == [
        'test_tips_withdrawal_manual_accept',
        'test_tips_withdrawal_block_withdrawal',
        'test_tips_withdrawal_block_account',
    ]
    assert rules_passed == ['test_tips_withdrawal_allow']
