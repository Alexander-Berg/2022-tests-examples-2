import pytest


@pytest.fixture(name='balancers_get_handler')
def _balancers_get_handler(mockserver):
    @mockserver.json_handler('/clowny-balancer/balancers/v1/service/get/')
    def _handler(request):
        if request.query['service_id'] == '1':
            return {
                'namespaces': [
                    {
                        'id': 1,
                        'awacs_namespace': 'test-service-1.taxi.yandex.net',
                        'env': 'stable',
                        'abc_quota_source': 'taxiquotaypdefault',
                        'is_external': False,
                        'is_shared': False,
                        'entry_points': [],
                    },
                    {
                        'id': 2,
                        'awacs_namespace': (
                            'test-service-1.taxi.tst.yandex.net'
                        ),
                        'env': 'testing',
                        'abc_quota_source': 'taxiquotaypdefault',
                        'is_external': False,
                        'is_shared': False,
                        'entry_points': [],
                    },
                ],
            }
        if request.query['service_id'] == '2':
            return {
                'namespaces': [
                    {
                        'id': 1,
                        'awacs_namespace': 'test-service-2.taxi.yandex.net',
                        'env': 'stable',
                        'abc_quota_source': 'taxiquotaypdefault',
                        'is_external': False,
                        'is_shared': False,
                        'entry_points': [],
                    },
                ],
            }
        return {'namespaces': []}

    return _handler


@pytest.fixture(name='get_namespace_handler')
def _get_namespace_handler(mockserver):
    @mockserver.json_handler('/client-awacs/api/GetNamespace/')
    def _handler(request):
        assert request.method == 'POST'
        return {
            'namespace': {
                'meta': {
                    'auth': {
                        'type': 'STAFF',
                        'staff': {
                            'owners': {
                                'logins': [
                                    'namespace-login-1',
                                    'namespace-login-2',
                                ],
                                'groupIds': ['50889'],
                            },
                        },
                    },
                    'id': request.json['id'],
                },
            },
        }

    return _handler
