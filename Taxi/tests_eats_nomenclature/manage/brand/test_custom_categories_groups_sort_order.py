import pytest


HANDLER = '/v1/manage/brand/custom_categories_groups/sort_order'
BRAND_ID = 1


@pytest.mark.pgsql('eats_nomenclature', files=['fill_brand_custom_groups.sql'])
async def test_404_unknown_brand_id(taxi_eats_nomenclature, load_json):
    request = load_json('request.json')
    unknown_brand_id = 3
    response = await taxi_eats_nomenclature.post(
        HANDLER + f'?brand_id={unknown_brand_id}', json=request,
    )
    assert response.status_code == 404
    assert response.json()['message'] == f'Brand {unknown_brand_id} not found'


@pytest.mark.pgsql('eats_nomenclature', files=['fill_brand_custom_groups.sql'])
async def test_200(taxi_eats_nomenclature, pgsql, load_json):
    request = load_json('request.json')
    unknown_group_public_id = '12344444-4444-4444-4444-444444444444'
    unknown_group_sort_order = 101
    request['categories_groups'].append(
        {
            'id': unknown_group_public_id,
            'sort_order': unknown_group_sort_order,
        },
    )
    response = await taxi_eats_nomenclature.post(
        HANDLER + f'?brand_id={BRAND_ID}', json=request,
    )
    assert response.status_code == 200

    for categories_group in request['categories_groups']:
        sort_order_for_traits = _sql_get_sort_order(
            pgsql, BRAND_ID, categories_group['id'],
        )
        if categories_group['id'] != unknown_group_public_id:
            assert sort_order_for_traits
        else:
            assert not sort_order_for_traits
        for sort_order_for_trait in sort_order_for_traits:
            assert sort_order_for_trait == categories_group['sort_order']


def _sql_get_sort_order(pgsql, brand_id, categories_group_id):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""select bccg.sort_order
        from eats_nomenclature.brands_custom_categories_groups bccg
          join eats_nomenclature.custom_categories_groups ccg
          on ccg.id = bccg.custom_categories_group_id
            where bccg.brand_id = {brand_id}
              and ccg.public_id = '{categories_group_id}'::uuid""",
    )
    return {row[0] for row in cursor.fetchall()}
