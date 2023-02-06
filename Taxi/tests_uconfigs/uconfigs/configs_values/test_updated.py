import pytest


CONFIGS_VALUES_URL = 'configs/values'


@pytest.mark.parametrize(
    'updated, code, result',
    [
        (None, 200, '2018-08-24T18:36:00.15Z'),
        ('2018-08-24T18:36:00.150Z', 200, '2018-08-24T18:36:00.15Z'),
        ('2018-08-24T18:36:00.151Z', 200, '2018-08-24T18:36:00.15Z'),
        ('bad_param', 400, None),
    ],
)
async def test_updated(taxi_uconfigs, updated, code, result):
    request_body = {}
    if updated:
        request_body['updated_since'] = updated
    response = await taxi_uconfigs.post(CONFIGS_VALUES_URL, json=request_body)
    assert response.status_code == code
    if code == 200:
        data = response.json()
        assert data['updated_at'] == result
