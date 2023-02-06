# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
import datetime

from aiohttp import web
import pytest

import taxi_billing_limits.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['taxi_billing_limits.generated.service.pytest_plugins']


@pytest.fixture
def simple_secdist(simple_secdist):
    simple_secdist['settings_override'].update(
        STARTRACK_API_PROFILES={
            'budgetalert': {
                'oauth_token': 'secret',
                'org_id': 0,
                'url': 'http://startrek/',
            },
        },
    )
    return simple_secdist


@pytest.fixture(autouse=True)
def billing_accounts(mock_billing_accounts, load_json):
    now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()

    class _Mock:
        @mock_billing_accounts('/v1/accounts/search')
        @staticmethod
        async def accounts_search(request):
            accounts = load_json('accounts_search.json')
            return web.json_response(
                [
                    account
                    for account in accounts
                    if account['entity_external_id']
                    == request.json['entity_external_id']
                ],
            )

        @mock_billing_accounts('/v1/entities/create')
        @staticmethod
        async def entities_create(request):
            entity = request.json
            entity['created'] = now
            return web.json_response(entity)

        @mock_billing_accounts('/v1/accounts/create')
        @staticmethod
        async def accounts_create(request):
            account = request.json
            account.update(account_id=1, opened=now)
            return web.json_response(account)

    return _Mock()


@pytest.fixture(autouse=True)
def billing_docs(mock_billing_docs):

    actual_docs = []
    doc_id_seq = 1000

    @mock_billing_docs('/v1/docs/create')
    async def _docs_create(request):
        now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat(
            timespec='microseconds',
        )
        nonlocal doc_id_seq
        doc = {
            'data': request.json['data'],
            'event_at': request.json['event_at'],
            'external_event_ref': request.json['external_event_ref'],
            'external_obj_id': request.json['external_obj_id'],
            'kind': request.json['kind'],
            'service': request.json['service'],
            'status': request.json['status'],
            'journal_entries': request.json['journal_entries'],
            'doc_id': doc_id_seq,
            'created': now,
            'process_at': now,
            'tags': [],
        }
        nonlocal actual_docs
        actual_docs.append(doc)
        doc_id_seq += 1
        return web.json_response(doc)

    @mock_billing_docs('/v1/docs/finish_processing')
    async def _docs_finish(request):
        data = {'finished': True, 'status': request.json['status']}
        return web.json_response(data)

    return actual_docs
