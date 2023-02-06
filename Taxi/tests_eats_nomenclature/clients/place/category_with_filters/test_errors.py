import pytest

HANDLER = '/v1/place/category_products/filtered'
CATEGORY_ID = 11


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_404_unknown_place(taxi_eats_nomenclature):
    unknown_place_id = 9999

    response = await taxi_eats_nomenclature.post(
        HANDLER + f'?place_id={unknown_place_id}&category_id=1',
        json={'filters': []},
    )

    assert response.status == 404


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_404_no_brand(taxi_eats_nomenclature, sql_delete_brand_place):
    place_id = 1

    sql_delete_brand_place(place_id)

    response = await taxi_eats_nomenclature.post(
        HANDLER + f'?place_id={place_id}&category_id=1', json={'filters': []},
    )

    assert response.status == 404


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_400_no_filters(taxi_eats_nomenclature):
    response = await taxi_eats_nomenclature.post(
        HANDLER + f'?place_id=1&category_id=1',
    )
    assert response.status == 400


@pytest.mark.parametrize('filter_id', ['fat_content', 'volume'])
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_400_bad_decimal_filter_option(
        taxi_eats_nomenclature,
        update_taxi_config,
        # parametrize params
        filter_id,
):
    update_taxi_config(
        'EATS_NOMENCLATURE_FILTERS_INFO',
        {'filters_info': {filter_id: {'name': 'Имя'}}},
    )
    update_taxi_config(
        'EATS_NOMENCLATURE_CATEGORY_BRAND_FILTERS_INFO',
        {CATEGORY_ID: {'default_category_settings': {filter_id: {}}}},
    )
    response = await taxi_eats_nomenclature.post(
        HANDLER + f'?place_id=1&category_id={CATEGORY_ID}',
        json={
            'filters': [
                {
                    'id': filter_id,
                    'type': 'multiselect',
                    'chosen_options': ['not_decimal_value'],
                },
            ],
        },
    )
    assert response.status == 400


@pytest.mark.parametrize('filter_id', ['fat_content', 'volume'])
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_400_filter_not_in_category_config(
        taxi_eats_nomenclature,
        update_taxi_config,
        # parametrize params
        filter_id,
):
    update_taxi_config(
        'EATS_NOMENCLATURE_FILTERS_INFO',
        {'filters_info': {filter_id: {'name': 'Имя'}}},
    )
    response = await taxi_eats_nomenclature.post(
        HANDLER + f'?place_id=1&category_id={CATEGORY_ID}',
        json={
            'filters': [
                {
                    'id': filter_id,
                    'type': 'multiselect',
                    'chosen_options': ['not_decimal_value'],
                },
            ],
        },
    )
    assert response.status == 400
