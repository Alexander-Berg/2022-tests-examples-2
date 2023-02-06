import decimal

import pytest


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'fill_place_data.sql',
        'fill_additional_place_data.sql',
    ],
)
async def test_place_product_merging_brand_queue(
        brand_task_enqueue, pgsql, testpoint,
):
    @testpoint('yt-logger-new-prices')
    def yt_logger(data):
        assert False

    # check current data
    assert get_place_products(pgsql) == {
        (1, 1, 'item_origin_1', decimal.Decimal('999.0000'), None, None, None),
        (
            1,
            2,
            'item_origin_2',
            decimal.Decimal('999.0000'),
            decimal.Decimal('10'),
            None,
            None,
        ),
        (
            1,
            3,
            'item_origin_3',
            decimal.Decimal('999.0000'),
            decimal.Decimal('20'),
            None,
            None,
        ),
        (
            1,
            4,
            'item_origin_4',
            decimal.Decimal('999.0000'),
            decimal.Decimal('30'),
            None,
            None,
        ),
        (
            1,
            5,
            'item_origin_5',
            decimal.Decimal('999.0000'),
            decimal.Decimal('40'),
            None,
            None,
        ),
    }
    assert get_stocks(pgsql) == {(1, 10), (2, 20), (3, 30), (4, 0), (5, None)}

    # upload new nomenclature
    await brand_task_enqueue()

    # check merge without updating prices
    assert get_place_products(pgsql) == {
        (1, 1, 'item_origin_1', decimal.Decimal('999.0000'), None, None, None),
        (
            1,
            2,
            'item_origin_2',
            decimal.Decimal('999.0000'),
            decimal.Decimal('10'),
            None,
            None,
        ),
        (
            1,
            3,
            'item_origin_3',
            decimal.Decimal('999.0000'),
            decimal.Decimal('20'),
            None,
            None,
        ),
        (
            1,
            4,
            'item_origin_4',
            decimal.Decimal('999.0000'),
            decimal.Decimal('30'),
            'item 4 vendor code',
            'item 4 location',
        ),
        (
            1,
            5,
            'item_origin_5',
            decimal.Decimal('999.0000'),
            decimal.Decimal('40'),
            'vendor_code',
            'item 5 location',
        ),
        (1, 6, 'item_origin_6', None, None, 'vendor_code', 'item 6 location'),
        (2, 6, 'item_origin_6', None, None, 'vendor_code', 'item 6 location'),
        (2, 5, 'item_origin_5', None, None, 'vendor_code', 'item 5 location'),
        (
            2,
            4,
            'item_origin_4',
            None,
            None,
            'item 4 vendor code',
            'item 4 location',
        ),
    }
    assert get_stocks(pgsql) == {
        (1, 10),
        (2, 20),
        (3, 30),
        (4, 0),
        (5, None),
        (6, 0),
        (7, 0),
        (8, 0),
        (9, 0),
    }

    assert not yt_logger.has_calls


def get_place_products(pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        """
        select
          place_id, product_id, origin_id, price, vat, vendor_code, position
        from eats_nomenclature.places_products
        """,
    )
    return set(cursor)


def get_stocks(pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        """
        select
          place_product_id, value
        from eats_nomenclature.stocks
        """,
    )
    return set(cursor)
