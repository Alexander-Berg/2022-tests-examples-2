# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import datetime

import pytest

from fleet_payouts_plugins import *  # noqa: F403 F401

from tests_fleet_payouts.utils import billing


@pytest.fixture
def mock_parks(mockserver, load_json):
    parks = load_json('parks.json')

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def handler(request):
        park_ids = set(request.json['query']['park']['ids'])
        return {'parks': [park for park in parks if park['id'] in park_ids]}

    return handler


@pytest.fixture
def mock_parks_by_clids(mockserver, load_json):
    parks = load_json('parks.json')

    @mockserver.json_handler('/fleet-parks/v1/parks/list-by-clids')
    def handler(request):
        clids = set(request.json['query']['park']['clids'])
        res_parks = []
        for park in parks:
            clid = park.get('provider_config', {}).get('clid')
            if clid and clid in clids:
                res_parks.append(park)
        return {'parks': res_parks}

    return handler


@pytest.fixture
def mock_users(mockserver, load_json):
    users = load_json('users.json')

    @mockserver.json_handler('/dispatcher-access-control/v1/parks/users/list')
    def handler(request):
        query = request.json['query']
        park_id = query['park']['id']
        (passport_uid,) = query['user']['passport_uid']

        response = {'users': [], 'offset': 0}
        for user in users:
            if (
                    user['park_id'] == park_id
                    and user['passport_uid'] == passport_uid
            ):
                response['users'].append(user)
                break

        return response

    return handler


@pytest.fixture(name='mock_doc_store')
def mock_doc_store_(load_json):
    return billing.DocStore(load_json('documents.json'))


@pytest.fixture
def mock_docs_select(mockserver, mock_doc_store):
    @mockserver.json_handler('/billing-reports/v1/docs/select')
    def v1_docs_select(request):
        request = request.json
        docs = mock_doc_store.select(
            request['external_obj_id'],
            request.get('external_event_ref'),
            request['begin_time'],
            request['end_time'],
        )
        if 'sort' in request:
            desc = request['sort'] == 'desc'
            docs.sort(key=lambda x: x['event_at'], reverse=desc)
        return {'docs': docs[: request['limit']], 'cursor': {}}

    return v1_docs_select


@pytest.fixture
def mock_docs_by_id(mockserver, mock_doc_store):
    @mockserver.json_handler('/billing-reports/v1/docs/by_id')
    def v1_docs_by_id(request):
        docs = []
        for doc_id in request.json['doc_ids']:
            doc = mock_doc_store.by_id(doc_id)
            if not doc:
                raise LookupError(f'Document with id \'{doc_id}\' not found.')
            docs.append(
                {
                    **doc,
                    'topic': doc['external_obj_id'],
                    'external_ref': doc['external_event_ref'],
                },
            )
        return {'docs': docs}

    return v1_docs_by_id


@pytest.fixture
def mock_process_async(mockserver, mock_doc_store):
    doc_id = 9000

    @mockserver.json_handler('/billing-orders/v2/process/async')
    def v2_process_async(request):
        orders = []

        nonlocal doc_id
        for order in request.json['orders']:
            now = datetime.datetime.now()
            mock_doc_store.add(
                {
                    'doc_id': doc_id,
                    'created': now,
                    'kind': order['kind'],
                    'external_obj_id': order['topic'],
                    'external_event_ref': order['external_ref'],
                    'event_at': order['event_at'],
                    'process_at': now,
                    'service': 'fleet-payouts',
                    'data': order['data'],
                    'status': 'new',
                    'tags': [],
                },
            )
            orders.append(
                {
                    'topic': order['topic'],
                    'external_ref': order['external_ref'],
                    'doc_id': doc_id,
                },
            )
            doc_id += 1

        return {'orders': orders}

    return v2_process_async
