async def test_proxies(taxi_authproxy_manager):
    response = await taxi_authproxy_manager.post('/v1/proxies/list')
    assert response.status_code == 200
    assert response.json() == {
        'proxies': [
            {
                'name': 'passenger-authorizer',
                'type': 'passenger-authorizer',
                'tvm_service_name': 'passenger-authorizer',
            },
            {
                'name': 'grocery-authproxy',
                'type': 'passenger-authorizer',
                'tvm_service_name': 'grocery-authproxy',
            },
            {
                'name': 'ya-authproxy',
                'type': 'passenger-authorizer',
                'tvm_service_name': 'ya-authproxy',
            },
            {
                'name': 'int-authproxy',
                'type': 'int-authproxy',
                'tvm_service_name': 'int-authproxy',
            },
            {
                'name': 'eats-authproxy',
                'type': 'eats-authproxy',
                'tvm_service_name': 'eats-authproxy',
            },
            {
                'name': 'exams-authproxy',
                'type': 'exams-authproxy',
                'tvm_service_name': 'exams-authproxy',
            },
            {
                'name': 'pro-web-authproxy',
                'type': 'pro-web-authproxy',
                'tvm_service_name': 'pro-web-authproxy',
            },
            {
                'name': 'corp-authproxy',
                'type': 'corp-authproxy',
                'tvm_service_name': 'corp-authproxy',
            },
            {
                'name': 'pro-gateway',
                'type': 'pro-gateway',
                'tvm_service_name': 'pro-gateway',
            },
        ],
    }
