import pytest


_REQUEST = {
    'amount': '100.500',
    'currency': 'RUB',
    'ip': '8.8.8.8',
    'metrica_device_id': 'metrica_device_id',
    'park_db_id': 'park_db_id',
    'position': {'lat': 50.401515, 'lon': 30.606771},
    'uuid': 'uuid',
}


def _make_experiment(uuid=None):
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
                                    'value': 'refuel',
                                },
                                'type': 'eq',
                            },
                            {
                                'init': {
                                    'arg_name': 'uuid',
                                    'arg_type': 'string',
                                    'value': (
                                        uuid
                                        if uuid is not None
                                        else _REQUEST['uuid']
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


@pytest.mark.experiments3(**_make_experiment())
async def test_base(taxi_uantifraud, testpoint):
    @testpoint('script_compile_failed')
    def script_compile_failed_tp(_):
        pass

    @testpoint('script_run_failed')
    def script_run_failed_tp(_):
        pass

    @testpoint('rule_exec_failed')
    def rule_exec_failed_tp(_):
        pass

    response = await taxi_uantifraud.post('/v1/refuel/check', json=_REQUEST)
    assert response.status_code == 200
    assert response.json() == {'status': 'allow'}

    assert not script_compile_failed_tp.has_calls
    assert not script_run_failed_tp.has_calls
    assert not rule_exec_failed_tp.has_calls


@pytest.mark.parametrize(
    'req,status',
    [
        (_REQUEST, 'block'),
        (
            {
                'amount': '199.64',
                'currency': 'RUB',
                'ip': '176.59.111.222',
                'metrica_device_id': '868798041349556',
                'park_db_id': '441696c5565a4ea0b50ac24c6a1e569e',
                'position': {
                    'lon': 49.3029326459711,
                    'lat': 53.549291732156433,
                },
                'uuid': 'c7048ccf1319725b92041528530f8842',
            },
            'block',
        ),
    ],
)
async def test_triggered(
        taxi_uantifraud, experiments3, testpoint, req, status,
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

    experiments3.add_experiment(**_make_experiment(uuid=req['uuid']))

    for _ in range(10):
        response = await taxi_uantifraud.post('/v1/refuel/check', json=req)
        assert response.status_code == 200
        assert response.json() == {'status': status}

        assert not script_compile_failed_tp.has_calls
        assert not script_run_failed_tp.has_calls
        assert not rule_exec_failed_tp.has_calls

        await taxi_uantifraud.invalidate_caches(
            cache_names=['auto-entity-map-cache'],
        )
