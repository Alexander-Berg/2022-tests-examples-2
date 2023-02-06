# Feel free to provide your custom implementation to override generated tests.

# pylint: disable=import-error,wildcard-import
from hejmdal_plugins.generated_tests import *  # noqa


async def test_service_envs(taxi_hejmdal):
    await taxi_hejmdal.run_task('tuner/initialize')

    response = await taxi_hejmdal.get('/v1/service/envs', params={})
    assert response.status_code == 400
    assert response.json()['message'] == 'Missing id in query'

    response = await taxi_hejmdal.get(
        '/v1/service/envs', params={'id': 100500},
    )
    assert response.status_code == 404
    assert (
        response.json()['message'] == 'service with id 100500 was not found.'
    )

    response = await taxi_hejmdal.get('/v1/service/envs', params={'id': 139})
    assert response.status_code == 200
    assert response.json() == {'envs': ['stable', 'testing']}

    response = await taxi_hejmdal.get(
        '/v1/service/envs', params={'id': 123456},
    )
    assert response.status_code == 200
    assert response.json() == {
        'envs': ['stable', 'prestable', 'testing', 'unstable'],
    }
