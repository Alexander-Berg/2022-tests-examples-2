# root conftest for service eats-full-text-search
import dataclasses
import typing

import pytest

from tests_eats_full_text_search import rest_menu_storage


pytest_plugins = ['eats_full_text_search_plugins.pytest_plugins']


@pytest.fixture(autouse=True, name='grocery_api')
def grocery_api(mockserver):
    """
    Фикстура сервиса grocery-api.
    """

    @mockserver.json_handler('/grocery-api/lavka/v1/api/v1/search')
    def _grocery_api(request):
        return mockserver.make_response('Internal Server Error', status=500)


@pytest.fixture(autouse=True, name='eats_nomenclature')
def eats_nomenclature(mockserver):
    """
    Фикстура сервиса eats-numenclature
    """

    @mockserver.json_handler('/eats-nomenclature/v2/place/assortment/details')
    def _eats_nomenclature(request):
        return mockserver.make_response('Internal Server Error', status=500)


@pytest.fixture(autouse=True, name='eats_fts_elastic_search')
def eats_fts_elastic_search(mockserver):
    """
    Фикстура elastic search
    """

    @mockserver.json_handler(
        '/eats-fts-elastic-search/menu_item_production/_search',
    )
    def _eats_fts_elastic_search(request):
        return mockserver.make_response('Internal Server Error', status=500)


@pytest.fixture(autouse=True, name='umlaas_eats')
def umlaas_eats(mockserver):
    """
    Фикстура umlaas-eats
    """

    @mockserver.json_handler('/umlaas-eats/umlaas-eats/v1/eats-search-ranking')
    def _umlaas_eats(request):
        return mockserver.make_response('Internal Server Error', status=500)


@pytest.fixture(autouse=True, name='eats_catalog')
def eats_catalog(mockserver):
    class Context:
        def __init__(self):
            self.blocks = []
            self.assert_callback = None

        def add_block(self, block):
            self.blocks.append(block)

        def reset(self):
            self.blocks = []
            self.assert_callback = None

        @property
        def times_called(self) -> int:
            return catalog_for_full_text_search.times_called

    ctx = Context()

    @mockserver.json_handler(
        '/eats-catalog/internal/v1/catalog-for-full-text-search',
    )
    def catalog_for_full_text_search(request):
        if ctx.assert_callback:
            ctx.assert_callback(request)
        blocks = list(dataclasses.asdict(block) for block in ctx.blocks)
        return {'blocks': blocks}

    return ctx


@pytest.fixture(autouse=True, name='check_headers')
def check_headers():
    def _check_headers(request_headers, expected_headers):
        assert request_headers['x-platform'] == expected_headers['x-platform']
        assert (
            request_headers['x-app-version']
            == expected_headers['x-app-version']
        )
        assert (
            request_headers['X-YaTaxi-User']
            == expected_headers['X-YaTaxi-User']
        )
        assert (
            request_headers['x-device-id'] == expected_headers['x-device-id']
        )

    return _check_headers


@pytest.fixture()
def rest_menu_storage_items_preview(mockserver):
    class Context:
        def __init__(self):
            self.places: typing.List[rest_menu_storage.Place] = []
            self.status_code: int = 200
            self.assert_callback: typing.Optional[typing.Callable] = None

        @property
        def times_called(self) -> int:
            return items_preview.times_called

    ctx = Context()

    @mockserver.json_handler(
        '/eats-rest-menu-storage/internal/v1/items-preview',
    )
    def items_preview(request):
        if ctx.assert_callback:
            ctx.assert_callback(request)  # pylint: disable=not-callable
        response = rest_menu_storage.ItemsPreviewResponse(places=ctx.places)
        return mockserver.make_response(
            json=response.as_dict(), status=ctx.status_code,
        )

    return ctx


@pytest.fixture()
def rest_menu_storage_get_items(mockserver):
    class Context:
        def __init__(self):
            self.places: typing.List[rest_menu_storage.Place] = []
            self.status_code: int = 200
            self.assert_callback: typing.Optional[typing.Callable] = None

        @property
        def times_called(self) -> int:
            return get_items.times_called

    ctx = Context()

    @mockserver.json_handler('/eats-rest-menu-storage/internal/v1/get-items')
    def get_items(request):
        if ctx.assert_callback:
            ctx.assert_callback(request)  # pylint: disable=not-callable
        response = rest_menu_storage.GetItemsResponse(places=ctx.places)
        return mockserver.make_response(
            json=response.as_dict(), status=ctx.status_code,
        )

    return ctx


@pytest.fixture(autouse=True, name='set_retail_settings')
def set_retail_settings(taxi_config):
    def _set_retail_settings(
            items_formula_name='items_formula',
            categories_formula_name='categories_formula',
            star_settings='both',
            no_star_items_threshold=1,
            should_group_by_places=False,
            docs_in_group_count=None,
            groups_count=None,
            use_synonyms_dict=False,
            synonyms_dict_name='',
    ):
        taxi_config.set_values(
            {
                'EATS_FULL_TEXT_SEARCH_RETAIL_SAAS_SETTINGS': {
                    'service': 'eats_retail_search',
                    'categories_prefix': 1,
                    'items_prefix': 2,
                    'misspell': 'try_at_first',
                    'numdoc': 100,
                    'disjunction_batch_size': 100,
                    'saas_request_pool': 10,
                    'star_settings': star_settings,
                    'no_star_items_threshold': no_star_items_threshold,
                    'should_group_by_places': should_group_by_places,
                    'docs_in_group_count': docs_in_group_count,
                    'groups_count': groups_count,
                    'items_formula_name': items_formula_name,
                    'categories_formula_name': categories_formula_name,
                    'wizard_settings': {
                        'use_synonyms_dict': use_synonyms_dict,
                        'synonyms_dict_name': synonyms_dict_name,
                    },
                },
                'EATS_FULL_TEXT_SEARCH_SAAS_SETTINGS': {
                    'service': 'eats_fts',
                    'prefix': 3,
                    'misspell': 'force',
                },
                'EATS_FULL_TEXT_SEARCH_BLOCK_SETTINGS': {
                    'products_title': 'items_block',
                    'categories_title': 'categories_block',
                    'other_categories_title': 'other_category_block',
                    'other_products_title': 'other_items_block',
                },
                'EATS_FULL_TEXT_SEARCH_NOMENCLATURE_SETTINGS': {
                    'products_info_batch_size': 250,
                    'place_products_info_batch_size': 250,
                    'place_categories_get_parents_batch_size': 50,
                    'place_settings': {
                        '__default__': {'handlers_version': 'v2'},
                    },
                },
                'EATS_FULL_TEXT_SEARCH_SELECTOR': {
                    'min_versions': [
                        {'platform': 'ios_app', 'version': '5.15.0'},
                    ],
                },
            },
        )

    return _set_retail_settings


@pytest.fixture(name='sql_set_place')
def sql_set_place(pgsql):
    def _sql_set_place(place_id, place_slug, business):
        cursor = pgsql['eats_full_text_search_indexer'].cursor()
        cursor.execute(
            """
            INSERT INTO fts.place (
                place_id,
                place_slug,
                enabled,
                business
            ) VALUES (
                %s,
                %s,
                true,
                %s
            ) ON CONFLICT (place_id) DO UPDATE SET
                place_slug = excluded.place_slug,
                enabled = excluded.enabled,
                business = excluded.business
    """,
            (place_id, place_slug, business),
        )

    return _sql_set_place


@pytest.fixture(name='set_retail_saas_experiment')
def set_retail_saas_experiment(experiments3):
    def _set_retail_saas_experiment(enable):
        experiments3.add_experiment(
            name='eats_fts_retail_saas',
            consumers=['eats-full-text-search/saas'],
            match={'predicate': {'type': 'true'}, 'enabled': True},
            clauses=[
                {
                    'title': 'Title',
                    'predicate': {'type': 'true'},
                    'value': {'enable': enable},
                },
            ],
        )

    return _set_retail_saas_experiment
