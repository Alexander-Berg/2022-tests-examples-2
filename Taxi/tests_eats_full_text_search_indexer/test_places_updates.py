import pytest


SERVICE = 'eats_fts'


@pytest.mark.config(
    EATS_FULL_TEXT_SEARCH_INDEXER_PLACES_UPDATES_SETTINGS={
        'saas_settings': {
            'service_alias': SERVICE,
            'prefix': 2,
            'place_document_batch_size': 1,
        },
        'use_document_meta': True,
        'use_market_document_meta': True,
        'market_prefix': 42,
    },
)
async def test_catalog_storage_periodic(
        taxi_eats_full_text_search_indexer, mockserver, load_json,
):
    """
    Проверяем отправку документов с информацией
    о заведении в saas из catalog-storage
    """

    # multiline path just to pass flake8
    @mockserver.json_handler(
        (
            '/eats-catalog-storage'
            '/internal/eats-catalog-storage/v1'
            '/places/updates'
        ),
    )
    def catalog_storage(request):
        return load_json('catalog_storage_response.json')

    @mockserver.json_handler(
        '/saas-push/push/{service}'.format(service=SERVICE),
    )
    def saas_push(request):
        assert request.json == load_json('saas_place_document.json')
        return {
            'written': True,
            'attempts': [
                {
                    'comment': 'ok',
                    'written': True,
                    'attempt': 0,
                    'shard': '0-65535',
                },
            ],
            'comment': 'ok',
        }

    await taxi_eats_full_text_search_indexer.run_task(
        'catalog-storage-periodic',
    )

    assert catalog_storage.times_called > 0
    assert saas_push.times_called > 0
