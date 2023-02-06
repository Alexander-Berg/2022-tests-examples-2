import typing as tp

import aiohttp
import pytest

from taxi.clickhouse import clickhouse


@pytest.fixture
def mock_clickhouse_host(patch_aiohttp_session, response_mock):
    def patch_request(clickhouse_response, request_url):
        @patch_aiohttp_session(request_url)
        def clickhouse_request(*args, **kwargs):
            return clickhouse_response(*args, **kwargs)

        return clickhouse_request

    return patch_request


@pytest.fixture
def clickhouse_connection():
    default_session = aiohttp.client.ClientSession()

    def _connection(
            session: tp.Optional[aiohttp.ClientSession] = None,
            db: tp.Optional[str] = None,
            user: tp.Optional[str] = None,
            password: tp.Optional[str] = None,
    ):
        settings = clickhouse.settings.ConnectionSettings(
            db=db or 'test_db',
            user=user or 'user',
            password=password or 'password',
        )
        return clickhouse.connection.Connection(
            session=session or default_session, connection_settings=settings,
        )

    return _connection


@pytest.fixture
def policy():
    default_host_list = [
        'super_awesome_db.db.yandex.net',
        'less_awesome_db.db.yandex.net',
    ]

    def _policy(
            conn: clickhouse.connection.Connection,
            host_list: tp.Optional[tp.List[str]] = None,
    ):
        policy_settings = clickhouse.settings.PolicySettings(
            host_list=host_list or default_host_list,
            host_status_update_delay_sec=2,
        )
        return clickhouse.policy.Policy(
            conn=conn, policy_settings=policy_settings,
        )

    return _policy
