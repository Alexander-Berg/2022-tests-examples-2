import pytest


@pytest.fixture
def mock_authorizer_w_details_403(mockserver, request):
    @mockserver.json_handler('/eats-restapp-authorizer/v1/user-access/check')
    def _mock_authorizer(request):
        return mockserver.make_response(
            status=403,
            json={
                'code': '400',
                'message': 'Error',
                'details': {
                    'permissions': ['other_permission'],
                    'place_ids': [1],
                },
            },
        )


@pytest.fixture
def mock_core_places_info_request(mockserver, request):
    @mockserver.json_handler('/eats-core/v1/places/info')
    def _mock_core(request):
        return mockserver.make_response(
            status=200,
            json={
                'payload': [
                    {
                        'id': 1,
                        'name': 'Нунануна',
                        'available': True,
                        'currency': {
                            'code': 'JPY',
                            'sign': '¥',
                            'decimal_places': 2,
                        },
                        'country_code': 'JP',
                        'show_shipping_time': False,
                        'integration_type': 'native',
                        'slug': 'nunanuna',
                    },
                ],
            },
        )

    return _mock_core
