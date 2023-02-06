import pytest


@pytest.mark.parametrize(
    'queue_name, failed, testpoint_name',
    [
        ('sample_queue_done', False, 'queue-sample-done'),
        ('sample_queue_failed', True, 'queue-sample-failed'),
    ],
)
async def test_it_works(
        stq_runner, testpoint, queue_name, failed, testpoint_name,
):
    @testpoint(testpoint_name)
    def _mock_performer(request):
        return {}

    await getattr(stq_runner, queue_name).call(
        task_id='sample_task',
        args=[1, 2, 3],
        kwargs={'a': {'b': 'c'}, 'd': 1},
        expect_fail=failed,
        reschedule_counter=0,
        exec_tries=0,
    )

    assert (await _mock_performer.wait_call())['request'] == {
        'id': 'sample_task',
        'args': [1, 2, 3],
        'kwargs': {'a': {'b': 'c'}, 'd': 1},
    }
