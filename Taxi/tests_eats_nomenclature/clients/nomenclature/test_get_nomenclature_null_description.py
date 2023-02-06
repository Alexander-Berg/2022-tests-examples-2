import pytest


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_get_nomenclature_null_description(
        taxi_eats_nomenclature, pgsql,
):

    clear_product_descriptions(pgsql)
    response = await taxi_eats_nomenclature.get(
        '/v1/nomenclature?slug=slug&category_id=category_1_origin',
    )

    assert response.status == 200


def clear_product_descriptions(pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        """
    update eats_nomenclature.products
    set description = null""",
    )
