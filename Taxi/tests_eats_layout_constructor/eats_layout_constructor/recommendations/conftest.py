import pytest


@pytest.fixture(name='recommendations')
def recommendations(taxi_eats_layout_constructor):
    class Context:
        async def make_request(self, headers: dict = None, body: dict = None):
            default_headers: dict = {
                'Content-Type': 'application/json',
                'Cookie': '{}',
                'X-Platform': 'ios_app',
                'X-App-Version': '10.0.0',
                'X-Eats-User': 'user_id=12345',
                'X-Eats-Session': 'blabla',
            }
            if headers:
                default_headers.update(headers)

            response = await taxi_eats_layout_constructor.post(
                '/eats/v1/layout-constructor/v1/recommendations',
                headers=default_headers,
                json=(body or {}),
            )
            return response

    ctx = Context()
    return ctx
