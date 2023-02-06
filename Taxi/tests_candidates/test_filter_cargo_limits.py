import pytest


@pytest.mark.config(
    CARGO_TYPE_LIMITS={
        'lcv_m': {
            'carrying_capacity_max_kg': 1500,
            'carrying_capacity_min_kg': 1000,
            'height_max_cm': 200,
            'height_min_cm': 100,
            'length_max_cm': 300,
            'length_min_cm': 200,
            'width_max_cm': 200,
            'width_min_cm': 100,
            'requirement_value': 1,
        },
        'lcv_s': {
            'carrying_capacity_max_kg': 1000,
            'carrying_capacity_min_kg': 700,
            'height_max_cm': 200,
            'height_min_cm': 100,
            'length_max_cm': 300,
            'length_min_cm': 200,
            'width_max_cm': 200,
            'width_min_cm': 100,
            'requirement_value': 2,
        },
        'van': {
            'carrying_capacity_max_kg': 2001,
            'carrying_capacity_min_kg': 300,
            'height_max_cm': 201,
            'height_min_cm': 90,
            'length_max_cm': 290,
            'length_min_cm': 170,
            'width_max_cm': 201,
            'width_min_cm': 96,
            'requirement_value': 3,
        },
    },
)
@pytest.mark.parametrize(
    'request_cargo_type, request_cargo_type_int,'
    'expected_drivers_count, expected_status_code',
    [
        # One driver on large cargo found,
        # old-style (string-only) request
        ('lcv_s', None, 1, 200),
        # No driver on medium cargo found, but
        # temp-style (string or int) request is valid
        ('lcv_m', None, 0, 200),
        # No matching cargo type at our config, invalid request
        ('nonexistent', None, 0, 400),
        # No driver on medium cargo found
        (None, 1, 0, 200),
        # One driver on large cargo found
        (None, 2, 1, 200),
        # One driver on large cargo found
        (None, 3, 1, 200),
        # No matching cargo type at our config, invalid request
        (None, 10, 0, 400),
    ],
)
async def test_cargo_type(
        taxi_candidates,
        driver_positions,
        request_cargo_type,
        request_cargo_type_int,
        expected_drivers_count,
        expected_status_code,
):
    await driver_positions(
        [{'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]}],
    )
    request_body = {
        'geoindex': 'kdtree',
        'limit': 3,
        'filters': ['product/cargo_limits'],
        'point': [55, 35],
        'zone_id': 'moscow',
    }
    if request_cargo_type:
        request_body['requirements'] = {'cargo_type': request_cargo_type}
    elif request_cargo_type_int:
        request_body['requirements'] = {
            'cargo_type_int': request_cargo_type_int,
        }

    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == expected_status_code
    data = response.json()
    if expected_status_code == 200:
        assert 'drivers' in data
        assert len(data['drivers']) == expected_drivers_count
    else:
        assert data['message'] == 'product/cargo_limits: wrong cargo limits'
