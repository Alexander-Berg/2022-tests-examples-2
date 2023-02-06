import pytest


@pytest.mark.pgsql(
    'driver_promocodes', files=['series.sql', 'promocodes_to_activate.sql'],
)
@pytest.mark.now('2020-06-01T12:00:00+0300')
@pytest.mark.parametrize(
    'request_body,expected_response',
    [('request.json', 'expected_response.json')],
)
async def test_active_list(
        taxi_driver_promocodes, load_json, request_body, expected_response,
):

    response = await taxi_driver_promocodes.post(
        'internal/v1/promocodes/active', json=load_json(request_body),
    )
    assert response.status_code == 200
    assert response.json() == load_json(expected_response)
