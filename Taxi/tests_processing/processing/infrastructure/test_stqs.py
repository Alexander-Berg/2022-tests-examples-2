import datetime

from dateutil import parser as date_parser
import pytest


STQ_NAME = 'testsuite_example'


@pytest.mark.processing_queue_config(
    'handler-enabled.yaml', scope='testsuite', queue='example',
)
@pytest.mark.parametrize('stqs_enabled', [True, False])
async def test_stqs_enabled(stq, processing, stqs_enabled):
    item_id = '1'

    with stq.flushing():
        await processing.testsuite.example.handle_single_event(
            item_id, payload={'stqs_enabled': stqs_enabled},
        )
        if stqs_enabled:
            assert stq[STQ_NAME].times_called == 1
            params = stq[STQ_NAME].next_call()
            assert params.get('id') == 'some-task'
            assert params.get('args') == ['some-args']
        else:
            assert stq[STQ_NAME].times_called == 0


TIME = '2021-01-01T00:00:00+03'
DEFAULT_FORMAT = '%Y-%m-%dT%H:%M:%S%z'
CUSTOM_FORMAT = '%H:%M:%S %Y-%m-%d'


@pytest.mark.processing_queue_config(
    'handler-eta.yaml', scope='testsuite', queue='example',
)
@pytest.mark.now(TIME)
async def test_stqs_eta(stq, processing):
    item_id = '1'

    def shift_time(timestamp, dsec):
        return date_parser.parse(TIME) + datetime.timedelta(seconds=dsec)

    with stq.flushing():
        await processing.testsuite.example.handle_single_event(
            item_id,
            payload={
                'stqs_default_timestring': shift_time(TIME, 1).strftime(
                    DEFAULT_FORMAT,
                ),
                'stqs_custom_timestring': shift_time(TIME, 2).strftime(
                    CUSTOM_FORMAT,
                ),
                'stqs_custom_format': CUSTOM_FORMAT,
            },
        )
        assert stq[STQ_NAME].times_called == 2
        for _ in range(2):
            params = stq[STQ_NAME].next_call()
            if params['id'] == 'some-default-task':
                assert params['eta'].replace(
                    tzinfo=datetime.timezone.utc,
                ) == shift_time(TIME, 1)
            elif params['id'] == 'some-custom-task':
                # fixing lost timezone
                offset = datetime.timedelta(hours=3)
                assert params['eta'].replace(
                    tzinfo=datetime.timezone(offset),
                ) == shift_time(TIME, 2)
            else:
                assert 0
