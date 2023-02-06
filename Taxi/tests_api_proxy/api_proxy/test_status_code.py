import random
import string

import pytest


@pytest.mark.parametrize(
    'status_code_def,status_code_expected',
    [
        ({}, 200),
        ({'status-code': 201}, 201),
        ({'status-code#integer': 202}, 202),
        ({'status-code': 201, 'status-code#integer': 202}, 201),
        (
            {
                'status-code#if': {
                    'condition#boolean': False,
                    'then#integer': 200,
                    'else#integer': 203,
                },
            },
            203,
        ),
        ({'status-code': -200}, 500),
        ({'status-code#integer': -200}, 500),
        ({'status-code#string': '200'}, 500),
        ({'status-code#boolean': True}, 500),
        ({'status-code#object': []}, 500),
    ],
)
async def test_status_code(
        taxi_api_proxy, endpoints, status_code_def, status_code_expected,
):
    # build header def
    handler_def = {
        'default-response': 'resp-ok',
        'enabled': True,
        'allow-unauthorized': True,
        'responses': [{'id': 'resp-ok', 'content-type': 'application/json'}],
    }
    handler_def['responses'][0].update(status_code_def)

    # build new path
    path = '/tests/api-proxy/test_status_code_%s' % (
        ''.join(random.choice(string.ascii_lowercase) for i in range(15)),
    )

    # create an endpoint
    await endpoints.safely_create_endpoint(path, get_handler=handler_def)

    # call the endpoint
    response = await taxi_api_proxy.get(path)
    assert response.status_code == status_code_expected
