import pytest

from . import utils


@pytest.mark.parametrize(
    'place_id, response_json',
    [
        [
            1,
            {
                'racks': [
                    {
                        'id': 1,
                        'place_id': 1,
                        'name': 'first',
                        'description': 'some description',
                        'cells': [
                            {'id': 1, 'rack_id': 1, 'number': 1},
                            {'id': 2, 'rack_id': 1, 'number': 2},
                            {'id': 3, 'rack_id': 1, 'number': 3},
                        ],
                    },
                    {
                        'id': 2,
                        'place_id': 1,
                        'name': 'second',
                        'cells': [{'id': 4, 'rack_id': 2, 'number': 1}],
                    },
                ],
            },
        ],
        [
            2,
            {
                'racks': [
                    {
                        'id': 3,
                        'place_id': 2,
                        'name': 'third',
                        'cells': [{'id': 5, 'rack_id': 3, 'number': 1}],
                    },
                ],
            },
        ],
        [3, {'racks': []}],
    ],
)
@pytest.mark.parametrize(
    'url, headers',
    [
        (
            '/4.0/eats-picker-racks/api/v1/racks?place_id={}',
            utils.da_headers('111'),
        ),
        ('/api/v1/racks?place_id={}', ''),
    ],
)
async def test_get_racks(
        taxi_eats_picker_racks,
        init_postgresql,
        place_id,
        response_json,
        url,
        headers,
):
    response = await taxi_eats_picker_racks.get(
        url.format(place_id), headers=headers,
    )
    assert response.status == 200
    assert response.json() == response_json
