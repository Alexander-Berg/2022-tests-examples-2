import pytest

from tests_uapi_keys import utils


ENDPOINT = '/v2/keys'


@pytest.mark.parametrize('key_id', ['aaa', '4', '7', '123'])
async def test_not_found(taxi_uapi_keys, key_id):
    response = await taxi_uapi_keys.get(ENDPOINT, params={'id': key_id})

    assert response.status_code == 404
    assert response.json() == {
        'code': 'key_not_found',
        'message': f'key with id `{key_id}` was not found',
    }


@pytest.mark.parametrize(
    'key_id, key',
    [('1', utils.V2KEY_1), ('2', utils.V2KEY_2), ('3', utils.V2KEY_3)],
)
async def test_found(taxi_uapi_keys, key_id, key):
    response = await taxi_uapi_keys.get(ENDPOINT, params={'id': key_id})

    assert response.status_code == 200, response.text
    assert response.json() == key
