import typing as tp

import pandas
import pytest

from taxi.stq import async_worker_ng
from taxi.util import dates

from mayak_inspector.common import constants
from mayak_inspector.common import utils
from mayak_inspector.common.utils import stq as stq_utils
from mayak_inspector.storage.ydb import extractors
from mayak_inspector.stq import batching_jobs
from test_mayak_inspector.stq import data as test_data


@pytest.mark.parametrize(
    'kwargs',
    [
        pytest.param(
            {
                'extra': {
                    'mayak_import_uuid': 1,
                    'bucket_id': 0,
                    'type_id': 0,
                },
                'job_type': constants.JobTypes.read_metrics.value,
            },
            id='default',
        ),
    ],
)
async def test_trigger_read_metrics(stq3_context, stq, kwargs, patch):
    repo_module = 'mayak_inspector.storage.ydb.metrics.MetricsRepo'

    @patch(repo_module + '.get_import')
    async def _get_import(*args, **kwargs):
        return extractors.ImportRecord(
            mayak_import_uuid=1,
            name=str(),
            locked=False,
            loaded=False,
            created_at=dates.localize(),
            updated_at=dates.localize(),
        )

    cursor = extractors.MetricsCursor(
        left=0, right=10, created_at=0, mayak_entity_uuid=0,
    )

    @patch(repo_module + '.get_cursor')
    async def _get_cursor(*args, **kwargs):
        return cursor

    @patch(repo_module + '.get_metrics_with_cursor')
    async def _get_metrics_with_cursor(*args, **kwargs):
        metrics = dict(
            driver_tariff='spb', driver_tariff_zone='comfort', metric='1',
        )
        page = [
            extractors.MetricsRecord(
                mayak_entity_uuid=0,
                metrics=metrics,
                created_at=utils.from_ydb_timestamp(0),
                original_entity_id='1',
            ),
        ]
        return page, cursor

    @patch(repo_module + '.upsert_actions_history')
    async def _upsert_actions_history(*args, **kwargs):
        return None

    # test setup
    job_id = await stq_utils.setup_job(
        stq3_context,
        **kwargs,
        queue_name=constants.StqQueueNames.batching_jobs,
    )
    task = stq.mayak_inspector_batching_jobs.next_call()
    assert task['kwargs'] == kwargs

    # stq_runner call ignores patches
    task_info = async_worker_ng.TaskInfo(
        job_id, 0, 0, queue=constants.StqQueueNames.batching_jobs.value,
    )
    await batching_jobs.task(stq3_context, task_info, **kwargs)


@pytest.mark.parametrize(
    'kwargs, actions, expected_tickets, expected_content, '
    'expected_comments, expected_status_values',
    [
        pytest.param(
            {
                'extra': {'mayak_import_uuid': 1},
                'job_type': constants.JobTypes.batching_actions.value,
            },
            [
                {
                    'mayak_action_uuid': 1,
                    'action_type': 'tariff_block_startrek',
                    'entity_type': 'contractor',
                    'action_entity_id': '1',
                    'rule_name': 'unique',
                    'zone': 'helsinki',
                    'tariff': 'econom',
                    'status': 2,
                    'mayak_entity_uuid': 1,
                    'mayak_import_uuid': 1,
                    'created_at': dates.localize(),
                    'updated_at': dates.localize(),
                    'extra': {
                        'driver_country': 'Finland',
                        'driver_city': 'Helsinki',
                    },
                    'action_params': {
                        'tariff': 'low_tariff',
                        'message': 'message',
                        'mark': 1,
                        'author': 'me',
                        'queue': 'TEST',
                        'summary': 'summary',
                        'summonees': 'me,you',
                    },
                    'triggered_context': {
                        'tags': list(),
                        'entity': test_data.SIMPLE_ENTITY,
                    },
                },
            ],
            [
                {
                    'author': 'me',
                    'description': '',
                    'followers': [],
                    'queue': {'key': 'TEST'},
                    'summary': 'summary',
                    'unique': '1',
                },
            ],
            [
                {
                    'action': 'low_tariff',
                    'driver_city': 'Helsinki',
                    'driver_country': 'Finland',
                    'driver_fio': '',
                    'driver_license': 123,
                    'driver_tariff': 'econom',
                    'mark': 1,
                    'message': 'message',
                    'reason': 'unique',
                    'unique_driver_id': 1,
                },
            ],
            [
                {
                    'attachmentIds': ['1'],
                    'summonees': ['me', 'you'],
                    'text': (
                        '\n'
                        '#|\n'
                        '||country|low_tariff|Total||\n'
                        '||Finland|1|1||\n'
                        '||Total|1|1||\n'
                        '|#'
                    ),
                },
            ],
            [{'mayak_action_uuid': 1, 'status': 1}],
            id='default',
        ),
        pytest.param(
            {
                'extra': {'mayak_import_uuid': 1},
                'job_type': constants.JobTypes.batching_actions.value,
            },
            [
                {
                    'mayak_action_uuid': 1,
                    'action_type': 'tariff_block_startrek',
                    'entity_type': 'contractor',
                    'action_entity_id': 'wrong_udid',
                    'rule_name': 'unique',
                    'zone': 'helsinki',
                    'tariff': 'econom',
                    'status': 2,
                    'mayak_entity_uuid': 1,
                    'mayak_import_uuid': 1,
                    'created_at': dates.localize(),
                    'updated_at': dates.localize(),
                    'extra': {
                        'driver_country': 'Finland',
                        'driver_city': 'Helsinki',
                    },
                    'action_params': {
                        'tariff': 'low_tariff',
                        'message': 'message',
                        'mark': 1,
                        'author': 'me',
                        'queue': 'TEST',
                        'summary': 'summary',
                        'summonees': 'me,you',
                    },
                    'triggered_context': {
                        'tags': list(),
                        'entity': test_data.EMPTY_ENTITY,
                    },
                },
            ],
            [],
            [],
            [],
            [{'mayak_action_uuid': 1, 'status': 4}],
            id='wrong_udid',
        ),
    ],
)
async def test_trigger_batching_actions(
        stq3_context,
        stq,
        patch,
        patch_aiohttp_session,
        response_mock,
        kwargs,
        actions,
        expected_tickets,
        expected_content,
        expected_comments,
        expected_status_values,
):
    repo_module = 'mayak_inspector.storage.ydb.metrics.MetricsRepo'

    @patch(repo_module + '.get_cursor_incomplete_count')
    async def _get_cursor_incomplete_count(*args, **kwargs):
        return 0

    action: tp.Optional[extractors.ActionRecord] = None

    @patch(repo_module + '.get_batching_actions_cursor')
    async def _get_batching_actions_cursor(*args, **kwargs):
        nonlocal action
        for action_ in actions:
            action = extractors.ActionRecord(**action_)
            yield action

    status_values = list()

    @patch(repo_module + '.update_actions_history_statuses')
    async def _update_actions_history_statuses(status_values_):
        status_values.extend(status_values_)

    st_path = 'https://st-api.test.yandex-team.ru/v2'
    ticket = 'TEST-1'
    attachment = '1'

    ticket_queries = list()

    @patch_aiohttp_session(st_path + '/issues')
    def _ticket(*args, json, **kwargs):
        ticket_queries.append(json)
        return response_mock(json=dict(key=ticket))

    content = list()

    @patch_aiohttp_session(st_path + '/attachments')
    def _attach(*args, data, params, **kwargs):
        assert data['file']
        assert params['filename'].startswith(action.action_params['tariff'])

        dataframe = pandas.read_excel(data['file']).fillna('')
        content.extend(dataframe.to_dict('records'))
        return response_mock(json=dict(id=attachment))

    comments = list()

    @patch_aiohttp_session(st_path + f'/issues/{ticket}/comments')
    def _comment(*args, json, **kwargs):
        comments.append(json)
        return response_mock(json=dict(id='1'))

    # test setup
    job_id = await stq_utils.setup_job(
        stq3_context,
        **kwargs,
        queue_name=constants.StqQueueNames.batching_jobs,
    )
    task = stq.mayak_inspector_batching_jobs.next_call()
    assert task['kwargs'] == kwargs

    # stq_runner call ignores patches
    task_info = async_worker_ng.TaskInfo(
        job_id, 0, 0, queue=constants.StqQueueNames.batching_jobs.value,
    )
    await batching_jobs.task(stq3_context, task_info, **kwargs)

    assert ticket_queries == expected_tickets
    assert content == expected_content
    assert comments == expected_comments
    assert status_values == expected_status_values
