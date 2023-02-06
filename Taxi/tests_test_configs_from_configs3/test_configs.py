import pytest


TICKET_HEADER = 'X-Ya-Service-Ticket'

# ya tool tvmknife unittest service --src 1 --dst 2345
TICKET = (
    '3:serv:CBAQ__________9_IgUIARCpEg:B1OWwLHw9Zu-LlZJJT4KoaMPD5GPZlod_t6N-'
    '8nLpYEILB6g2HdyGwBU42BS3YFiZwAVWUV8JqwqetLXH59E-5Eo3z6SiH274JuOC9d2PZfl'
    'tO_FTGtnWa56vwbmKkCZbUoXW4usroRwopjZ7-eKGs4y2jt0vU_tmTt5_W8OAs0'
)

SET_TVM_INFO_RESPONSE = pytest.mark.exp3_proxy_tvm_info(
    tvm_services={
        'test-service': 1,
        'experiments3-proxy': 2,
        # default service id in testsuite
        'test-configs-from-configs3': 2345,
    },
    tvm_rules=[
        dict(src='test-service', dst='test-configs-from-configs3'),
        dict(src='test-configs-from-configs3', dst='experiments3-proxy'),
    ],
)


@pytest.mark.uservice_oneshot()
@pytest.mark.experiments3(
    is_config=True,
    name='EXPERIMENTS3_CACHE_BULK_SIZE_LIMIT',
    consumers=['userver/market'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value=200,
    skip_check_schema=True,
)
@pytest.mark.experiments3(
    is_config=True,
    name='EXPERIMENTS3_CLIENT_DISABLE_API_KEY',
    consumers=['userver/market'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value=True,
    skip_check_schema=True,
)
@pytest.mark.experiments3(
    is_config=True,
    name='EXPERIMENTS3_COMMON_LIBRARY_SETTINGS',
    consumers=['userver/market'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={
        'general_settings': {
            'mandatory_config_loading_retries': 777,
            'mandatory_config_loading_retry_timeout': 555,
        },
        'features': {'f1': True, 'f2': False, 'f3': True},
    },
    skip_check_schema=True,
)
@SET_TVM_INFO_RESPONSE
async def test_config(taxi_test_configs_from_configs3):
    response = await taxi_test_configs_from_configs3.get(
        '/v1/config?name=EXPERIMENTS3_CACHE_BULK_SIZE_LIMIT',
        headers={TICKET_HEADER: TICKET},
    )
    assert response.status_code == 200
    assert response.json() == {'value': 200}

    response = await taxi_test_configs_from_configs3.get(
        '/v1/config?name=EXPERIMENTS3_CLIENT_DISABLE_API_KEY',
        headers={TICKET_HEADER: TICKET},
    )

    assert response.status_code == 200
    assert response.json() == {'value': True}

    response = await taxi_test_configs_from_configs3.get(
        '/v1/config?name=EXPERIMENTS3_COMMON_LIBRARY_SETTINGS',
        headers={TICKET_HEADER: TICKET},
    )

    assert response.status_code == 200
    assert response.json() == {
        'value': {
            'general_settings': {
                'mandatory_config_loading_retries': 777,
                'mandatory_config_loading_retry_timeout': 555,
            },
            'features': {'f1': True, 'f2': False, 'f3': True},
        },
    }


@pytest.mark.uservice_oneshot()
@SET_TVM_INFO_RESPONSE
async def test_start_service_with_no_config_overwrites(
        taxi_test_configs_from_configs3,
):
    response = await taxi_test_configs_from_configs3.get(
        '/v1/config?name=EXPERIMENTS3_CACHE_BULK_SIZE_LIMIT',
        headers={TICKET_HEADER: TICKET},
    )
    assert response.status_code == 200
    assert response.json() == {'value': 100}
