import pytest

from eats_place_groups_replica.generated.cron import run_cron

CRON_SETTINGS = [
    'eats_place_groups_replica.crontasks.update_place_groups',
    '-t',
    '0',
]


async def test_should_not_start_if_disabled(
        cron_context, cron_runner, mock_eats_core_retail,
):
    @mock_eats_core_retail('/v1/place-groups/parser-info/retrieve/page-count')
    async def mock_page_count_retrieve():
        return {}

    await run_cron.main(CRON_SETTINGS)

    assert not mock_page_count_retrieve.has_calls


@pytest.mark.parametrize(
    'skip_fields,parser_index',
    [([], 0), (['clientId', 'clientSecret', 'scope', 'vendorHost'], 1)],
)
async def test_should_insert_new_place_groups(
        taxi_config,
        cron_context,
        cron_runner,
        mock_eats_core_retail,
        pgsql,
        load_json,
        skip_fields,
        parser_index,
        stq,
):
    taxi_config.set(
        EATS_PLACE_GROUPS_REPLICA_UPDATE_PLACE_GROUPS_AND_PLACES_SETTINGS=(
            {
                'enabled': True,
                'place_groups_rate_limit': 10,
                'parser_names': ['retail_menu'],
                'parser_options_dont_save_fields': skip_fields,
            }
        ),
    )

    @mock_eats_core_retail('/v1/place-groups/parser-info/retrieve/page-count')
    async def mock_page_count_retrieve(request):
        return load_json('pages_response.json')

    @mock_eats_core_retail('/v1/place-groups/parser-info/retrieve')
    async def mock_place_groups_retrieve(request):
        return load_json('place_groups_response.json')['new']

    assert _get_count(pgsql, 'place_groups') == 0

    await run_cron.main(CRON_SETTINGS)

    assert mock_page_count_retrieve.times_called == 1
    assert mock_place_groups_retrieve.times_called == 2
    assert _get_count(pgsql, 'place_groups') == 4
    res = _get_time(pgsql, 'place_groups')
    data = load_json('place_groups_response.json')['new']['items']
    assert len(res) == len(data)
    for index, place_group in enumerate(res):
        assert place_group['parser_hours'] == data[index]['parser_hours']
        assert (
            place_group['price_parser_times']
            == data[index]['price_parser_times']
        )

    res = _get_parser_options(pgsql, 'place_groups')
    data = load_json('place_groups_response.json')['parser_options'][
        parser_index
    ]
    assert len(res) == len(data)
    for index, place_group in enumerate(res):
        assert place_group['parser_options'] == data[index]

    assert (
        stq.eats_integration_shooter_update_place_group_settings.times_called
        == 2
    )


def _get_count(pgsql, table_name):
    with pgsql['eats_place_groups_replica'].dict_cursor() as cursor:
        cursor.execute(f'select count(*) from {table_name}')
        count = cursor.fetchone()
    return count[0]


def _get_time(pgsql, table_name):
    with pgsql['eats_place_groups_replica'].dict_cursor() as cursor:
        cursor.execute(
            f'select parser_hours, price_parser_times from {table_name}',
        )
        data = cursor.fetchall()
    return data


def _get_parser_options(pgsql, table_name):
    with pgsql['eats_place_groups_replica'].dict_cursor() as cursor:
        cursor.execute(f'select parser_options from {table_name}')
        data = cursor.fetchall()
    return data
