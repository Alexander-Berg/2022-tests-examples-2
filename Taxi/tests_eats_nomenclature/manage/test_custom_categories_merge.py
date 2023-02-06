import pytest


HANDLER = '/v1/manage/custom_categories_groups'


@pytest.mark.pgsql('eats_nomenclature', files=['fill_products.sql'])
async def test_categories_merge(
        taxi_eats_nomenclature, load_json, sql_get_categories,
):
    response = await taxi_eats_nomenclature.post(
        HANDLER, json=load_json('request.json'),
    )
    assert response.status_code == 200
    expected_categories = [
        {
            'name': 'Молоко',
            'picture_url': None,
            'picture_processed_url': None,
            'sort_order': 100,
            'description': 'Молоко (описание)',
        },
        {
            'name': 'Молоко и сыры',
            'picture_url': 'url_3',
            'picture_processed_url': None,
            'sort_order': 200,
            'description': 'Молоко и сыры (описание)',
        },
        {
            'name': 'Молочные продукты',
            'picture_url': 'url_2',
            'picture_processed_url': 'processed_url_2',
            'sort_order': 100,
            'description': '',
        },
        {
            'name': 'Фрукты',
            'picture_url': 'url_1',
            'picture_processed_url': None,
            'sort_order': 400,
            'description': '',
        },
        {
            'name': 'Фрукты',
            'picture_url': 'url_4',
            'picture_processed_url': None,
            'sort_order': 300,
            'description': '',
        },
        {
            'name': 'Фрукты и овощи',
            'picture_url': 'url_5',
            'picture_processed_url': None,
            'sort_order': 100,
            'description': 'Фрукты и овощи (описание)',
        },
    ]
    assert sql_get_categories() == expected_categories
