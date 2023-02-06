# pylint: disable=redefined-outer-name
import asyncio
import copy
import datetime
import http
import uuid

import pytest

from taxi.stq import async_worker_ng

import discounts_operation_calculations.repositories.multidraft_tasks_storage as storage_lib  # noqa: E501
from discounts_operation_calculations.stq import multidraft

MULTIDRAFTS_URL = 'test_url/multidraft/{multidraft_id}/?multi=true'
MULTIDRAFT_ID = 42
NEW_SUGGEST_ID = 2
DATETIME_STR = '2020-10-01 15:54:32.123456'
CHECK_QUERY = """SELECT author, status, draft_url, draft_id, date_from, date_to
FROM discounts_operation_calculations.suggests ORDER BY id"""


SQL_FILES = [
    'fill_pg_suggests_to_publish.sql',
    'fill_pg_segment_stats_hist.sql',
    'fill_pg_multidraft_tasks.sql',
]


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
        'Санкт-Петербург': ['peter'],
        'Казань': ['kazan'],
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
@pytest.mark.pgsql('discounts_operation_calculations', files=SQL_FILES)
@pytest.mark.config(**CONFIGS)
async def test_publish_suggest_async(
        pgsql,
        web_app_client,
        mock_other_services,
        mock_taxi_approvals,
        patch,
        stq3_context,
):
    # happy path
    @patch('uuid.uuid4')
    def _uuid():
        return uuid.UUID(int=0, version=4)

    task_id = uuid.uuid4().hex

    custom_date_to = datetime.datetime(2020, 10, 17, 15, 54, 32).isoformat()

    response = await web_app_client.post(
        '/v2/suggests/publish',
        headers={'X-Yandex-Login': 'test_user'},
        params={'suggest_id': 4, 'date_to': custom_date_to},
    )
    assert response.status == http.HTTPStatus.OK
    content = await response.json()
    assert content == {'task_id': task_id}

    storage = storage_lib.MultiDraftTasksStorage(stq3_context)
    task_data = dict(await storage.get_task(task_id))
    assert task_data['params'] == {
        'date_to': custom_date_to,
        'active_suggest_id': 3,
        'not_approved_suggests': [],
        'suggest_id': 4,
        'x_yandex_login': 'test_user',
    }
    assert task_data['created_by'] == 'test_user'

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
    assert content == {'multidraft': 'test_url/multidraft/142/?multi=true'}

    # check suggests
    cursor = pgsql['discounts_operation_calculations'].cursor()
    cursor.execute(CHECK_QUERY)
    suggests = list(cursor)
    assert len(suggests) == 6
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
        (
            'test_user',
            'NEED_APPROVAL',
            'test_url/multidraft/142/?multi=true',
            142,
            datetime.datetime(2020, 10, 3, 15, 54, 32),
            datetime.datetime(2020, 10, 17, 15, 54, 32),
        ),
        (
            'another_user',
            'NEED_APPROVAL',
            'ya.ru/99',
            999,
            datetime.datetime(2020, 9, 1, 1, 0),
            datetime.datetime(2021, 9, 1, 1, 0),
        ),
        (None, 'NOT_PUBLISHED', None, None, None, None),
    ]

    # test not approved suggests
    @mock_taxi_approvals('/drafts/list/')
    async def _drafts_list_handler(request):
        return [{'id': 11, 'version': 3, 'tickets': ['TESTQUEUE-11']}]

    @mock_taxi_approvals('/drafts/bulk_reject/')
    async def _drafts_bulk_reject_handler(request):
        drafts_to_reject = [{'id': 11, 'version': 3}]
        assert request.json == {
            'comment': (
                'reject old not approved drafts '
                'by discounts-operation-calculations'
            ),
            'drafts': drafts_to_reject,
        }
        return {'rejected': [{'id': 11, 'version': 3}], 'not_rejected': []}

    @patch(
        'discounts_operation_calculations.internals.startrek.'
        'StartrackClient.close_tickets',
    )
    async def _close_tickets(*args, **kwargs):
        pass

    @patch('uuid.uuid4')
    def _uuid1():
        return uuid.UUID(int=1, version=4)

    task_id = uuid.uuid4().hex

    response = await web_app_client.post(
        '/v2/suggests/publish',
        headers={'X-Yandex-Login': 'test_user'},
        params={'suggest_id': 6},
    )
    assert response.status == http.HTTPStatus.BAD_REQUEST
    content = await response.json()
    assert content == {
        'code': 'BadRequest::NotApprovedDrafts',
        'message': 'Cannot create rules while exists not approved drafts',
    }

    good_response = await web_app_client.post(
        '/v2/suggests/publish',
        headers={'X-Yandex-Login': 'another_user'},
        params={'suggest_id': 6, 'reject_not_approved_drafts': 'true'},
    )
    assert good_response.status == http.HTTPStatus.OK
    content = await good_response.json()
    assert content == {'task_id': task_id}

    storage = storage_lib.MultiDraftTasksStorage(stq3_context)
    task_data = dict(await storage.get_task(task_id))
    assert task_data['params'] == {
        'active_suggest_id': None,
        'not_approved_suggests': [[5, 999]],
        'suggest_id': 6,
        'x_yandex_login': 'another_user',
    }
    assert task_data['created_by'] == 'another_user'

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
    assert response.status == http.HTTPStatus.OK
    content = await response.json()
    assert content == {'multidraft': 'test_url/multidraft/242/?multi=true'}

    cursor.execute(CHECK_QUERY)
    suggests = list(cursor)
    assert len(suggests) == 6
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
        (
            'test_user',
            'NEED_APPROVAL',
            'test_url/multidraft/142/?multi=true',
            142,
            datetime.datetime(2020, 10, 3, 15, 54, 32),
            datetime.datetime(2020, 10, 17, 15, 54, 32),
        ),
        (
            'another_user',
            'REJECTED',
            'ya.ru/99',
            999,
            datetime.datetime(2020, 9, 1, 1, 0),
            datetime.datetime(2021, 9, 1, 1, 0),
        ),
        (
            'another_user',
            'NEED_APPROVAL',
            'test_url/multidraft/242/?multi=true',
            242,
            datetime.datetime(2020, 10, 1, 16, 54, 32),
            datetime.datetime(2020, 10, 6, 16, 54, 32),
        ),
    ]

    cursor.close()


def remove_tagiil_from_config():
    result = copy.deepcopy(CONFIGS)
    new_config = {'Москва': ['moscow'], 'Санкт-Петербург': ['peter']}
    result['DISCOUNTS_OPERATION_CALCULATIONS_CITY_TZ_MAPPING'] = new_config
    return result


@pytest.mark.now(DATETIME_STR)
@pytest.mark.pgsql('discounts_operation_calculations', files=SQL_FILES)
@pytest.mark.config(**remove_tagiil_from_config())
async def test_publish_suggest_async_missing_tz(
        pgsql, web_app_client, mock_other_services, patch, stq3_context,
):
    # test missing tagiiil in configs
    @patch('uuid.uuid4')
    def _uuid():
        return uuid.UUID(int=0, version=4)

    task_id = uuid.uuid4().hex
    response = await web_app_client.post(
        '/v2/suggests/publish',
        headers={'X-Yandex-Login': 'test_user'},
        params={'suggest_id': 4},
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
    status_check = await web_app_client.get(
        f'/v1/multidraft/tasks/{task_id}/status/',
    )
    assert status_check.status == http.HTTPStatus.OK
    content = await status_check.json()
    assert content['status'] == 'FAILED'

    response = await web_app_client.get(
        f'/v1/multidraft/tasks/{task_id}/result/',
    )
    assert response.status == http.HTTPStatus.BAD_REQUEST
    content = await response.json()
    assert content == {
        'code': 'RuntimeError::UnknownError',
        'message': 'type: <class \'KeyError\'>, msg: \'Нижний Тагил\'',
    }


@pytest.mark.now(DATETIME_STR)
@pytest.mark.pgsql('discounts_operation_calculations', files=SQL_FILES)
@pytest.mark.config(**CONFIGS)
async def test_publish_suggest_async_bad_date_to(
        pgsql, web_app_client, patch, stq3_context,
):
    @patch('uuid.uuid4')
    def _uuid():
        return uuid.UUID(int=0, version=4)

    task_id = uuid.uuid4().hex

    custom_date_to = datetime.datetime(2020, 11, 17, 15, 54, 32).isoformat()

    response = await web_app_client.post(
        '/v2/suggests/publish',
        headers={'X-Yandex-Login': 'test_user'},
        params={'suggest_id': 4, 'date_to': custom_date_to},
    )
    assert response.status == http.HTTPStatus.OK
    content = await response.json()
    assert content == {'task_id': task_id}

    storage = storage_lib.MultiDraftTasksStorage(stq3_context)
    task_data = dict(await storage.get_task(task_id))
    assert task_data['params'] == {
        'date_to': custom_date_to,
        'active_suggest_id': 3,
        'not_approved_suggests': [],
        'suggest_id': 4,
        'x_yandex_login': 'test_user',
    }
    assert task_data['created_by'] == 'test_user'

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

    result_check = await web_app_client.get(
        f'/v1/multidraft/tasks/{task_id}/result/',
    )
    assert result_check.status == http.HTTPStatus.BAD_REQUEST
    content = await result_check.json()
    assert content['code'] == 'BadRequest::DiscountDuration'


@pytest.mark.now(DATETIME_STR)
@pytest.mark.pgsql('discounts_operation_calculations', files=SQL_FILES)
@pytest.mark.config(**CONFIGS)
async def test_publish_suggest_cannot_attach_draft(
        pgsql,
        web_app_client,
        mock_other_services,
        mock_taxi_approvals,
        mockserver,
        patch,
        stq3_context,
):
    @mockserver.aiohttp_json_handler('/taxi-approvals/drafts/attach/')
    async def _handler(request):
        json_request = await asyncio.create_task(request.json())
        json_response = {
            'status': '404',
            'message': (
                f'Draft with id={json_request["multidraft_id"]} '
                'was not found'
            ),
        }
        return mockserver.make_response(status=404, json=json_response)

    @mock_taxi_approvals('/drafts/bulk_reject/')
    async def _drafts_bulk_reject_handler(request):
        drafts_to_reject = [{'id': 1, 'version': 2}]
        assert request.json == {
            'comment': 'Cannot attach draft to multidraft',
            'drafts': drafts_to_reject,
        }
        return {'rejected': [{'id': 1, 'version': 3}], 'not_rejected': []}

    @patch(
        'discounts_operation_calculations.internals.startrek.'
        'StartrackClient.close_tickets',
    )
    async def _close_tickets(*args, **kwargs):
        pass

    # test that all retries from /drafts/attach failed
    @patch('uuid.uuid4')
    def _uuid():
        return uuid.UUID(int=0, version=4)

    task_id = uuid.uuid4().hex

    custom_date_to = datetime.datetime(2020, 10, 17, 15, 54, 32).isoformat()

    response = await web_app_client.post(
        '/v2/suggests/publish',
        headers={'X-Yandex-Login': 'test_user'},
        params={'suggest_id': 4, 'date_to': custom_date_to},
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
    status_check = await web_app_client.get(
        f'/v1/multidraft/tasks/{task_id}/status/',
    )
    assert status_check.status == http.HTTPStatus.OK
    content = await status_check.json()
    assert content['status'] == 'FAILED'

    response = await web_app_client.get(
        f'/v1/multidraft/tasks/{task_id}/result/',
    )
    assert response.status == http.HTTPStatus.BAD_REQUEST
    content = await response.json()
    assert content == {
        'code': 'RuntimeError::DraftAttach',
        'message': 'Cannot attach draft 1 to multidraft 142',
    }


@pytest.mark.now(DATETIME_STR)
@pytest.mark.pgsql('discounts_operation_calculations', files=SQL_FILES)
@pytest.mark.config(**CONFIGS)
async def test_publish_suggest_cannot_attach_draft_once(
        pgsql,
        web_app_client,
        mock_other_services,
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

    custom_date_to = datetime.datetime(2020, 10, 17, 15, 54, 32).isoformat()

    response = await web_app_client.post(
        '/v2/suggests/publish',
        headers={'X-Yandex-Login': 'test_user'},
        params={'suggest_id': 4, 'date_to': custom_date_to},
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
    assert content == {'multidraft': 'test_url/multidraft/142/?multi=true'}


@pytest.mark.now(DATETIME_STR)
@pytest.mark.pgsql('discounts_operation_calculations', files=SQL_FILES)
@pytest.mark.config(**CONFIGS)
async def test_publish_suggest_failed_draft(
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

    custom_date_to = datetime.datetime(2020, 10, 17, 15, 54, 32).isoformat()

    response = await web_app_client.post(
        '/v2/suggests/publish',
        headers={'X-Yandex-Login': 'test_user'},
        params={'suggest_id': 4, 'date_to': custom_date_to},
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
    status_check = await web_app_client.get(
        f'/v1/multidraft/tasks/{task_id}/status/',
    )
    assert status_check.status == http.HTTPStatus.OK
    content = await status_check.json()
    assert content['status'] == 'FAILED'

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


def change_config(share):
    configs = copy.deepcopy(CONFIGS)

    algo_configs = configs[
        'DISCOUNTS_OPERATION_CALCULATIONS_ALGORITHMS_CONFIGS'
    ]
    exps_config = {'partitions': []}
    for algo_name, algo_shares in share.items():
        algo_configs[algo_name]['control_share'] = algo_shares['control_share']
        if algo_shares.get('partition'):
            exps_config['partitions'].append(
                {
                    'algo_name': algo_name,
                    'partition': algo_shares['partition'],
                },
            )
    configs.update(
        **{
            'DISCOUNTS_OPERATION_CALCULATIONS_ALGORITHMS_CONFIGS': (
                algo_configs
            ),
            'DISCOUNTS_OPERATION_CALCULATIONS_EXPERIMENTS_CONFIG': exps_config,
        },
    )

    return configs


@pytest.mark.parametrize('expected_create_draft_request_path', [''])
@pytest.mark.now(DATETIME_STR)
@pytest.mark.pgsql(
    'discounts_operation_calculations',
    files=[
        'fill_pg_suggests_to_publish_detailed.sql',
        'fill_pg_calc_segment_stats_tasks.sql',
        'fill_pg_segment_stats_all.sql',
    ],
)
@pytest.mark.parametrize(
    'share',
    [
        pytest.param(
            share,
            marks=[pytest.mark.config(**change_config(share))],
            id=str(i),
        )
        for i, share in enumerate(
            [
                {
                    'kt2': {'control_share': 0},
                    'kt5': {'control_share': 0},
                },  # without control
                {
                    'kt2': {'control_share': 20},
                    'kt5': {'control_share': 20},
                },  # without partitions
                {
                    'kt2': {'control_share': 20, 'partition': [0, 50]},
                    'kt5': {'control_share': 20, 'partition': [50, 100]},
                },  # with partitions
                {
                    'kt2': {'control_share': 10, 'partition': [0, 25]},
                    'kt5': {'control_share': 30, 'partition': [25, 100]},
                },  # change shares
            ],
        )
    ],
)
async def test_publish_suggest_log_hist_to_pg(
        share,
        expected_create_draft_request_path,
        calc_segment_stats_mock,
        pgsql,
        web_app_client,
        mock_other_services,
        patch,
        stq3_context,
        load_json,
        taxi_config,
):
    # fix segment stats to make it usable
    cursor = pgsql['discounts_operation_calculations'].cursor()
    fix_kt2_query = """UPDATE discounts_operation_calculations.segment_stats_all
    SET suggest_id = 7, city = 'Казань', algorithm_id = 'kt2'
    WHERE algorithm_id = 'kt'"""
    fix_kt5_query = """UPDATE discounts_operation_calculations.segment_stats_all
    SET suggest_id = 7, city = 'Казань', algorithm_id = 'kt5'
    WHERE algorithm_id = 'kt1'"""
    cursor.execute(fix_kt2_query)
    cursor.execute(fix_kt5_query)

    @patch('uuid.uuid4')
    def _uuid():
        return uuid.UUID(int=42, version=4)

    task_id = uuid.uuid4().hex
    suggest_id = 7

    custom_date_to = datetime.datetime(2020, 10, 12, 15, 54, 32).isoformat()

    response = await web_app_client.post(
        '/v2/suggests/publish',
        headers={'X-Yandex-Login': 'test_user'},
        params={'suggest_id': suggest_id, 'date_to': custom_date_to},
    )

    assert response.status == http.HTTPStatus.OK
    content = await response.json()
    assert content == {'task_id': task_id}

    storage = storage_lib.MultiDraftTasksStorage(stq3_context)
    task_data = dict(await storage.get_task(task_id))
    assert task_data['params'] == {
        'date_to': custom_date_to,
        'active_suggest_id': None,
        'not_approved_suggests': [],
        'suggest_id': suggest_id,
        'x_yandex_login': 'test_user',
    }

    # Run multidraft task
    await multidraft.task(
        stq3_context,
        async_worker_ng.TaskInfo(
            id=task_id, exec_tries=0, reschedule_counter=0, queue='',
        ),
    )

    # check logger_data
    get_segment_stats_hist_query = """SELECT
            algorithm_id,
            segment,
            price_from,
            discount,
            trips,
            extra_trips,
            gmv,
            new_gmv,
            metric,
            weekly_budget,
            is_uploaded_to_yt,
            actions
         FROM discounts_operation_calculations.segment_stats_all_hist
         where discount > 0
         order by segment, discount, price_from, algorithm_id"""
    cursor.execute(get_segment_stats_hist_query)
    segment_stats_hist = list(cursor)
    cursor.close()

    kt2_share = share['kt2']
    kt2_control_share = kt2_share.get('control_share', 20) / 100
    kt2_exp_parts = kt2_share.get('partition')
    kt2_exp_share = (
        100 if not kt2_exp_parts else kt2_exp_parts[1] - kt2_exp_parts[0]
    ) / 100
    kt2_coef = (1 - kt2_control_share) * kt2_exp_share

    kt5_share = share['kt5']
    kt5_control_share = kt5_share.get('control_share', 20) / 100
    kt5_exp_parts = kt5_share.get('partition')
    kt5_exp_share = (
        100 if not kt5_exp_parts else kt5_exp_parts[1] - kt5_exp_parts[0]
    ) / 100
    kt5_coef = (1 - kt5_control_share) * kt5_exp_share

    assert len(segment_stats_hist) == 101
    assert segment_stats_hist[88:91] == [
        (
            'kt2',
            'random',
            50,
            pytest.approx(12.0),
            pytest.approx(1099.0),
            pytest.approx(105.504 * kt2_coef),
            pytest.approx(71995.0),
            pytest.approx(78904.168),
            pytest.approx(105.504 * kt2_coef),
            pytest.approx(946556.016 * kt2_coef),
            False,
            [],
        ),
        (
            'kt5',
            'random',
            75,
            pytest.approx(12.0),
            pytest.approx(1099.5),
            pytest.approx(105.528 * kt5_coef),
            pytest.approx(143990.0),
            pytest.approx(208496.344),
            pytest.approx(105.528 * kt5_coef),
            pytest.approx(16377.44472 * kt5_coef),
            False,
            ['push'],
        ),
        (
            'kt2',
            'random',
            100,
            pytest.approx(12.0),
            pytest.approx(3257.5),
            pytest.approx(312.72 * kt2_coef),
            pytest.approx(445496.5),
            pytest.approx(476572.852),
            pytest.approx(312.72 * kt2_coef),
            pytest.approx(4257460.224 * kt2_coef),
            False,
            [],
        ),
    ]
