import pytest

from eats_integration_workers.generated.cron import run_cron


async def test_should_not_start_if_disabled(
        cron_context, cron_runner, mock_eats_core_retail,
):
    @mock_eats_core_retail('/v1/content_filters/retrieve/page_count')
    async def mock_page_count(request):
        return {}

    @mock_eats_core_retail('/v1/content_filters/retrieve')
    async def mock_retrieve(request):
        return {}

    await run_cron.main(
        [
            'eats_integration_workers.crontasks.upsert_content_filters',
            '-t',
            '0',
        ],
    )

    assert not mock_page_count.has_calls
    assert not mock_retrieve.has_calls


@pytest.mark.config(
    EATS_INTEGRATION_WORKERS_UPDATE_CONTENT_FILTERS_SETTINGS={
        'enable_cron_task': True,
    },
)
async def test_should_correct_execute(
        cron_context, pgsql, cron_runner, mock_eats_core_retail, load_json,
):
    @mock_eats_core_retail('/v1/content_filters/retrieve/page_count')
    async def mock_page_count(request):
        return {'page_count': 1}

    @mock_eats_core_retail('/v1/content_filters/retrieve')
    async def mock_retrieve(request):
        return load_json('content_filters_data.json')

    assert get_place_filters_count(pgsql) == 0
    assert get_group_filters_count(pgsql) == 0
    assert get_brand_filters_count(pgsql) == 0
    await run_cron.main(
        [
            'eats_integration_workers.crontasks.upsert_content_filters',
            '-t',
            '0',
        ],
    )
    assert get_place_filters_count(pgsql) == 1
    assert get_group_filters_count(pgsql) == 2
    assert get_brand_filters_count(pgsql) == 3

    assert mock_page_count.has_calls
    assert mock_retrieve.has_calls


def get_objects_count(pgsql, query):
    with pgsql['eats_integration_workers'].cursor() as cursor:
        cursor.execute(query)
        count = list(row[0] for row in cursor)[0]
    return count


def get_place_filters_count(pgsql):
    return get_objects_count(
        pgsql, 'select count(*) from eats_integration_workers.place_filters',
    )


def get_group_filters_count(pgsql):
    return get_objects_count(
        pgsql, 'select count(*) from eats_integration_workers.group_filters',
    )


def get_brand_filters_count(pgsql):
    return get_objects_count(
        pgsql, 'select count(*) from eats_integration_workers.brand_filters',
    )
