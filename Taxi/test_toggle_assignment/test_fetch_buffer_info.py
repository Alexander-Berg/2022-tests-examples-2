import dateutil.parser
import pytest

from tests_dispatch_buffer.test_toggle_assignment import data


EXPECTED_BUFFER_INFOS = [
    {
        'draw_cnt': 2,
        'first_dispatch_run': '2020-03-16T17:10:31+00:00',
        'last_dispatch_run': '2020-03-16T17:10:34+00:00',
    },
    {
        'draw_cnt': 3,
        'first_dispatch_run': '2020-03-16T17:10:31+00:00',
        'last_dispatch_run': '2020-03-16T17:10:32+00:00',
    },
    {'draw_cnt': 0, 'first_dispatch_run': '2020-03-16T17:10:31+00:00'},
    {
        'draw_cnt': 1,
        'first_dispatch_run': '2020-03-16T17:10:31+00:00',
        'last_dispatch_run': '2020-03-16T17:10:35+00:00',
    },
]


@pytest.mark.config(DISPATCH_BUFFER_ENABLED=False)
@pytest.mark.pgsql('driver_dispatcher', files=['dispatch_meta_insert.sql'])
async def test_simple(
        taxi_dispatch_buffer, mockserver, mocked_time, testpoint,
):
    now = dateutil.parser.parse('2020-03-16T17:10:27+00:00')
    mocked_time.set(now)

    @mockserver.json_handler('/candidates/order-search')
    def _mock_order_search(request):
        assert request.headers.get('Content-Type') == 'application/json'
        return {'candidates': [data.CANDIDATE]}

    @mockserver.json_handler('/driver_scoring/v2/score-candidates-bulk')
    def _mock_driver_scoring_bulk(request):
        buffer_infos = [
            entry['search'].get('buffer_info', None)
            for entry in request.json['requests']
        ]
        assert buffer_infos == EXPECTED_BUFFER_INFOS
        return {'responses': [data.SCORING_RESPONSE]}

    await taxi_dispatch_buffer.run_task('distlock/buffer_assignment')
