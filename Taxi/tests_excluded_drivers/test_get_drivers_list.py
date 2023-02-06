import pytest


@pytest.mark.now('2018-08-10T21:01:00')
@pytest.mark.parametrize(
    ['phone_id', 'response_list', 'code'],
    (
        pytest.param(
            '5bbb5faf15870bd76635d5e2',
            ['id1', 'id2', 'id3', 'id5'],
            200,
            id='get_list',
        ),
        pytest.param(
            '5bbb5faf15870bd76635d5e2',
            ['id1', 'id3', 'id5'],
            200,
            id='get_list_with_delta',
            marks=pytest.mark.config(EXCLUDED_DRIVERS_DELTA=60),
        ),
        pytest.param('c18ef4392ec74a70b1aa2d21', None, 500, id='no_pd_id'),
        pytest.param('c18ef4392ec74a70b1aa2dff', [], 200, id='no_exclusion'),
    ),
)
async def test_get_drivers(
        taxi_excluded_drivers, phone_id, response_list, code,
):
    request = {'phone_id': phone_id}
    response = await taxi_excluded_drivers.get(
        '/excluded-drivers/v1/drivers/list', params=request,
    )
    assert response.status_code == code
    if code == 200:
        ids = response.json()['excluded_drivers_pd_ids']
        assert set(ids) == set(response_list)


async def test_get_drivers_personal_phone_id(taxi_excluded_drivers):
    request = {
        'phone_id': 'a34ef4392ec74a70b1aa2d78',
        'personal_phone_id': 'p_5bbb5faf15870bd76635d5e2',
    }
    response = await taxi_excluded_drivers.get(
        '/excluded-drivers/v1/drivers/list', params=request,
    )
    assert response.status_code == 200
    assert set(response.json()['excluded_drivers_pd_ids']) == set(['id6'])
