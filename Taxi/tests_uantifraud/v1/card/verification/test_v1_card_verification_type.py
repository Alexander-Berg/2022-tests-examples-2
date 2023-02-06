import pytest

_REQUEST = {
    'passport_uid': 'passport_uid',
    'service_id': 'service_id',
    'login_id': 'login_id',
    'application': 'application',
    'language': 'language',
    'user_id': 'user_id',
    'pass_flags': 'pass_flags',
    'user': 'user',
    'bound_uids': 'bound_uids',
    'payload': {'field1': 'value1', 'field2': ['value2']},
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
                                    'value': 'card_verify_type',
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


@pytest.mark.parametrize(
    'req,result',
    [
        (_REQUEST, 'auto'),
        ({**_REQUEST, **{'type': 'additional'}}, 'standard2_force_cvv'),
    ],
)
@pytest.mark.experiments3(**_make_experiment(_REQUEST['passport_uid']))
async def test_base(taxi_uantifraud, testpoint, req, result):
    @testpoint('script_compile_failed')
    def script_compile_failed_tp(_):
        pass

    @testpoint('script_run_failed')
    def script_run_failed_tp(_):
        pass

    @testpoint('rule_exec_failed')
    def rule_exec_failed_tp(_):
        pass

    resp = await taxi_uantifraud.post('/v1/card/verification/type', json=req)

    assert resp.status_code == 200
    assert resp.json() == {'result': result}

    # await test_args_tp.wait_call()

    assert not script_compile_failed_tp.has_calls
    assert not script_run_failed_tp.has_calls
    assert not rule_exec_failed_tp.has_calls


@pytest.mark.experiments3(**_make_experiment(_REQUEST['passport_uid']))
async def test_base_test_rule(taxi_uantifraud, testpoint):
    @testpoint('script_compile_failed')
    def script_compile_failed_tp(_):
        pass

    @testpoint('script_run_failed')
    def script_run_failed_tp(_):
        pass

    @testpoint('rule_exec_failed')
    def rule_exec_failed_tp(_):
        pass

    @testpoint('rule_exec')
    def rule_exec_tp(_):
        pass

    response = await taxi_uantifraud.post(
        '/v1/card/verification/type', json=_REQUEST,
    )

    assert response.status_code == 200
    assert response.json() == {'result': 'random_amt'}

    assert not script_compile_failed_tp.has_calls
    assert not script_run_failed_tp.has_calls
    assert not rule_exec_failed_tp.has_calls

    assert (
        [
            await rule_exec_tp.wait_call()
            for _ in range(rule_exec_tp.times_called)
        ]
        == [
            {
                '_': {
                    'is_test_mode': True,
                    'is_triggered': False,
                    'result': '{"result":"auto"}',
                    'rule_id': 'test_rule2',
                },
            },
            {
                '_': {
                    'is_test_mode': True,
                    'is_triggered': True,
                    'result': '{"result":"standard2_3ds"}',
                    'rule_id': 'test_rule1',
                },
            },
            {
                '_': {
                    'is_test_mode': False,
                    'is_triggered': False,
                    'result': '{"result":"random_amt"}',
                    'rule_id': 'rule1',
                },
            },
        ]
    )


@pytest.mark.experiments3(**_make_experiment(_REQUEST['passport_uid']))
async def test_rule_ret_priority(taxi_uantifraud, testpoint):
    @testpoint('script_compile_failed')
    def script_compile_failed_tp(_):
        pass

    @testpoint('script_run_failed')
    def script_run_failed_tp(_):
        pass

    @testpoint('rule_exec_failed')
    def rule_exec_failed_tp(_):
        pass

    @testpoint('rule_exec')
    def rule_exec_tp(_):
        pass

    response = await taxi_uantifraud.post(
        '/v1/card/verification/type', json=_REQUEST,
    )

    assert response.status_code == 200
    assert response.json() == {'result': 'standard2_3ds'}

    assert not script_compile_failed_tp.has_calls
    assert not script_run_failed_tp.has_calls
    assert not rule_exec_failed_tp.has_calls

    assert (
        [
            await rule_exec_tp.wait_call()
            for _ in range(rule_exec_tp.times_called)
        ]
        == [
            {
                '_': {
                    'is_test_mode': False,
                    'is_triggered': False,
                    'result': '{"result":"standard0"}',
                    'rule_id': 'rule1',
                },
            },
            {
                '_': {
                    'is_test_mode': False,
                    'is_triggered': False,
                    'result': '{"result":"standard1"}',
                    'rule_id': 'rule2',
                },
            },
            {
                '_': {
                    'is_test_mode': False,
                    'is_triggered': False,
                    'result': '{"result":"standard2"}',
                    'rule_id': 'rule3',
                },
            },
            {
                '_': {
                    'is_test_mode': False,
                    'is_triggered': False,
                    'result': '{"result":"random_amt"}',
                    'rule_id': 'rule4',
                },
            },
            {
                '_': {
                    'is_test_mode': False,
                    'is_triggered': True,
                    'result': '{"result":"standard2_3ds"}',
                    'rule_id': 'rule5',
                },
            },
        ]
    )


@pytest.mark.experiments3(**_make_experiment(_REQUEST['passport_uid']))
async def test_args(taxi_uantifraud, testpoint):
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
            'application': 'application',
            'auto_entity_map': {},
            'bound_uids': 'bound_uids',
            'language': 'language',
            'login_id': 'login_id',
            'pass_flags': 'pass_flags',
            'passport_uid': 'passport_uid',
            'yandex_uid': 'passport_uid',
            'payload': {'field1': 'value1', 'field2': ['value2']},
            'service_id': 'service_id',
            'type': _REQUEST.get('type', 'primary'),
            'user': 'user',
            'user_id': 'user_id',
        }
        return {'result': 'standard2_3ds'}

    resp = await taxi_uantifraud.post(
        '/v1/card/verification/type', json=_REQUEST,
    )

    assert resp.status_code == 200
    assert resp.json() == {'result': 'standard2_3ds'}

    assert await test_args_tp.wait_call()

    assert not script_compile_failed_tp.has_calls
    assert not script_run_failed_tp.has_calls
    assert not rule_exec_failed_tp.has_calls


@pytest.mark.experiments3(**_make_experiment(_REQUEST['passport_uid']))
@pytest.mark.config(AFS_CARD_VERIFY_REQUIRED_RESULT_FETCH=True)
async def test_card_verify_required_results_fetch(taxi_uantifraud):
    response = await taxi_uantifraud.post(
        '/v1/card/verification/type', json=_REQUEST,
    )

    assert response.status_code == 200
    assert response.json() == {'result': 'standard2_3ds'}
