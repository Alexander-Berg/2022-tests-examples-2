import pytest


MOSCOW_REGION_ID = 213
TEL_AVIV_REGION_ID = 131


ITEM_IN_STOCK = {
    'id': '123-grocery',
    'categories': ['some_category_id'],
    'name': 'Яндекс Станция',
    'description': ('Яндекс Станция 100г. ' 'Производитель: Яндекс.Лавка'),
    'price': '100',
    'images': ['http://url/{w}x{h}'],
    'currency': 'RUB',
    'in_stock': 4,
    'age_group': '12',
    'unit': 'unit',
    'quantity': 4,
    'depot_slug': 'depot_slug',
}

ITEM_NOT_IN_STOCK = {
    'id': '124-grocery',
    'categories': ['some_category_id'],
    'name': 'Яндекс Станция мини',
    'description': ('Яндекс Станция мини 50г. ' 'Производитель: Яндекс.Лавка'),
    'price': '0',
    'images': ['http://url/{w}x{h}'],
    'currency': 'RUB',
    'in_stock': 0,
    'age_group': '12',
    'unit': 'unit',
    'quantity': 4,
    'depot_slug': 'depot_slug',
}


YATAXI_EXPECTED_FEEDS = {
    'mobile_fb': 'mobile_fb_feed.xml',
    'mobile_direct': 'mobile_direct_feed.xml',
    'mobile_google': 'mobile_google_feed.csv',
    'web_fb': 'web_fb_feed.xml',
    'web_direct': 'web_direct_feed.xml',
    'web_google': 'web_google_feed.csv',
    'lavket_ios_direct': 'lavket_ios_direct_feed.xml',
    'lavket_android_direct': 'lavket_android_direct_feed.xml',
}

YANGO_EXPECTED_FEEDS = {
    'mobile_fb': 'mobile_yango_fb_feed.xml',
    'mobile_direct': 'mobile_yango_direct_feed.xml',
    'mobile_google': 'mobile_yango_google_feed.csv',
    'web_fb': 'web_yango_fb_feed.xml',
    'web_direct': 'web_yango_direct_feed.xml',
    'web_google': 'web_yango_google_feed.csv',
    'lavket_ios_direct': 'lavket_ios_direct_feed.xml',
    'lavket_android_direct': 'lavket_android_direct_feed.xml',
}


GROCERY_FEEDS_BRAND_META = pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='grocery_feeds_brand_meta',
    consumers=['grocery-feeds/common'],
    clauses=[
        {
            'title': 'yataxi',
            'value': {'brand': 'yataxi'},
            'predicate': {
                'type': 'eq',
                'init': {
                    'arg_name': 'region_id',
                    'arg_type': 'int',
                    'value': MOSCOW_REGION_ID,
                },
            },
        },
        {
            'title': 'yango',
            'value': {'brand': 'yango'},
            'predicate': {
                'type': 'eq',
                'init': {
                    'arg_name': 'region_id',
                    'arg_type': 'int',
                    'value': TEL_AVIV_REGION_ID,
                },
            },
        },
    ],
)

GROCERY_FEEDS_LOCALE = pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='grocery_feeds_locale',
    consumers=['grocery-feeds/common'],
    clauses=[
        {
            'title': 'isr',
            'value': {'locale': 'en-il'},
            'predicate': {
                'type': 'eq',
                'init': {
                    'arg_name': 'region_id',
                    'arg_type': 'int',
                    'value': TEL_AVIV_REGION_ID,
                },
            },
        },
    ],
    default_value={'locale': 'default_locale'},
)


@pytest.mark.now('2020-05-01T12:00:00+0300')
@GROCERY_FEEDS_BRAND_META
@GROCERY_FEEDS_LOCALE
@pytest.mark.config(
    GROCERY_FEEDS_S3_SETTINGS={'max_retries': 3, 'timeout_ms': 120000},
    GROCERY_FEEDS_PERIODIC_TASK={'period_seconds': 3600, 'max_offers': 0},
)
@pytest.mark.parametrize(
    'region_id, expected_feeds',
    [
        (MOSCOW_REGION_ID, YATAXI_EXPECTED_FEEDS),
        (TEL_AVIV_REGION_ID, YANGO_EXPECTED_FEEDS),
    ],
)
async def test_basic(
        taxi_grocery_feeds,
        mockserver,
        testpoint,
        load,
        mds_s3,
        region_id,
        expected_feeds,
):
    @testpoint('feeds-distlock-finished')
    def feeds_distlock_finished(arg):
        pass

    @mockserver.json_handler('/overlord-catalog/admin/catalog/v1/countries')
    def countries_mock(request):
        return {
            'countries': [
                {'country_id': 'some_country_id', 'name': 'some_country_name'},
            ],
        }

    @mockserver.json_handler('/overlord-catalog/admin/catalog/v1/cities')
    def cities_mock(request):
        return {
            'cities': [{'city_id': str(region_id), 'name': 'some_city_name'}],
        }

    @mockserver.json_handler('/overlord-catalog/feeds/raw_items_data')
    def items_mock(request):
        return {
            'categories': [
                {
                    'id': 'some_category_id',
                    'parent_id': 'some_parent_id',
                    'name': 'some_category',
                    'deep_link': 'some_deep_link',
                },
            ],
            'goods': [ITEM_IN_STOCK, ITEM_NOT_IN_STOCK],
        }

    if region_id == MOSCOW_REGION_ID:
        mds_s3.set_data(
            facebook={'mobile': load(expected_feeds['mobile_fb'])},
            direct={
                'mobile': load(expected_feeds['mobile_direct']),
                'web': load(expected_feeds['web_direct']),
                'lavket_ios': load(expected_feeds['lavket_ios_direct']),
                'lavket_android': load(
                    expected_feeds['lavket_android_direct'],
                ),
            },
            google={
                'mobile': load(expected_feeds['mobile_google']),
                'web': load(expected_feeds['web_google']),
            },
        )
    else:
        mds_s3.set_data(
            facebook={'mobile': load(expected_feeds['mobile_fb'])},
            direct={
                'mobile': load(expected_feeds['mobile_direct']),
                'web': load(expected_feeds['web_direct']),
            },
            google={
                'mobile': load(expected_feeds['mobile_google']),
                'web': load(expected_feeds['web_google']),
            },
        )

    await taxi_grocery_feeds.run_distlock_task('feeds-generation-component')

    assert (await feeds_distlock_finished.wait_call())['arg'][
        'success_regions'
    ] == [region_id]

    assert countries_mock.times_called == 1
    assert cities_mock.times_called == 1
    assert items_mock.times_called == 1
