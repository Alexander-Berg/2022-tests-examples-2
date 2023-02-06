import dateutil.parser
import pytest

from tests_dispatch_buffer.test_toggle_assignment import data

ORDERS_SORTING_CRITERIA_NAME = 'orders-sorting-criteria'


@pytest.mark.config(DISPATCH_BUFFER_ENABLED=False)
@pytest.mark.pgsql('driver_dispatcher', files=['dispatch_meta_insert.sql'])
@pytest.mark.parametrize(
    'key,sorting_order,missing_key_priority,expected_answer',
    [
        ('draw_cnt', 'descending', 'lowest', [3, 2, 1, 4]),
        ('last_dispatch_run', 'descending', 'lowest', [1, 2, 3, 4]),
        ('last_dispatch_run', 'descending', 'highest', [4, 1, 2, 3]),
        ('last_dispatch_run', 'ascending', 'lowest', [3, 2, 1, 4]),
    ],
)
async def test_orders_sorting_criteria(
        taxi_dispatch_buffer,
        pgsql,
        testpoint,
        mockserver,
        mocked_time,
        load_json,
        experiments3,
        key,
        sorting_order,
        missing_key_priority,
        expected_answer,
):
    now = dateutil.parser.parse('2020-03-16T17:10:27+00:00')
    mocked_time.set(now)

    @mockserver.json_handler('/candidates/order-search')
    def _mock_order_search(request):
        assert request.headers.get('Content-Type') == 'application/json'
        return {'candidates': [data.CANDIDATE]}

    @mockserver.json_handler('/driver_scoring/v2/score-candidates-bulk')
    def _mock_driver_scoring_bulk(request):
        return {'responses': [data.SCORING_RESPONSE]}

    @testpoint(ORDERS_SORTING_CRITERIA_NAME)
    def get_sorted_orders(answer):
        return answer

    exp3_json = load_json('base_experiment3.json')
    exp3_json['configs'][0]['clauses'][0]['value'].update(
        {
            'key': key,
            'sorting_order': sorting_order,
            'missing_key_priority': missing_key_priority,
        },
    )
    experiments3.add_experiments_json(exp3_json)
    await taxi_dispatch_buffer.invalidate_caches()

    await taxi_dispatch_buffer.run_task('distlock/buffer_assignment')

    assert (await get_sorted_orders.wait_call())['answer'] == expected_answer
