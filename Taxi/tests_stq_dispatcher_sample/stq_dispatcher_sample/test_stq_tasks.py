import pytest


@pytest.mark.parametrize(
    'queue_name, failed, testpoint_name',
    [
        ('sample_queue_done', False, 'queue-sample-done'),
        ('sample_queue_failed', True, 'queue-sample-failed'),
    ],
)
async def test_sample_tasks(
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


@pytest.mark.parametrize(
    'args, kwargs, expect_fail, expected_request',
    [
        (
            ('sample_task_id', 2),
            {'static': 'one'},
            False,
            {
                'arg_with_default': False,
                'double_param': 2.0,
                'task_id': 'sample_task_id',
                'static': 'one',
            },
        ),
        (
            ('sample_task_id', 2),
            {'optional_arg': 3},
            False,
            {
                'arg_with_default': False,
                'double_param': 2.0,
                'optional_arg': 3,
                'task_id': 'sample_task_id',
            },
        ),
        (('sample_task_id',), {'optional_arg': 3}, True, None),
        (
            ('sample_task_id', 2),
            {
                'optional_arg': 3,
                'arg_with_default': True,
                'vector_arg': [
                    '2020-02-02T12:00:00.000Z',
                    '2020-02-02T14:00:00.000Z',
                ],
            },
            False,
            {
                'arg_with_default': True,
                'double_param': 2.0,
                'optional_arg': 3,
                'task_id': 'sample_task_id',
                'vector_arg': [
                    '2020-02-02T12:00:00+00:00',
                    '2020-02-02T14:00:00+00:00',
                ],
            },
        ),
        (
            ('sample_task_id', 2),
            {'log_extra': {'extra_key': 'extra_value'}},
            False,
            {
                'arg_with_default': False,
                'double_param': 2.0,
                'task_id': 'sample_task_id',
            },
        ),
        (
            ('sample_task_id', 2),
            {'log_extra': {'extra_key': 200}},
            False,
            {
                'arg_with_default': False,
                'double_param': 2.0,
                'task_id': 'sample_task_id',
            },
        ),
        ((), {}, True, None),
        (('a', 2, 3, True, [1, 2, 3], 'unexpected_arg'), {}, True, None),
        (('sample_task_id', 2), {'double_param': 3}, True, None),
        (('sample_task_id',), {'double_param': 'non-double'}, True, None),
        (
            ('sample_task_id', 2),
            {
                'log_extra': {'extra_key': 200},
                'custom_user_type_arg': 200,
                'complex_obj_arg': {
                    'first': 'a',
                    'second': 2,
                    'third': [True],
                },
                'datetime_field': {'$date': '2018-12-27T16:38:00.123Z'},
                'object_id_field': {'$oid': '1dcf5804abae14bb0d31d02d'},
            },
            False,
            {
                'arg_with_default': False,
                'double_param': 2.0,
                'task_id': 'sample_task_id',
                'complex_obj_arg': {
                    'first': 'a',
                    'second': 2,
                    'third': [True],
                },
                'custom_user_type_arg': 200,
                'datetime_field': '2018-12-27T16:38:00.123+00:00',
                'object_id_field': {'$oid': '1dcf5804abae14bb0d31d02d'},
            },
        ),
    ],
)
async def test_sample_task_with_args(
        stq_runner, testpoint, args, kwargs, expect_fail, expected_request,
):
    @testpoint('queue-sample-with-args')
    def _mock_performer(request):
        return {}

    await stq_runner.sample_queue_with_args.call(
        task_id='sample_task',
        args=args,
        kwargs=kwargs,
        expect_fail=expect_fail,
    )
    if not expect_fail:
        assert (await _mock_performer.wait_call())[
            'request'
        ] == expected_request
