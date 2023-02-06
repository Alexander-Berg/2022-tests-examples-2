import pytest


CONFIGS_VALUES_URL = 'configs/values'


@pytest.mark.parametrize(
    'ids, code, result',
    [
        (
            ['SECOND_CONFIG'],
            200,
            {
                'configs': {'SECOND_CONFIG': 200},
                'updated_at': '2018-08-24T18:36:00.15Z',
            },
        ),
        (
            ['GITCONFIG'],
            200,
            {
                'configs': {'GITCONFIG': 10},
                'updated_at': '2018-08-24T18:36:00.15Z',
            },
        ),
        (None, 200, None),
    ],
)
async def test_ids(taxi_uconfigs, config_schemas, ids, code, result):
    config_schemas.defaults.answer = {
        'commit': 'hash',
        'defaults': {'GITCONFIG': 10},
    }
    await taxi_uconfigs.invalidate_caches()

    request_body = {}
    if ids is not None:
        request_body['ids'] = ids
    response = await taxi_uconfigs.post(CONFIGS_VALUES_URL, json=request_body)
    assert response.status_code == code
    data = response.json()
    if result:
        assert data == result
