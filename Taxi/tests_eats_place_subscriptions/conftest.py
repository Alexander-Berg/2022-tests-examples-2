from psycopg2 import extras
import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from eats_place_subscriptions_plugins import *  # noqa: F403 F401

from tests_eats_place_subscriptions import utils


@pytest.fixture
def mock_restapp_authorizer(mockserver, request):
    @mockserver.json_handler('/eats-restapp-authorizer/v1/user-access/check')
    def _mock_authorizer(request):
        return mockserver.make_response(status=200)


@pytest.fixture
def pg_cursor(pgsql):
    return pgsql['eats_place_subscriptions'].cursor()


@pytest.fixture
def pg_realdict_cursor(pgsql):
    return pgsql['eats_place_subscriptions'].cursor(
        cursor_factory=extras.RealDictCursor,
    )


@pytest.fixture(name='mock_catalog_storage_common')
def _mock_catalog_common(mockserver):
    @mockserver.json_handler(utils.CATALOG_STORAGE_URL)
    def mock(request):
        return mockserver.make_response(
            json={
                'places': [
                    {
                        'id': 100,
                        'revision_id': 1,
                        'updated_at': '2020-04-28T12:00:00+03:00',
                        'name': 'Ulala',
                        'region': {
                            'id': 1,
                            'geobase_ids': [],
                            'time_zone': 'Europe/Moscow',
                        },
                        'country': {
                            'id': 123,
                            'code': 'ru',
                            'name': 'russia',
                            'currency': {'sign': 'R', 'code': 'RUB'},
                        },
                        'business': 'restaurant',
                    },
                    {
                        'id': 123,
                        'revision_id': 1,
                        'updated_at': '2020-04-28T12:00:00+03:00',
                        'name': 'Ulala',
                        'region': {
                            'id': 1,
                            'geobase_ids': [],
                            'time_zone': 'Europe/Moscow',
                        },
                        'country': {
                            'id': 123,
                            'code': 'ru',
                            'name': 'russia',
                            'currency': {'sign': 'R', 'code': 'RUB'},
                        },
                        'business': 'restaurant',
                    },
                    {
                        'id': 124,
                        'revision_id': 1,
                        'updated_at': '2020-04-28T12:00:00+03:00',
                        'name': 'BingBong',
                        'region': {
                            'id': 1,
                            'geobase_ids': [],
                            'time_zone': 'Asia/Yekaterinburg',
                        },
                        'country': {
                            'id': 123,
                            'code': 'ru',
                            'name': 'russia',
                            'currency': {'sign': 'R', 'code': 'RUB'},
                        },
                        'business': 'store',
                    },
                    {
                        'id': 125,
                        'revision_id': 1,
                        'updated_at': '2020-04-28T12:00:00+03:00',
                        'name': 'Opop',
                        'region': {
                            'id': 1,
                            'geobase_ids': [],
                            'time_zone': 'America/Sao_Paulo',
                        },
                        'country': {
                            'id': 123,
                            'code': 'ru',
                            'name': 'russia',
                            'currency': {'sign': 'R', 'code': 'RUB'},
                        },
                        'business': 'restaurant',
                    },
                    {
                        'id': 128,
                        'revision_id': 1,
                        'updated_at': '2020-04-28T12:00:00+03:00',
                        'name': 'Abcd',
                        'region': {
                            'id': 1,
                            'geobase_ids': [],
                            'time_zone': 'America/Sao_Paulo',
                        },
                        'country': {
                            'id': 123,
                            'code': 'ru',
                            'name': 'russia',
                            'currency': {'sign': 'R', 'code': 'RUB'},
                        },
                        'business': 'restaurant',
                    },
                ],
                'not_found_place_ids': [127],
            },
            status=200,
        )

    return mock
