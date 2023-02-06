import pytest

from eats_integration_workers.generated.cron import run_cron


@pytest.mark.config(
    EATS_INTEGRATION_WORKERS_PLACE_ITEMS_SETTINGS={'enable_cron_task': False},
)
async def test_should_not_start_if_disabled(
        cron_context, cron_runner, mock_eats_core_retail,
):
    @mock_eats_core_retail('/v1/place/items/retrieve')
    async def mock_brands_retrieve():
        return {}

    await run_cron.main(
        ['eats_integration_workers.crontasks.update_place_items', '-t', '0'],
    )

    assert not mock_brands_retrieve.has_calls


@pytest.mark.config(
    EATS_INTEGRATION_WORKERS_PLACE_ITEMS_SETTINGS={
        'enable_cron_task': True,
        'parsers': ['parser_name'],
    },
)
@pytest.mark.pgsql('eats_integration_workers', files=['parser_infos_data.sql'])
async def test_should_correct_execute(
        cron_context, pgsql, cron_runner, mock_eats_core_retail, load_json,
):
    @mock_eats_core_retail('/v1/place/items/retrieve')
    def mock_get_items(request):
        if 'cursor' in request.json:
            return load_json('eats_core_retail_get_items_2.json')

        return load_json('eats_core_retail_get_items.json')

    assert get_place_items_count(pgsql) == 1
    await run_cron.main(
        ['eats_integration_workers.crontasks.update_place_items', '-t', '0'],
    )
    assert mock_get_items.has_calls
    assert get_place_items_count(pgsql) == 4


def get_place_items_count(pgsql):
    with pgsql['eats_integration_workers'].cursor() as cursor:
        cursor.execute(
            'SELECT COUNT(*) FROM eats_integration_workers.place_items',
        )
        count = list(row[0] for row in cursor)[0]
    return count
