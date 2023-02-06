import pytest

import tests_eats_nomenclature.parametrize.displayed_stock_limits as stocks_utils  # noqa: E501 pylint: disable=line-too-long

ASSORTMENT_ID = 1
PLACE_SLUG = 'slug'
CATEGORY_ID = 'category_1_origin'


@stocks_utils.PARAMETRIZE_STOCKS_LIMITS
@pytest.mark.parametrize('stocks_reset_limit', [0, 1, 5])
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_get_nomenclature_products_stocks(
        taxi_eats_nomenclature,
        experiments3,
        pg_cursor,
        pg_realdict_cursor,
        # parametrize
        stocks_reset_limit,
        displayed_stocks_limits_applied,
        displayed_stocks_limits_exp_enabled,
):
    _sql_set_place_stock_limit(pg_cursor, PLACE_SLUG, stocks_reset_limit)
    stocks = _sql_get_stocks(pg_realdict_cursor, ASSORTMENT_ID)
    stocks_list = sorted(stocks)
    public_id_to_disp_stock_limit = {
        stocks_list[0][0]: 2,
        stocks_list[1][0]: 4,
    }

    if displayed_stocks_limits_exp_enabled:
        await stocks_utils.enable_displ_stock_limits_exp(
            taxi_eats_nomenclature,
            experiments3,
            public_id_to_disp_stock_limit,
        )

    response = await taxi_eats_nomenclature.get(
        f'/v1/nomenclature?slug={PLACE_SLUG}&category_id={CATEGORY_ID}',
    )

    assert response.status == 200

    _apply_limit_to_stocks(stocks, stocks_reset_limit)
    if displayed_stocks_limits_applied:
        _apply_displayed_limit_to_stocks(stocks, public_id_to_disp_stock_limit)

    assert map_response(response.json()) == stocks


def map_response(json):
    categories = json['categories']
    items = []
    for category in categories:
        for item in category['items']:
            items.append(item)

    return {
        p['public_id']: p['in_stock'] if 'in_stock' in p else None
        for p in items
    }


def _apply_limit_to_stocks(stocks, stocks_reset_limit):
    for public_id, value in stocks.items():
        if value is not None and value != 0 and value < stocks_reset_limit:
            stocks[public_id] = 0


def _apply_displayed_limit_to_stocks(stocks, public_id_to_disp_stock_limit):
    for public_id, value in stocks.items():
        if public_id not in public_id_to_disp_stock_limit:
            continue
        displayed_stock_limit = public_id_to_disp_stock_limit[public_id]
        if value is not None and value != 0 and value > displayed_stock_limit:
            stocks[public_id] = displayed_stock_limit


def _sql_set_place_stock_limit(pg_cursor, place_slug, stock_reset_limit):
    pg_cursor.execute(
        """
        update eats_nomenclature.places
        set stock_reset_limit = %s
        where slug = %s
        """,
        (stock_reset_limit, place_slug),
    )


def _sql_get_stocks(pg_realdict_cursor, assortment_id):
    cursor = pg_realdict_cursor
    cursor.execute(
        """
select p.public_id, cast(s.value as double precision) as value
from eats_nomenclature.places_products pp
join eats_nomenclature.categories_products cp
    on pp.product_id = cp.product_id
left join eats_nomenclature.stocks s
    on s.place_product_id = pp.id
left join eats_nomenclature.products p
    on p.origin_id = pp.origin_id
where pp.price > 0
    and cp.assortment_id = %s
order by p.public_id""",
        (assortment_id,),
    )
    return {i['public_id']: i['value'] for i in cursor}
