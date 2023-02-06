import decimal
import itertools

import dateutil.parser
import pytest


async def test_get_status_works(
        load_json, put_order_in_queue, get_order_status,
):
    order = load_json('order_eats_1_v1_order.json')
    response = await put_order_in_queue(order)
    assert response.status_code == 200

    response = await get_order_status(
        {'kind': order['kind'], 'topic': order['topic']},
    )
    assert response.status_code == 200
    assert response.json()['status'] == 'new'
    assert not response.json()['processed']


@pytest.mark.parametrize(
    'status, processed',
    [('new', False), ('pending', False), ('failed', True), ('complete', True)],
)
async def test_processed_flag(
        load_json,
        put_order_in_queue,
        get_order_status,
        _create_order_in_status,
        status,
        processed,
):
    order = load_json('order_eats_1_v1_order.json')
    order_id = {'kind': order['kind'], 'topic': order['topic']}

    await _create_order_in_status(order, status)

    put_response = await put_order_in_queue(order)
    get_response = await get_order_status(order_id)
    for response in (put_response, get_response):
        assert response.status_code == 200
        assert response.json()['status'] == status
        assert response.json()['processed'] == processed


async def test_successful_flow(
        load_json, _create_services, call_process_order,
):
    dummy_services = _create_services()  # noqa: F841
    order = load_json('order_eats_1_v1_order.json')
    response = await call_process_order(order)

    assert response.status_code == 200
    assert response.json()['status'] == 'complete'


async def test_journal_entries_like_in_order(load_json, _process_orders):
    # like in order means:
    #   - in the same order
    #   - with the same amounts

    order = load_json('order_eats_1_v1_order.json')
    services = await _process_orders(order)

    docs_service = services.docs.service
    acc_service = services.accounts.service

    assert len(docs_service.find_docs()) == 1
    doc_info = docs_service.find_docs()[0]

    assert doc_info.doc['external_event_ref'] == '1'

    for order_entry, doc_entry in itertools.zip_longest(
            order['journal_entries'], doc_info.journal_entries,
    ):
        doc_acc = _account_from_accounts_service(
            acc_service, acc_service.find_by_id(doc_entry['account_id']),
        )
        assert order_entry['account'] == doc_acc

        order_sum = decimal.Decimal(order_entry['amount'])
        doc_sum = decimal.Decimal(doc_entry['amount'])
        assert order_sum == doc_sum

        order_event_at = dateutil.parser.parse(order['event_at'])
        doc_event_at = dateutil.parser.parse(doc_entry['event_at'])
        assert order_event_at == doc_event_at


async def test_new_revision_reverts_old(load_json, _process_orders):
    order_v1 = load_json('order_eats_1_v1_order.json')
    order_v2 = load_json('order_eats_1_v2_order.json')
    services = await _process_orders(order_v1, order_v2)

    docs_service = services.docs.service
    acc_service = services.accounts.service

    assert len(docs_service.find_docs()) == 3
    doc1 = docs_service.find_by_id(1)  # first order
    doc2 = docs_service.find_by_id(2)  # reverted first

    assert doc2.doc['external_event_ref'] == '1/reversal'

    for entry1, entry2 in itertools.zip_longest(
            doc1.journal_entries, doc2.journal_entries,
    ):
        acc1 = _account_from_accounts_service(acc_service, entry1)
        acc2 = _account_from_accounts_service(acc_service, entry2)
        assert acc1 == acc2

        # reverted sums
        sum1 = decimal.Decimal(entry1['amount'])
        sum2 = decimal.Decimal(entry2['amount'])
        assert sum2 == -1 * sum1

        # with event_at from second order
        reverted_event_at = dateutil.parser.parse(entry2['event_at'])
        order2_event_at = dateutil.parser.parse(order_v2['event_at'])
        assert reverted_event_at == order2_event_at


async def test_last_revision_applied(load_json, _process_orders):
    order_v1 = load_json('order_eats_1_v1_order.json')
    order_v2 = load_json('order_eats_1_v2_order.json')
    services = await _process_orders(order_v1, order_v2)

    docs_service = services.docs.service
    acc_service = services.accounts.service

    assert len(docs_service.find_docs()) == 3
    doc = docs_service.find_by_id(3)  # latest document

    assert doc.doc['external_event_ref'] == '2'

    for order_entry, doc_entry in itertools.zip_longest(
            order_v2['journal_entries'], doc.journal_entries,
    ):
        doc_account = _account_from_accounts_service(acc_service, doc_entry)
        assert order_entry['account'] == doc_account

        order_sum = decimal.Decimal(order_entry['amount'])
        doc_sum = decimal.Decimal(doc_entry['amount'])
        assert order_sum == doc_sum

        doc_event_at = dateutil.parser.parse(doc_entry['event_at'])
        order_v2_event_at = dateutil.parser.parse(order_v2['event_at'])
        assert order_v2_event_at == doc_event_at


async def test_idempotent_processing(load_json, _process_orders):
    order_v1 = load_json('order_eats_1_v1_order.json')
    order_v2 = load_json('order_eats_1_v2_order.json')
    services = await _process_orders(order_v1, order_v2)
    services = await _process_orders(order_v1, order_v2, services=services)

    assert len(services.docs.service.find_docs()) == 3


@pytest.fixture
def _process_orders(_create_services, call_process_order):
    async def _wrapper(*orders, services=None):
        if services is None:
            services = _create_services()
        for order in orders:
            response = await call_process_order(order)
            assert response.status_code == 200
            assert response.json()['status'] == 'complete'
        return services

    return _wrapper


@pytest.fixture
def _create_services(billing_docs_service, billing_accounts_service):
    def _wrapper():
        class Services:
            docs = billing_docs_service()
            accounts = billing_accounts_service()

        return Services()

    return _wrapper


_ORDER_TO_ACC_FIELDS_MAP = {
    'entity': 'entity_external_id',
    'agreement': 'agreement_id',
    'currency': 'currency',
    'sub_account': 'sub_account',
}


def _account_from_accounts_service(accounts_service, account_obj):
    if 'account_id' in account_obj:
        account = accounts_service.find_by_id(account_obj['account_id'])
    else:
        account = accounts_service.find_accounts(account_obj)
    order_acc = {}
    for order_field, account_field in _ORDER_TO_ACC_FIELDS_MAP.items():
        order_acc[order_field] = account[account_field]
    return order_acc


@pytest.fixture
def _create_order_in_status(put_order_in_queue, call_sync, mockserver):
    async def _wrapper(order, status):
        put_response = await put_order_in_queue(order)
        assert put_response.status_code == 200

        if status == 'new':
            return

        pending_count = await call_sync()
        assert pending_count == 1

        if status == 'pending':
            return

        order_status = {
            'kind': order['kind'],
            'topic': order['topic'].copy(),
            'status': status,
            'processed': True,
        }

        @mockserver.json_handler('/corp-billing-orders/internal/order/process')
        def handler(request):  # pylint: disable=W0612
            return order_status

        pending_count = await call_sync()
        assert pending_count == 0

    return _wrapper
