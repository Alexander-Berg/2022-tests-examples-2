import dataclasses

import pytest


@dataclasses.dataclass
class ParserInfos:
    # pylint: disable=invalid-name
    id: str
    brand_id: str
    external_id: str
    parser_name: str
    stock_reset_limit: int
    place_group_id: str
    dev_filter: str
    menu_parser_options: str


@pytest.mark.parametrize(
    'place_id, brand_id, external_id, place_group_id, task_id, '
    'stock_reset_limit, dev_filter, menu_parser_options',
    [['1', '12', '123', '1234', '12345', 1, '{}', '{}']],
)
async def test_fill_parser_infos(
        pgsql,
        stq3_context,
        cron_runner,
        load_json,
        taxi_config,
        place_id,
        brand_id,
        external_id,
        place_group_id,
        task_id,
        stock_reset_limit,
        dev_filter,
        menu_parser_options,
):
    parser_infos = ParserInfos(
        id=place_id,
        brand_id=brand_id,
        external_id=external_id,
        parser_name='parser_name',
        stock_reset_limit=stock_reset_limit,
        place_group_id=place_group_id,
        dev_filter=dev_filter,
        menu_parser_options=menu_parser_options,
    )
    query, binds = stq3_context.sqlt.parser_info_upsert(
        parser_infos=[parser_infos],
    )
    await stq3_context.pg.master.execute(query, *binds)
    query, binds = stq3_context.sqlt.parser_info_get(place_id=place_id)
    row = await stq3_context.pg.secondary.fetchrow(query, *binds)

    assert row['place_id'] == place_id
    assert row['brand_id'] == brand_id
    assert row['external_id'] == external_id
    assert row['parser_name'] == 'parser_name'
    assert row['stock_reset_limit'] == stock_reset_limit
    assert row['place_group_id'] == place_group_id
    assert row['dev_filter'] == dev_filter
    assert row['menu_parser_options'] == menu_parser_options
