import pytest


@pytest.mark.parametrize(
    'x_request_application,expected_brand,expected_application',
    [
        ('app_brand=yango,app_name=yango_android', 'yango', 'yango_android'),
        ('app_brand=uber,app_name=uber_android', 'uber', 'uber_android'),
        ('app_brand=yandex,app_name=iphone', 'yandex', 'iphone'),
    ],
)
async def test_basic(
        taxi_api_proxy,
        endpoints,
        load_yaml,
        x_request_application,
        expected_brand,
        expected_application,
):
    await endpoints.safely_create_endpoint(
        '/endpoint', get_handler=load_yaml('endpoint.yaml'),
    )
    response = await taxi_api_proxy.get(
        '/endpoint',
        headers={
            'X-Request-Application': x_request_application,
            'X-Eats-User': 'user_id=123',
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body['application'] == expected_application
    assert body['app-brand'] == expected_brand
