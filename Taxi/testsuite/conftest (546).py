import pytest

# root conftest for service pro-profiles
pytest_plugins = ['pro_profiles_plugins.pytest_plugins']


@pytest.fixture(autouse=True)
def mock_salesforce_auth(mockserver):
    @mockserver.json_handler('/salesforce/services/oauth2/token')
    def _auth_sf(request):
        return {
            'access_token': 'access_token',
            'id': 'id',
            'instance_url': 'instance_url',
            'issued_at': '2050-01-01T12:00:00+00:00',
            'signature': 'signature',
            'token_type': 'bearer',
        }
