import pytest

ENDPOINT = '/scooter-accumulator/v1/admin-api/suggests/cabinet/name'

CABINET_NAME1 = 'cabinet_name1'
CABINET_NAME2 = 'cabinet_name2'
CABINET_NAME3 = 'cabinet_name3'


@pytest.mark.parametrize(
    'cursor, limit, response_json',
    [
        pytest.param(
            None,
            1,
            {
                'cabinet_names': [CABINET_NAME3],
                'cursor': (
                    'MjAxOS0xMi0xN1QwNDozODo1NiswMDAwfGNhYmluZXRfbmFtZTM'
                ),
            },
            id='first request',
        ),
        pytest.param(
            'MjAxOS0xMi0xN1QwNDozODo1NiswMDAwfGNhYmluZXRfbmFtZTM',
            2,
            {'cabinet_names': [CABINET_NAME2, CABINET_NAME1]},
            id='second request',
        ),
        pytest.param(
            None,
            3,
            {'cabinet_names': [CABINET_NAME3, CABINET_NAME2, CABINET_NAME1]},
            id='one big request',
        ),
    ],
)
async def test_ok(taxi_scooter_accumulator, cursor, limit, response_json):
    params = {'limit': limit}
    if cursor:
        params['cursor'] = cursor

    response = await taxi_scooter_accumulator.get(ENDPOINT, params=params)

    assert response.status_code == 200
    assert response.json() == response_json
