import pytest


DEFAULT_RACK_ID = 1
DEFAULT_PLACE_ID = 1
MODIFIED_NAME = 'first_modified'
MODIFIED_DESCRIPTION = 'some description'


@pytest.mark.parametrize(
    'modified_name, modified_description, cells_number',
    [
        [MODIFIED_NAME, MODIFIED_DESCRIPTION, 3],
        [MODIFIED_NAME, MODIFIED_DESCRIPTION, 5],
        [MODIFIED_NAME, MODIFIED_DESCRIPTION, 1],
    ],
)
async def test_rack_modify_existing_204(
        taxi_eats_picker_racks,
        init_postgresql,
        modified_name,
        modified_description,
        cells_number,
):
    response = await taxi_eats_picker_racks.patch(
        f'/api/v1/rack?rack_id={DEFAULT_RACK_ID}',
        json={
            'name': modified_name,
            'description': modified_description,
            'cells_number': cells_number,
            'has_fridge': True,
            'has_freezer': False,
        },
    )
    assert response.status == 204

    response = await taxi_eats_picker_racks.get(
        f'/api/v1/racks?place_id={DEFAULT_PLACE_ID}',
    )
    assert response.status == 200

    modified_racks = [
        rack
        for rack in response.json()['racks']
        if rack['id'] == DEFAULT_RACK_ID
    ]
    assert len(modified_racks) == 1
    modified_rack = modified_racks[0]
    assert modified_rack['name'] == modified_name
    assert modified_rack['description'] == modified_description
    assert len(modified_rack['cells']) == cells_number
    assert modified_rack['cells'][0]['number'] == 1
    assert modified_rack['has_fridge']
    assert not modified_rack['has_freezer']


async def test_rack_modify_not_found_404(
        taxi_eats_picker_racks, init_postgresql,
):
    response = await taxi_eats_picker_racks.patch(
        f'/api/v1/rack?rack_id=999',
        json={'name': MODIFIED_NAME, 'cells_number': 1},
    )
    assert response.status == 404
