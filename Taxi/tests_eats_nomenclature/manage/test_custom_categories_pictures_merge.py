import pytest


HANDLER = '/v1/manage/custom_categories_groups'


@pytest.mark.pgsql('eats_nomenclature', files=['fill_products.sql'])
async def test_pictures_merge(
        taxi_eats_nomenclature, load_json, sql_get_pictures,
):
    response = await taxi_eats_nomenclature.post(
        HANDLER, json=load_json('request.json'),
    )
    assert response.status_code == 200
    assert sql_get_pictures() == {
        ('url_1', None, True),
        ('url_2', 'processed_url_2', False),
        ('url_3', None, False),
        # new pictures are set as needing a subscription
        ('url_4', None, True),
        ('url_5', None, True),
    }
