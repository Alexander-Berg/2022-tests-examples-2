import dataclasses
from typing import List

import pytest
from tests_processing import util


@dataclasses.dataclass
class Checkpoint:
    scope: str
    queue: str
    item_id: str
    condition_key: str
    pipeline: str
    stage: str


@pytest.fixture(name='ydb_checkpoints')
def get_ydb_checkpoints(ydb):
    def inner() -> List[Checkpoint]:
        cursor = ydb.execute(
            'SELECT scope, queue, item_id, condition_key, pipeline, stage'
            ' FROM processing_state',
        )
        return [
            Checkpoint(
                *list(
                    [item.decode() if item else None for item in row.values()],
                ),
            )
            for row in cursor[0].rows
        ]

    return inner


@pytest.mark.config(
    PROCESSING_ENABLE_CHECKPOINTS={'default': True, 'overrides': []},
)
@pytest.mark.parametrize(
    'fallback_policy',
    [
        pytest.param(
            'simple',
            marks=[
                pytest.mark.processing_queue_config(
                    'handler.yaml',
                    scope='testsuite',
                    queue='example',
                    first_handler_url=util.UrlMock('/first_stage'),
                    second_handler_url=util.UrlMock('/second_stage'),
                ),
            ],
        ),
        pytest.param(
            'deadline',
            marks=[
                pytest.mark.processing_queue_config(
                    'handler-deadline.yaml',
                    scope='testsuite',
                    queue='example',
                    first_handler_url=util.UrlMock('/first_stage'),
                    second_handler_url=util.UrlMock('/second_stage'),
                ),
            ],
        ),
    ],
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
async def test_checkpoint_reset(
        mockserver,
        processing,
        ydb_checkpoints,
        fallback_policy,
        use_ydb,
        use_fast_flow,
):
    item_id = '1'
    iteration_number = 0  # First iteration with fail on second stage

    @mockserver.json_handler('/first_stage')
    def mock_first(request):
        return {'result': iteration_number}

    @mockserver.json_handler('/second_stage')
    def mock_second(request):
        return mockserver.make_response(status=500)

    await processing.testsuite.example.send_event(
        item_id, payload={}, expect_fail=True,
    )

    assert mock_first.times_called == 1
    assert mock_second.times_called == 1
    assert not ydb_checkpoints()

    await processing.testsuite.example.send_event(
        item_id, payload={}, expect_fail=True,
    )

    assert mock_first.times_called == 2
    assert mock_second.times_called == 2
    assert not ydb_checkpoints()


@pytest.mark.config(
    PROCESSING_ENABLE_CHECKPOINTS={'default': True, 'overrides': []},
)
@pytest.mark.processing_queue_config(
    'handler-v1.yaml',
    scope='testsuite',
    queue='example',
    starter_api_url=util.UrlMock('/start-stage'),
    pool_api_url=util.UrlMock('/poll-stage'),
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
async def test_checkpoint_on_broken_state(
        mockserver, processing, ydb_checkpoints, use_ydb, use_fast_flow,
):
    @mockserver.json_handler('/start-stage')
    def mock_start(request):
        mock_start.job_id += 1
        return {'job-id': mock_start.job_id}

    mock_start.job_id = 0

    @mockserver.json_handler('/poll-stage')
    def mock_poll(request):
        return mockserver.make_response(status=500)

    item_id = '1'

    await processing.testsuite.example.send_event(
        item_id,
        payload={'action': 'init', 'draft-id': 'deafbeef'},
        expect_fail=False,
    )

    assert mock_start.times_called == 0
    assert mock_poll.times_called == 0

    await processing.testsuite.example.send_event(
        item_id, payload={'action': 'polling'}, expect_fail=True,
    )

    assert mock_start.times_called == 1
    assert mock_poll.times_called == 1

    # ensure has processing state
    current_checkpoints = ydb_checkpoints()
    assert current_checkpoints == [
        Checkpoint(
            'testsuite',
            'example',
            '1',
            'handle-polling',
            'polling-pipeline',
            'poll-long-task-stage',
        ),
    ]

    await processing.load_fs_queue_config(
        module='handler-v2.yaml',
        scope='testsuite',
        queue='example',
        starter_api_url=util.UrlMock('/start-stage'),
        pool_api_url=util.UrlMock('/poll-stage'),
    )

    # should fail since checkpoint is invalid and should cleanup
    await processing.testsuite.example.send_event(
        item_id, payload={'action': 'finish'}, expect_fail=True,
    )

    assert mock_start.times_called == 1
    assert mock_poll.times_called == 1
    assert not ydb_checkpoints()

    # run on new configuration from a clean state
    await processing.testsuite.example.call(item_id, expect_fail=False)
