import pytest


CONFIGS_VALUES_URL = 'configs/values'


@pytest.mark.parametrize(
    'ids, updated, code, result',
    [
        (
            ['SECOND_CONFIG'],
            '2018-08-23T18:36:00.15Z',
            200,
            {
                'configs': {'SECOND_CONFIG': 200},
                'updated_at': '2018-08-24T18:36:00.15Z',
            },
        ),
        (
            ['SECOND_CONFIG', 'SOME_CONFIG'],
            '2018-08-23T18:36:00.15Z',
            200,
            {
                'configs': {'SECOND_CONFIG': 200},
                'updated_at': '2018-08-24T18:36:00.15Z',
            },
        ),
        (
            ['SOME_CONFIG'],
            '2018-08-23T18:36:00.15Z',
            200,
            {'configs': {}, 'updated_at': '2018-08-24T18:36:00.15Z'},
        ),
        (
            None,
            '2018-08-23T18:36:00.15Z',
            200,
            {
                'configs': {'SECOND_CONFIG': 200},
                'updated_at': '2018-08-24T18:36:00.15Z',
            },
        ),
        (
            None,
            '2018-08-19T18:36:00.15Z',
            200,
            {
                'configs': {
                    'SECOND_CONFIG': 200,
                    'SOME_CONFIG': [1, 2, 3, 4, 5],
                },
                'updated_at': '2018-08-24T18:36:00.15Z',
            },
        ),
        (
            ['SECOND_CONFIG', 'SOME_CONFIG'],
            '2019-08-19T18:36:00.15Z',
            200,
            {'configs': {}, 'updated_at': '2018-08-24T18:36:00.15Z'},
        ),
        (
            ['SECOND_CONFIG', 'GITCONFIG'],
            '2019-08-19T18:36:00.15Z',
            200,
            {'configs': {}, 'updated_at': '2018-08-24T18:36:00.15Z'},
        ),
    ],
)
async def test_diff(taxi_uconfigs, config_schemas, ids, updated, code, result):
    config_schemas.defaults.answer = {
        'commit': 'hash',
        'defaults': {'GITCONFIG': 10},
    }
    await taxi_uconfigs.invalidate_caches()

    request_body = {}
    if ids is not None:
        request_body['ids'] = ids
    if updated is not None:
        request_body['updated_since'] = updated

    response = await taxi_uconfigs.post(CONFIGS_VALUES_URL, json=request_body)
    assert response.status_code == code
    data = response.json()
    if result:
        assert data == result
