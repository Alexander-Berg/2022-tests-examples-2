import pytest


@pytest.fixture
def service_client_default_headers():
    return {'Some-Header': 'SomeValue'}


@pytest.mark.parametrize(
    'headers,expected',
    [
        (None, {'name': 'Some-Header', 'value': 'SomeValue'}),
        (
            {'Some-Header': 'Override'},
            {'name': 'Some-Header', 'value': 'Override'},
        ),
        (
            {'Another-Header': 'AnotherValue'},
            {'name': 'Some-Header', 'value': 'SomeValue'},
        ),
    ],
)
async def test_default_header(taxi_example_service_web, headers, expected):
    response = await taxi_example_service_web.get(
        '/echo-header', params={'header': 'Some-Header'}, headers=headers,
    )
    assert await response.json() == expected
