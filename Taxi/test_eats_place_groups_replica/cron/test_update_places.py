import pytest

from eats_place_groups_replica.generated.cron import run_cron


@pytest.mark.config(
    EATS_PLACE_GROUPS_REPLICA_UPDATE_PLACE_SETTINGS={'enabled': False},
)
async def test_should_not_start_if_disabled(
        cron_context, cron_runner, mock_eats_core_retail,
):
    @mock_eats_core_retail('/v1/places/by-place-group-ids/retrieve/page-count')
    async def mock_page_count_retrieve():
        return {}

    await run_cron.main(
        ['eats_place_groups_replica.crontasks.update_places', '-t', '0'],
    )

    assert not mock_page_count_retrieve.has_calls


@pytest.mark.config(
    EATS_PLACE_GROUPS_REPLICA_UPDATE_PLACE_SETTINGS={
        'enabled': True,
        'parsers': ['parser_name'],
        'places_rate_limit': 10,
    },
)
@pytest.mark.pgsql('eats_place_groups_replica', files=['places.sql'])
async def test_should_correct_execute(
        cron_context, pgsql, cron_runner, mock_eats_core_retail, load_json,
):
    @mock_eats_core_retail('/v1/places/by-place-group-ids/retrieve/page-count')
    async def mock_page_count_retrieve(request):
        return load_json('pages_response.json')

    @mock_eats_core_retail('/v1/places/by-place-group-ids/retrieve')
    def mock_get_items(request):
        return load_json('places_data.json')

    assert get_place_items_count(pgsql) == 1
    await run_cron.main(
        ['eats_place_groups_replica.crontasks.update_places', '-t', '0'],
    )
    assert mock_get_items.has_calls
    assert mock_page_count_retrieve.has_calls
    assert get_place_items_count(pgsql) == 2
    assert (
        get_business_type(pgsql)[0]['business_type']
        == load_json('places_data.json')['items'][0]['business_type']
    )


def get_place_items_count(pgsql):
    with pgsql['eats_place_groups_replica'].dict_cursor() as cursor:
        cursor.execute('SELECT COUNT(*) FROM places')
        count = cursor.fetchone()
    return count[0]


def get_business_type(pgsql):
    with pgsql['eats_place_groups_replica'].dict_cursor() as cursor:
        cursor.execute(f'select business_type from places')
        data = cursor.fetchall()
    return data
