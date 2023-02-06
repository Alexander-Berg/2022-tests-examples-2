import pytest


SERVICE = 'eats_fts'


def generate_config(enable: bool, quantity: int):
    return pytest.mark.config(
        EATS_FULL_TEXT_SEARCH_INDEXER_PLACE_TAGS={
            'enable': enable,
            'quantity': quantity,
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
    ('place_name', 'categories', 'expected_tags'),
    [
        pytest.param(
            'KFC',
            [
                {'id': 1, 'name': 'Фастфуд'},
                {'id': 2, 'name': 'Американская'},
                {'id': 3, 'name': 'Бургеры'},
            ],
            ['Фастфуд', 'Американская', 'Бургеры'],
            marks=generate_config(True, 0),
            id='test1',
        ),
        pytest.param(
            'KFC',
            [
                {'id': 1, 'name': 'Фастфуд'},
                {'id': 2, 'name': 'Американская'},
                {'id': 3, 'name': 'Бургеры'},
            ],
            ['Фастфуд', 'Американская', 'Бургеры'],
            marks=generate_config(True, 3),
            id='test2',
        ),
        pytest.param(
            'Torro Grill',
            [
                {'id': 1, 'name': 'Европейская'},
                {'id': 2, 'name': 'Американская'},
                {'id': 3, 'name': 'Бургеры'},
                {'id': 4, 'name': 'Стейки'},
            ],
            ['Европейская', 'Американская', 'Бургеры', 'Стейки'],
            marks=generate_config(True, 6),
            id='test3',
        ),
        pytest.param(
            'Prime',
            [
                {'id': 1, 'name': 'Здоровая еда'},
                {'id': 2, 'name': 'Суши'},
                {'id': 3, 'name': 'Европейская'},
                {'id': 4, 'name': 'Десерты'},
                {'id': 5, 'name': 'Выпечка'},
                {'id': 6, 'name': 'Завтраки'},
                {'id': 7, 'name': 'Сэндвичи'},
            ],
            ['Здоровая еда', 'Суши'],
            marks=generate_config(True, 2),
            id='test4',
        ),
        pytest.param(
            'Prime', [], None, marks=generate_config(True, 2), id='test5',
        ),
        pytest.param(
            'Prime', None, None, marks=generate_config(True, 2), id='test6',
        ),
        pytest.param(
            'KFC',
            [
                {'id': 1, 'name': 'Фастфуд'},
                {'id': 2, 'name': 'Американская'},
                {'id': 3, 'name': 'Бургеры'},
            ],
            None,
            marks=generate_config(False, 2),
            id='test7',
        ),
    ],
)
async def test_place_tags(
        taxi_eats_full_text_search_indexer,
        mockserver,
        place_name,
        categories,
        expected_tags,
):
    """
    Проверяем передачу тегов заведений в SaaS
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
        response = {
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
                    'categories': categories,
                },
            ],
        }
        if categories is not None:
            response['places'][0]['categories'] = categories
        return response

    @mockserver.json_handler(
        '/saas-push/push/{service}'.format(service=SERVICE),
    )
    def saas_push(request):
        data = request.json
        doc = data['docs'][0]
        assert doc['title'] == {'type': '#zp', 'value': place_name}
        if expected_tags is not None:
            tags = ' '.join(expected_tags)
            assert doc['z_tags'] == {'type': '#zp', 'value': tags}
        else:
            assert doc.get('z_tags') is None
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
