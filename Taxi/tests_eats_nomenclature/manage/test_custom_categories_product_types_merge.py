import pytest


HANDLER = '/v1/manage/custom_categories_groups'


@pytest.mark.pgsql('eats_nomenclature', files=['fill_products.sql'])
async def test_categories_product_types_merge(
        taxi_eats_nomenclature, load_json, sql_get_cat_prod_types,
):
    response = await taxi_eats_nomenclature.post(
        HANDLER, json=load_json('request.json'),
    )
    assert response.status_code == 200
    expected_cat_prod_types = {
        ('Молочные продукты', 1),
        ('Фрукты', 2),
        ('Фрукты', 3),
    }
    assert sql_get_cat_prod_types() == expected_cat_prod_types
