import pytest

PLACE_ID = 3105
EATS_CATALOG_STORAGE_CACHE_SETTINGS = [
    {
        'id': PLACE_ID,
        'revision_id': 5,
        'updated_at': '2020-11-26T10:00:00.000000Z',
        'brand': {
            'id': 3105,
            'slug': 'slug',
            'name': 'brand_name',
            'picture_scale_type': 'aspect_fit',
        },
        'business': 'restaurant',
    },
]


@pytest.mark.eats_catalog_storage_cache(EATS_CATALOG_STORAGE_CACHE_SETTINGS)
async def test_stq_finish_order(stq_runner):
    await stq_runner.eats_order_stats_finish_order.call(
        task_id='finish_order',
        kwargs={
            'order_nr': '300-400',
            'place_id': str(PLACE_ID),
            'order_type': 'order_type',
            'shipping_type': 'delivery',
            'finished_at': '2021-08-27T18:01:00+00:00',
        },
    )
