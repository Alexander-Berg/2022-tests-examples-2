import datetime

import pytest


@pytest.mark.experiments3(
    name='lookup_contractor_usage',
    consumers=['lookup/acquire'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'predicate': {'type': 'true'},
            'value': {'enable': True},
            'title': 'Title',
            'enabled': True,
        },
    ],
    default_value={'enable': True},
)
@pytest.mark.parametrize(
    'res_delta',
    [
        pytest.param(
            20,
            marks=(pytest.mark.experiments3(filename='exp3_test_exact.json')),
        ),
        pytest.param(
            14,
            marks=(
                pytest.mark.experiments3(filename='exp3_test_nonexact.json')
            ),
        ),
        pytest.param(
            14,
            marks=(
                pytest.mark.experiments3(filename='exp3_test_all_lower.json')
            ),
        ),
        pytest.param(
            10,
            marks=(
                pytest.mark.experiments3(filename='exp3_test_all_higher.json')
            ),
        ),
        pytest.param(
            10,
            marks=(pytest.mark.experiments3(filename='exp3_test_empty.json')),
        ),
    ],
)
async def test_lookup_next_call_eta(
        mocked_time, stq_runner, testpoint, mockserver, res_delta,
):
    @testpoint('lookup_next_call_eta')
    def _lookup_next_call_eta(data):
        assert data['wave'] == 3
        assert data['delta'] == res_delta

    @mockserver.json_handler('/candidates/order-search')
    def _order_search(request):
        return mockserver.make_response(
            '{"candidates":[]}', 200, content_type='application/json',
        )

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/order-proc/set-fields',
    )
    def order_core_set(request):
        return mockserver.make_response('', 200)

    now_time = datetime.datetime(
        2021, 7, 14, 8, 57, 36, tzinfo=datetime.timezone.utc,
    )
    mocked_time.set(now_time)
    await stq_runner.lookup_contractor.call(
        task_id='order_id', args=[], kwargs={'order_id': 'id'},
    )

    assert order_core_set.has_calls
    assert _lookup_next_call_eta.times_called == 1
