# pylint: disable=unused-variable
import datetime
import io

from aiohttp import web
import pandas as pd
import pytest

from supportai_lib.tasks import base_task

from supportai_statistics.generated.stq3 import stq_context
from . import common

CALLS_CHUNK_LIMIT = 100


@pytest.fixture(name='mock_get_project_config')
def mock_project_config(mockserver):
    @mockserver.json_handler(
        'supportai-calls/supportai-calls/v1/project-configs',
    )
    def sai_calls_handler(request):
        assert request.query['project_slug'] == 'some_project'
        return {
            'project_slug': 'some_project',
            'dispatcher_params': {
                'call_service': 'voximplant',
                'account_id': 123,
                'api_key': 'some_api_key',
                'rule_id': 0,
            },
        }


@pytest.mark.project(slug='some_project')
async def test_sai_calls_error(
        stq3_context: stq_context.Context,
        stq_runner,
        response_mock,
        mockserver,
        create_task,
        get_task_file,
):
    @mockserver.json_handler(
        'supportai-calls/supportai-calls/v1/project-configs',
    )
    def sai_calls_handler(request):
        return web.json_response(status=204)

    task = create_task(type_='export_voximplant_resources_usage', params={})
    await stq_runner.supportai_statistics_processing.call(
        task_id='vox_export', args=(), kwargs={'task_id': task.id},
    )

    error_message = 'No project config for project some_project'
    assert task.status == base_task.TaskStatus.ERROR.value
    assert task.error_message == error_message


def _get_vox_now() -> str:
    return (
        datetime.datetime.now()
        .astimezone(tz=datetime.timezone.utc)
        .strftime('%Y-%m-%d %H:%M:%S')
    )


def _compare_vox_datetimes(lhs, rhs):
    lhs_dt = datetime.datetime.strptime(lhs, '%Y-%m-%d %H:%M:%S')
    rhs_dt = datetime.datetime.strptime(rhs, '%Y-%m-%d %H:%M:%S')
    return abs((lhs_dt - rhs_dt).total_seconds()) <= 2


@pytest.mark.project(slug='some_project')
async def test_simple(
        stq3_context: stq_context.Context,
        stq_runner,
        response_mock,
        mockserver,
        create_task,
        get_task_file,
        mock_get_project_config,
):
    vox_now = _get_vox_now()
    from_dt = datetime.datetime.now().astimezone() - datetime.timedelta(
        hours=2,
    )
    from_ts = int(from_dt.timestamp())
    from_utc_str = from_dt.astimezone(tz=datetime.timezone.utc).strftime(
        '%Y-%m-%d %H:%M:%S',
    )
    params = {'from_date': from_ts}
    task = create_task(
        type_='export_voximplant_resources_usage', params=params,
    )

    vox_call_count = 0

    @mockserver.json_handler('voximplant/platform_api/GetCallHistory')
    def vox_handler(request):
        nonlocal vox_call_count
        if vox_call_count == 0:
            assert request.query['api_key'] == 'some_api_key'
            assert request.query['account_id'] == '123'
            assert request.query['from_date'] == from_utc_str
            assert _compare_vox_datetimes(request.query['to_date'], vox_now)
            assert request.query['with_records'] == 'true'
            assert request.query['with_calls'] == 'true'
            assert request.query['count'] == str(CALLS_CHUNK_LIMIT)
            assert request.query['offset'] == '0'
            vox_call_count += 1
            return {
                'result': [
                    {
                        'records': [{'duration': 40}],
                        'duration': 41,
                        'other_resource_usage': [
                            {
                                'resource_type': 'TTS_SOMETHING',
                                'resource_quantity': 1,
                            },
                            {
                                'resource_type': 'ASR_SOMETHING',
                                'resource_quantity': 45,
                            },
                            {
                                'resource_type': 'ASR_SOMETHING',
                                'resource_quantity': 46,
                            },
                            {
                                'resource_type': 'RANDOM_SOMETHING',
                                'resource_quantity': 123,
                            },
                        ],
                        'calls': [
                            {
                                'duration': 45,
                                'direction': '',
                                'incoming': True,
                            },
                            {
                                'duration': 10,
                                'direction': '',
                                'incoming': True,
                            },
                        ],
                        'call_session_history_id': 1,
                        'start_date': '2022-03-24 09:28:56',
                    },
                    {
                        'records': [],
                        'duration': 0,
                        'other_resource_usage': [],
                        'calls': [],
                        'call_session_history_id': 2,
                        'start_date': '2022-03-24 09:29:56',
                    },
                ],
            }
        assert request.query['offset'] == str(CALLS_CHUNK_LIMIT)
        return {'result': []}

    vox_now = _get_vox_now()
    await stq_runner.supportai_statistics_processing.call(
        task_id='vox_export', args=(), kwargs={'task_id': task.id},
    )
    assert (
        task.status == base_task.TaskStatus.COMPLETED.value
    ), task.error_message

    assert task.file_id is not None
    file_data = get_task_file(task.file_id)
    assert file_data is not None

    all_data = pd.read_excel(
        io.BytesIO(file_data[1]), sheet_name=None, na_filter=False,
    )
    assert set(all_data) == {
        'Общий расход ресурсов за период',
        'Детализация расхода ресурсов по звонкам',
    }

    expected_common_columns = [
        'Использование TTS, 10-символьные отрезки',
        'Использование ASR, 15-секундные отрезки',
        'Запись разговора, с',
        'Длительность основного звонка, с',
        'Время работы робота, с',
        'Длительность дополнительных звонков, с',
    ]
    summary_dataframe = all_data['Общий расход ресурсов за период']
    details_dataframe = all_data['Детализация расхода ресурсов по звонкам']
    assert (
        list(summary_dataframe.columns)
        == ['Всего звонков'] + expected_common_columns
    )
    assert (
        list(details_dataframe.columns)
        == ['Id сессии'] + expected_common_columns
    )

    assert common.dataframe_to_table(summary_dataframe) == [
        [2, 1, 7, 40, 45, 35, 10],
    ]
    assert common.dataframe_to_table(details_dataframe) == [
        [1, 1, 7, 40, 45, 35, 10],
        [2, 0, 0, 0, 0, 0, 0],
    ]


@pytest.mark.project(slug='some_project')
async def test_chunks_boundaries(
        stq3_context: stq_context.Context,
        stq_runner,
        response_mock,
        mockserver,
        create_task,
        get_task_file,
        mock_get_project_config,
):
    vox_now = ''

    # session_id, start_at
    calls_chunks = [
        [
            (1, '2022-01-01 00:00:00'),
            (2, '2022-01-01 00:00:00'),
            (3, '2022-01-01 00:00:01'),
        ],
    ]
    calls_chunks += [
        [
            (4, '2022-01-01 00:00:01'),
            (5, '2022-01-01 00:00:02'),
            (6, '2022-01-01 00:00:02'),
        ],
    ] * 19
    calls_chunks += [
        [
            (5, '2022-01-01 00:00:02'),
            (6, '2022-01-01 00:00:02'),
            (7, '2022-01-01 00:00:02'),
        ],
    ]
    calls_chunks += [
        [
            (8, '2022-01-01 00:00:02'),
            (9, '2022-01-01 00:00:03'),
            (10, '2022-01-01 00:00:04'),
        ],
    ] * 19
    calls_chunks += [
        [
            (10, '2022-01-01 00:00:04'),
            (11, '2022-01-01 00:00:04'),
            (12, '2022-01-01 00:00:04'),
        ],
    ]
    calls_chunks += [
        [
            (12, '2022-01-01 00:00:05'),
            (13, '2022-01-01 00:00:06'),
            (14, '2022-01-01 00:00:06'),
        ],
    ] * 19
    calls_chunks += [[(14, '2022-01-01 00:00:06')]]
    expected_session_ids = (
        [1, 2, 3] + [4, 5, 6] * 19 + [7] + [8, 9, 10] * 19 + [11, 12]
    )
    expected_session_ids += [12, 13, 14] * 19

    vox_call_count = 0

    @mockserver.json_handler('voximplant/platform_api/GetCallHistory')
    def vox_handler(request):
        nonlocal vox_call_count
        assert request.query['count'] == str(CALLS_CHUNK_LIMIT)
        assert request.query['offset'] == str(
            (vox_call_count % 20) * CALLS_CHUNK_LIMIT,
        )

        assert _compare_vox_datetimes(request.query['to_date'], vox_now)
        if vox_call_count < 20:
            assert request.query['from_date'] == '2000-01-01 00:00:00'
        else:
            last_batch_last_chunk = calls_chunks[
                vox_call_count - vox_call_count % 20 - 1
            ]
            assert request.query['from_date'] == last_batch_last_chunk[-1][1]

        calls_chunk = calls_chunks[vox_call_count]
        vox_call_count += 1

        return {
            'result': [
                {
                    'records': [],
                    'duration': 0,
                    'other_resource_usage': [],
                    'calls': [],
                    'call_session_history_id': session_id,
                    'start_date': start_date,
                }
                for session_id, start_date in calls_chunk
            ],
        }

    task = create_task(type_='export_voximplant_resources_usage', params={})

    vox_now = _get_vox_now()
    await stq_runner.supportai_statistics_processing.call(
        task_id='vox_export', args=(), kwargs={'task_id': task.id},
    )
    assert (
        task.status == base_task.TaskStatus.PROCESSING.value
    ), task.error_message

    vox_now = _get_vox_now()
    await stq_runner.supportai_statistics_processing.call(
        task_id='vox_export', args=(), kwargs={'task_id': task.id},
    )
    assert (
        task.status == base_task.TaskStatus.COMPLETED.value
    ), task.error_message

    details_sheet = pd.read_excel(
        io.BytesIO(get_task_file(task.file_id)[1]), sheet_name=1,
    )
    session_ids = details_sheet['Id сессии']
    assert list(session_ids) == expected_session_ids


def _session_ids_from_file_content(file_content):
    all_data = pd.read_excel(io.BytesIO(file_content), sheet_name=None)
    assert len(all_data) == 2
    summary_sheet = all_data['Общий расход ресурсов за период']
    details_sheet = all_data['Детализация расхода ресурсов по звонкам']
    calls_total = summary_sheet['Всего звонков']
    assert len(calls_total) == 1
    session_ids = list(details_sheet['Id сессии'])
    assert list(calls_total)[0] == len(session_ids)
    return session_ids


CLIENT_ERROR = 'client_error'
INTERNAL_ERROR = 'internal_error'


@pytest.mark.project(slug='some_project')
@pytest.mark.parametrize(
    (
        'voximplant_error_types',
        'expected_final_status',
        'expected_session_ids_list',
        'breakdown_counts',
    ),
    [
        ([None, None, None, None], 'completed', [[1, 2, 3, 4, 5, 6]], [0]),
        (
            [None, None, CLIENT_ERROR, INTERNAL_ERROR, None, None, None],
            'completed',
            [[1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4, 5, 6]],
            [1, 2, 0],
        ),
        (
            [None, CLIENT_ERROR, None, None, INTERNAL_ERROR, None, None],
            'completed',
            [[1, 2], [1, 2, 3, 4, 5], [1, 2, 3, 4, 5, 6]],
            [1, 2, 0],
        ),
        (
            [CLIENT_ERROR, None, INTERNAL_ERROR, None, None, None, None, None],
            'completed',
            [[], [1, 2], [1, 2, 3, 4, 5, 6]],
            [1, 2, 0],
        ),
        (
            [None, CLIENT_ERROR, INTERNAL_ERROR, CLIENT_ERROR],
            'error',
            [[1, 2], [1, 2], [1, 2]],
            [1, 2, 3],
        ),
    ],
)
async def test_breakdown(
        stq3_context: stq_context.Context,
        stq_runner,
        response_mock,
        mockserver,
        create_task,
        get_task_file,
        mock_get_project_config,
        voximplant_error_types,
        expected_final_status,
        expected_session_ids_list,
        breakdown_counts,
):
    vox_now = ''
    file_id = None
    voximplant_responses = {
        # from_date -> (session_id, start_at)
        '2000-01-01 00:00:00': [
            (1, '2022-07-27 00:00:00'),
            (2, '2022-07-27 00:00:03'),
            (3, '2022-07-27 00:00:03'),
            (4, '2022-07-27 00:00:05'),
            (5, '2022-07-27 00:00:08'),
            (6, '2022-07-27 00:00:08'),
        ],
        '2022-07-27 00:00:03': [
            (2, '2022-07-27 00:00:03'),
            (3, '2022-07-27 00:00:03'),
            (4, '2022-07-27 00:00:05'),
            (5, '2022-07-27 00:00:08'),
            (6, '2022-07-27 00:00:08'),
        ],
        '2022-07-27 00:00:05': [
            (4, '2022-07-27 00:00:05'),
            (5, '2022-07-27 00:00:08'),
            (6, '2022-07-27 00:00:08'),
        ],
        '2022-07-27 00:00:08': [
            (5, '2022-07-27 00:00:08'),
            (6, '2022-07-27 00:00:08'),
        ],
    }

    vox_call_total_count = 0
    vox_call_count = 0
    continuous_success_count = 0
    qos_attempt_number = 0
    last_from_date_before_crush = '2000-01-01 00:00:00'
    last_from_date = '2000-01-01 00:00:00'

    @mockserver.json_handler('voximplant/platform_api/GetCallHistory')
    def vox_handler(request):
        nonlocal vox_call_count
        nonlocal vox_call_total_count
        nonlocal continuous_success_count
        nonlocal last_from_date_before_crush
        nonlocal last_from_date
        nonlocal qos_attempt_number
        assert request.query['offset'] == str(
            continuous_success_count * CALLS_CHUNK_LIMIT,
        )
        assert request.query['from_date'] == last_from_date_before_crush
        assert _compare_vox_datetimes(request.query['to_date'], vox_now)

        vox_call_total_count += 1

        offset = int(request.query['offset']) // (CALLS_CHUNK_LIMIT // 2)
        error_type = voximplant_error_types[vox_call_count]
        vox_call_count += 1
        if error_type is not None:
            if error_type == CLIENT_ERROR:
                if qos_attempt_number < 2:
                    vox_call_count -= 1
                    qos_attempt_number += 1
                else:
                    qos_attempt_number = 0
                    continuous_success_count = 0
                    last_from_date_before_crush = last_from_date
                return web.json_response(status=500)
            continuous_success_count = 0
            last_from_date_before_crush = last_from_date
            return {'error': {'code': 123, 'msg': 'hello!'}}

        continuous_success_count += 1
        history_tail = voximplant_responses[request.query['from_date']]
        response_chunk = history_tail[offset : offset + 2]
        if response_chunk:
            last_from_date = response_chunk[-1][1]
        return {
            'result': [
                {
                    'records': [],
                    'duration': 0,
                    'other_resource_usage': [],
                    'calls': [],
                    'call_session_history_id': session_id,
                    'start_date': start_date,
                }
                for session_id, start_date in response_chunk
            ],
        }

    def get_written_session_ids(task_):
        nonlocal file_id
        if file_id is None:
            file_id = task_.file_id
        else:
            assert file_id == task_.file_id
        return _session_ids_from_file_content(get_task_file(task_.file_id)[1])

    task = create_task(type_='export_voximplant_resources_usage', params={})

    for idx, (expected_session_ids, breakdown_count) in enumerate(
            zip(expected_session_ids_list, breakdown_counts),
    ):
        vox_now = _get_vox_now()
        await stq_runner.supportai_statistics_processing.call(
            task_id='vox_export', args=(), kwargs={'task_id': task.id},
        )

        assert (
            task.params.extra['consecutive_breakdowns_count']
            == breakdown_count
        )
        assert get_written_session_ids(task) == expected_session_ids
        if idx < len(expected_session_ids_list) - 1:
            assert (
                task.status == base_task.TaskStatus.PROCESSING.value
            ), task.error_message
        else:
            assert task.status == expected_final_status


@pytest.mark.project(slug='some_project')
async def test_clear_breakdown_counter(
        stq3_context: stq_context.Context,
        stq_runner,
        response_mock,
        mockserver,
        create_task,
        get_task_file,
        mock_get_project_config,
):
    file_id = None
    vox_now = ''
    is_breakdown = False
    chunk_size = 2

    breakdowns = [True, False, True, True, False, False, True, False, False]
    max_session_ids = [0]
    for is_breakdown in breakdowns[1:]:
        last_max_session_id = max_session_ids[-1]
        if is_breakdown:
            max_session_ids.append(last_max_session_id)
        else:
            max_session_ids.append(last_max_session_id + 78)

    @mockserver.json_handler('voximplant/platform_api/GetCallHistory')
    def vox_handler(request):
        if is_breakdown:
            return web.json_response(status=500)

        offset = int(request.query['offset']) // CALLS_CHUNK_LIMIT * chunk_size
        from_date = request.query['from_date']
        assert _compare_vox_datetimes(request.query['to_date'], vox_now)
        if from_date == '2000-01-01 00:00:00':
            from_date = '0'

        session_id_from = int(from_date)
        return {
            'result': [
                {
                    'records': [],
                    'duration': 0,
                    'other_resource_usage': [],
                    'calls': [],
                    'call_session_history_id': session_id,
                    'start_date': str(session_id),
                }
                for session_id in range(
                    session_id_from + offset,
                    session_id_from + offset + chunk_size,
                )
            ],
        }

    def get_written_session_ids(task_):
        nonlocal file_id
        if file_id is None:
            file_id = task_.file_id
        else:
            assert file_id == task_.file_id
        return _session_ids_from_file_content(get_task_file(task_.file_id)[1])

    task = create_task(type_='export_voximplant_resources_usage', params={})
    breakdown_count = 0
    for is_breakdown, max_session_id in zip(breakdowns, max_session_ids):
        vox_now = _get_vox_now()
        await stq_runner.supportai_statistics_processing.call(
            task_id='vox_export', args=(), kwargs={'task_id': task.id},
        )
        assert task.processing_state == 'working'

        if is_breakdown:
            breakdown_count += 1
        else:
            breakdown_count = 0

        assert (
            task.params.extra['consecutive_breakdowns_count']
            == breakdown_count
        )
        written_session_ids = get_written_session_ids(task)
        if max_session_id == 0:
            assert written_session_ids == []
        else:
            assert written_session_ids == list(range(max_session_id + 1))
