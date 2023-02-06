import psycopg2

from . import utils


async def test_update_place_mapping(
        taxi_eats_full_text_search, mockserver, stq_runner, pgsql,
):
    """
    Проверяем stq задачу обновления маппингов
    идентификаторов для 1 плейса
    """

    place_id = 1
    place_slug = 'place_slug'
    brand_id = 1000
    brand_slug = 'brand_slug'
    picture_scale = 'acpect_fit'

    categories_mapping = {
        'place_id': place_id,
        'origin_id': 'O_1',
        'core_id': 10,
        'core_parent_id': 100,
    }

    items_mapping = {
        'place_id': place_id,
        'origin_id': 'O_2',
        'core_id': 20,
        'core_parent_category_id': 200,
    }

    @mockserver.json_handler(
        '/eats-core-retail/v1/nomenclature/id-mapping/retrieve',
    )
    def _mapping_retrive(request):
        args = request.json
        assert args['place_id'] == place_slug
        return {
            'place_id': place_id,
            'brand': {
                'brand_id': brand_id,
                'slug': brand_slug,
                'scale': picture_scale,
            },
            'categories': [
                {
                    'nomenclature_id': categories_mapping['origin_id'],
                    'eats_id': categories_mapping['core_id'],
                    'parent_eats_id': categories_mapping['core_parent_id'],
                },
            ],
            'originals_to_mapped': [
                {
                    'nomenclature_id': items_mapping['origin_id'],
                    'eats_id': items_mapping['core_id'],
                    'eats_category_id': items_mapping[
                        'core_parent_category_id'
                    ],
                },
                {
                    'nomenclature_id': items_mapping['origin_id'],
                    'eats_id': items_mapping['core_id'],
                    'eats_category_id': (
                        items_mapping['core_parent_category_id'] + 1
                    ),
                    # Проверяем что дубликаты eats_id,nomenclature_id
                    # ничего не ломают
                },
            ],
            'total': 1,
        }

    await stq_runner.eats_full_text_search_update_place_mapping.call(
        task_id='update_mapping', kwargs={'place_slug': place_slug},
    )

    assert _mapping_retrive.times_called == 1
    cursor = pgsql['eats_full_text_search_indexer'].cursor(
        cursor_factory=psycopg2.extras.DictCursor,
    )
    places = utils.get_all_places(cursor)
    assert len(places) == 1
    place = places[0]
    assert place['place_id'] == place_id
    assert place['place_slug'] == place_slug
    assert place['brand_id'] == brand_id

    scale = utils.get_brand_scale(cursor, brand_id)
    assert scale == picture_scale

    db_items_mapping = utils.get_items_mapping(cursor, place_id)
    assert len(db_items_mapping) == 1
    assert db_items_mapping[0]['core_id'] == items_mapping['core_id']
    assert (
        db_items_mapping[0]['core_parent_category_id']
        == items_mapping['core_parent_category_id']
    )
    assert db_items_mapping[0]['origin_id'] == items_mapping['origin_id']
