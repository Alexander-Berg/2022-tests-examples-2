from tests_eats_products import conftest
from tests_eats_products import utils


def sql_read_products(pgsql):
    cursor = pgsql['eats_products'].cursor()
    cursor.execute(
        """
            select place_id, brand_id, origin_id, public_id
            from eats_products.place_products;
        """,
    )
    return {(row[0], row[1], row[2]): row[3] for row in cursor}


def sql_insert_product_core_id(pgsql, place_id, origin_id, core_id):
    cursor = pgsql['eats_products'].cursor()
    cursor.execute(
        f"""
            insert into eats_products.place_products(
                place_id, origin_id, core_id
            ) values(
                {place_id}, '{origin_id}', {core_id}
            );
        """,
    )


async def test_update_product_mapping(
        pgsql, mockserver, load_json, stq_runner, add_place_products_mapping,
):
    @mockserver.json_handler(utils.Handlers.NOMENCLATURE)
    def _mock_eats_nomenclature(request):
        response = load_json('nomenclature-response.json')
        if 'category_id' in request.query:
            if request.query['category_id'] == '2':
                return {}
            return response
        for category in response['categories']:
            category['items'] = []
        return response

    add_place_products_mapping(
        [
            conftest.ProductMapping(
                origin_id='item_id_1',
                public_id='99999999-9999-9999-9999-999999999999',
            ),
            conftest.ProductMapping(
                origin_id='item_id_2',
                public_id='88888888-8888-8888-8888-888888888888',
            ),
            conftest.ProductMapping(origin_id='item_id_3', core_id=3),
        ],
    )

    await stq_runner.eats_products_update_nomenclature_product_mapping.call(
        task_id=str(utils.PLACE_ID), kwargs={'place_id': str(utils.PLACE_ID)},
    )

    place_products_mapping = sql_read_products(pgsql)
    assert (
        place_products_mapping[(utils.PLACE_ID, utils.BRAND_ID, 'item_id_1')]
        == '11111111-1111-1111-1111-111111111111'
    )
    assert (
        place_products_mapping[(utils.PLACE_ID, utils.BRAND_ID, 'item_id_2')]
        == '22222222-2222-2222-2222-222222222222'
    )
    assert (
        place_products_mapping[(utils.PLACE_ID, utils.BRAND_ID, 'item_id_3')]
        == '33333333-3333-3333-3333-333333333333'
    )
    assert (
        place_products_mapping[(utils.PLACE_ID, utils.BRAND_ID, 'item_id_4')]
        == '44444444-4444-4444-4444-444444444444'
    )
    assert (
        place_products_mapping[(utils.PLACE_ID, utils.BRAND_ID, 'item_id_5')]
        == '55555555-5555-5555-5555-555555555555'
    )
