import pytest

from eats_order_integration.generated.cron import run_cron

CRON_SETTINGS = ['eats_order_integration.crontasks.update_places', '-t', '0']


@pytest.mark.config(
    EATS_ORDER_INTEGRATION_UPDATE_PLACES_SETTINGS={'enabled': False},
)
async def test_should_not_start_if_disabled(mock_eats_core_retail):
    @mock_eats_core_retail('/v1/places/by-place-groups/retrieve/page-count')
    async def mock_page_count():
        return {}

    @mock_eats_core_retail('/v1/places/by-place-groups/retrieve')
    async def mock_retrieve():
        return {}

    await run_cron.main(CRON_SETTINGS)

    assert not mock_page_count.has_calls
    assert not mock_retrieve.has_calls


@pytest.mark.config(
    EATS_ORDER_INTEGRATION_UPDATE_PLACES_SETTINGS={
        'enabled': True,
        'place_group_ids_per_request': 30,
    },
)
async def test_should_fail_if_nothing_updated(mock_eats_core_retail):
    @mock_eats_core_retail('/v1/places/by-place-group-ids/retrieve/page-count')
    async def mock_page_count(request):
        return {'page_count': 0}

    with pytest.raises(Exception, match='No places updated'):
        await run_cron.main(CRON_SETTINGS)

    assert mock_page_count.has_calls


@pytest.mark.config(
    EATS_ORDER_INTEGRATION_UPDATE_PLACES_SETTINGS={
        'enabled': True,
        'places_rate_limit': 10,
        'place_group_ids_per_request': 10,
    },
)
async def test_should_insert_new(
        cron_context, mock_eats_core_retail, pgsql, load_json,
):
    @mock_eats_core_retail('/v1/places/by-place-group-ids/retrieve/page-count')
    async def mock_page_count(request):  # pylint:disable=unused-variable
        return {'page_count': 1}

    @mock_eats_core_retail('/v1/places/by-place-group-ids/retrieve')
    async def mock_retrieve(request):
        return load_json('places_response.json')['new']

    assert _get_count(pgsql, 'places') == 1

    await run_cron.main(CRON_SETTINGS)

    assert mock_page_count.times_called == 1
    assert mock_retrieve.times_called == 1
    assert _get_count(pgsql, 'places') == 2

    await _check_places_data(
        pgsql, load_json('places_data.json')['insert_new'],
    )


@pytest.mark.config(
    EATS_ORDER_INTEGRATION_UPDATE_PLACES_SETTINGS={
        'enabled': True,
        'places_rate_limit': 10,
        'place_group_ids_per_request': 10,
    },
)
async def test_should_update_existing(
        cron_context, mock_eats_core_retail, pgsql, load_json,
):
    @mock_eats_core_retail('/v1/places/by-place-group-ids/retrieve/page-count')
    async def mock_page_count(request):  # pylint:disable=unused-variable
        return {'page_count': 1}

    @mock_eats_core_retail('/v1/places/by-place-group-ids/retrieve')
    async def mock_retrieve(request):
        return load_json('places_response.json')['existing']

    assert _get_count(pgsql, 'places') == 1

    await run_cron.main(CRON_SETTINGS)

    assert mock_page_count.times_called == 1
    assert mock_retrieve.times_called == 1
    assert _get_count(pgsql, 'places') == 1

    await _check_places_data(
        pgsql, load_json('places_data.json')['update_existing'],
    )


async def _check_places_data(pgsql, expected_data):
    with pgsql['eats_order_integration'].dict_cursor() as cursor:
        cursor.execute('SELECT * FROM places')
        actual_data = [row for row in cursor]

    for i, expected_elem in enumerate(expected_data):
        assert actual_data[i]['place_id'] == expected_elem['place_id']
        assert (
            actual_data[i]['place_group_id'] == expected_elem['place_group_id']
        )
        assert actual_data[i]['brand_id'] == expected_elem['brand_id']
        assert actual_data[i]['brand_name'] == expected_elem['brand_name']


def _get_count(pgsql, table_name):
    with pgsql['eats_order_integration'].cursor() as cursor:
        cursor.execute(f'select count(*) from {table_name}')
        count = list(row[0] for row in cursor)[0]
    return count
