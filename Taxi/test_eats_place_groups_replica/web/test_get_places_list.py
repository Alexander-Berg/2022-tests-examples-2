import pytest


@pytest.mark.parametrize(
    'place_group_id,expected_items',
    [
        ['place_group_id1', 'place_group_id1'],
        ['place_group_id2', 'place_group_id2'],
        ['not_existed', 'empty'],
    ],
)
@pytest.mark.pgsql('eats_place_groups_replica', files=['places.sql'])
async def test_should_correct_return_data(
        place_group_id,
        expected_items,
        load_json,
        taxi_eats_place_groups_replica_web,
):
    response = await taxi_eats_place_groups_replica_web.get(
        '/v1/places', params={'place_group_id': place_group_id},
    )
    assert response.status == 200
    response_json = await response.json()

    expected_elements = load_json('result.json')[expected_items]
    assert response_json['items'] == expected_elements
