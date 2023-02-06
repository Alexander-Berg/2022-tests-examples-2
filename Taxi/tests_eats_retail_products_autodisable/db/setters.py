from typing import List

import pytest

from .. import models


@pytest.fixture(name='save_autodisabled_products_to_db')
def _save_autodisabled_products_to_db(pg_cursor):
    def do_save_disabled_products_to_db(
            autodisabled_products: List[models.AutodisabledProduct],
    ):
        for autodisabled_product in autodisabled_products:
            pg_cursor.execute(
                f"""
                insert into
                eats_retail_products_autodisable.autodisabled_products
                (
                    place_id,
                    origin_id,
                    force_unavailable_until,
                    algorithm_name,
                    last_disabled_at
                )
                values (
                    '{autodisabled_product.place_id}',
                    '{autodisabled_product.origin_id}',
                    '{autodisabled_product.force_unavailable_until}',
                    '{autodisabled_product.algorithm_name}',
                    '{autodisabled_product.last_disabled_at}'
                )
                on conflict (place_id, origin_id, algorithm_name) do nothing
                """,
            )

    return do_save_disabled_products_to_db
