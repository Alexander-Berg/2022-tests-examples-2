import datetime

import pytest


@pytest.mark.now('2019-08-26T14:00:00Z')
async def test_stq_queue(taxi_userver_sample, stq):
    response = await taxi_userver_sample.post(
        'stq-agent-queue',
        json={
            'task_id': 'stq-agent-queue',
            'double_param': 1,
            'static': 'one',
            'optional_arg': 10,
            'arg_with_default': True,
            'vector_arg': ['2019-08-26T14:00:00Z', '2019-08-26T14:10:00Z'],
            'custom_user_type_arg': 100000,
            'complex_obj_arg': {'first': 'a', 'second': 2, 'third': [True]},
        },
    )
    assert response.status_code == 200
    assert response.json() == {}

    assert stq.sample_queue_with_args.times_called == 1

    sample_queue_with_args_call = stq.sample_queue_with_args.next_call()
    link = sample_queue_with_args_call['kwargs']['log_extra']['_link']
    assert link
    assert isinstance(link, str)

    assert sample_queue_with_args_call == {
        'queue': 'sample_queue_with_args',
        'id': 'stq-agent-queue',
        'eta': datetime.datetime(2019, 8, 26, 14, 0),
        'args': [],
        'kwargs': {
            'task_id': 'stq-agent-queue',
            'double_param': 1,
            'static': 'one',
            'optional_arg': 10,
            'arg_with_default': True,
            'vector_arg': [
                '2019-08-26T14:00:00+00:00',
                '2019-08-26T14:10:00+00:00',
            ],
            'custom_user_type_arg': 100000,
            'complex_obj_arg': {'first': 'a', 'second': 2, 'third': [True]},
            'log_extra': {'_link': link},
            'object_id_field': {'$oid': '1dcf5804abae14bb0d31d02d'},
        },
    }


@pytest.mark.now('2019-08-26T14:11:22.123456Z')
async def test_stq_queue_link(taxi_userver_sample, stq):
    response = await taxi_userver_sample.post(
        'stq-agent-queue',
        json={
            'task_id': 'stq-agent-queue',
            'link': 'stq-agent-link',
            'double_param': 2.7,
        },
    )
    assert response.status_code == 200
    assert response.json() == {}

    assert stq.sample_queue_with_args.times_called == 1
    assert stq.sample_queue_with_args.next_call() == {
        'queue': 'sample_queue_with_args',
        'id': 'stq-agent-queue',
        'eta': datetime.datetime(2019, 8, 26, 14, 11, 22, 123456),
        'args': [],
        'kwargs': {
            'task_id': 'stq-agent-queue',
            'double_param': 2.7,
            'log_extra': {'_link': 'stq-agent-link'},
            'object_id_field': {'$oid': '1dcf5804abae14bb0d31d02d'},
        },
    }
