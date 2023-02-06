import random
import string

import pytest


@pytest.mark.parametrize(
    'x_request_application,expected_brand,expected_type',
    [
        ('app_brand=yango,app_name=yango_android', 'yango', 'yango_android'),
        ('app_brand=uber,app_name=uber_android', 'uber', 'uber_android'),
        ('app_brand=yandex,app_name=iphone', 'yandex', 'iphone'),
    ],
)
async def test_request_application(
        taxi_api_proxy,
        endpoints,
        x_request_application,
        expected_brand,
        expected_type,
):
    # build header def
    handler_def = {
        'default-response': 'resp-ok',
        'enabled': True,
        'allow-unauthorized': True,
        'responses': [
            {
                'id': 'resp-ok',
                'content-type': 'application/json',
                'body#object': [
                    {'key': 'brand', 'value#request-application': 'brand'},
                    {'key': 'type', 'value#request-application': 'type'},
                ],
            },
        ],
    }

    # build new path
    path = '/tests/api-proxy/test_request_application_%s' % (
        ''.join(random.choice(string.ascii_lowercase) for i in range(15)),
    )

    # create an endpoint
    await endpoints.safely_create_endpoint(path, get_handler=handler_def)

    # call the endpoint
    response = await taxi_api_proxy.get(
        path, headers={'X-Request-Application': x_request_application},
    )
    assert response.status_code == 200
    assert response.json() == {'type': expected_type, 'brand': expected_brand}
