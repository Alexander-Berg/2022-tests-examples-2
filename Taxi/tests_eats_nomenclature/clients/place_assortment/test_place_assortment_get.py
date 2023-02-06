import pytest

HANDLER = 'v1/place/assortments/data'


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_unknown_place_id(taxi_eats_nomenclature):
    response = await taxi_eats_nomenclature.get(HANDLER + '?place_id=3')
    assert response.status == 404


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_place_assortment_get(taxi_eats_nomenclature):
    response = await taxi_eats_nomenclature.get(HANDLER + '?place_id=1')
    expected_response = {
        'assortments': [
            {'name': 'assortment_name_1'},
            {'name': 'assortment_name_2'},
            {'name': 'experiment_assortment_name'},
            {'name': 'partner'},
        ],
    }
    assert response.status == 200
    response = sorted(response.json()['assortments'], key=lambda k: k['name'])
    expected_response = sorted(
        expected_response['assortments'], key=lambda k: k['name'],
    )
    assert response == expected_response
