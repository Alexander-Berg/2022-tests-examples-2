import typing

import pytest

from taxi.stq import async_worker_ng

from taxi_takeout.db_access import deletions as deletions_db
from taxi_takeout.generated.stq3 import stq_context
from taxi_takeout.stq import delete_user_data

TAKEOUT_SERVICES_CONFIG = [
    {
        'name': 'eda_service',
        'data_category': 'eda',
        'host': 'http://eda_service.taxi.dev.yandex.net',
        'endpoints': {'delete': {'path': '/eda_service/delete'}},
    },
    {
        'name': 'taxi_service_0',
        'data_category': 'taxi',
        'host': 'http://taxi_service_0.taxi.dev.yandex.net',
        'endpoints': {},
    },
    {
        'name': 'taxi_service_1',
        'data_category': 'taxi',
        'host': 'http://taxi_service_1.taxi.dev.yandex.net',
        'endpoints': {
            'delete': {
                'path': '/taxi_service_1/delete',
                'retries': 1,
                'timeout': 100,
            },
        },
    },
    {
        'name': 'taxi_service_2',
        'data_category': 'taxi',
        'host': 'http://taxi_service_2.taxi.dev.yandex.net',
        'endpoints': {'delete': {'path': '/taxi_service_2/delete'}},
    },
    {
        'name': 'taxi_service_stq_1',
        'data_category': 'taxi',
        'host': 'http://taxi_service_stq_1.taxi.dev.yandex.net',
        'endpoints': {
            'delete': {
                'path': '/stq-agent/delete',
                'tvm_name': 'stq-agent',
                'host': 'http://stq-agent.taxi.dev.yandex.net',
                'body': {
                    'queue_name': 'order_takeout_anonymize_order',
                    'task_id': '{{ takeout_request.takeout_service_id }}',
                    'args': [],
                    'kwargs': {
                        'request_id': '{{ takeout_user.request_id }}',
                        'yandex_uids': '{{ takeout_user.yandex_uids }}',
                        'date_delete_before': (
                            '{{ takeout_user.date_request_at }}'
                        ),
                    },
                    'eta': '{{ takeout_user.date_request_at }}',
                },
            },
        },
    },
]

REQUEST_DATA = {
    'request_id': 'request_id',
    'yandex_uids': [
        {'uid': 'phonish_uid', 'is_portal': False},
        {'uid': 'yandex_uid', 'is_portal': True},
    ],
    'date_request_at': '2010-01-01T12:00:35.172+03:00',
    'phone_ids': ['phone_id1', 'phone_id2'],
    'takeout_task_id': 'takeout_task_id_1',
}
STQ_REQUEST_ARGS = {
    'queue_name': 'order_takeout_anonymize_order',
    'task_id': 'taxi:taxi_service_stq_1:takeout_task_id_1',
    'args': [],
    'kwargs': {
        'request_id': 'request_id',
        'yandex_uids': [
            {'is_portal': False, 'uid': 'phonish_uid'},
            {'is_portal': True, 'uid': 'yandex_uid'},
        ],
        'date_delete_before': '2010-01-01T12:00:35.172+03:00',
    },
    'eta': '2010-01-01T12:00:35.172+03:00',
}


@pytest.fixture(name='mock_delete')
def mock_delete_fixture(patch_aiohttp_session, response_mock, load_json):
    def _mock_delete(service_name, request_data=None, response_status=200):
        host_url = f'http://{service_name}.taxi.dev.yandex.net'

        @patch_aiohttp_session(host_url, 'POST')
        def _mock_api(method, url, *args, **kwargs):
            _mock_api.times_called += 1
            assert url == host_url + f'/{service_name}/delete'
            if request_data:
                assert kwargs['json'] == request_data
            return response_mock(status=response_status)

        _mock_api.times_called = 0
        return _mock_api

    return _mock_delete


async def _check_db(
        stq3_context: stq_context.Context,
        status: typing.Optional[deletions_db.DeletionStatus],
):
    deletions = await stq3_context.deletions_db.get_deletions(
        'yandex_uid', {'taxi', 'eda'},
    )
    if status is None:
        return
    assert len(deletions) == 1
    deletion = deletions[0]
    assert deletion.data_category == 'taxi'
    assert deletion.yandex_uid == 'yandex_uid'
    assert deletion.status == status
    if status == deletions_db.DeletionStatus.DELETED:
        assert deletion.deleted_at is not None
    else:
        assert deletion.deleted_at is None


@pytest.mark.config(TAKEOUT_SERVICES_V2=TAKEOUT_SERVICES_CONFIG)
@pytest.mark.pgsql('taxi_takeout', files=['pg_taxi_takeout.sql'])
async def test_delete(stq3_context: stq_context.Context, mock_delete):
    mock_eda = mock_delete('eda_service')
    mock_taxi_0 = mock_delete('taxi_service_0')
    mock_taxi_1 = mock_delete('taxi_service_1', REQUEST_DATA)
    mock_taxi_2 = mock_delete('taxi_service_2', REQUEST_DATA)
    mock_stq_agent = mock_delete('stq-agent', STQ_REQUEST_ARGS)

    task_info = async_worker_ng.TaskInfo(
        id='id',
        exec_tries=0,
        reschedule_counter=0,
        queue='takeout_delete_user_data',
    )

    await delete_user_data.task(
        context=stq3_context,
        task_info=task_info,
        data_category='taxi',
        yandex_uid='yandex_uid',
        **REQUEST_DATA,
    )

    await _check_db(stq3_context, deletions_db.DeletionStatus.DELETED)

    assert mock_eda.times_called == 0
    assert mock_taxi_0.times_called == 0
    assert mock_taxi_1.times_called == 1
    assert mock_taxi_2.times_called == 1
    assert mock_stq_agent.times_called == 1


@pytest.mark.config(TAKEOUT_SERVICES_V2=TAKEOUT_SERVICES_CONFIG)
async def test_delete_rescheduled(
        stq3_context: stq_context.Context, mock_delete, patch,
):

    mock_taxi_1 = mock_delete('taxi_service_1', REQUEST_DATA, 500)
    mock_taxi_2 = mock_delete('taxi_service_2', REQUEST_DATA)
    mock_delete('eda_service')
    mock_stq_agent = mock_delete('stq-agent', STQ_REQUEST_ARGS)

    task_info = async_worker_ng.TaskInfo(
        id='id',
        exec_tries=0,
        reschedule_counter=0,
        queue='takeout_delete_user_data',
    )

    is_rescheduled = False

    @patch(
        'taxi_takeout.generated.service.stq_client.plugin.'
        'QueueClient.call_later',
    )
    async def _call_later(*args, **kwargs):
        assert kwargs['kwargs'] == dict(
            data_category='taxi', yandex_uid='yandex_uid', **REQUEST_DATA,
        )
        nonlocal is_rescheduled
        is_rescheduled = True

    await delete_user_data.task(
        context=stq3_context,
        task_info=task_info,
        data_category='taxi',
        yandex_uid='yandex_uid',
        **REQUEST_DATA,
    )

    assert is_rescheduled

    await _check_db(stq3_context, status=None)

    assert mock_taxi_1.times_called == 2
    assert mock_taxi_2.times_called == 1
    assert mock_stq_agent.times_called == 1


@pytest.mark.config(TAKEOUT_SERVICES_V2=TAKEOUT_SERVICES_CONFIG)
async def test_delete_retry_failed(
        stq3_context: stq_context.Context, mock_delete, patch,
):
    mock_taxi_1 = mock_delete('taxi_service_1', REQUEST_DATA)
    mock_taxi_2 = mock_delete('taxi_service_2', REQUEST_DATA)
    mock_delete('eda_service')

    task_info = async_worker_ng.TaskInfo(
        id='id',
        exec_tries=3,
        reschedule_counter=0,
        queue='takeout_delete_user_data',
    )

    await delete_user_data.task(
        context=stq3_context,
        task_info=task_info,
        data_category='taxi',
        yandex_uid='yandex_uid',
        **REQUEST_DATA,
    )

    await _check_db(stq3_context, deletions_db.DeletionStatus.DELETE_FAILED)

    assert mock_taxi_1.times_called == 0
    assert mock_taxi_2.times_called == 0


@pytest.mark.config(TAKEOUT_SERVICES_V2=TAKEOUT_SERVICES_CONFIG)
async def test_delete_reschedule_failed(
        stq3_context: stq_context.Context, mock_delete, patch,
):
    mock_taxi_1 = mock_delete('taxi_service_1', REQUEST_DATA, 500)
    mock_taxi_2 = mock_delete('taxi_service_2', REQUEST_DATA)
    mock_stq_agent = mock_delete('stq-agent', STQ_REQUEST_ARGS)
    mock_delete('eda_service')

    task_info = async_worker_ng.TaskInfo(
        id='id',
        exec_tries=0,
        reschedule_counter=3,
        queue='takeout_delete_user_data',
    )

    is_rescheduled = False

    @patch(
        'taxi_takeout.generated.service.stq_client.plugin.'
        'QueueClient.call_later',
    )
    async def _call_later(*args, **kwargs):
        nonlocal is_rescheduled
        is_rescheduled = True

    await delete_user_data.task(
        context=stq3_context,
        task_info=task_info,
        data_category='taxi',
        yandex_uid='yandex_uid',
        **REQUEST_DATA,
    )

    assert not is_rescheduled

    await _check_db(stq3_context, deletions_db.DeletionStatus.DELETE_FAILED)

    assert mock_taxi_1.times_called == 2
    assert mock_taxi_2.times_called == 1
    assert mock_stq_agent.times_called == 1
