import pytest


@pytest.fixture(autouse=True)
def clowny_balancer_mock(mock_clowny_balancer):
    @mock_clowny_balancer('/balancers/v1/service/get/')
    def _services_get(service_id: int):
        return {
            'namespaces': [
                {
                    'id': 1,
                    'awacs_namespace': 'test_service.taxi.yandex.net',
                    'env': 'stable',
                    'abc_quota_source': 'some_test_abc_quouta',
                    'is_external': False,
                    'is_shared': True,
                    'entry_points': [
                        {
                            'protocol': 'https',
                            'dns_name': 'clowny-balancer.taxi.yandex.net',
                            'is_external': False,
                            'awacs_domain_id': 'test_domain_id',
                            'upstreams': [],
                        },
                    ],
                },
            ],
        }
