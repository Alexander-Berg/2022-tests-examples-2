import json

import pytest

BRAND_ID = 1


@pytest.fixture
def mock_core_max_overweight(mockserver):
    class MockCtx:
        def __init__(self):
            self._place_id_to_max_overweight = dict()
            self._default_max_overweight = 0

        def add_data(self, place_id, max_overweight):
            place_id = str(place_id)
            self._place_id_to_max_overweight[place_id] = max_overweight

        def reset_data(self):
            self._place_id_to_max_overweight = dict()

        def get_data(self, place_id):
            place_id = str(place_id)
            if place_id not in self._place_id_to_max_overweight:
                return self._default_max_overweight
            return self._place_id_to_max_overweight[place_id]

    mock_ctx = MockCtx()

    @mockserver.handler('/eats-core-retail/v1/place/max-overweight/retrieve')
    def _mock(request):
        return mockserver.make_response(
            json.dumps(
                {
                    'max_overweight_in_percent': mock_ctx.get_data(
                        request.query['place_id'],
                    ),
                },
            ),
            200,
        )

    return mock_ctx


@pytest.fixture
def sql_add_product_for_vendor_and_barcode_test(
        pg_cursor,
):  # pylint: disable=C0103
    def impl(place_id, vendor_code=None, barcode=None, origin_id=None):
        assert vendor_code or barcode

        vendor_code = vendor_code or barcode
        barcode = barcode or vendor_code

        unique_key = f'{vendor_code}|{barcode}'
        origin_id = origin_id or unique_key

        pg_cursor.execute(
            f"""
            insert into eats_nomenclature.products(
                origin_id,
                description,
                shipping_type_id,
                vendor_id,
                name,
                quantum,
                measure_unit_id,
                measure_value,
                adult,
                is_catch_weight,
                is_choosable,
                brand_id
            )
            values (
                '{origin_id}',
                'descr',
                1,
                1,
                'name_{unique_key}',
                0.2,
                1,
                1000,
                false,
                false,
                true,
                {BRAND_ID}
            )
            returning id
        """,
        )
        product_id = pg_cursor.fetchone()[0]

        pg_cursor.execute(
            f"""
            insert into eats_nomenclature.barcodes(
                unique_key,
                value
            )
            values ('{barcode}', '{barcode}')
            on conflict(unique_key)
            do update set updated_at = now()
            returning id
        """,
        )
        barcode_id = pg_cursor.fetchone()[0]

        pg_cursor.execute(
            f"""
            insert into eats_nomenclature.product_barcodes(
                product_id,
                barcode_id
            )
            values ({product_id}, {barcode_id})
        """,
        )

        pg_cursor.execute(
            f"""
            insert into eats_nomenclature.categories_products(
                assortment_id,
                category_id,
                product_id,
                sort_order
            )
            values (1, 1, {product_id}, 1)
        """,
        )

        pg_cursor.execute(
            f"""
            insert into eats_nomenclature.places_products(
                place_id,
                product_id,
                origin_id,
                price,
                vendor_code,
                available_from
            )
            values (
                {place_id},
                {product_id},
                '{origin_id}',
                999,
                '{vendor_code}',
                now()
            )
            returning id
        """,
        )

    return impl
