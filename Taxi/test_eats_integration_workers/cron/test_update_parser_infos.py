import pytest

from eats_integration_workers.generated.cron import run_cron


async def test_should_not_start_if_disabled(
        cron_context, cron_runner, mock_eats_core_retail,
):
    @mock_eats_core_retail('/v1/brands/retrieve')
    async def mock_brands_retrieve():
        return {}

    await run_cron.main(
        ['eats_integration_workers.crontasks.update_parser_infos', '-t', '0'],
    )

    assert not mock_brands_retrieve.has_calls


@pytest.mark.config(
    EATS_INTEGRATION_WORKERS_UPDATE_PARSER_INFOS_SETTINGS={'enabled': True},
)
async def test_should_correct_execute(
        cron_context, pgsql, cron_runner, mock_eats_core_retail,
):
    @mock_eats_core_retail('/v1/brands/retrieve')
    async def mock_brands_retrieve(request):
        return {'brands': [{'id': 'id', 'name': 'name', 'slug': 'slug'}]}

    @mock_eats_core_retail('/v1/brand/places/retrieve')
    async def mock_places_retrieve(request):
        return {
            'places': [
                dict(
                    enabled=True,
                    id='place_id',
                    parser_enabled=True,
                    slug='slug_id',
                    brand_id='brand_id',
                    external_id='external_id',
                    parser_name='parser_name',
                    stock_reset_limit=123,
                    place_group_id='1',
                ),
            ],
            'meta': {'limit': 10},
        }

    # pylint: disable=unused-variable
    @mock_eats_core_retail('/v1/brand/place-groups/retrieve')
    async def mock_place_groups_retrieve(request):
        return {
            'place_groups': [
                dict(
                    id='1',
                    name='mock_name',
                    parser_days_of_week='1111111',
                    parser_hours='09:00',
                    stop_list_enabled=False,
                    is_vendor=False,
                    stock_reset_limit=123,
                    dev_filter='{"menu": 1}',
                    menu_parser_options='{"should_retrieve_ids_for_stocks_from_feed": true}',  # noqa: F401,E501
                ),
            ],
        }

    assert get_parser_infos_count(pgsql) == 0
    await run_cron.main(
        ['eats_integration_workers.crontasks.update_parser_infos', '-t', '0'],
    )
    assert get_parser_infos_count(pgsql) == 1
    with pgsql['eats_integration_workers'].cursor() as cursor:
        cursor.execute(
            'select dev_filter, menu_parser_options '
            'from eats_integration_workers.parser_infos '
            'limit 1',
        )
        row = next(cursor)
        dev_filter, menu_parser_options = row[0], row[1]
        assert dev_filter['menu'] == 1
        assert menu_parser_options['should_retrieve_ids_for_stocks_from_feed']

    assert mock_brands_retrieve.has_calls
    assert mock_places_retrieve.has_calls


def get_parser_infos_count(pgsql):
    with pgsql['eats_integration_workers'].cursor() as cursor:
        cursor.execute(
            'select count(*) from eats_integration_workers.parser_infos',
        )
        count = list(row[0] for row in cursor)[0]
    return count
