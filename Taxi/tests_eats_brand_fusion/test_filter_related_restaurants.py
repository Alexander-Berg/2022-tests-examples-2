import pytest

TASK_PATH = 'brand-fusion'


@pytest.mark.config(
    EATS_BRAND_FUSION_EXCLUDED_PLACE_AND_BRAND_ID={
        'excluded_brand_ids': ['13', '1984'],
        'excluded_place_ids': ['1', '11111', '31'],
    },
    EATS_BRAND_FUSION_START_PERIODIC_BRAND_FUSION=True,
)
@pytest.mark.eats_catalog_storage_cache(
    [
        {
            'id': 1,
            'revision_id': 1,
            'updated_at': '2020-11-26T00:00:00.000000Z',
            'brand': {
                'id': 122333,
                'slug': 'slug',
                'name': 'name',
                'picture_scale_type': 'aspect_fit',
            },
        },
        {
            'id': 2,
            'revision_id': 2,
            'updated_at': '2020-11-26T00:00:00.000000Z',
            'brand': {
                'id': 122323313,
                'slug': 'slug',
                'name': 'name',
                'picture_scale_type': 'aspect_fit',
            },
        },
        {
            'id': 3,
            'revision_id': 3,
            'updated_at': '2020-11-26T00:00:00.000000Z',
            'brand': {
                'id': 122323313,
                'slug': 'slug',
                'name': 'name',
                'picture_scale_type': 'aspect_fit',
            },
        },
        {
            'id': 4,
            'revision_id': 4,
            'updated_at': '2020-11-26T00:00:00.000000Z',
            'brand': {
                'id': 122323313,
                'slug': 'slug',
                'name': 'name',
                'picture_scale_type': 'aspect_fit',
            },
        },
    ],
)
@pytest.mark.yt(
    static_table_data=[
        'yt_related_restaurants_data_filter_by_exception_sets.yaml',
    ],
)
@pytest.mark.usefixtures('yt_apply')
async def test_task_filter_by_exception_sets(
        testpoint,
        taxi_eats_brand_fusion,
        yt_apply_force,
        yt_apply,
        yt_client,
        eats_catalog_storage_cache,
):
    @testpoint('before-filter-related-restaurants')
    def before_filter(data):
        pass

    @testpoint('after-filter-related-restaurants')
    def after_filter(data):
        pass

    await taxi_eats_brand_fusion.run_task(TASK_PATH)

    assert before_filter.next_call()['data'] == {'size_before_filter': 2}
    assert after_filter.next_call()['data'] == {'size_after_filter': 1}


@pytest.mark.config(EATS_BRAND_FUSION_START_PERIODIC_BRAND_FUSION=True)
@pytest.mark.eats_catalog_storage_cache(
    [
        {
            'id': 5,
            'revision_id': 1,
            'updated_at': '2020-11-26T00:00:00.000000Z',
            'brand': {
                'id': 122333,
                'slug': 'slug',
                'name': 'name',
                'picture_scale_type': 'aspect_fit',
            },
        },
        {
            'id': 6,
            'revision_id': 2,
            'updated_at': '2020-11-26T00:00:00.000000Z',
            'brand': {
                'id': 122323313,
                'slug': 'slug',
                'name': 'name',
                'picture_scale_type': 'aspect_fit',
            },
        },
        {
            'id': 7,
            'revision_id': 3,
            'updated_at': '2020-11-26T00:00:00.000000Z',
            'brand': {
                'id': 122323313,
                'slug': 'slug',
                'name': 'name',
                'picture_scale_type': 'aspect_fit',
            },
        },
        {
            'id': 8,
            'revision_id': 4,
            'updated_at': '2020-11-26T00:00:00.000000Z',
            'brand': {
                'id': 122323313,
                'slug': 'slug',
                'name': 'name',
                'picture_scale_type': 'aspect_fit',
            },
        },
    ],
)
@pytest.mark.yt(static_table_data=['yt_related_restaurants_data.yaml'])
@pytest.mark.usefixtures('yt_apply')
async def test_task_filter_nothing(
        testpoint,
        taxi_eats_brand_fusion,
        taxi_eats_brand_fusion_monitor,
        yt_apply_force,
        yt_apply,
        yt_client,
        eats_catalog_storage_cache,
):
    @testpoint('before-filter-related-restaurants')
    def before_filter(data):
        pass

    @testpoint('after-filter-related-restaurants')
    def after_filter(data):
        pass

    await taxi_eats_brand_fusion.run_task(TASK_PATH)

    assert before_filter.next_call()['data'] == {'size_before_filter': 3}
    assert after_filter.next_call()['data'] == {'size_after_filter': 3}

    statistics = await taxi_eats_brand_fusion_monitor.get_metric(
        'eats_brand_fusion_sizes_of_table',
    )

    assert statistics['table_size_before_filter'] == 3
    assert statistics['table_size_after_filter'] == 3
    assert statistics['connected_components'] == 1


@pytest.mark.config(EATS_BRAND_FUSION_START_PERIODIC_BRAND_FUSION=True)
@pytest.mark.eats_catalog_storage_cache(
    [
        {
            'id': 666,
            'revision_id': 1,
            'updated_at': '2020-11-26T00:00:00.000000Z',
            'brand': {
                'id': 122333,
                'slug': 'slug',
                'name': 'name',
                'picture_scale_type': 'aspect_fit',
            },
        },
        {
            'id': 667,
            'revision_id': 2,
            'updated_at': '2020-11-26T00:00:00.000000Z',
            'brand': {
                'id': 122323313,
                'slug': 'slug',
                'name': 'name',
                'picture_scale_type': 'aspect_fit',
            },
        },
        {
            'id': 26,
            'revision_id': 3,
            'updated_at': '2020-11-26T00:00:00.000000Z',
            'brand': {
                'id': 122333,
                'slug': 'slug',
                'name': 'name',
                'picture_scale_type': 'aspect_fit',
            },
        },
        {
            'id': 31,
            'revision_id': 4,
            'updated_at': '2020-11-26T00:00:00.000000Z',
            'brand': {
                'id': 122333,
                'slug': 'slug',
                'name': 'name',
                'picture_scale_type': 'aspect_fit',
            },
        },
        {
            'id': 465226,
            'revision_id': 5,
            'updated_at': '2020-11-26T00:00:00.000000Z',
            'brand': {
                'id': 122333,
                'slug': 'slug',
                'name': 'name',
                'picture_scale_type': 'aspect_fit',
            },
        },
        {
            'id': 465231,
            'revision_id': 6,
            'updated_at': '2020-11-26T00:00:00.000000Z',
            'brand': {
                'id': 122333,
                'slug': 'slug',
                'name': 'name',
                'picture_scale_type': 'aspect_fit',
            },
        },
    ],
)
@pytest.mark.yt(
    static_table_data=['yt_related_restaurants_data_big_table.yaml'],
)
@pytest.mark.usefixtures('yt_apply')
async def test_task_sync(
        testpoint,
        taxi_eats_brand_fusion,
        yt_apply_force,
        yt_apply,
        yt_client,
        eats_catalog_storage_cache,
):
    @testpoint('before-filter-related-restaurants')
    def before_filter(data):
        pass

    @testpoint('after-filter-related-restaurants')
    def after_filter(data):
        pass

    await taxi_eats_brand_fusion.run_task(TASK_PATH)

    assert before_filter.next_call()['data'] == {'size_before_filter': 14}
    assert after_filter.next_call()['data'] == {'size_after_filter': 14}
