import pytest


@pytest.fixture(name='sql_add_sku')
def _sql_add_sku(pg_cursor):
    def do_sql_add_sku(uuid, alternate_name='some_alternate_name'):
        pg_cursor.execute(
            """
            insert into eats_nomenclature.sku(
                uuid, alternate_name
            )
            values (
                %s, %s
            )
            returning id;
            """,
            (uuid, alternate_name),
        )
        return pg_cursor.fetchone()[0]

    return do_sql_add_sku


@pytest.fixture(name='sql_add_product')
def _sql_add_product(pg_cursor):
    def do_sql_add_product(
            origin_id='origin_id',
            sku_id=1,
            overriden_sku_id=None,
            place_id=1,
            brand_id=1,
            price=100,
            old_price=200,
            is_available=True,
            stocks=10,
    ):
        pg_cursor.execute(
            f"""
            insert into eats_nomenclature.products(
                origin_id, name, brand_id, sku_id
            )
            values (
                '{origin_id}', '{origin_id}', {brand_id}, {sku_id}
            )
            returning id, public_id;
            """,
        )
        product_id, public_id = pg_cursor.fetchone()

        if overriden_sku_id:
            pg_cursor.execute(
                f"""
                insert into eats_nomenclature.overriden_product_sku(
                    product_id, sku_id
                )
                values (
                    {product_id}, {overriden_sku_id}
                );
                """,
            )

        pg_cursor.execute(
            f"""
            insert into eats_nomenclature.places_products(
                place_id, product_id, origin_id,
                price, old_price, available_from
            )
            values (
                {place_id}, {product_id}, '{origin_id}',
                {price}, {old_price}, {'now()' if is_available else 'null'}
            )
            returning id;
        """,
        )
        place_product_id = pg_cursor.fetchone()[0]

        pg_cursor.execute(
            f"""
            insert into eats_nomenclature.stocks(
                place_product_id, value
            )
            values (
                {place_product_id}, {stocks}
            );
        """,
        )
        return public_id

    return do_sql_add_product
