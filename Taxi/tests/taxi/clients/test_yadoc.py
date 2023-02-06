# pylint: disable=redefined-outer-name

import aiohttp
import pytest

from taxi.clients.helpers import base_client

# https://wiki.yandex-team.ru/servis-yadoc/instrukcija-po-ispolzovaniju-jadok-dlja-servisov/
YADOC_GET_DOCUMENTS_RESPONSE_BODY = {
    'date_from': '2020-07-30',
    'date_to': '2020-07-31',
    'party_id': 7899,
    'contract_id': 7800,
    'documents': [
        {
            'doc_type': 'INV',
            'doc_date': '2020-07-30',
            'doc_id:': 7895,
            'doc_number': 'B79999',
            'is_reversed': False,
        },
        {
            'doc_type': 'ACT',
            'doc_date': '2020-07-30',
            'doc_id:': 7898,
            'doc_number': '7999559',
            'is_reversed': False,
        },
    ],
}


@pytest.fixture
async def client(loop, db, simple_secdist):
    from taxi import config
    from taxi.clients import yadoc
    from taxi.clients import tvm

    session = aiohttp.ClientSession(loop=loop)
    config_ = config.Config(db)
    yield yadoc.YaDocClient(
        session=session,
        tvm_client=tvm.TVMClient(
            service_name='developers',
            secdist=simple_secdist,
            config=config_,
            session=session,
        ),
    )
    await session.close()


async def test_get_documents(patch, client):
    @patch('taxi.clients.helpers.base_client.BaseClient.request')
    async def _request(
            method, url, log_extra=None, return_binary=False, **kwargs,
    ):
        return base_client.Response(
            body=YADOC_GET_DOCUMENTS_RESPONSE_BODY, headers={},
        )

    await client.get_documents(
        contract_id='7800', date_from='2020-07-30', date_to='2020-07-31',
    )
    assert _request.calls == [
        {
            'kwargs': {
                'json': {
                    'contract_id': '7800',
                    'date_from': '2020-07-30',
                    'date_to': '2020-07-31',
                },
            },
            'log_extra': None,
            'return_binary': False,
            'method': 'POST',
            'url': '$mockserver/yadoc/documents',
        },
    ]


async def test_download_document(patch, client):
    @patch('taxi.clients.helpers.base_client.BaseClient.request')
    async def _request(
            method, url, log_extra=None, return_binary=False, **kwargs,
    ):
        return base_client.Response(body={}, headers={})

    doc_id = 7898
    await client.download_document(doc_id=doc_id)
    assert _request.calls == [
        {
            'kwargs': {},
            'log_extra': None,
            'return_binary': True,
            'method': 'GET',
            'url': f'$mockserver/yadoc/documents/{doc_id}/download',
        },
    ]
