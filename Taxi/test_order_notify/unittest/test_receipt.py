import typing

import pytest

from order_notify.generated.stq3 import stq_context
from order_notify.repositories import receipt
from order_notify.repositories.order_info import OrderData


DEFAULT_PERFORMER = {'taxi_alias': {'id': '234'}}


@pytest.fixture(name='mock_server')
def mock_server_fixture(mockserver):
    @mockserver.json_handler('/taxi-receipt-fetching/receipts')
    def handle(request):
        order_id = request.json['order_ids'][0]
        assert order_id in ('3', '4')
        if order_id == '3':
            return {
                'receipts': [{'order_id': '3', 'receipt_url': 'fetched_url'}],
            }
        return {'receipts': []}

    return handle


@pytest.fixture(name='mock_functions')
def mock_receipt_functions(patch):
    class Counter:
        def __init__(self):
            self.times_called = 0

        def call(self):
            self.times_called += 1

    class Counters:
        def __init__(self):
            self.get_trust_receipt_url = Counter()

    counters = Counters()

    @patch('order_notify.repositories.receipt._get_trust_receipt_url')
    def _get_trust_receipt_url(
            context: stq_context.Context, order_data: OrderData,
    ) -> typing.Optional[str]:
        counters.get_trust_receipt_url.call()
        order_id = order_data.order_proc['_id']
        assert order_id in ('1', '2')
        if order_id == '1':
            return 'trust_url'
        return None

    return counters


@pytest.mark.parametrize(
    'zone, _id, times_called, expected_url',
    [
        pytest.param('moscow', '1', [0, 1], 'trust_url', id='trust'),
        pytest.param('moscow', '2', [0, 1], None, id='trust_but_None'),
        pytest.param('riga', '3', [1, 0], 'fetched_url', id='fetch'),
        pytest.param('riga', '4', [1, 0], None, id='fetch_but_None'),
        pytest.param('paris', '5', [0, 0], None, id='None'),
    ],
)
@pytest.mark.config(
    ORDERS_HISTORY_SHOW_FETCHED_RECEIPT_IN_COUNTRIES=['lva'],
    ORDERS_HISTORY_SHOW_TRUST_RECEIPT_IN_COUNTRIES=['rus'],
)
async def test_get_receipt_url(
        stq3_context: stq_context.Context,
        mock_get_cashed_zones,
        mock_server,
        mock_functions,
        zone,
        _id,
        times_called,
        expected_url,
):
    url = await receipt.get_receipt_url(
        context=stq3_context,
        order_data=OrderData(
            brand='', country='', order={'nz': zone}, order_proc={'_id': _id},
        ),
    )
    assert url == expected_url
    assert [
        mock_server.times_called,
        mock_functions.get_trust_receipt_url.times_called,
    ] == times_called


@pytest.mark.parametrize(
    'order, expected_url',
    [
        pytest.param({'performer': {}}, None, id='no_taxi_alias'),
        pytest.param(
            {'performer': {'taxi_alias': {}}}, None, id='no_alias_id',
        ),
        pytest.param(
            {'performer': DEFAULT_PERFORMER, 'payment_tech': {'type': 'cash'}},
            None,
            id='no_in_trust_receipt_payment_methods',
        ),
        pytest.param(
            {'performer': DEFAULT_PERFORMER, 'payment_tech': {'type': 'card'}},
            None,
            id='no_service_type',
        ),
        pytest.param(
            {
                'performer': DEFAULT_PERFORMER,
                'payment_tech': {'type': 'card'},
                'invoice_request': {'billing_service': 'card'},
            },
            'vaf/124-234/',
            id='correct',
        ),
    ],
)
@pytest.mark.config(
    ORDERS_HISTORY_SHOW_TRUST_RECEIPT_FOR_PAYMENT_METHODS=['card'],
    BILLING_RECEIPT_URL='vaf/{}-{}/',
)
def test_get_trust_receipt_url(
        stq3_context: stq_context.Context, order, expected_url,
):
    url = receipt._get_trust_receipt_url(  # pylint: disable=W0212
        context=stq3_context,
        order_data=OrderData(
            brand='', country='', order=order, order_proc={'order': order},
        ),
    )
    assert url == expected_url
