import pytest


DEFAULT_ACCESS_TOKEN = 'some-secret-access-token'


@pytest.fixture(name='uber_login', autouse=True)
def mock_uber_login(mockserver):
    access_token = DEFAULT_ACCESS_TOKEN

    @mockserver.json_handler('/uber-login/oauth/v2/token')
    def _get_oauth_token():
        return mockserver.make_response(
            status=200,
            json={'access_token': access_token, 'expires_in': 2592000},
        )

    class Context:
        @property
        def access_token(self):
            return access_token

    context = Context()
    return context
