import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from eats_nomenclature_plugins import *  # noqa: F403 F401


@pytest.fixture(name='sql_set_need_recalculation')
def _sql_set_need_recalculation(pgsql):
    def do_smth(place_id, product_id, need_recalculation):
        cursor = pgsql['eats_nomenclature'].cursor()
        cursor.execute(
            f"""
            update eats_nomenclature.autodisabled_products
            set need_recalculation = %s
            where place_id = %s
              and product_id = %s
            """,
            (need_recalculation, place_id, product_id),
        )

    return do_smth


@pytest.fixture(name='sql_has_need_recalculation')
def _sql_has_need_recalculation(pgsql):
    def do_smth(place_id, product_id):
        cursor = pgsql['eats_nomenclature'].cursor()
        cursor.execute(
            f"""
            select 1 from eats_nomenclature.autodisabled_products
            where need_recalculation = true
              and place_id = {place_id}
              and product_id = {product_id}
            """,
        )
        result = cursor.fetchone()
        return result and result[0]

    return do_smth


@pytest.fixture(name='sql_set_force_unavailable_until')
def _sql_set_force_unavailable_until(pgsql):
    def do_smth(place_id, origin_id, force_unavailable_until):
        cursor = pgsql['eats_nomenclature'].cursor()
        cursor.execute(
            f"""
            update eats_nomenclature.places_products
            set force_unavailable_until = %s
            where place_id = %s
              and origin_id = %s
            """,
            (force_unavailable_until, place_id, origin_id),
        )

    return do_smth


@pytest.fixture(name='sql_get_force_unavailable_until')
def _sql_get_force_unavailable_until(pgsql):
    def do_smth(place_id, origin_id):
        cursor = pgsql['eats_nomenclature'].cursor()
        cursor.execute(
            f"""
            select force_unavailable_until
            from eats_nomenclature.places_products
            where place_id = %s
              and origin_id = %s
            """,
            (place_id, origin_id),
        )
        result = cursor.fetchone()
        return result and result[0]

    return do_smth


@pytest.fixture(name='sql_is_force_unavailable')
def _sql_is_force_unavailable(pgsql):
    def do_smth(place_id, origin_id):
        cursor = pgsql['eats_nomenclature'].cursor()
        cursor.execute(
            f"""
            select 1 from eats_nomenclature.places_products
            where place_id = %s
              and origin_id = %s
              and force_unavailable_until > now()
            """,
            (place_id, origin_id),
        )
        result = cursor.fetchone()
        return bool(result and result[0])

    return do_smth


@pytest.fixture(name='sql_add_place_product')
def _sql_add_place_product(pgsql):
    def do_smth(
            origin_id,
            place_id,
            brand_id,
            stock=None,
            available_from=None,
            price=10,
    ):
        cursor = pgsql['eats_nomenclature'].cursor()
        cursor.execute(
            f"""
            insert into eats_nomenclature.brands (id)
            values ({brand_id})
            on conflict(id)
            do nothing
            """,
        )

        cursor.execute(
            f"""
            insert into eats_nomenclature.products(
                origin_id, description, shipping_type_id,
                vendor_id, name, quantum, measure_unit_id, measure_value,
                adult, is_catch_weight, is_choosable, brand_id
            ) values (
                '{origin_id}', 'ghi', 2, 2,
                'item_{origin_id}', 1.0, null, null, false,
                true, true, {brand_id})
            returning id
            """,
        )
        product_id = cursor.fetchone()[0]
        cursor.execute(
            f"""
            insert into eats_nomenclature.places_products(
                place_id, product_id, origin_id, price, available_from
            ) values (
                {place_id}, {product_id}, '{origin_id}', {price},
                {f"'{available_from}'" if available_from else 'null'}
            )
            returning id
            """,
        )
        place_product_id = cursor.fetchone()[0]

        cursor.execute(
            f"""
            insert into eats_nomenclature.stocks (
                place_product_id, value
            ) values (
                {place_product_id}, {'null' if stock is None else stock}
            )""",
        )

    return do_smth
