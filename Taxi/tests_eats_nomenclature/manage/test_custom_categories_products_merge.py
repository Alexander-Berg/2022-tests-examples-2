import pytest


HANDLER = '/v1/manage/custom_categories_groups'


@pytest.mark.pgsql('eats_nomenclature', files=['fill_products.sql'])
async def test_categories_products_merge(
        taxi_eats_nomenclature, load_json, sql_get_categories_products,
):
    response = await taxi_eats_nomenclature.post(
        HANDLER, json=load_json('request.json'),
    )
    assert response.status_code == 200
    expected_categories_products = {
        ('Молоко', 1),
        ('Молоко', 2),
        ('Фрукты', 1),
        ('Фрукты', 3),
        ('Фрукты', 4),
        ('Фрукты и овощи', 5),
    }
    assert sql_get_categories_products() == expected_categories_products
