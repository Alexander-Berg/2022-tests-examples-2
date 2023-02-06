# pylint: disable=redefined-outer-name,unused-variable
import aiohttp
import pytest

from taxi import config
from taxi.clients import personal


@pytest.fixture
async def mock_client(loop, db, unittest_settings):
    session = aiohttp.ClientSession(loop=loop)
    yield personal.PersonalApiClient(
        config=config.Config(db),
        settings=unittest_settings,
        session=session,
        tvm_client=None,
    )
    await session.close()


async def test_disabled(mock_client, monkeypatch):
    monkeypatch.setattr('taxi.config.Config.PERSONAL_SERVICE_ENABLED', False)

    try:
        await mock_client.store('phones', '+71111111111')
        assert False
    except personal.PersonalDisabledError:
        pass

    try:
        await mock_client.bulk_store('phones', ['+71111111111'])
        assert False
    except personal.PersonalDisabledError:
        pass


async def test_store_phone(mock_client, patch, monkeypatch, response_mock):
    async def mock_request(cls, path, payload, log_extra):
        assert path == 'v1/phones/store'
        assert payload == {'value': '+71111111111', 'validate': True}
        response = {'id': 'personal_id', 'value': '+71111111111'}
        return response_mock(json=response)

    monkeypatch.setattr(personal.PersonalApiClient, '_request', mock_request)

    personal_doc = await mock_client.store('phones', '+71111111111')
    assert personal_doc == {'id': 'personal_id', 'phone': '+71111111111'}


async def test_store_license(mock_client, patch, monkeypatch, response_mock):
    async def mock_request(cls, path, payload, log_extra):
        assert path == 'v1/driver_licenses/store'
        assert payload == {'value': '1111111111', 'validate': True}
        response = {'id': 'personal_id', 'value': '1111111111'}
        return response_mock(json=response)

    monkeypatch.setattr(personal.PersonalApiClient, '_request', mock_request)

    personal_doc = await mock_client.store('driver_licenses', '1111111111')
    assert personal_doc == {'id': 'personal_id', 'license': '1111111111'}


async def test_retrieve_phone(mock_client, patch, monkeypatch, response_mock):
    async def mock_request(cls, path, payload, log_extra):
        assert path == 'v1/phones/retrieve'
        assert payload == {'id': 'personal_id'}
        response = {'id': 'personal_id', 'value': '+71111111111'}
        return response_mock(json=response)

    monkeypatch.setattr(personal.PersonalApiClient, '_request', mock_request)

    personal_doc = await mock_client.retrieve('phones', 'personal_id')
    assert personal_doc == {'id': 'personal_id', 'phone': '+71111111111'}


async def test_find_phone(mock_client, patch, monkeypatch, response_mock):
    async def mock_request(cls, path, payload, log_extra):
        assert path == 'v1/phones/find'
        assert payload == {'value': '+71111111111'}
        response = {'id': 'personal_id', 'value': '+71111111111'}
        return response_mock(json=response)

    monkeypatch.setattr(personal.PersonalApiClient, '_request', mock_request)

    personal_doc = await mock_client.find('phones', '+71111111111')
    assert personal_doc == {'id': 'personal_id', 'phone': '+71111111111'}


async def test_bulk_store_phones(
        mock_client, patch, monkeypatch, response_mock,
):
    async def mock_request(cls, path, payload, log_extra):
        assert path == 'v1/phones/bulk_store'
        assert payload == {
            'items': [{'value': '+71111111111'}],
            'validate': True,
        }
        response = {'items': [{'id': 'personal_id', 'value': '+71111111111'}]}
        return response_mock(json=response)

    monkeypatch.setattr(personal.PersonalApiClient, '_request', mock_request)

    personal_docs = await mock_client.bulk_store('phones', ['+71111111111'])
    assert personal_docs == [{'id': 'personal_id', 'phone': '+71111111111'}]


async def test_bulk_retrieve_phones(
        mock_client, patch, monkeypatch, response_mock,
):
    async def mock_request(cls, path, payload, log_extra):
        assert path == 'v1/phones/bulk_retrieve'
        assert payload == {'items': [{'id': 'personal_id'}]}
        response = {'items': [{'id': 'personal_id', 'value': '+71111111111'}]}
        return response_mock(json=response)

    monkeypatch.setattr(personal.PersonalApiClient, '_request', mock_request)

    personal_docs = await mock_client.bulk_retrieve('phones', ['personal_id'])
    assert personal_docs == [{'id': 'personal_id', 'phone': '+71111111111'}]
