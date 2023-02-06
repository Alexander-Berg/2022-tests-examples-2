import pytest


INTERVAL = 3600


@pytest.mark.config(
    EATS_FULL_TEXT_SEARCH_INDEXER_CATALOG_STORAGE_PERIODIC={
        'full_update_interval': 7200,
        'incremental_update_interval': 3600,
        'updates_limit': 100,
        'updates_correction': 10,
        'enable': False,
        'enable_check_interval': INTERVAL,
    },
)
async def test_catalog_storage_periodic_disabled(
        testpoint, taxi_eats_full_text_search_indexer, mockserver,
):
    """
    Проверяем что код периодика catalog-storage не выполняется,
    если он выключен в конфиге
    """

    @testpoint('components:catalog-storage-periodic-disabled')
    def catalog_periodic_disabled(arg):
        pass

    @mockserver.json_handler(
        (
            '/eats-catalog-storage'
            '/internal/eats-catalog-storage/v1'
            '/places/updates'
        ),
    )
    def _catalog_storage(request):
        assert False, 'Should be unreacheble'

    await taxi_eats_full_text_search_indexer.run_task(
        'catalog-storage-periodic',
    )

    await catalog_periodic_disabled.wait_call()

    assert _catalog_storage.times_called == 0
