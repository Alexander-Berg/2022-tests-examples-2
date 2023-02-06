# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
import datetime

import aiohttp
import pytest

from taxi.clients import driver_profiles
from taxi.clients import user_api
from taxi.stq import async_worker_ng

from taxi_receipt_fetching.clients import billing_replication
from taxi_receipt_fetching.common import http_client
import taxi_receipt_fetching.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301
from client_order_archive import (  # noqa:I100,I201
    components as client_order_archive,
)

pytest_plugins = ['taxi_receipt_fetching.generated.service.pytest_plugins']


@pytest.fixture
def fetch_receipt_task_info():
    return async_worker_ng.TaskInfo(
        id='order_id', queue='', exec_tries=0, reschedule_counter=0,
    )


@pytest.fixture
def async_monkeypatch(monkeypatch, mock):
    def _wrap(obj, name, value):
        @mock
        async def new_method(*args, **kwargs):
            return value

        monkeypatch.setattr(obj, name, new_method)
        return new_method

    return _wrap


@pytest.fixture
def client_session_request_mock(async_monkeypatch, response_mock):
    def _wrap(resp_data, status=200):
        return async_monkeypatch(
            aiohttp.ClientSession,
            'request',
            response_mock(json=resp_data, status=status),
        )

    return _wrap


@pytest.fixture
def http_client_make_request_mock(async_monkeypatch, response_mock):
    def _wrap(resp_data, status=200):
        return async_monkeypatch(
            http_client.HttpClient,
            'make_request',
            response_mock(json=resp_data, status=status),
        )

    return _wrap


@pytest.fixture
def archive_mock(stq3_context, async_monkeypatch):
    def _wrap(data, method):
        return async_monkeypatch(stq3_context.client_archive_api, method, data)

    return _wrap


@pytest.fixture
def user_api_mock(async_monkeypatch):
    def _wrap(resp_data):
        return async_monkeypatch(user_api.UserApiClient, '_request', resp_data)

    return _wrap


@pytest.fixture
def personal_api_mock(stq3_context, async_monkeypatch):
    def _wrap(resp_data):
        class StubResponse:
            async def json(self):
                return resp_data

        return async_monkeypatch(
            stq3_context.client_personal, '_request', StubResponse(),
        )

    return _wrap


@pytest.fixture
def create_receipt(web_context):
    async def _wrap(order_id, receipt_url):
        query = web_context.postgres_queries['create_receipt.sql']
        created = datetime.datetime.utcnow()
        args = (created, order_id, receipt_url)
        postgres = web_context.postgresql.receipt_fetching[0]
        await postgres.execute(query, *args)

    return _wrap


@pytest.fixture
def simple_secdist(simple_secdist):
    simple_secdist['settings_override'].update(
        {
            'MOLDOVA_AUTH_USERNAME': 'keke',
            'MOLDOVA_AUTH_PASSWORD': 'hehe',
            'BUHTA_API_TOKEN': 'secret',
        },
    )
    return simple_secdist


@pytest.fixture
def br_person_mock(async_monkeypatch):
    def _wrap(resp_data):
        return async_monkeypatch(
            billing_replication.BillingReplicationClient,
            'get_park_info',
            resp_data,
        )

    return _wrap


@pytest.fixture
def order_proc_retrieve_mock(async_monkeypatch):
    def _wrap(resp_data):
        return async_monkeypatch(
            client_order_archive.OrderArchiveClient,
            'order_proc_retrieve',
            resp_data,
        )

    return _wrap


@pytest.fixture
def driver_profiles_mock(async_monkeypatch, response_mock):
    def _wrap(driver_profile):
        return async_monkeypatch(
            driver_profiles.DriverProfilesApiClient,
            'retrieve',
            {'profiles': [driver_profile]},
        )

    return _wrap


@pytest.fixture
def br_contracts_mock(monkeypatch, mock):
    def _wrap(general_contracts, spendable_contracts):
        @mock
        async def new_method(*args, **kwargs):
            return (
                general_contracts
                if kwargs['contract_type'] == 'GENERAL'
                else spendable_contracts
            )

        monkeypatch.setattr(
            billing_replication.BillingReplicationClient,
            'get_contracts',
            new_method,
        )
        return new_method

    return _wrap
