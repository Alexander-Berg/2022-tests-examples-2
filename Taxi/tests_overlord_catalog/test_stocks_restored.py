# pylint: disable=protected-access
import datetime

from . import sql_queries


EARLIER = datetime.datetime(
    2021, 8, 5, 16, 10, 0, tzinfo=datetime.timezone.utc,
)
EARLIER_UPDATED = EARLIER
EARLIER_DEPLETED = EARLIER
EARLIER_RESTORED = EARLIER
EMPTY = 0.0000
SOME = 1.0000
COLUMN_IN_STOCK = 4
COLUMN_UPDATED = 2
COLUMN_RESTORED = 6


def add_stocks(
        db,
        product_id,
        depot_id,
        shelf_type='store',
        *,
        in_stock=EMPTY,
        depleted=EARLIER_DEPLETED,
        updated=EARLIER_UPDATED,
        restored=EARLIER_RESTORED,
):
    cursor = db.cursor()
    cursor.execute(
        sql_queries._add_to_stocks_query(
            product_id,
            depot_id,
            in_stock,
            depleted,
            updated,
            restored,
            shelf_type,
        ),
    )


def update_stocks(
        db, product_id, depot_id, shelf_type='store', *, in_stock=EMPTY,
):
    cursor = db.cursor()
    cursor.execute(
        sql_queries._update_stocks_query(
            product_id, depot_id, shelf_type, in_stock,
        ),
    )


def fetch_stocks(db, product_id, depot_id, shelf_type='store'):
    cursor = db.cursor()
    cursor.execute(
        sql_queries._fetch_stocks_query(product_id, depot_id, shelf_type),
    )
    return next(enumerate(cursor))[1]


def get_in_stock(row):
    return row[COLUMN_IN_STOCK]


def get_restored(row):
    return row[COLUMN_RESTORED]


def get_updated(row):
    return row[COLUMN_UPDATED]


# Если для товара, которого не было в наличии, приходят ненулевые остатки,
# в БД возводится флаг restored.
async def test_stocks_restored(taxi_overlord_catalog, pgsql):
    product_id = '1'
    depot_id = '1'

    db = pgsql['overlord_catalog']

    add_stocks(
        db,
        product_id,
        depot_id,
        in_stock=EMPTY,
        updated=EARLIER_UPDATED,
        depleted=EARLIER_DEPLETED,
        restored=EARLIER_RESTORED,
    )
    after_add = fetch_stocks(db, product_id, depot_id)

    assert get_restored(after_add) == EARLIER_RESTORED

    update_stocks(db, product_id, depot_id, in_stock=SOME)
    after_update = fetch_stocks(db, product_id, depot_id)

    assert get_in_stock(after_update) == SOME
    assert get_restored(after_update) > EARLIER_RESTORED
    assert get_restored(after_update) == get_updated(after_update)
