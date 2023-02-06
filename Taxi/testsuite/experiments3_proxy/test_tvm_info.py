import pytest


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_FORBIDDEN=False,
    TVM_USER_TICKETS_ENABLED=True,
    TVM_REQUEST_RETRY=5,
    TVM_REQUEST_TIMEOUT=1000,
    TVM_API_URL='test-url',
    TVM_SERVICES={
        'service1': 1,
        'service2': 2,
        'service3': 3,
        'test-service': 4,
        'some-extra-service': 5,
    },
    TVM_RULES=[
        {'src': 'test-service', 'dst': 'service1'},
        {'src': 'service1', 'dst': 'service2'},
        {'src': 'service1', 'dst': 'service3'},
        {'src': 'service2', 'dst': 'service1'},
        {'src': 'service2', 'dst': 'service3'},
        {'src': 'service2', 'dst': 'test-service'},
        {'src': 'service3', 'dst': 'service1'},
        {'src': 'service3', 'dst': 'service2'},
        {'src': 'service3', 'dst': 'test-service'},
    ],
    TVM_SERVICE_TICKETS_PAGE_SIZE=100,
    TVM_HEALTH={
        'warn-on-service-tickets-delay-hours': 2,
        'error-on-service-tickets-delay-hours': 3,
        'warn-on-public-keys-delay-hours': 4,
    },
)
def test_tvm_info(taxi_experiments3_proxy):
    response = taxi_experiments3_proxy.get('/v1/tvm-info')
    assert response.status_code == 404

    response = taxi_experiments3_proxy.get('/v1/tvm-info/does-not-exist')
    assert response.status_code == 404

    response = taxi_experiments3_proxy.get('/v1/tvm-info/test-service')
    assert response.status_code == 200
    assert response.json() == {
        'tvm_services': {
            'service1': 1,
            'service2': 2,
            'service3': 3,
            'test-service': 4,
        },
        'tvm_rules': [
            {'src': 'service2', 'dst': 'test-service'},
            {'src': 'service3', 'dst': 'test-service'},
            {'src': 'test-service', 'dst': 'service1'},
        ],
    }

    response = taxi_experiments3_proxy.get(
        '/v1/tvm-info/test-service?extended=true',
    )
    assert response.status_code == 200
    assert response.json() == {
        'tvm_services': {
            'service1': 1,
            'service2': 2,
            'service3': 3,
            'test-service': 4,
        },
        'tvm_rules': [
            {'src': 'service2', 'dst': 'test-service'},
            {'src': 'service3', 'dst': 'test-service'},
            {'src': 'test-service', 'dst': 'service1'},
        ],
        'extended_configs': {
            'tvm_enabled': True,
            'tvm_forbidden': False,
            'tvm_user_tickets_enabled': True,
            'tvm_request_retry': 5,
            'tvm_request_timeout': 1000,
            'tvm_api_url': 'test-url',
            'tvm_service_tickets_page_size': 100,
            'tvm_health': {
                'warn-on-service-tickets-delay-hours': 2,
                'error-on-service-tickets-delay-hours': 3,
                'warn-on-public-keys-delay-hours': 4,
            },
        },
    }
