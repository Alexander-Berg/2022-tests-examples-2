import pytest


@pytest.mark.parametrize(
    'position, exp_resp, exp_resp_code',
    [
        ('37.618423,55.751244', {'country_code': 'ru'}, 200),
        ('13.381777,52.531677', {'country_code': 'de'}, 200),
        (
            '0,0',
            {'code': 'COUNTRY_NOT_FOUND', 'message': 'Can\'t lookup country'},
            404,
        ),
    ],
)
async def test_simple(taxi_persey_core, position, exp_resp, exp_resp_code):
    response = await taxi_persey_core.get(
        f'/geo/position/?position={position}',
    )

    assert response.status_code == exp_resp_code
    assert response.json() == exp_resp
