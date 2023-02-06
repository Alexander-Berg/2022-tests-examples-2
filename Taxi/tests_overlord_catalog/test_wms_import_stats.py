# pylint: disable=redefined-outer-name
import pytest


class WmsStatsContext:
    def __init__(self):
        self._stats = None
        self._api = None

    def set_api(self, stats_api):
        self._api = stats_api

    async def ensure_initialized(self):
        self._stats = {}
        stats = await self._get_stats_from_api()
        for name, json in stats.items():
            self._stats[name] = json

    #  returns diff between current stats and stats from
    #  timepoint when ensure_initialized was called
    #  'errors_in_a_row' returns from current stats
    async def get_stats(self):
        assert self._stats is not None

        stats = await self._get_stats_from_api()

        result = {}
        for name, json in stats.items():
            cur_stats = {} if name not in self._stats else self._stats[name]
            result[name] = {}
            for key, value in json.items():
                result[name][key] = value
                if key in cur_stats and key != 'errors_in_a_row':
                    result[name][key] -= cur_stats[key]

        return result

    async def _get_stats_from_api(self):
        assert self._api is not None

        stats_response = await self._api.get('/')
        assert stats_response.status_code == 200

        result = stats_response.json()['wms-imports']
        return {} if result is None else result


@pytest.fixture
def wms_stats_context(taxi_overlord_catalog_monitor):
    context = WmsStatsContext()
    context.set_api(taxi_overlord_catalog_monitor)

    return context


@pytest.mark.suspend_periodic_tasks('wms-assortment-sync-periodic')
async def test_assortment_import_stats(
        taxi_overlord_catalog, wms_stats_context, mockserver,
):
    await wms_stats_context.ensure_initialized()

    @mockserver.json_handler('/grocery-wms/api/external/assortments/v1/list')
    def _mock_assorment(request):
        assortments = (
            [
                {
                    'assortment_id': (
                        'a738bf0a70004eeabd83700908bcb37e000100010001'
                    ),
                    'created': '2020-03-13 07:11:02+0000',
                    'external_id': 'cbfef720-64f9-11ea-ae57-5f48aa4c17d2',
                    'lsn': 13,
                    'parent_id': (
                        '3ee237535f5c41a0b4b98ec43f353265000100010001'
                    ),
                    'serial': 4,
                    'status': 'active',
                    'title': 'DEMO Общий',
                    'updated': '2020-03-13 07:12:36+0000',
                    'parents': [],
                },
            ]
            if request.json['cursor'] != 'end'
            else []
        )
        return {'assortments': assortments, 'code': 'OK', 'cursor': 'end'}

    @mockserver.json_handler(
        '/grocery-wms/api/external/assortments/v1/products',
    )
    def _mock_assorment_items(request):
        products = (
            [
                {
                    'ap_id': '4db20b8c029644ef98a48f306dda3244000300010000',
                    'assortment_id': (
                        'b0911dc9664a4818a6faf9dea67b8828000200010001'
                    ),
                    'cob_time': 0,
                    'created': '2020-02-21 12:48:56+0000',
                    'lsn': 1,
                    'max': 12,
                    'min': 2,
                    'order': 50,
                    'product_id': (
                        '495fbfcf9d544d8a9c44db6ab2dee67e000200010000'
                    ),
                    'serial': 1,
                    'status': 'active',
                    'ttl_show': 0,
                    'updated': '2020-02-21 12:48:56+0000',
                },
            ]
            if request.json['cursor'] != 'end'
            else []
        )
        return {'assortment_products': products, 'code': 'OK', 'cursor': 'end'}

    await _run_assortment_sync(taxi_overlord_catalog)

    wms_stats = await wms_stats_context.get_stats()

    for name in ['wms_assortment', 'wms_assortment_items']:
        stats = wms_stats[name]
        assert stats['items_fetched'] == 1
        assert stats['errors'] == 0
        assert stats['errors_in_a_row'] == 0


@pytest.mark.suspend_periodic_tasks('wms-nomenclature-sync-periodic')
async def test_nomenclature_import_stats(
        taxi_overlord_catalog, wms_stats_context, mockserver,
):
    await wms_stats_context.ensure_initialized()

    @mockserver.json_handler('/grocery-wms/api/external/products/v1/products')
    def _mock_products(request):
        return {
            'code': 'OK',
            'cursor': 'end',
            'locale': 'ru_RU',
            'products': [],
        }

    @mockserver.json_handler('/grocery-wms/api/external/products/v1/groups')
    def _mock_categories(request):
        return {'code': 'OK', 'cursor': 'end', 'groups': [], 'locale': 'ru_RU'}

    await _run_nomenclature_sync(taxi_overlord_catalog)

    wms_stats = await wms_stats_context.get_stats()

    for name in ['wms_products', 'wms_groups']:
        stats = wms_stats[name]
        assert stats['items_fetched'] == 0
        assert stats['errors'] == 0
        assert stats['errors_in_a_row'] == 0


@pytest.mark.suspend_periodic_tasks('wms-price-lists-sync-periodic')
async def test_price_list_import_stats(
        taxi_overlord_catalog, wms_stats_context, mockserver,
):
    await wms_stats_context.ensure_initialized()

    @mockserver.json_handler('/grocery-wms/api/external/price_lists/v1/list')
    def _mock_price_lists(request):
        return {'code': 'OK', 'cursor': 'done', 'price_lists': []}

    @mockserver.json_handler(
        '/grocery-wms/api/external/price_lists/v1/products',
    )
    def _mock_price_list_items(request):
        return {'code': 'OK', 'cursor': 'done', 'price_list_products': []}

    await _run_price_list_sync(taxi_overlord_catalog)

    wms_stats = await wms_stats_context.get_stats()

    for name in ['wms_price_list', 'wms_price_list_item']:
        stats = wms_stats[name]
        assert stats['items_fetched'] == 0
        assert stats['errors'] == 0
        assert stats['errors_in_a_row'] == 0


@pytest.mark.now('2020-01-16T17:15:00+00:00')
@pytest.mark.suspend_periodic_tasks('wms-stocks-sync-periodic')
async def test_stocks_import_stats(
        taxi_overlord_catalog, wms_stats_context, mockserver,
):
    await wms_stats_context.ensure_initialized()
    old_errors_in_a_row = (await wms_stats_context.get_stats()).get(
        'wms_stock', {'errors_in_a_row': 0},
    )['errors_in_a_row']

    @mockserver.json_handler('/grocery-wms/api/external/products/v1/stocks')
    def _mock_stocks(request):
        return mockserver.make_response('{}', 500)

    await _run_stock_sync(taxi_overlord_catalog)
    stats = (await wms_stats_context.get_stats())['wms_stock']
    assert stats['items_fetched'] == 0
    assert stats['errors'] == 1
    assert stats['errors_in_a_row'] == old_errors_in_a_row + 1


@pytest.mark.now(
    '2020-01-16T18:15:00+00:00',
)  # at least +15s from previous test
@pytest.mark.suspend_periodic_tasks('wms-stocks-sync-periodic')
async def test_import_stats_errors_in_a_row(
        taxi_overlord_catalog, wms_stats_context, mockserver,
):
    await wms_stats_context.ensure_initialized()

    @mockserver.json_handler('/grocery-wms/api/external/products/v1/stocks')
    def _mock_stocks(request):
        stocks = (
            [
                {
                    'count': 34,
                    'product_id': (
                        'fb70ba514e8e48378242939903da92f0000300010000'
                    ),
                    'store_id': 'ddb8a6fbcee34b38b5281d8ea6ef749a000100010000',
                    'shelf_type': 'store',
                },
            ]
            if request.json['cursor'] != 'end'
            else []
        )
        return {'code': 'OK', 'cursor': 'end', 'stocks': stocks}

    await _run_stock_sync(taxi_overlord_catalog)
    stats = (await wms_stats_context.get_stats())['wms_stock']
    assert stats['items_fetched'] == 1
    assert stats['errors'] == 0
    assert stats['errors_in_a_row'] == 0


@pytest.mark.suspend_periodic_tasks('wms-assortment-sync-periodic')
@pytest.mark.suspend_periodic_tasks('wms-nomenclature-sync-periodic')
@pytest.mark.suspend_periodic_tasks('wms-price-lists-sync-periodic')
@pytest.mark.suspend_periodic_tasks('wms-stocks-sync-periodic')
@pytest.mark.now(
    '2020-01-16T19:15:00+00:00',
)  # at least +15s from previous test
async def test_all_imports_present_in_stats(
        taxi_overlord_catalog, wms_stats_context, mockserver,
):
    await wms_stats_context.ensure_initialized()

    @mockserver.json_handler('/grocery-wms/api/external/assortments/v1/list')
    @mockserver.json_handler(
        '/grocery-wms/api/external/assortments/v1/products',
    )
    @mockserver.json_handler('/grocery-wms/api/external/products/v1/products')
    @mockserver.json_handler('/grocery-wms/api/external/products/v1/groups')
    @mockserver.json_handler('/grocery-wms/api/external/price_lists/v1/list')
    @mockserver.json_handler(
        '/grocery-wms/api/external/price_lists/v1/products',
    )
    @mockserver.json_handler('/grocery-wms/api/external/products/v1/stocks')
    def _mock_wms_500(request):
        return mockserver.make_response('{}', 500)

    await _run_assortment_sync(taxi_overlord_catalog)
    await _run_nomenclature_sync(taxi_overlord_catalog)
    await _run_price_list_sync(taxi_overlord_catalog)
    await _run_stock_sync(taxi_overlord_catalog)

    wms_stats = await wms_stats_context.get_stats()

    names = [
        'wms_assortment',
        'wms_assortment_items',
        'wms_groups',
        'wms_price_list',
        'wms_price_list_item',
        'wms_products',
        'wms_stock',
    ]
    assert len(wms_stats) == len(names)

    for name in names:
        assert name in wms_stats


async def _run_assortment_sync(taxi_overlord_catalog):
    await taxi_overlord_catalog.run_periodic_task(
        'wms-assortment-sync-periodic',
    )


async def _run_nomenclature_sync(taxi_overlord_catalog):
    await taxi_overlord_catalog.run_periodic_task(
        'wms-nomenclature-sync-periodic',
    )


async def _run_price_list_sync(taxi_overlord_catalog):
    await taxi_overlord_catalog.run_periodic_task(
        'wms-price-lists-sync-periodic',
    )


async def _run_stock_sync(taxi_overlord_catalog):
    await taxi_overlord_catalog.run_periodic_task('wms-stocks-sync-periodic')
