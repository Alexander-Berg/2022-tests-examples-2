from typing import List

import pytest

from .. import models


@pytest.fixture(name='get_autodisabled_products_from_db')
def _get_autodisabled_products_from_db(pg_realdict_cursor, to_utc_datetime):
    def do_work() -> List[models.AutodisabledProduct]:
        pg_realdict_cursor.execute(
            f"""
        select
            place_id,
            origin_id,
            force_unavailable_until,
            algorithm_name,
            last_disabled_at
        from eats_retail_products_autodisable.autodisabled_products
        """,
        )

        return sorted(
            [
                models.AutodisabledProduct(
                    place_id=row['place_id'],
                    origin_id=row['origin_id'],
                    force_unavailable_until=to_utc_datetime(
                        row['force_unavailable_until'],
                    ),
                    algorithm_name=row['algorithm_name'],
                    last_disabled_at=to_utc_datetime(row['last_disabled_at']),
                )
                for row in pg_realdict_cursor
            ],
        )

    return do_work
