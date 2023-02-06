import pytest

from clowny_perforator.generated.cron import run_cron


PROD_RULES = [
    {'src': 'not-existed', 'dst': 'a-serv'},
    {'src': 'a-serv', 'dst': 'b-serv'},
    {'src': 'b-serv', 'dst': 'c-serv'},
    {'src': 'c-serv', 'dst': 'd-serv'},
    {'src': 'd-serv', 'dst': 'e-serv'},
    {'src': 'a-serv', 'dst': 'c-serv'},
    {'src': 'not-existed', 'dst': 'b-serv'},
    {'src': 'not-existed', 'dst': 'c-serv'},
    {'src': 'some-service', 'dst': 'd-serv'},
    {'src': 'some-service', 'dst': 'e-serv'},
    {'src': 'e-serv', 'dst': 'some-service-2'},
]

TST_RULES = [
    {'src': 'a-serv', 'dst': 'not-existed'},
    {'src': 'a-serv', 'dst': 'b-serv'},
    {'src': 'b-serv', 'dst': 'c-serv'},
    {'src': 'c-serv', 'dst': 'd-serv'},
    {'src': 'd-serv', 'dst': 'e-serv'},
    {'src': 'a-serv', 'dst': 'c-serv'},
]

REASON = 'Автоматическое изменение ' 'конфига из сервиса clowny-perforator'


@pytest.fixture
def get_tvm_services(relative_load_json):
    def _wrapper(env_type):
        if env_type == 'production':
            return {
                'value': {
                    'a-serv': 1,
                    'b-serv': 2,
                    'c-serv': 3,
                    'd-serv': 4,
                    'e-serv': 5,
                },
            }
        return {'value': {'a-serv': 10, 'b-serv': 20, 'c-serv': 30}}

    return _wrapper


@pytest.fixture
def get_tvm_rules(relative_load_json):
    def _wrapper(env_type):
        if env_type == 'production':
            return {'value': PROD_RULES}
        return {'value': TST_RULES}

    return _wrapper


@pytest.fixture(name='run_test')
def _run_test(cte_configs_mockserver):
    async def _wrapper(expected_calls):
        mock = cte_configs_mockserver()
        await run_cron.main(
            ['clowny_perforator.crontasks.remove_unused_tvm_rules', '-t', '0'],
        )
        assert mock.times_called == len(expected_calls)
        for expeceted_call in expected_calls:
            call = mock.next_call()['request']
            assert call.method == expeceted_call['method']
            assert expeceted_call['config'] in call.url
            assert expeceted_call['env'] in call.url
            if call.method == 'POST':
                assert call.json == expeceted_call['json']

    return _wrapper


@pytest.mark.config(
    CLOWNY_PERFORATOR_UNUSED_TVM_RULES={
        'enabled': True,
        'turn_off_dry_run_for': ['production'],
        'tvm_services': {
            'rules_threshold': 2,
            'enabled_for_any': False,
            'disabled_for': ['d-serv'],
            'enabled_for': ['a-serv', 'b-serv', 'c-serv'],
        },
    },
)
async def test_remove_2_rules_prod(run_test):
    expected_calls = [
        {'method': 'GET', 'config': 'TVM_SERVICES', 'env': 'production'},
        {'method': 'GET', 'config': 'TVM_RULES', 'env': 'production'},
        {
            'method': 'POST',
            'config': 'TVM_RULES',
            'env': 'production',
            'json': {
                'new_value': [
                    {'src': 'a-serv', 'dst': 'b-serv'},
                    {'src': 'b-serv', 'dst': 'c-serv'},
                    {'src': 'c-serv', 'dst': 'd-serv'},
                    {'src': 'd-serv', 'dst': 'e-serv'},
                    {'src': 'a-serv', 'dst': 'c-serv'},
                    {'src': 'not-existed', 'dst': 'c-serv'},
                    {'src': 'some-service', 'dst': 'd-serv'},
                    {'src': 'some-service', 'dst': 'e-serv'},
                    {'src': 'e-serv', 'dst': 'some-service-2'},
                ],
                'old_value': PROD_RULES,
                'reason': REASON,
            },
        },
        {'method': 'GET', 'config': 'TVM_SERVICES', 'env': 'testing'},
        {'method': 'GET', 'config': 'TVM_RULES', 'env': 'testing'},
    ]
    await run_test(expected_calls)


@pytest.mark.config(
    CLOWNY_PERFORATOR_UNUSED_TVM_RULES={
        'enabled': True,
        'turn_off_dry_run_for': ['production'],
        'tvm_services': {
            'rules_threshold': 5,
            'enabled_for_any': True,
            'disabled_for': [],
            'enabled_for': [],
        },
    },
)
async def test_remove_5_rules_any_prod(run_test):
    expected_calls = [
        {'method': 'GET', 'config': 'TVM_SERVICES', 'env': 'production'},
        {'method': 'GET', 'config': 'TVM_RULES', 'env': 'production'},
        {
            'method': 'POST',
            'config': 'TVM_RULES',
            'env': 'production',
            'json': {
                'new_value': [
                    {'src': 'a-serv', 'dst': 'b-serv'},
                    {'src': 'b-serv', 'dst': 'c-serv'},
                    {'src': 'c-serv', 'dst': 'd-serv'},
                    {'src': 'd-serv', 'dst': 'e-serv'},
                    {'src': 'a-serv', 'dst': 'c-serv'},
                    {'src': 'e-serv', 'dst': 'some-service-2'},
                ],
                'old_value': PROD_RULES,
                'reason': REASON,
            },
        },
        {'method': 'GET', 'config': 'TVM_SERVICES', 'env': 'testing'},
        {'method': 'GET', 'config': 'TVM_RULES', 'env': 'testing'},
    ]
    await run_test(expected_calls)


@pytest.mark.config(
    CLOWNY_PERFORATOR_UNUSED_TVM_RULES={
        'enabled': True,
        'turn_off_dry_run_for': ['testing'],
        'tvm_services': {
            'rules_threshold': 5,
            'enabled_for_any': True,
            'disabled_for': [],
            'enabled_for': [],
        },
    },
)
async def test_remove_3_rules_any_tst(run_test):
    expected_calls = [
        {'method': 'GET', 'config': 'TVM_SERVICES', 'env': 'production'},
        {'method': 'GET', 'config': 'TVM_RULES', 'env': 'production'},
        {'method': 'GET', 'config': 'TVM_SERVICES', 'env': 'testing'},
        {'method': 'GET', 'config': 'TVM_RULES', 'env': 'testing'},
        {
            'method': 'POST',
            'config': 'TVM_RULES',
            'env': 'testing',
            'json': {
                'new_value': [
                    {'src': 'a-serv', 'dst': 'b-serv'},
                    {'src': 'b-serv', 'dst': 'c-serv'},
                    {'src': 'a-serv', 'dst': 'c-serv'},
                ],
                'old_value': TST_RULES,
                'reason': REASON,
            },
        },
    ]
    await run_test(expected_calls)


@pytest.mark.config(
    CLOWNY_PERFORATOR_UNUSED_TVM_RULES={
        'enabled': True,
        'turn_off_dry_run_for': ['testing', 'production'],
        'tvm_services': {
            'rules_threshold': 5,
            'enabled_for_any': True,
            'disabled_for': [],
            'enabled_for': [],
        },
    },
)
async def test_remove_any_rules_any_env(run_test):
    expected_calls = [
        {'method': 'GET', 'config': 'TVM_SERVICES', 'env': 'production'},
        {'method': 'GET', 'config': 'TVM_RULES', 'env': 'production'},
        {
            'method': 'POST',
            'config': 'TVM_RULES',
            'env': 'production',
            'json': {
                'new_value': [
                    {'src': 'a-serv', 'dst': 'b-serv'},
                    {'src': 'b-serv', 'dst': 'c-serv'},
                    {'src': 'c-serv', 'dst': 'd-serv'},
                    {'src': 'd-serv', 'dst': 'e-serv'},
                    {'src': 'a-serv', 'dst': 'c-serv'},
                    {'src': 'e-serv', 'dst': 'some-service-2'},
                ],
                'old_value': PROD_RULES,
                'reason': REASON,
            },
        },
        {'method': 'GET', 'config': 'TVM_SERVICES', 'env': 'testing'},
        {'method': 'GET', 'config': 'TVM_RULES', 'env': 'testing'},
        {
            'method': 'POST',
            'config': 'TVM_RULES',
            'env': 'testing',
            'json': {
                'new_value': [
                    {'src': 'a-serv', 'dst': 'b-serv'},
                    {'src': 'b-serv', 'dst': 'c-serv'},
                    {'src': 'a-serv', 'dst': 'c-serv'},
                ],
                'old_value': TST_RULES,
                'reason': REASON,
            },
        },
    ]
    await run_test(expected_calls)
