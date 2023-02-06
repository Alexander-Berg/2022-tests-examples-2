import psycopg2

from . import utils


async def test_update_place_existing_mapping(
        taxi_eats_full_text_search, mockserver, stq_runner, pgsql,
):
    """
    Проверяем stq задачу обновления маппингов
    идентификаторов для 1 плейса
    при этом в базе уже есть данные
    1. place_id -> brand_id
    2. brand_id picture_scale = 'aspect_fit', должен измениться
    на null
    3. Есть по одному маппингу id в базе
    в ответе ручки будут новые данные для существующих маппингов
    """

    place_id = 1
    place_slug = 'place_slug'
    brand_id = 1000
    brand_slug = 'brand_slug'

    cursor = pgsql['eats_full_text_search_indexer'].cursor(
        cursor_factory=psycopg2.extras.DictCursor,
    )
    db_items_mapping = utils.get_items_mapping(cursor, place_id)
    assert len(db_items_mapping) == 1

    categories_mapping = [
        {
            'place_id': place_id,
            'origin_id': 'O_1',
            'core_id': 10,
            'core_parent_id': 101,
        },
        {
            'place_id': place_id,
            'origin_id': 'O_1_1',
            'core_id': 11,
            'core_parent_id': 101,
        },
    ]

    items_mapping = [
        {
            'place_id': place_id,
            'origin_id': 'O_2_2',
            'core_id': 20,
            'core_parent_category_id': 201,
            'updated_at': db_items_mapping[0]['updated_at'],
        },
        {
            'place_id': place_id,
            'origin_id': 'O_2',
            'core_id': 22,
            'core_parent_category_id': 202,
            'updated_at': db_items_mapping[0]['updated_at'],
        },
    ]

    @mockserver.json_handler(
        '/eats-core-retail/v1/nomenclature/id-mapping/retrieve',
    )
    def _mapping_retrive(request):
        args = request.json
        assert args['place_id'] == place_slug
        return {
            'place_id': place_id,
            'brand': {'brand_id': brand_id, 'slug': brand_slug},
            'categories': [
                {
                    'nomenclature_id': mapping['origin_id'],
                    'eats_id': mapping['core_id'],
                    'parent_eats_id': mapping['core_parent_id'],
                }
                for mapping in categories_mapping
            ],
            'originals_to_mapped': [
                {
                    'nomenclature_id': mapping['origin_id'],
                    'eats_id': mapping['core_id'],
                    'eats_category_id': mapping['core_parent_category_id'],
                }
                for mapping in items_mapping
            ],
            'total': 1,
        }

    await stq_runner.eats_full_text_search_update_place_mapping.call(
        task_id='update_mapping', kwargs={'place_slug': place_slug},
    )

    assert _mapping_retrive.times_called == 1
    places = utils.get_all_places(cursor)
    assert len(places) == 1
    place = places[0]
    assert place['place_id'] == place_id
    assert place['place_slug'] == place_slug
    assert place['brand_id'] == brand_id

    scale = utils.get_brand_scale(cursor, brand_id)
    assert scale is None

    db_items_mapping = utils.get_items_mapping(cursor, place_id)
    assert len(db_items_mapping) == 2
    for idx, mapping in enumerate(items_mapping):
        assert db_items_mapping[idx]['core_id'] == mapping['core_id']
        assert (
            db_items_mapping[idx]['core_parent_category_id']
            == mapping['core_parent_category_id']
        )
        assert db_items_mapping[idx]['origin_id'] == mapping['origin_id']
        assert db_items_mapping[idx]['updated_at'] > mapping['updated_at']
