import pytest


SERVICE = 'eats_fts'
SYNONYMS = ['kfc', 'кфс', 'кфц']


def set_synonyms(place_name: str):
    return pytest.mark.config(
        EATS_FULL_TEXT_SEARCH_INDEXER_STATIC_SYNONYMS={
            'list': [{'name': place_name, 'synonyms': SYNONYMS}],
        },
    )


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
@pytest.mark.parametrize(
    'place_name',
    (
        pytest.param('KFC', marks=set_synonyms('KFC'), id='Exact match eng'),
        pytest.param(
            'Теремок', marks=set_synonyms('Теремок'), id='Exact match rus',
        ),
        pytest.param(
            'KFC', marks=set_synonyms('kFc'), id='case insensitive eng',
        ),
        pytest.param(
            'Теремок',
            marks=set_synonyms('теремоК'),
            id='case insensitive rus',
        ),
    ),
)
async def test_static_synonyms(
        taxi_eats_full_text_search_indexer, mockserver, place_name,
):
    """
    Проверяем доклеивание синонимов для kfc
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
        return {
            'last_known_revision': 1,
            'places': [
                {
                    'business': 'restaurant',
                    'enabled': True,
                    'launched_at': '2021-09-02T00:00:00+03:00',
                    'name': place_name,
                    'id': 1,
                    'slug': 'my_place_slug',
                    'brand': {
                        'id': 1,
                        'slug': 'brand_slug_1',
                        'name': 'brand_name',
                        'picture_scale_type': 'aspect_fit',
                    },
                    'rating': {'admin': 4.7, 'count': 0, 'users': 0},
                    'region': {'geobase_ids': [], 'id': 1, 'time_zone': ''},
                    'updated_at': '2021-09-02T12:00:00+03:00',
                    'revision_id': 1,
                },
            ],
        }

    @mockserver.json_handler(
        '/saas-push/push/{service}'.format(service=SERVICE),
    )
    def saas_push(request):
        data = request.json
        expected_synonyms = ' '.join(SYNONYMS)
        doc = data['docs'][0]
        assert doc['title'] == {'type': '#zp', 'value': place_name}
        assert doc['z_eats_static_synonyms'] == {
            'type': '#zp',
            'value': expected_synonyms,
        }
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
