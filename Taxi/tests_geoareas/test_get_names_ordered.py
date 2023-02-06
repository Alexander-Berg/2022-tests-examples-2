import pytest


@pytest.mark.filldb(subvention_geoareas='unordered')
@pytest.mark.parametrize(
    'point, expected_response',
    [
        ('0.5, 0.5', 'expected_response_point_1.json'),
        ('2.5, 2.5', 'expected_response_point_2.json'),
        ('3.5, 3.5', 'expected_response_point_3.json'),
        ('10, 10', 'expected_response_point_4.json'),
    ],
)
async def test_get_sg_names_ordered_using_point(
        taxi_geoareas, load_json, mongodb, point, expected_response,
):

    res = await taxi_geoareas.get(
        '/subvention-geoareas/v1/names_ordered_by_area',
        params={'point': point},
    )

    expected = load_json(expected_response)
    got = res.json()
    assert got == expected


@pytest.mark.filldb(subvention_geoareas='unordered')
@pytest.mark.parametrize(
    'ids, expected_response',
    [
        ('9,4', 'expected_response_point_1.json'),
        ('9,16,1', 'expected_response_point_2.json'),
        ('16', 'expected_response_point_3.json'),
        ('90', 'expected_response_point_4.json'),
    ],
)
async def test_get_sg_names_ordered_using_ids(
        taxi_geoareas, load_json, mongodb, ids, expected_response,
):

    res = await taxi_geoareas.get(
        '/subvention-geoareas/v1/names_ordered_by_area', params={'ids': ids},
    )

    expected = load_json(expected_response)
    got = res.json()
    assert got == expected


@pytest.mark.filldb(subvention_geoareas='unordered')
@pytest.mark.parametrize(
    'point, ids, expected_error',
    [
        (
            '10, 10',
            '9,4',
            'point and not empty ids cannot be specified at the same time',
        ),
        (None, None, 'point or not empty ids must be specified'),
    ],
)
async def test_get_sg_names_ordered_error(
        taxi_geoareas, load_json, mongodb, point, ids, expected_error,
):
    params = {}
    if point is not None:
        params['point'] = point
    if ids is not None:
        params['ids'] = ids

    res = await taxi_geoareas.get(
        '/subvention-geoareas/v1/names_ordered_by_area', params=params,
    )

    got = res.json()
    assert got['code'] == '400'
    assert got['message'] == expected_error
