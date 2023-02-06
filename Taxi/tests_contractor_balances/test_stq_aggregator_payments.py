import pytest


ENDPOINT = '/taximeter-xservice/utils/aggregator-payment/add'


@pytest.fixture(name='mock_aggregator_payment_add')
def _mock_aggregator_payment_add(mockserver):
    @mockserver.json_handler(ENDPOINT)
    def mock(request):
        return mockserver.make_response(status=200)

    return mock


@pytest.fixture(name='mock_aggregator_payment_add_500')
def _mock_aggregator_payment_add_500(mockserver):
    @mockserver.json_handler(ENDPOINT)
    def mock(request):
        return mockserver.make_response(status=500)

    return mock


@pytest.mark.parametrize(
    'case',
    [
        'ok',
        'correction',
        'group_not_found',
        'no_order',
        'order_no_commission_percent',
        'order_no_cost',
        'multiple_groups',
        'sum_amounts',
        'aggregation_disabled',
    ],
)
async def test_ok(stq_runner, load_json, mock_aggregator_payment_add, case):
    await stq_runner.contractor_balances_aggregator_payments.call(
        task_id='task-id', kwargs=load_json(f'{case}_event.json'),
    )

    expected_requests = load_json(f'{case}_requests.json')

    requests_count = len(expected_requests)
    assert mock_aggregator_payment_add.times_called == requests_count

    for _ in range(requests_count):
        request = mock_aggregator_payment_add.next_call()['request']
        expected_requests.remove(request.json)

    assert not expected_requests


async def test_fail(stq_runner, load_json, mock_aggregator_payment_add_500):
    await stq_runner.contractor_balances_aggregator_payments.call(
        task_id='task-id',
        kwargs=load_json(f'ok_event.json'),
        expect_fail=True,
    )

    assert mock_aggregator_payment_add_500.has_calls
