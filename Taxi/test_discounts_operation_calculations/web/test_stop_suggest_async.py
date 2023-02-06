# pylint: disable=redefined-outer-name
import asyncio
import datetime
import http
from unittest import mock
import uuid

import pytest

from taxi.stq import async_worker_ng

import discounts_operation_calculations.repositories.multidraft_tasks_storage as storage_lib  # noqa: E501
from discounts_operation_calculations.stq import multidraft

MULTIDRAFTS_URL = 'test_url/multidraft/{multidraft_id}/?multi=true'
MULTIDRAFT_ID = 42
DATETIME_STR = '2020-10-01 15:54:32.123456'
CHECK_QUERY = """SELECT author, status, draft_url, draft_id, date_from, date_to
FROM discounts_operation_calculations.suggests ORDER BY id"""

CONFIGS = {
    'DISCOUNTS_OPERATION_CALCULATIONS_ALGORITHMS_CONFIGS': {
        'kt2': {
            'name': 'kt2',
            'metric_name': 'test_metric_name',
            'algorithm_type': 'katusha',
            'max_absolute_value': 300,
            'max_value': 0.5,
            'min_value': 0.05,
            'discount_duration': 5,
            'classes': ['econom', 'uberx'],
            'disable_by_surge': 1.2,
            'payment_types': ['card'],
        },
        'kt5': {
            'name': 'kt5',
            'metric_name': 'test_metric_name',
            'algorithm_type': 'katusha',
            'max_absolute_value': 300,
            'max_value': 0.5,
            'min_value': 0.05,
            'discount_duration': 5,
            'classes': ['econom', 'uberx'],
            'disable_by_surge': 1.2,
            'payment_types': ['card'],
        },
    },
    'DISCOUNTS_OPERATION_CALCULATIONS_COMMON_CONFIG': {
        'apply_for_airport_orders': True,
        'discount_class': 'katusha',
        'fallback_discount_class': 'katusha-flat',
        'discount_method': 'subvention-fix',
        'discount_target': 'tag_service',
        'point_a_is_enough': False,
        'round_digits': 2,
    },
    'DISCOUNTS_OPERATION_CALCULATIONS_CITY_TZ_MAPPING': {
        'Москва': ['moscow'],
        'Нижний Тагил': ['tagiiil'],
        'Аккра': ['accra'],
    },
    'MULTIDRAFTS_URL': MULTIDRAFTS_URL,
    'DISCOUNTS_OPERATION_CALCULATIONS_STARTRACK_CONFIG': {
        '__default__': {
            'queue': 'TESTQUEUE',
            'tags': ['test'],
            'assignee': 'test_user',
            'followers': [],
        },
        'kt2': {'followers': ['test_user']},
    },
    'DISCOUNTS_OPERATION_CALCULATIONS_CRON_CONTROL': {
        'discounts_operation_calculations': {
            'update_suggests_statuses': {'run_permission': True},
        },
    },
    'DISCOUNTS_OPERATION_CALCULATIONS_PUSHES_CONFIG': {
        'discount_duration': {'__default__': 14},
        'push_discounts_close_lag': 2880,
    },
}


@pytest.mark.now(DATETIME_STR)
@pytest.mark.pgsql(
    'discounts_operation_calculations',
    files=['fill_pg_suggests_to_publish.sql'],
)
@pytest.mark.config(**CONFIGS)
async def test_stop_suggest_async(
        pgsql,
        web_app_client,
        mock_other_services,
        mock_ride_discounts,
        mockserver,
        patch,
        stq3_context,
):
    # test happy path
    @patch('uuid.uuid4')
    def _uuid():
        return uuid.UUID(int=0, version=4)

    task_id = uuid.uuid4().hex

    response = await web_app_client.post(
        '/v2/suggests/stop',
        headers={'X-Yandex-Login': 'test_user2'},
        params={'city': 'Нижний Тагил'},
    )
    assert response.status == http.HTTPStatus.OK
    content = await response.json()
    assert content == {'task_id': task_id}

    storage = storage_lib.MultiDraftTasksStorage(stq3_context)
    task_data = dict(await storage.get_task(task_id))
    assert task_data['params'] == {
        'active_suggest_id': 3,
        'city': 'Нижний Тагил',
        'not_approved_suggests': [],
        'x_yandex_login': 'test_user2',
        'closed_at': None,
    }
    assert task_data['created_by'] == 'test_user2'

    # Check task is not completed yet
    status_check = await web_app_client.get(
        f'/v1/multidraft/tasks/{task_id}/status/',
    )
    assert status_check.status == http.HTTPStatus.OK
    content = await status_check.json()
    assert content['status'] == 'CREATED'

    result_check = await web_app_client.get(
        f'/v1/multidraft/tasks/{task_id}/result/',
    )
    assert result_check.status == http.HTTPStatus.CONFLICT
    content = await result_check.json()
    assert content['code'] == 'Conflict::TaskNotCompleted'

    # Run task
    await multidraft.task(
        stq3_context,
        async_worker_ng.TaskInfo(
            id=task_id, exec_tries=0, reschedule_counter=0, queue='',
        ),
    )

    # Check result
    status_check = await web_app_client.get(
        f'/v1/multidraft/tasks/{task_id}/status/',
    )
    assert status_check.status == http.HTTPStatus.OK
    content = await status_check.json()
    assert content['status'] == 'COMPLETED'

    response = await web_app_client.get(
        f'/v1/multidraft/tasks/{task_id}/result/',
    )
    assert response.status == http.HTTPStatus.OK
    content = await response.json()
    assert content == {
        'multidraft': MULTIDRAFTS_URL.format(
            multidraft_id=MULTIDRAFT_ID + 100,
        ),
    }

    # check suggests
    cursor = pgsql['discounts_operation_calculations'].cursor()
    cursor.execute(CHECK_QUERY)
    suggests = list(cursor)
    cursor.close()
    assert len(suggests) == 7
    assert suggests == [
        (
            'another_user',
            'SUCCEEDED',
            'ya.ru/99',
            99,
            datetime.datetime(2020, 9, 1, 1, 0),
            datetime.datetime(2021, 9, 1, 1, 0),
        ),
        (None, 'NOT_PUBLISHED', None, None, None, None),
        (
            'artem-mazanov',
            'SUCCEEDED',
            'https://ya.ru/103',
            103,
            datetime.datetime(2020, 9, 23, 12, 49, 22, 373412),
            datetime.datetime(2020, 10, 7, 12, 49, 22, 373412),
        ),
        (None, 'NOT_PUBLISHED', None, None, None, None),
        (
            'another_user',
            'NEED_APPROVAL',
            'ya.ru/99',
            999,
            datetime.datetime(2020, 9, 1, 1, 0),
            datetime.datetime(2021, 9, 1, 1, 0),
        ),
        (None, 'NOT_PUBLISHED', None, None, None, None),
        (
            'test_user2',
            'NEED_APPROVAL',
            'test_url/multidraft/142/?multi=true',
            142,
            datetime.datetime(2020, 10, 3, 15, 54, 32),
            None,
        ),
    ]

    # test case when no discounts to stop
    @patch('uuid.uuid4')
    def _uuid1():
        return uuid.UUID(int=1, version=4)

    task_id = uuid.uuid4().hex

    @mock_ride_discounts('/v1/admin/match-discounts/find-discounts')
    async def _find_discounts2(request):
        return {
            'discounts_data': {
                'hierarchy_name': 'full_money_discounts',
                'discounts_info': [],
            },
        }

    response = await web_app_client.post(
        '/v2/suggests/stop',
        headers={'X-Yandex-Login': 'test_user'},
        params={'city': 'Аккра'},
    )

    assert response.status == http.HTTPStatus.OK
    content = await response.json()
    assert content == {'task_id': task_id}

    # Run task
    await multidraft.task(
        stq3_context,
        async_worker_ng.TaskInfo(
            id=task_id, exec_tries=0, reschedule_counter=0, queue='',
        ),
    )

    # Check result
    response = await web_app_client.get(
        f'/v1/multidraft/tasks/{task_id}/result/',
    )
    assert response.status == http.HTTPStatus.BAD_REQUEST
    content = await response.json()
    assert content == {
        'code': 'BadRequest::NoDiscountsToStop',
        'message': 'There is no discounts to stop',
    }


@pytest.mark.now(DATETIME_STR)
@pytest.mark.pgsql(
    'discounts_operation_calculations',
    files=['fill_pg_suggests_to_publish.sql'],
)
@pytest.mark.config(**CONFIGS)
async def test_stop_suggest_async_cannot_attach_draft_once(
        pgsql,
        web_app_client,
        mock_other_services,
        mock_taxi_approvals,
        mockserver,
        patch,
        stq3_context,
):
    # Test that one 404 response from /drafts/attach does not affect result
    def response_gen():
        for i in range(2):
            _json_request = yield
            if i == 0:
                yield {
                    'status': '404',
                    'message': (
                        f'Draft with id={_json_request["multidraft_id"]} '
                        'was not found'
                    ),
                }
            else:
                yield {'id': 1, 'version': 1}

    json_responses = response_gen()

    @mockserver.aiohttp_json_handler('/taxi-approvals/drafts/attach/')
    async def _handler(request):
        json_request = await asyncio.create_task(request.json())
        next(json_responses)
        json_response = json_responses.send(json_request)

        return mockserver.make_response(
            status=int(json_response.get('status', '200')), json=json_response,
        )

    @patch('uuid.uuid4')
    def _uuid():
        return uuid.UUID(int=0, version=4)

    task_id = uuid.uuid4().hex

    response = await web_app_client.post(
        '/v2/suggests/stop',
        headers={'X-Yandex-Login': 'test_user2'},
        params={'city': 'Нижний Тагил'},
    )
    assert response.status == http.HTTPStatus.OK
    content = await response.json()
    assert content == {'task_id': task_id}

    # Run task
    await multidraft.task(
        stq3_context,
        async_worker_ng.TaskInfo(
            id=task_id, exec_tries=0, reschedule_counter=0, queue='',
        ),
    )

    # Check status
    status_check = await web_app_client.get(
        f'/v1/multidraft/tasks/{task_id}/status/',
    )
    assert status_check.status == http.HTTPStatus.OK
    content = await status_check.json()
    assert content['status'] == 'COMPLETED'

    # Check result
    response = await web_app_client.get(
        f'/v1/multidraft/tasks/{task_id}/result/',
    )
    assert response.status == http.HTTPStatus.OK
    content = await response.json()
    assert content == {'multidraft': 'test_url/multidraft/142/?multi=true'}


@pytest.mark.now(DATETIME_STR)
@pytest.mark.pgsql(
    'discounts_operation_calculations',
    files=['fill_pg_suggests_to_publish.sql'],
)
@pytest.mark.config(**CONFIGS)
async def test_stop_suggest_async_failed_draft(
        pgsql,
        web_app_client,
        mock_other_services,
        mock_taxi_approvals,
        mockserver,
        patch,
        stq3_context,
):
    # Test failed draft
    @mock_taxi_approvals('/drafts/1/')
    async def _get_draft_handler(request):
        return {'id': 1, 'version': 2, 'status': 'failed'}

    @patch('uuid.uuid4')
    def _uuid():
        return uuid.UUID(int=0, version=4)

    task_id = uuid.uuid4().hex

    response = await web_app_client.post(
        '/v2/suggests/stop',
        headers={'X-Yandex-Login': 'test_user2'},
        params={'city': 'Нижний Тагил'},
    )
    assert response.status == http.HTTPStatus.OK
    content = await response.json()
    assert content == {'task_id': task_id}

    # Run task
    await multidraft.task(
        stq3_context,
        async_worker_ng.TaskInfo(
            id=task_id, exec_tries=0, reschedule_counter=0, queue='',
        ),
    )

    # Check status
    status_check = await web_app_client.get(
        f'/v1/multidraft/tasks/{task_id}/status/',
    )
    assert status_check.status == http.HTTPStatus.OK
    content = await status_check.json()
    assert content['status'] == 'FAILED'

    # Check result
    response = await web_app_client.get(
        f'/v1/multidraft/tasks/{task_id}/result/',
    )
    assert response.status == http.HTTPStatus.BAD_REQUEST
    content = await response.json()
    assert content == {
        'code': 'RuntimeError::DraftStatus',
        'message': (
            'Draft 1 is in status failed that cannot be attached to '
            'multidraft. Check what is wrong with draft'
        ),
    }


@pytest.fixture(scope='function')
def mock_constraints(patch):
    async def check_not_approved_suggests(context, city):
        return [], 1

    yield patch(
        'discounts_operation_calculations.internals.constraints'
        '.check_not_approved_suggests',
    )(check_not_approved_suggests)


@pytest.fixture(scope='function')
def mock_task_storage(patch):
    task_storage_mock = mock.MagicMock()

    async def create_task(task_id, task_type, params):
        return None

    async def start_task(*_):
        return None

    task_storage_mock.create_task = patch(
        'discounts_operation_calculations.repositories.'
        'multidraft_tasks_storage.MultiDraftTasksStorage.create_task',
    )(create_task)

    task_storage_mock.start_task = patch(
        'discounts_operation_calculations.repositories.'
        'multidraft_tasks_storage.MultiDraftTasksStorage.start_task',
    )(start_task)

    yield task_storage_mock


@pytest.mark.parametrize(
    'city, closed_at_params, closed_at_task',
    [
        ('test_city', None, None),
        ('test_city', '2022-06-22 19:10:00', '2022-06-22T19:10:00'),
        ('test_city', '2022-06-22 19:10:30', '2022-06-22T19:10:00'),
        ('test_city', '2022-06-22 23:10:00+03:00', '2022-06-22T20:10:00'),
        ('test_city_push', '20220809T183142', '2022-08-09T18:31:00'),
    ],
)
@pytest.mark.now('2022-06-22 17:30:00')
@pytest.mark.usefixtures('mock_active_discounts')
async def test_stop_suggest_task_params(
        web_app_client,
        mock_constraints,
        mock_task_storage,
        city,
        closed_at_params,
        closed_at_task,
):
    params = {'city': city}
    if closed_at_params:
        params['closed_at'] = closed_at_params

    response = await web_app_client.post(
        '/v2/suggests/stop',
        headers={'X-Yandex-Login': 'test_user2'},
        params=params,
    )

    assert response.status == 200

    calls = mock_task_storage.create_task.calls
    assert len(calls) == 1
    assert calls[0]['params'] == {
        'city': city,
        'x_yandex_login': 'test_user2',
        'active_suggest_id': 1,
        'not_approved_suggests': [],
        'closed_at': closed_at_task,
    }


@pytest.mark.parametrize(
    'city, closed_at, close_lag',
    [
        ('test_city', '2022-06-22 16:45:30', 10),
        ('test_city', '2022-06-22 18:10:00+04:00', 10),
        ('test_city', '2022-06-22 17:39:30', 10),
        ('test_city', '2022-06-22 21:38:00+04:00', 10),
        ('test_city_push', '2022-06-22 18:15:30', 50),
        ('test_city_push', '2022-06-22 21:00:00+03:00', 50),
    ],
)
@pytest.mark.now('2022-06-22 17:30:00')
@pytest.mark.usefixtures('mock_active_discounts')
async def test_stop_suggest_invalid_close_time(
        web_app_client, mock_constraints, city, closed_at, close_lag,
):
    response = await web_app_client.post(
        '/v2/suggests/stop',
        headers={'X-Yandex-Login': 'test_user2'},
        params={'city': city, 'closed_at': closed_at},
    )

    assert response.status == 400
    content = await response.json()
    assert content == {
        'code': 'BadRequest::InvalidTime',
        'message': (
            'Discount end date '
            f'could not be earlier then now + '
            f'{datetime.timedelta(minutes=close_lag)}'
        ),
    }


@pytest.mark.parametrize('closed_at', ['random string', '784574958T58859'])
@pytest.mark.usefixtures('mock_active_discounts')
async def test_stop_suggest_invalid_time_format(web_app_client, closed_at):
    response = await web_app_client.post(
        '/v2/suggests/stop',
        headers={'X-Yandex-Login': 'test_user2'},
        params={'city': 'Нижний Тагил', 'closed_at': closed_at},
    )

    assert response.status == 400
    content = await response.json()
    assert content == {
        'code': 'REQUEST_VALIDATION_ERROR',
        'details': {
            'reason': (
                'Invalid value for closed_at: failed to parse '
                f'datetime from \'{closed_at}\''
            ),
        },
        'message': 'Some parameters are invalid',
    }
