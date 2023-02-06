import copy
from typing import List

import pytest

from tests_eats_retail_market_integration import models


@pytest.fixture(name='save_places_to_db')
def _save_places_to_db(pg_cursor):
    def do_save_places_to_db(places: List[models.Place]):
        for place in places:
            assert place.brand_id is not None
            pg_cursor.execute(
                f"""
                insert into eats_retail_market_integration.places(
                    id,
                    slug,
                    brand_id
                )
                values (
                    '{place.place_id}',
                    '{place.slug}',
                    '{place.brand_id}'
                )
                on conflict (id) do update
                set
                    slug = excluded.slug,
                    brand_id = excluded.brand_id
                """,
            )

    return do_save_places_to_db


@pytest.fixture(name='save_places_info_to_db')
def _save_places_info_to_db(pg_cursor):
    def do_save_places_info_to_db(places_info: List[models.PlaceInfo]):
        for place_info in places_info:
            place_info_dict = copy.deepcopy(place_info).__dict__
            pg_cursor.execute(
                """
                insert into eats_retail_market_integration.places_info(
                    partner_id,
                    place_id,
                    place_name,
                    brand_name,
                    legal_name,
                    legal_address,
                    legal_address_postcode,
                    reg_number,
                    email,
                    address_full,
                    phone,
                    inn,
                    kpp,
                    geo_id,
                    schedule,
                    assembly_cost,
                    brand_id
                )
                values (
                    %(partner_id)s,
                    %(place_id)s,
                    %(place_name)s,
                    %(brand_name)s,
                    %(legal_name)s,
                    %(legal_address)s,
                    %(legal_address_postcode)s,
                    %(reg_number)s,
                    %(email)s,
                    %(address_full)s,
                    %(phone)s,
                    %(inn)s,
                    %(kpp)s,
                    %(geo_id)s,
                    %(schedule)s,
                    %(assembly_cost)s,
                    %(brand_id)s
                )
                on conflict (partner_id) do nothing
                """,
                place_info_dict,
            )

    return do_save_places_info_to_db


@pytest.fixture(name='save_brands_to_db')
def _save_brands_to_db(pg_cursor, save_places_to_db):
    def do_save_brands_to_db(brands: List[models.Brand]):
        for brand in brands:
            pg_cursor.execute(
                f"""
                insert into eats_retail_market_integration.brands(
                    id,
                    slug
                )
                values (
                    '{brand.brand_id}',
                    '{brand.slug}'
                )
                on conflict (id) do update
                set
                    slug = excluded.slug
                """,
            )

            save_places_to_db(list(brand.get_places().values()))

    return do_save_brands_to_db


@pytest.fixture(name='save_market_brand_places_to_db')
def _save_market_brand_places_to_db(pg_cursor, save_places_to_db):
    def do_save_mbp_to_db(market_brand_places: List[models.MarketBrandPlace]):
        for market_brand_place in market_brand_places:
            pg_cursor.execute(
                f"""
                insert into eats_retail_market_integration.market_brand_places(
                    brand_id,
                    place_id,
                    business_id,
                    partner_id,
                    feed_id
                )
                values (
                    '{market_brand_place.brand_id}',
                    '{market_brand_place.place_id}',
                    {market_brand_place.business_id},
                    {market_brand_place.partner_id},
                    {market_brand_place.feed_id}
                )
                """,
            )

    return do_save_mbp_to_db


@pytest.fixture(name='save_orders_to_db')
def _save_orders_to_db(pg_cursor):
    def do_save_orders_to_db(orders: List[models.Order]):
        for order in orders:
            pg_cursor.execute(
                f"""
                insert into eats_retail_market_integration.orders(
                    order_nr,
                    eater_id
                )
                values (
                    '{order.order_nr}',
                    '{order.eater_id}'
                )
                """,
            )

    return do_save_orders_to_db
