import pytest


CONFIGS_VALUES_URL = 'configs/values'


@pytest.mark.parametrize(
    'ids, updated, service, result',
    [
        (
            ['SOME_CONFIG'],
            None,
            'some-service',
            {
                'configs': {'SOME_CONFIG': [1, 2, 3, 4, 5]},
                'updated_at': '2018-08-24T18:36:00.15Z',
            },
        ),
        (
            ['SECOND_CONFIG'],
            None,
            'some-service',
            {
                'configs': {'SECOND_CONFIG': 228},
                'updated_at': '2018-08-24T18:36:00.15Z',
            },
        ),
        (
            None,
            '2018-08-19T18:36:00.15Z',
            'some-service',
            {
                'configs': {
                    'SECOND_CONFIG': 228,
                    'SOME_CONFIG': [1, 2, 3, 4, 5],
                },
                'updated_at': '2018-08-24T18:36:00.15Z',
            },
        ),
        (
            None,
            '2018-08-19T18:36:00.15Z',
            'another-service',
            {
                'configs': {
                    'SECOND_CONFIG': 200,
                    'SOME_CONFIG': [1, 2, 3, 4, 5],
                },
                'updated_at': '2018-08-24T18:36:00.15Z',
            },
        ),
    ],
)
async def test_service_override(taxi_uconfigs, ids, updated, service, result):
    request_body = {}
    if ids is not None:
        request_body['ids'] = ids
    if updated is not None:
        request_body['updated_since'] = updated
    if service is not None:
        request_body['service'] = service
    response = await taxi_uconfigs.post(CONFIGS_VALUES_URL, json=request_body)
    assert response.status_code == 200
    assert response.json() == result
