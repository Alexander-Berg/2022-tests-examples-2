# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest

from eats_full_text_search_indexer_plugins import *  # noqa: F403 F401


SERVICE = 'eats_fts'
PREFIX = 1


@pytest.fixture(name='mock_yql')
def mock_yql_operations(mockserver):
    @mockserver.json_handler('/yql/api/v2/operations')
    def _mock_yql_operations(req):
        assert req.json['action'] == 'RUN'
        assert 'content' in req.json
        return mockserver.make_response(
            status=200,
            json={
                'createdAt': '2021-02-02T00:00:00.060326Z',
                'execMode': 'RUN',
                'externalQueryIds': [],
                'id': '1234',
                'projectId': '5f97ce6768a6f5c079a61aa3',
                'queryData': {
                    'attributes': {'user_agent': ''},
                    'clusterType': 'UNKNOWN',
                    'content': '',
                    'files': [],
                    'parameters': {},
                    'type': 'SQLv1',
                },
                'queryType': 'SQLv1',
                'status': 'PENDING',
                'title': '',
                'updatedAt': '2021-02-02T00:00:00.132560Z',
                'username': 'testsuite',
                'version': 0,
                'workerId': '6974305d-f18339ad-174b72f9-376d5dea',
            },
        )

    return _mock_yql_operations


@pytest.fixture(name='saas_mock')
def saas_mock(mockserver):
    @mockserver.json_handler(
        '/saas-push/push/{service}'.format(service=SERVICE),
    )
    def _saas_push(request):
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

    return _saas_push


SAAS_FTS_SERVICE = 'eats_fts'
SAAS_FTS_PREFIX = 1
SAAS_RETAIL_SEARCH_SERVICE = 'eats_retail_search'
SAAS_RETAIL_SEARCH_CATEGORIES_PREFIX = 1
SAAS_RETAIL_SEARCH_ITEMS_PREFIX = 2


@pytest.fixture
def set_retail_settings(taxi_config):
    def impl(
            saas_service_send_to=SAAS_RETAIL_SEARCH_SERVICE,
            use_document_meta=True,
            track_document_changes=True,
            store_price=False,
            integration_version='v2',
            integration_version_per_place=None,
            index_root_categories=True,
            index_promo_categories=True,
            index_only_default_assortment=False,
            assortment_names_to_index_per_brand=None,
            fail_limit=1,
    ):
        taxi_config.set_values(
            {
                'EATS_FULL_TEXT_SEARCH_INDEXER_UPDATE_RETAIL_PLACE_SETTINGS': {
                    'saas_settings': {
                        'service_alias': SAAS_FTS_SERVICE,
                        'prefix': SAAS_FTS_PREFIX,
                        'place_document_batch_size': 1,
                    },
                    'retail_saas_settings': {
                        'service_alias': SAAS_RETAIL_SEARCH_SERVICE,
                        'items_prefix': SAAS_RETAIL_SEARCH_ITEMS_PREFIX,
                        'categories_prefix': (
                            SAAS_RETAIL_SEARCH_CATEGORIES_PREFIX
                        ),
                        'place_document_batch_size': 1,
                    },
                    'saas_service_send_to': saas_service_send_to,
                    'use_retail_document_meta': use_document_meta,
                    'track_retail_document_changes': track_document_changes,
                    'use_document_meta': use_document_meta,
                    'track_document_changes': track_document_changes,
                    'store_price': store_price,
                    'fail_limit': fail_limit,
                    'min_retry_delay_ms': 60000,
                    'max_retry_delay_ms': 1800000,
                },
                'EATS_FULL_TEXT_SEARCH_INDEXER_NOMENCLATURE_SETTINGS': {
                    'integration_version': integration_version,
                    'integration_version_per_place': (
                        integration_version_per_place
                    ),
                    'index_root_categories': index_root_categories,
                    'index_promo_categories': index_promo_categories,
                    'index_only_default_assortment': (
                        index_only_default_assortment
                    ),
                    'assortment_names_to_index_per_brand': (
                        assortment_names_to_index_per_brand
                    ),
                },
            },
        )

    return impl
