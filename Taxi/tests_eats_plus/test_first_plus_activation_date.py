import pytest

PLACE_1 = {
    'place_id': 1,
    'first_plus_activation_date': '2020-11-01T07:10:00+00:00',
    'active': False,
}

PLACE_2 = {
    'place_id': 2,
    'first_plus_activation_date': '2020-11-02T07:10:00+00:00',
    'active': True,
}


@pytest.mark.parametrize(
    'place_ids, response_json',
    (
        pytest.param([1], {'places': [PLACE_1]}, id='one_existing_place'),
        pytest.param(
            [1, 3, 2], {'places': [PLACE_1, PLACE_2]}, id='test_a_few_places',
        ),
        pytest.param([3], {'places': []}, id='one_non_existent_place'),
        pytest.param(
            [4], {'places': []}, id='place_without_place_active_from',
        ),
    ),
)
async def test_first_plus_activation_date(
        taxi_eats_plus, place_ids, response_json,
):
    response = await taxi_eats_plus.post(
        '/internal/eats-plus/v1/first_plus_activation_date',
        json={'place_ids': place_ids},
    )
    assert response.status_code == 200
    assert response.json() == response_json
