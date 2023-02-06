import pytest


@pytest.mark.config(
    FORM_BUILDER_GEOBASE_CACHED={
        'region_concurrency': 10,
        'db_insert_bulk_size': 50,
    },
)
async def test_do_stuff(mock_geobase, cron_runner, cron_context):
    @mock_geobase('/')
    def _handler_info(_):
        return {'last_update_timestamp': 1234}

    @mock_geobase('/subtree')
    def _handler_subtree(request):
        if int(request.query['id']) == 0:
            return [1, 2, 3]
        return []

    @mock_geobase('/region_by_id')
    def _handler_region_by_id(request):
        _regions = {
            1: {'id': 1, 'parent_id': 0, 'type': 5, 'population': 10},
            2: {'id': 2, 'parent_id': 1, 'type': 6, 'population': 5},
        }
        return _regions.get(
            int(request.query['id']), mock_geobase.make_response(status=400),
        )

    @mock_geobase('/find_country')
    def _handler_find_country(request):
        return {2: 1}.get(int(request.query['id']), 0)

    @mock_geobase('/supported_linguistics')
    def _handler_supported_linguistics(_):
        return ['ru', 'en']

    @mock_geobase('/linguistics_for_region')
    def _handler_linguistics_for_region(request):
        id_ = int(request.query['id'])
        lang = request.query['lang']
        linguistics = [
            {'nominative_case': 'Russia', 'lang': 'en', 'id': 1},
            {'nominative_case': 'Россия', 'lang': 'ru', 'id': 1},
            {'nominative_case': 'Moscow', 'lang': 'en', 'id': 2},
            {'nominative_case': 'Москва', 'lang': 'ru', 'id': 2},
        ]
        found = [
            x for x in linguistics if x['id'] == id_ and x['lang'] == lang
        ]
        return found[0] if found else mock_geobase.make_response(status=400)

    await cron_runner.preload_geodata()

    assert _handler_supported_linguistics.times_called == 1
    regions = await cron_context.pg.primary.fetch(
        'SELECT * FROM caches.geodata_regions ORDER BY id',
    )
    assert [dict(x) for x in regions] == [
        {
            'country_id': None,
            'id': 1,
            'last_updated_ts': 1234,
            'parent_id': None,
            'region_type': 5,
            'population': 10,
        },
        {
            'country_id': 1,
            'id': 2,
            'last_updated_ts': 1234,
            'parent_id': 1,
            'region_type': 6,
            'population': 5,
        },
    ]
    names = await cron_context.pg.primary.fetch(
        'SELECT * FROM caches.geodata_localized_names '
        'ORDER BY region_id, lang',
    )
    assert [dict(x) for x in names] == [
        {
            'real_name': 'Russia',
            'lower_name': 'russia',
            'lang': 'en',
            'region_id': 1,
        },
        {
            'real_name': 'Россия',
            'lower_name': 'россия',
            'lang': 'ru',
            'region_id': 1,
        },
        {
            'real_name': 'Moscow',
            'lower_name': 'moscow',
            'lang': 'en',
            'region_id': 2,
        },
        {
            'real_name': 'Москва',
            'lower_name': 'москва',
            'lang': 'ru',
            'region_id': 2,
        },
    ]
