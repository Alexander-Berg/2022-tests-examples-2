from typing import List

import pytest

from tests_eats_retail_market_integration import models


@pytest.fixture(name='get_places_info_from_db')
def _get_places_info_from_db(pg_realdict_cursor):
    def do_get_places_info_from_db() -> List[models.PlaceInfo]:
        pg_realdict_cursor.execute(
            f"""
            select
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
            from eats_retail_market_integration.places_info
            """,
        )

        return sorted([models.PlaceInfo(**row) for row in pg_realdict_cursor])

    return do_get_places_info_from_db


@pytest.fixture(name='get_orders_from_db')
def _get_orders_from_db(pg_realdict_cursor):
    def do_get_orders_from_db() -> List[models.Order]:
        pg_realdict_cursor.execute(
            f"""
            select order_nr, eater_id
            from eats_retail_market_integration.orders
            """,
        )

        return sorted(
            [
                models.Order(
                    order_nr=row['order_nr'], eater_id=row['eater_id'],
                )
                for row in pg_realdict_cursor
            ],
        )

    return do_get_orders_from_db
