# flake8: noqa
# pylint: disable=import-error,wildcard-import
from test_service_noexpose_plugins.generated_tests import *


async def test_nolog(taxi_test_service_noexpose):
    response = await taxi_test_service_noexpose.post(
        '/json-echo',
        headers={'content-type': 'application/json'},
        data='{"field": 1}',
    )
    assert response.status == 200
    assert response.text == ''

    response = await taxi_test_service_noexpose.post(
        '/json-echo', headers={'content-type': 'application/json'}, data='',
    )
    assert response.status == 400
    assert response.json() == {
        'code': '400',
        'message': 'Invalid JSON in request body',
    }

    response = await taxi_test_service_noexpose.post(
        '/json-echo',
        headers={'content-type': 'application/json'},
        data='{"field": ',
    )
    assert response.status == 400
    assert response.json() == {
        'code': '400',
        'message': 'Invalid JSON in request body',
    }

    response = await taxi_test_service_noexpose.post(
        '/json-echo',
        headers={'content-type': 'application/json'},
        data='{"smth": 12}',
    )
    assert response.status == 400
    assert response.json() == {
        'code': '400',
        'message': 'Invalid JSON in request body',
    }
