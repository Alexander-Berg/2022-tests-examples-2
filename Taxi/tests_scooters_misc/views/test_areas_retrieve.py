import pytest

HANDLER_URL = '/scooters-misc/v1/areas'


def _stable_response(response):
    body = response.json()
    body['areas'].sort(key=lambda area: area['id'])
    for area in body['areas']:
        area['tags'].sort()
    return body


@pytest.mark.parametrize(
    ['tags', 'expected_response'],
    [
        pytest.param(
            ['test_tag_1', 'test_tag_2'],
            'areas_expected_response.json',
            id='Simple test',
        ),
        pytest.param(
            ['test_tag_3'],
            'tag_3_expected_response.json',
            id='Test for not first tag',
        ),
    ],
)
async def test_handler(taxi_scooters_misc, load_json, tags, expected_response):
    res = await taxi_scooters_misc.post(HANDLER_URL, {'tags': tags})
    assert res.status_code == 200
    assert _stable_response(res) == load_json(expected_response)


async def test_handler_with_location(taxi_scooters_misc, load_json):
    res = await taxi_scooters_misc.post(
        HANDLER_URL,
        {'tags': ['test_tag_1'], 'location': [37.286275, 55.605068]},
    )
    assert res.status_code == 200
    assert _stable_response(res) == load_json(
        'areas_by_tag_n_location_expected_response.json',
    )
