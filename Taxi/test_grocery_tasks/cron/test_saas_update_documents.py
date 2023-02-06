# pylint: disable=redefined-outer-name,protected-access
from datetime import datetime
import json
import typing

import pytest

from testsuite.utils import ordered_object

from grocery_tasks.saas.update_documents import make_ferryman_timestamp
from grocery_tasks.saas.update_documents import run

NOW = '2021-02-03T23:00:00+03:00'

PREFIX = 123
YT_BASEPATH = '//home/lavka/testing/services/grocery-tasks'
YT_FULLPATH = YT_BASEPATH + '/saas/docs'
DEFAULT_PREFIX_SETTINGS = {'kpses': [{'prefix': PREFIX}]}

TRANSLATIONS = pytest.mark.translations(
    wms_items={
        'product-1_title': {'ru': 'Йогурт «Чудо» клубника'},
        'product-1_long_title': {'ru': 'Йогурт «Чудо» клубника'},
    },
)

BASE_SETTINGS = {
    'yt-path': YT_BASEPATH,
    'prefix': PREFIX,
    'overlord-limit': 500,
    'grocery-menu-limit': 500,
}


def _make_translation_settings(locales):
    return {
        'products-keyset': 'wms_items',
        'categories-keyset': 'wms_items',
        'products-long-title-keyset': 'wms_items',
        'category-title-key-suffix': '_name',
        'title-key-suffix': '_title',
        'long-title-key-suffix': '_long_title',
        'categories-tags-keyset': 'wms_items',
        'products-tags-keyset': 'wms_items',
        'tags-key-suffix': '_synonyms',
        'tags-value-delimiter': ',',
        'one-zone-per-tag': True,
        'zone-tag-delimiter': ' ',
        'supported-locales': locales,
    }


@pytest.mark.now(NOW)
@pytest.mark.config(
    GROCERY_SAAS_SETTINGS={**BASE_SETTINGS, **DEFAULT_PREFIX_SETTINGS},
)
async def test_saas_ferryman_add_table_call(
        patch, mockserver, load_json, cron_context,
):
    @patch('grocery_tasks.saas.update_documents._yt_upload')
    async def _yt_upload(context, dict_entries):
        pass

    @mockserver.json_handler('/saas-ferryman/add-table')
    async def _mock_saas_ferryman(request):
        assert 'namespace' in request.query and request.query[
            'namespace'
        ] == str(PREFIX)
        assert 'path' in request.query and request.query['path'] == YT_FULLPATH
        assert 'timestamp' in request.query and request.query[
            'timestamp'
        ] == str(make_ferryman_timestamp(datetime.fromisoformat(NOW)))
        return mockserver.make_response(
            status=202, json={'batch': '1612338976637551'},
        )

    @mockserver.json_handler(
        '/overlord-catalog/internal/v1/catalog/v1/products-data',
    )
    async def _mock_overlord_products(request):
        return load_json('overlord_empty_response_products.json')

    @mockserver.json_handler(
        '/overlord-catalog/internal/v1/catalog/v1/categories-data',
    )
    async def _mock_overlord_categories(request):
        return load_json('overlord_empty_response_categories.json')

    await run(cron_context)
    assert _mock_saas_ferryman.times_called == 1


@pytest.mark.translations(
    wms_items={
        'id-1_name': {'ru': 'Вкусвилл'},
        'id-1_synonyms': {'ru': 'магазин,Здоровое питание'},
        'id-2_name': {'en': 'Bars'},
        'id-3_synonyms': {'ru': 'Десерт'},
        'id-4_synonyms': {'ru': 'йогурт,питьевой'},
        'id-4_title': {'ru': 'Йогурт «Чудо» клубника'},
        'id-4_long_title': {'ru': 'Йогурт «Чудо» клубника 2%'},
        'id-5_long_title': {'ru': 'Oreo молочное с печеньем'},
        'meta-product-1_long_title': {'ru': 'Комбо 1'},
    },
)
@pytest.mark.parametrize(
    'one_zone_per_tag, expected_tags_zones',
    [
        (
            False,
            [
                {
                    'z_ru_tags': {
                        'value': 'магазин Здоровое питание',
                        'type': '#z',
                    },
                },
                {'z_en_tags': {'value': '', 'type': '#z'}},
                {'z_ru_tags': {'value': 'йогурт питьевой', 'type': '#z'}},
                {'z_ru_tags': {'value': '', 'type': '#z'}},
            ],
        ),
        (
            True,
            [
                {
                    'z_ru_tags': [
                        {'value': 'магазин', 'type': '#z'},
                        {'value': 'Здоровое питание', 'type': '#z'},
                    ],
                },
                {'z_en_tags': {'value': '', 'type': '#z'}},
                {
                    'z_ru_tags': [
                        {'value': 'йогурт', 'type': '#z'},
                        {'value': 'питьевой', 'type': '#z'},
                    ],
                },
                {'z_ru_tags': {'value': '', 'type': '#z'}},
            ],
        ),
    ],
)
async def test_prepare_documents(
        patch,
        mockserver,
        load_json,
        cron_context,
        one_zone_per_tag,
        expected_tags_zones,
        grocery_menu,
):
    grocery_menu.set_return_data(True)

    cron_context.config.GROCERY_SAAS_SETTINGS = {
        **BASE_SETTINGS,
        'products-keyset': 'wms_items',
        'categories-keyset': 'wms_items',
        'products-long-title-keyset': 'wms_items',
        'category-title-key-suffix': '_name',
        'title-key-suffix': '_title',
        'long-title-key-suffix': '_long_title',
        'categories-tags-keyset': 'wms_items',
        'products-tags-keyset': 'wms_items',
        'tags-key-suffix': '_synonyms',
        'tags-value-delimiter': ',',
        'one-zone-per-tag': one_zone_per_tag,
        'zone-tag-delimiter': ' ',
        'supported-locales': ['ru', 'en'],
        **DEFAULT_PREFIX_SETTINGS,
    }

    @patch('grocery_tasks.saas.update_documents._yt_upload')
    async def yt_upload(context, dict_entries):
        pass

    @mockserver.json_handler('saas-ferryman/add-table')
    async def _mock_saas_ferryman(request):
        return mockserver.make_response(
            status=202, json={'batch': '1612338976637551'},
        )

    @mockserver.json_handler(
        '/overlord-catalog/internal/v1/catalog/v1/products-data',
    )
    async def _mock_overlord_products(request):
        if 'cursor' in request.json:
            return load_json('overlord_empty_response_products.json')
        return load_json('overlord_basic_response_products.json')

    @mockserver.json_handler(
        '/overlord-catalog/internal/v1/catalog/v1/categories-data',
    )
    async def _mock_overlord_categories(request):
        if 'cursor' in request.json:
            return load_json('overlord_empty_response_categories.json')
        return load_json('overlord_basic_response_categories.json')

    await run(cron_context)

    dict_entries = yt_upload.call['dict_entries']
    ordered_object.assert_eq(
        dict_entries,
        [
            {
                'JsonMessage': json.dumps(
                    {
                        'action': 'modify',
                        'prefix': PREFIX,
                        'docs': [
                            {
                                'options': {
                                    'mime_type': 'text/plain',
                                    'charset': 'uft8',
                                    'language': 'ru',
                                    'language2': 'en',
                                    'language_default': 'ru',
                                    'language_default2': 'en',
                                },
                                's_item_id': {'value': 'id-1', 'type': '#p'},
                                'i_item_type': {'value': '1', 'type': '#pi'},
                                'url': 'category/id-1',
                                'z_ru_title': {
                                    'value': 'Вкусвилл',
                                    'type': '#z',
                                },
                                **expected_tags_zones[0],
                            },
                        ],
                    },
                    ensure_ascii=False,
                ),
            },
            {
                'JsonMessage': json.dumps(
                    {
                        'action': 'modify',
                        'prefix': PREFIX,
                        'docs': [
                            {
                                'options': {
                                    'mime_type': 'text/plain',
                                    'charset': 'uft8',
                                    'language': 'ru',
                                    'language2': 'en',
                                    'language_default': 'ru',
                                    'language_default2': 'en',
                                },
                                's_item_id': {'value': 'id-2', 'type': '#p'},
                                'i_item_type': {'value': '1', 'type': '#pi'},
                                'url': 'category/id-2',
                                'z_en_title': {'value': 'Bars', 'type': '#z'},
                                **expected_tags_zones[1],
                            },
                        ],
                    },
                    ensure_ascii=False,
                ),
            },
            {
                'JsonMessage': json.dumps(
                    {
                        'action': 'modify',
                        'prefix': PREFIX,
                        'docs': [
                            {
                                'options': {
                                    'mime_type': 'text/plain',
                                    'charset': 'uft8',
                                    'language': 'ru',
                                    'language2': 'en',
                                    'language_default': 'ru',
                                    'language_default2': 'en',
                                },
                                's_item_id': {'value': 'id-4', 'type': '#p'},
                                'i_item_type': {'value': '2', 'type': '#pi'},
                                'url': 'product/id-4',
                                'z_ru_title': {
                                    'value': 'Йогурт «Чудо» клубника',
                                    'type': '#z',
                                },
                                'z_ru_long_title': {
                                    'value': 'Йогурт «Чудо» клубника 2%',
                                    'type': '#z',
                                },
                                **expected_tags_zones[2],
                            },
                        ],
                    },
                    ensure_ascii=False,
                ),
            },
            {
                'JsonMessage': json.dumps(
                    {
                        'action': 'modify',
                        'prefix': PREFIX,
                        'docs': [
                            {
                                'options': {
                                    'mime_type': 'text/plain',
                                    'charset': 'uft8',
                                    'language': 'ru',
                                    'language2': 'en',
                                    'language_default': 'ru',
                                    'language_default2': 'en',
                                },
                                's_item_id': {'value': 'id-5', 'type': '#p'},
                                'i_item_type': {'value': '2', 'type': '#pi'},
                                'url': 'product/id-5',
                                'z_ru_title': {'value': '', 'type': '#z'},
                                'z_ru_long_title': {
                                    'value': 'Oreo молочное с печеньем',
                                    'type': '#z',
                                },
                                **expected_tags_zones[3],
                            },
                        ],
                    },
                    ensure_ascii=False,
                ),
            },
            {
                'JsonMessage': json.dumps(
                    {
                        'action': 'modify',
                        'prefix': 123,
                        'docs': [
                            {
                                'options': {
                                    'mime_type': 'text/plain',
                                    'charset': 'uft8',
                                    'language': 'ru',
                                    'language2': 'en',
                                    'language_default': 'ru',
                                    'language_default2': 'en',
                                },
                                's_item_id': {
                                    'value': 'meta-product-1',
                                    'type': '#p',
                                },
                                'i_item_type': {'value': '3', 'type': '#pi'},
                                'url': 'combo/meta-product-1',
                                'z_ru_title': {
                                    'value': 'Комбо 1',
                                    'type': '#z',
                                },
                                'z_ru_tags': {'value': '', 'type': '#z'},
                            },
                        ],
                    },
                    ensure_ascii=False,
                ),
            },
        ],
        [''],
    )


@pytest.mark.config(
    GROCERY_SAAS_SETTINGS={
        **BASE_SETTINGS,
        **_make_translation_settings(['ru', 'en']),
        **DEFAULT_PREFIX_SETTINGS,
    },
)
@pytest.mark.translations(
    wms_items={
        'id-4_synonyms': {'ru': 'йогурт,питьевой', 'en': 'drinking,yogurt'},
        'id-4_title': {
            'ru': 'Йогурт «Чудо» клубника',
            'en': 'Yogurt «Chudo» strawberry',
        },
        'id-4_long_title': {
            'ru': 'Йогурт «Чудо» клубника 2%',
            'en': 'Yogurt «Chudo» strawberry 2%',
        },
        'id-5_long_title': {'ru': 'Oreo молочное с печеньем'},
    },
)
async def test_localized_strings_in_individual_zones(
        patch, mockserver, load_json, cron_context,
):
    @patch('grocery_tasks.saas.update_documents._yt_upload')
    async def yt_upload(context, dict_entries):
        pass

    @mockserver.json_handler('saas-ferryman/add-table')
    async def _mock_saas_ferryman(request):
        return mockserver.make_response(
            status=202, json={'batch': '1612338976637551'},
        )

    @mockserver.json_handler(
        '/overlord-catalog/internal/v1/catalog/v1/products-data',
    )
    async def _mock_overlord_products(request):
        if 'cursor' in request.json:
            return load_json('overlord_empty_response_products.json')
        return load_json('overlord_basic_response_products.json')

    @mockserver.json_handler(
        '/overlord-catalog/internal/v1/catalog/v1/categories-data',
    )
    async def _mock_overlord_categories(request):
        if 'cursor' in request.json:
            return load_json('overlord_empty_response_categories.json')
        return load_json('overlord_basic_response_categories.json')

    await run(cron_context)

    dict_entries = yt_upload.call['dict_entries']
    row = json.loads(dict_entries[0]['JsonMessage'])['docs'][0]
    assert row['z_ru_title']['value'] == 'Йогурт «Чудо» клубника'
    assert row['z_en_title']['value'] == 'Yogurt «Chudo» strawberry'
    assert row['z_ru_long_title']['value'] == 'Йогурт «Чудо» клубника 2%'
    assert row['z_en_long_title']['value'] == 'Yogurt «Chudo» strawberry 2%'
    assert row['z_ru_tags'][0]['value'] == 'йогурт'
    assert row['z_ru_tags'][1]['value'] == 'питьевой'
    assert row['z_en_tags'][0]['value'] == 'drinking'
    assert row['z_en_tags'][1]['value'] == 'yogurt'

    row = json.loads(dict_entries[1]['JsonMessage'])['docs'][0]
    assert 'z_en_title' not in row
    assert 'z_en_long_title' not in row
    assert 'z_en_tags' not in row


@TRANSLATIONS
@pytest.mark.config(
    GROCERY_SAAS_SETTINGS={
        **BASE_SETTINGS,
        **_make_translation_settings(['ru']),
        'kpses': [{'prefix': PREFIX, 'include_cpa_zone': True}],
        'cpa_collect_settings': {'interval_in_days': 1, 'clicks_threshold': 1},
    },
)
@pytest.mark.parametrize(
    'rows, expected_zones',
    [
        pytest.param(
            [['product-1', ['query-1', 'query-2', 'query-3']]],
            [
                {'type': '#z', 'value': 'query-1'},
                {'type': '#z', 'value': 'query-2'},
                {'type': '#z', 'value': 'query-3'},
            ],
            id='several clicks',
        ),
        pytest.param(
            [['product-1', ['query-1', b'query-2', 'query-3']]],
            [
                {'type': '#z', 'value': 'query-1'},
                {'type': '#z', 'value': 'query-3'},
            ],
            id='filter b-strings',
        ),
        pytest.param([], None, id='no clicks'),
    ],
)
async def test_include_cpa_zone(
        patch,
        mockserver,
        load_json,
        cron_context,
        overlord_catalog,
        rows,
        expected_zones,
):
    """ Тест проверяет, что для товаров, на которые кликнули в поисковой выдаче,
        добавляется специальная зона с текстами запросов, по которым эти выдачи
        были получены. """

    @patch('grocery_tasks.saas.update_documents._yt_upload')
    async def yt_upload(context, dict_entries):
        pass

    @mockserver.json_handler('saas-ferryman/add-table')
    async def _mock_saas_ferryman(request):
        return mockserver.make_response(
            status=202, json={'batch': '1612338976637551'},
        )

    # pylint: disable=unused-variable
    @patch('yql.api.v1.client.YqlClient.query')
    def query(*args, **kwargs):
        class MockedTable:
            def fetch_full_data(self):
                pass

            @property
            def rows(self):
                return rows

        class MockedResult:
            @property
            def status(self) -> str:
                return 'COMPLETED'

            @property
            def is_success(self) -> bool:
                return True

            @property
            def errors(self) -> typing.List[Exception]:
                return []

            def run(self):
                pass

            def get_results(self, *args, **kwargs):
                return self

            def __iter__(self):
                yield MockedTable()

        return MockedResult()

    overlord_catalog.add_product_data(
        product_id='product-1', title='product-1-title',
    )

    await run(cron_context)

    dict_entries = yt_upload.call['dict_entries']

    row = json.loads(dict_entries[0]['JsonMessage'])['docs'][0]
    assert (expected_zones and row['z_cpa'] == expected_zones) or (
        'z_cpa' not in row
    )


@TRANSLATIONS
@pytest.mark.parametrize(
    'prefixes',
    [
        pytest.param([], id='no one'),
        pytest.param([123], id='one'),
        pytest.param([123, 456, 789], id='multiple'),
    ],
)
async def test_include_multiple_prefixes(
        patch, mockserver, load_json, cron_context, overlord_catalog, prefixes,
):
    """ Тест проверяет, что в индекс может выгружаться разное число
        префиксов. """

    cron_context.config.GROCERY_SAAS_SETTINGS = {
        **BASE_SETTINGS,
        **_make_translation_settings(['ru']),
        'kpses': list(map(lambda prefix: {'prefix': prefix}, prefixes)),
    }

    @patch('grocery_tasks.saas.update_documents._yt_upload')
    async def yt_upload(context, dict_entries):
        pass

    @mockserver.json_handler('saas-ferryman/add-table')
    async def _mock_saas_ferryman(request):
        return mockserver.make_response(
            status=202, json={'batch': '1612338976637551'},
        )

    overlord_catalog.add_product_data(
        product_id='product-1', title='product-1-title',
    )

    await run(cron_context)

    dict_entries = yt_upload.call['dict_entries']
    assert len(dict_entries) == len(prefixes)

    found_prefixes = []
    for entry in dict_entries:
        row = json.loads(entry['JsonMessage'])
        prefix = row['prefix']
        found_prefixes.append(prefix)
        assert row['docs'][0]['s_item_id']['value'] == 'product-1'
    assert sorted(found_prefixes) == sorted(prefixes)


@pytest.mark.parametrize(
    'prefixes',
    [
        pytest.param([], id='no one'),
        pytest.param([123], id='one'),
        pytest.param([123, 456, 789], id='multiple'),
    ],
)
async def test_single_call_saas_ferryman(
        patch, mockserver, load_json, cron_context, overlord_catalog, prefixes,
):
    """ Тест проверяет, что для разного числа префиксов в индексе отправляется
        максимум одно сообщение add-table в saas-ferryman. """

    cron_context.config.GROCERY_SAAS_SETTINGS = {
        **BASE_SETTINGS,
        'kpses': list(map(lambda prefix: {'prefix': prefix}, prefixes)),
    }

    @patch('grocery_tasks.saas.update_documents._yt_upload')
    async def _yt_upload(context, dict_entries):
        pass

    @mockserver.json_handler('/saas-ferryman/add-table')
    async def _mock_saas_ferryman(request):
        return mockserver.make_response(
            status=202, json={'batch': '1612338976637551'},
        )

    await run(cron_context)
    assert _mock_saas_ferryman.times_called == (1 if prefixes else 0)
