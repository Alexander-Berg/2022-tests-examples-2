import pytest


@pytest.mark.processing_queue_config(
    'handler.yaml', scope='logging', queue='example',
)
@pytest.mark.parametrize(
    'use_ydb',
    [
        pytest.param(False),
        pytest.param(
            True, marks=[pytest.mark.experiments3(filename='use_ydb.json')],
        ),
    ],
)
@pytest.mark.parametrize(
    'use_fast_flow',
    [
        pytest.param(False),
        pytest.param(
            True, marks=[pytest.mark.experiments3(filename='ydb_flow.json')],
        ),
    ],
)
async def test_basic(
        processing, testpoint, mockserver, use_ydb, use_fast_flow,
):
    @testpoint('agl-user-log')
    def user_log(request):
        pass

    queue = processing.logging.example
    await queue.handle_single_event(
        '1233456', payload={}, prev_state={}, curr_state={},
    )

    assert user_log.next_call()['request'] == {
        'text': 'Hello, world!',
        'tags': {},
        'extra': {},
        'level': 'info',
    }
