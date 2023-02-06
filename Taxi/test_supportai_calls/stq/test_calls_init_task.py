# pylint: disable=too-many-lines
import collections
import copy
import datetime
import io
import json

from aiohttp import web
import pandas as pd
import pytest
import xlsxwriter

from generated.models import supportai_statistics as stats_models
from supportai_lib.tasks import base_task
from supportai_lib.tasks import constants

from supportai_calls import models as db_models
from test_supportai_calls import common

pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.config(
        TVM_RULES=[
            {'src': 'supportai-calls', 'dst': 'personal'},
            {'src': 'supportai-calls', 'dst': 'stq-agent'},
            {'src': 'supportai-calls', 'dst': 'supportai-context'},
            {'src': 'supportai-calls', 'dst': 'supportai-tasks'},
        ],
    ),
]


@pytest.mark.pgsql('supportai_calls', files=['sample_project.sql'])
@pytest.mark.parametrize(
    ('calls_from_db', 'used_entity'),
    [
        (True, 'phone'),
        (True, 'personal_id'),
        (False, 'phone'),
        (False, 'personal_id'),
        (False, 'external_phone_id'),
    ],
)
@pytest.mark.project(slug='sample_project')
async def test_outgoing_calls_init_task(
        stq3_context,
        stq_runner,
        mockserver,
        web_app_client,
        calls_from_db,
        used_entity,
        create_task_file,
        create_task,
        mock_calls_statistics,
        calls_statistics_batches,
):
    entities_for_file = [
        {
            'phone': '88005553535',
            'personal_id': '1',
            'external_phone_id': '11',
            'company': 'Lucshe pozvonit',
            'feature': 'Not Rules',
        },
        {
            'phone': '+74959379992',
            'personal_id': '2',
            'external_phone_id': '22',
            'company': 'Zhdi menya',
            'feature': 'Not Rules',
        },
        {
            'phone': '+74957397000',
            'personal_id': '3',
            'external_phone_id': '33',
            'company': 'Yandex',
            'feature': 'Rules',
        },
        {
            'phone': '+79101234567',
            'personal_id': '4',
            'external_phone_id': '44',
            'company': 'Test1',
            'feature': 'Rules',
        },
        {
            'phone': '+79107654321',
            'personal_id': '5',
            'external_phone_id': '55',
            'company': 'Test2',
            'feature': 'Rules',
        },
    ]

    entities_for_db = copy.deepcopy(entities_for_file)
    entities_for_db[0]['phone'] = '+78005553535'

    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    async def _stq_reschedule(_):
        return {}

    personal_mock_response = {
        'items': [
            {'id': entity['personal_id'], 'value': entity['phone']}
            for entity in entities_for_db
        ],
    }

    @mockserver.json_handler('/personal/v1/phones/bulk_store')
    def _(request):
        items = request.json['items']
        for item in items:
            assert item['value'][0:2] == '+7'
        return personal_mock_response

    @mockserver.json_handler('/personal/v1/phones/bulk_retrieve')
    def _(_):
        return personal_mock_response

    phone_to_feature = {
        entity['phone']: entity['feature'] for entity in entities_for_db
    }

    @mockserver.json_handler('/ivr-dispatcher/v1/ivr-framework/create-call')
    async def _(request):
        phone_number = request.json['actions'][0]['originate']['phone_number']
        feature_value = phone_to_feature[phone_number]
        assert request.json['context']['features'] == [
            {'key': 'feature', 'value': feature_value},
        ]

        assert (
            request.json['actions'][0]['originate']['phone_number'][0:2]
            == '+7'
        )
        return web.json_response()

    file_id = None

    if not calls_from_db:
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('phones')
        worksheet.write(0, 0, used_entity)
        worksheet.write(0, 1, 'feature')

        for row_num, entity in enumerate(entities_for_file):
            worksheet.write(row_num + 1, 1, entity['feature'])
            for entity_name, entity_value in entity.items():
                if entity_name == used_entity:
                    worksheet.write(row_num + 1, 0, entity_value)
                    break
        workbook.close()
        output.seek(0)

        file = create_task_file(
            filename='calls.xlsx',
            content_type=constants.XLSX_CONTENT_TYPE,
            content=output.read(),
        )
        file_id = file.id

    task = create_task(
        type_='outgoing_calls_init',
        file_id=file_id,
        params={'calls_from_db': calls_from_db},
    )

    async with stq3_context.pg.slave_pool.acquire() as conn:
        if calls_from_db:
            db_calls = [
                db_models.Call(
                    id=-1,
                    project_slug='sample_project',
                    call_service=db_models.CallService.IVR_FRAMEWORK,
                    direction=db_models.CallDirection.OUTGOING,
                    task_id=task.id,
                    phone=entity['phone']
                    if not used_entity == 'personal_id'
                    else '',
                    personal_phone_id=entity['personal_id']
                    if used_entity == 'personal_id'
                    else '',
                    chat_id=entity['phone'],
                    features=json.dumps(
                        [{'key': 'feature', 'value': entity['feature']}],
                    ),
                    status=db_models.CallStatus.QUEUED,
                    error_message=None,
                    created=datetime.datetime.now(),
                    ended=None,
                    initiated=None,
                    session_id=None,
                    has_record=False,
                    attempt_number=0,
                )
                for entity in entities_for_db
            ]

            await db_models.Call.insert_bulk(stq3_context, conn, db_calls)

    await stq_runner.supportai_calls_processing.call(
        task_id='out_call_task', args=(), kwargs={'task_id': task.id},
    )
    assert (
        task.status == base_task.TaskStatus.PROCESSING.value
    ), task.error_message

    initiated_calls = []
    queued_calls = []

    async with stq3_context.pg.slave_pool.acquire() as conn:
        calls = await db_models.Call.select_by_task_id(
            stq3_context, conn, task.id,
        )

        assert len(calls) == 5

        for call in calls:
            assert call.call_service == db_models.CallService.IVR_FRAMEWORK

            if call.status == db_models.CallStatus.INITIATED:
                assert call.attempt_number == 1
                initiated_calls.append(call)
            elif call.status == db_models.CallStatus.QUEUED:
                assert call.attempt_number == 0
                queued_calls.append(call)

        assert len(initiated_calls) == 2
        assert len(queued_calls) == 3

    chat_ids = [call.chat_id for call in initiated_calls + queued_calls]
    unknown_error = 'SOME ERROR WE HAVE NOT MET YET'
    error_codes = [
        None,
        None,
        'DESTINATION_BUSY',
        'ABONENT_HANGUP',
        unknown_error,
    ]
    error_code_indices = [None, None, 0, 1, 1]
    expected_statistics_statuses = [
        'ended',
        'forwarded',
        'user_busy',
        'hangup',
        'error',
    ]
    forwarded_idx = 1
    chat_id_to_statistics_status = {
        chat_id: expected_status
        for chat_id, expected_status in zip(
            chat_ids, expected_statistics_statuses,
        )
    }

    @mockserver.json_handler('/supportai-context/v1/contexts/multiple')
    async def _():
        contexts = [
            common.create_context(
                created_at=datetime.datetime.now().astimezone()
                + datetime.timedelta(minutes=5),
                chat_id=chat_id,
                error_code=error_code,
                error_code_index=error_code_index,
                num_records=4,
                is_forwarded=idx == forwarded_idx,
                is_ended=not idx == forwarded_idx,
                duration_s=5,
            )
            for idx, (chat_id, error_code, error_code_index) in enumerate(
                zip(chat_ids, error_codes, error_code_indices),
            )
        ]
        return web.json_response(
            data={'contexts': contexts, 'total': len(contexts)},
        )

    await stq_runner.supportai_calls_processing.call(
        task_id='out_call_task', args=(), kwargs={'task_id': task.id},
    )
    assert (
        task.status == base_task.TaskStatus.PROCESSING.value
    ), task.error_message

    expected_counts = [
        (db_models.CallStatus.INITIATED, 2),
        (db_models.CallStatus.ENDED, 2),
        (db_models.CallStatus.QUEUED, 1),
    ]
    async with stq3_context.pg.slave_pool.acquire() as conn:
        for status, count in expected_counts:
            assert (
                await db_models.Call.count_by_filters(
                    stq3_context,
                    conn,
                    project_slug='sample_project',
                    task_id=task.id,
                    statuses=[status],
                )
                == count
            ), status

    await stq_runner.supportai_calls_processing.call(
        task_id='dont care', args=(), kwargs={'task_id': task.id},
    )
    assert task.status == base_task.TaskStatus.PROCESSING.value

    expected_counts = [
        (db_models.CallStatus.INITIATED, 1),
        (db_models.CallStatus.ENDED, 4),
    ]
    async with stq3_context.pg.slave_pool.acquire() as conn:
        for status, count in expected_counts:
            assert (
                await db_models.Call.count_by_filters(
                    stq3_context,
                    conn,
                    project_slug='sample_project',
                    task_id=task.id,
                    statuses=[status],
                )
                == count
            ), status

    await stq_runner.supportai_calls_processing.call(
        task_id='out_call_task', args=(), kwargs={'task_id': task.id},
    )
    assert task.status == base_task.TaskStatus.COMPLETED.value

    expected_counts = [
        (db_models.CallStatus.ENDED, 4),
        (db_models.CallStatus.ERROR, 1),
    ]
    async with stq3_context.pg.slave_pool.acquire() as conn:
        for status, count in expected_counts:
            assert (
                await db_models.Call.count_by_filters(
                    stq3_context,
                    conn,
                    project_slug='sample_project',
                    task_id=task.id,
                    statuses=[status],
                )
                == count
            ), status

    assert _stq_reschedule.times_called == 3
    assert len(calls_statistics_batches) == 3
    assert list(map(len, calls_statistics_batches)) == [2, 2, 1]

    statistics_records = sum(calls_statistics_batches, [])
    for record in statistics_records:
        assert record.get('direction') == 'outgoing'
        assert record.get('batch_id') == task.id
        assert record.get('call_service') == 'ivr_framework'
        expected_status = chat_id_to_statistics_status.pop(
            record.get('chat_id'), None,
        )
        assert record.get('status') == expected_status
        if expected_status == 'error':
            assert record.get('error_code') == unknown_error
        elif expected_status == 'forwarded':
            assert record.get('forwarded_to') == 'something'
        if expected_status == 'user_busy':
            assert record.get('total_duration') is None
            assert record.get('talk_duration') is None
        else:
            assert record.get('total_duration') is not None
            assert record.get('talk_duration') == 5
    assert not chat_id_to_statistics_status


@pytest.mark.pgsql('supportai_calls', files=['sample_project.sql'])
@pytest.mark.project(slug='sample_project')
async def test_cancel_calls_from_beginning(
        stq3_context, stq_runner, web_app_client, mockserver, create_task,
):
    count_calls = 0

    @mockserver.json_handler('/ivr-dispatcher/v1/ivr-framework/create-call')
    async def _(_):
        nonlocal count_calls
        count_calls += 1
        return web.json_response()

    task = create_task(id_='2', type_='outgoing_calls_init')

    response_cancel = await web_app_client.post(
        f'v1/calls/tasks/{task.id}/cancel?'
        f'project_slug=sample_project&user_id=34',
    )
    assert response_cancel.status == 200

    await stq_runner.supportai_calls_processing.call(
        task_id='2',
        args=(),
        kwargs={'task_id': task.id, 'task_args': {'calls_from_db': True}},
    )

    assert task.status == base_task.TaskStatus.COMPLETED.value
    assert count_calls == 0


@pytest.mark.pgsql('supportai_calls', files=['sample_project.sql'])
@pytest.mark.project(slug='sample_project')
async def test_cancel_calls_in_between(
        stq3_context, stq_runner, web_app_client, mockserver, create_task,
):
    count_init_calls = 0

    @mockserver.json_handler('/ivr-dispatcher/v1/ivr-framework/create-call')
    async def _(_):
        nonlocal count_init_calls
        count_init_calls += 1
        return web.json_response()

    @mockserver.json_handler('/personal/v1/phones/bulk_store')
    def _(_):
        return {
            'items': [{'id': '1', 'value': '1'}, {'id': '2', 'value': '2'}],
        }

    task = create_task(id_='2', type_='outgoing_calls_init')

    await stq_runner.supportai_calls_processing.call(
        task_id='2',
        args=(),
        kwargs={'task_id': task.id, 'task_args': {'calls_from_db': True}},
    )

    response_cancel = await web_app_client.post(
        f'v1/calls/tasks/{task.id}/cancel?'
        f'project_slug=sample_project&user_id=34',
    )
    assert response_cancel.status == 200

    async with stq3_context.pg.slave_pool.acquire() as conn:
        num_initiated = await db_models.Call.count_by_filters(
            stq3_context,
            conn,
            project_slug='sample_project',
            task_id=task.id,
            statuses=[db_models.CallStatus.INITIATED],
        )
        num_cancelled = await db_models.Call.count_by_filters(
            stq3_context,
            conn,
            project_slug='sample_project',
            task_id=task.id,
            statuses=[db_models.CallStatus.CANCELLED],
        )

    assert (
        task.status == base_task.TaskStatus.PROCESSING.value
    ), task.error_message
    assert count_init_calls == 2
    assert num_initiated == 2
    assert num_cancelled == 2


@pytest.mark.pgsql('supportai_calls', files=['sample_project.sql'])
@pytest.mark.project(slug='sample_project')
@pytest.mark.parametrize('record_url', ['some://url.mp3', None])
@pytest.mark.parametrize('error_code', ['some error', None])
async def test_init_calls_with_voximplant(
        stq3_context,
        mockserver,
        stq_runner,
        create_task,
        record_url,
        error_code,
):
    task = create_task(
        type_='outgoing_calls_init', params={'calls_from_db': True},
    )

    calls = [
        common.get_preset_call(
            'sample_project',
            call_service=db_models.CallService.VOXIMPLANT,
            task_id=task.id,
            chat_id=str(i) * 3,
            created=datetime.datetime.now(),
            attempt_number=1,
        )
        for i in range(13)
    ]
    async with stq3_context.pg.master_pool.acquire() as conn:
        await db_models.Call.insert_bulk(stq3_context, conn, calls)
        await db_models.ProjectConfig.update(
            stq3_context,
            conn,
            project_slug='sample_project',
            call_service=db_models.CallService.VOXIMPLANT,
            dispatcher_params={
                'api_key': 'some api_key',
                'account_id': 4242,
                'rule_id': 7788,
            },
        )

    statuses = (
        ['New'] * 2
        + ['In progress'] * 5
        + ['Processed'] * 3
        + ['Cancelled'] * 1
        + ['Error'] * 2
    )
    chat_id_to_vox_status = {
        str(idx) * 3: status for idx, status in enumerate(statuses)
    }
    call_details_list = []

    @mockserver.json_handler('voximplant/platform_api/CreateCallList')
    async def _(request):
        phones_df = pd.read_csv(
            io.BytesIO(request.get_data()), sep=';', dtype=str,
        )
        assert 'number' in phones_df
        assert 'chat_id' in phones_df
        assert 'project_slug' in phones_df
        assert 'env_var' in phones_df
        assert len(phones_df['number']) == 13
        assert phones_df['project_slug'][0] == 'sample_project'
        assert phones_df['env_var'][0] == 'unittests'
        for _, row in phones_df.iterrows():
            status = chat_id_to_vox_status[row['chat_id']]
            result = {
                'start_execution_time': '',
                'attempts_left': 1,
                'status_id': 2,
                'list_id': 123,
                'finish_execution_time': '',
                'start_at': '',
                'custom_data': json.dumps(
                    {
                        'number': str(row['number']),
                        'chat_id': str(row['chat_id']),
                    },
                ),
                'last_attempt': '2021-10-14 09:07:12',
                'status': status,
            }

            result_data = {'call_connected': True}
            if record_url:
                result_data['record_url'] = record_url
                result_data['has_record'] = True
            if error_code:
                result_data['error_code'] = error_code
            if status == 'Processed':
                result_data['dialog_closed'] = True

            result['result_data'] = json.dumps(result_data)

            call_details_list.append(result)

        return {'result': True, 'list_id': 123, 'count': 10}

    await stq_runner.supportai_calls_processing.call(
        task_id='3',
        args=(),
        kwargs={'task_id': task.id, 'task_args': {'calls_from_db': True}},
    )

    assert (
        task.status == base_task.TaskStatus.PROCESSING.value
    ), task.error_message

    async with stq3_context.pg.master_pool.acquire() as conn:
        num_initiated = await db_models.Call.count_by_filters(
            stq3_context,
            conn,
            project_slug='sample_project',
            task_id=task.id,
            statuses=[db_models.CallStatus.INITIATED],
        )

    assert num_initiated == 13

    @mockserver.json_handler('voximplant/platform_api/GetCallListDetails')
    async def _(request):
        assert 'output' in request.query
        assert request.query['output'] == 'json'
        assert 'list_id' in request.query
        assert request.query['list_id'] == '123'
        return web.json_response(
            data={'result': call_details_list, 'count': 13},
        )

    await stq_runner.supportai_calls_processing.call(
        task_id='3', args=(), kwargs={'task_id': task.id},
    )

    assert (
        task.status == base_task.TaskStatus.PROCESSING.value
    ), task.error_message

    status_to_expected_count = {
        db_models.CallStatus.INITIATED: 2,
        db_models.CallStatus.PROCESSING: 5,
        db_models.CallStatus.ENDED: 3 if not error_code else 0,
        db_models.CallStatus.CANCELLED: 1,
        db_models.CallStatus.ERROR: 2 if not error_code else 5,
    }

    async with stq3_context.pg.master_pool.acquire() as conn:
        for status, expected_count in status_to_expected_count.items():
            calls_count = await db_models.Call.count_by_filters(
                stq3_context,
                conn,
                project_slug='sample_project',
                task_id=task.id,
                statuses=[status],
            )
            assert calls_count == expected_count, status

    async with stq3_context.pg.slave_pool.acquire() as conn:
        calls = await db_models.Call.select_by_task_id(
            stq3_context, conn, task.id,
        )

    for call in calls:
        assert call.call_service == db_models.CallService.VOXIMPLANT
        assert call.initiated is not None
        if call.status.value in ('ended', 'error'):
            if record_url:
                if chat_id_to_vox_status[call.chat_id] == 'Error':
                    assert call.has_record is False
                    assert call.call_record_id is None
                else:
                    assert call.has_record is True
                    assert call.call_record_id == record_url
            else:
                assert call.has_record is False
                assert call.call_record_id is None
            if error_code and chat_id_to_vox_status[call.chat_id] != 'Error':
                assert (
                    call.error_message
                    == f'Ошибка во время разговора: {error_code}'
                )
            elif chat_id_to_vox_status[call.chat_id] == 'Error':
                assert (
                    call.error_message
                    == 'some error occurred on voximplant side'
                )
            else:
                assert call.error_message is None
        else:
            assert call.has_record is False
        if call.status.value == 'error':
            assert call.error_message is not None
        else:
            assert call.error_message is None

    for vox_call in call_details_list:
        vox_call['status'] = 'Processed'

    await stq_runner.supportai_calls_processing.call(
        task_id='3', args=(), kwargs={'task_id': task.id},
    )

    assert task.status == base_task.TaskStatus.COMPLETED.value


@pytest.mark.project(slug='project_voximplant')
@pytest.mark.pgsql('supportai_calls', files=['sample_project.sql'])
async def test_voximplant_call_list_details_variants(
        stq3_context,
        stq_runner,
        mockserver,
        create_task,
        mock_calls_statistics,
        calls_statistics_batches,
):
    now = datetime.datetime.now().astimezone()
    minute = datetime.timedelta(minutes=1)
    initiated = now - minute * 5
    initiated_vox = initiated + minute
    started_at = initiated_vox + minute
    ended_at = started_at + minute

    task = create_task(
        type_='outgoing_calls_init',
        status=base_task.TaskStatus.PROCESSING,
        state=base_task.TaskProcessingState.Working,
        params={'list_id': 0},
    )

    chat_id_to_case = {
        # has result, with result_data, status, expected db status
        '0': (True, True, 'Processed', db_models.CallStatus.ENDED),
        '1': (True, False, 'Processed', db_models.CallStatus.ENDED),
        '2': (True, False, 'Error', db_models.CallStatus.ERROR),
        '3': (True, False, 'In progress', db_models.CallStatus.PROCESSING),
        '4': (False, None, None, db_models.CallStatus.ERROR),
    }

    calls = [
        common.get_preset_call(
            project_slug='project_voximplant',
            chat_id=chat_id,
            task_id=task.id,
            initiated=initiated,
            status=db_models.CallStatus.INITIATED,
            attempt_number=1,
        )
        for chat_id in chat_id_to_case
    ]
    async with stq3_context.pg.master_pool.acquire() as conn:
        await db_models.Call.insert_bulk(stq3_context, conn, calls)

    @mockserver.json_handler('voximplant/platform_api/GetCallListDetails')
    async def _(_):
        results = []
        for (
                chat_id,
                (has_result_, with_result_data_, status_, _),
        ) in chat_id_to_case.items():
            if not has_result_:
                continue

            result = {
                'start_execution_time': '',
                'attempts_left': 1,
                'status_id': 2,
                'list_id': 123,
                'finish_execution_time': '',
                'start_at': '',
                'custom_data': json.dumps({'chat_id': chat_id}),
                'last_attempt': initiated_vox.isoformat(),
                'status': status_,
            }
            if not with_result_data_:
                results.append(result)
                continue

            result_data = {
                'call_connected': True,
                'started_at': started_at.isoformat(),
                'ended_at': ended_at.isoformat(),
                'tags': ['first', 'second'],
            }
            result['result_data'] = json.dumps(result_data)
            results.append(result)

        return {'result': results, 'count': 4}

    await stq_runner.supportai_calls_processing.call(
        task_id=task.id,
        args=(),
        kwargs={
            'task_id': task.id,
            'task_args': {'callback_after': 5, 'list_id': '1'},
            'calls_from_db': True,
        },
    )
    assert (
        task.status == base_task.TaskStatus.PROCESSING.value
    ), task.error_message

    async with stq3_context.pg.slave_pool.acquire() as conn:
        updated_calls = await db_models.Call.select_by_task_id(
            stq3_context, conn, task.id,
        )
    assert len(updated_calls) == 5
    for call in updated_calls:
        has_result, with_result_data, _, expected_status = chat_id_to_case[
            call.chat_id
        ]
        assert call.status == expected_status
        if call.status == db_models.CallStatus.PROCESSING:
            assert call.initiated == initiated_vox
            assert call.ended is None
        elif has_result:
            assert call.initiated == initiated_vox
            if with_result_data:
                assert call.ended == ended_at
            else:
                assert (call.ended - now).total_seconds() < 5.0
        else:
            assert call.initiated == initiated
            assert (call.ended - now).total_seconds() < 5.0

    assert len(calls_statistics_batches) == 1
    records = calls_statistics_batches[0]
    assert len(records) == 4
    for record in records:
        api_record = stats_models.CallRecord.deserialize(record)
        has_result, with_result_data, _, status = chat_id_to_case[
            api_record.chat_id
        ]
        for attr in ('initiated_at', 'started_at', 'ended_at'):
            if getattr(api_record, attr) is None:
                continue

            setattr(
                api_record,
                attr,
                getattr(api_record, attr).replace(
                    tzinfo=datetime.timezone.utc,
                ),
            )

        assert status.value == api_record.status
        if status.value == 'error':
            assert api_record.started_at is None
            assert api_record.ended_at is None
            assert api_record.error_code == 'UNKNOWN_ERROR'
            if has_result:
                assert api_record.initiated_at == initiated_vox
            else:
                assert api_record.initiated_at == initiated
        elif with_result_data:
            assert api_record.initiated_at == initiated_vox
            assert api_record.started_at == started_at
            assert api_record.ended_at == ended_at
            assert api_record.talk_duration == 60
            assert api_record.total_duration == 120
        else:
            assert api_record.initiated_at == initiated_vox
            assert api_record.started_at == initiated_vox
            assert (api_record.ended_at - now).total_seconds() < 5.0
            assert api_record.talk_duration == api_record.total_duration
            assert abs(api_record.talk_duration - 240) < 5


@pytest.mark.project(slug='sample_project')
async def test_separated_call_limits_by_project(
        stq3_context, mockserver, stq_runner, create_task,
):
    call_lines_quota = stq3_context.config.SUPPORTAI_CALLS_CONFIG[
        'call_lines_common_quota'
    ]
    task_planned_calls_number = call_lines_quota * 2

    task_calls_data = [
        {'phone': str(idx), 'personal_id': str(idx)}
        for idx in range(task_planned_calls_number)
    ]

    task = create_task(
        type_='outgoing_calls_init',
        file_id=None,
        params={'calls_from_db': True},
    )

    db_calls = [
        db_models.Call(
            id=-1,
            project_slug='sample_project',
            direction=db_models.CallDirection.OUTGOING,
            call_service=db_models.CallService.IVR_FRAMEWORK,
            task_id=task.id,
            phone=call_data['phone'],
            personal_phone_id=call_data['personal_id'],
            chat_id=call_data['phone'],
            features=json.dumps({}),
            attempt_number=1,
            status=db_models.CallStatus.QUEUED,
            created=datetime.datetime.now(),
            has_record=False,
        )
        for call_data in task_calls_data
    ]

    side_calls_initiated_number = 10
    side_calls = [
        db_models.Call(
            id=-1,
            project_slug='side_project_with_initiated_calls',
            direction=db_models.CallDirection.OUTGOING,
            call_service=db_models.CallService.IVR_FRAMEWORK,
            task_id='12321',
            phone=str(idx),
            personal_phone_id=str(idx),
            chat_id=str(idx),
            features=json.dumps({}),
            attempt_number=1,
            status=db_models.CallStatus.INITIATED,
            created=datetime.datetime.now(),
            has_record=False,
        )
        for idx in range(side_calls_initiated_number)
    ]

    @mockserver.json_handler('/personal/v1/phones/bulk_store')
    def _(_):
        return web.json_response(
            data={
                'items': [
                    {
                        'id': call_data['personal_id'],
                        'value': call_data['phone'],
                    }
                    for call_data in task_calls_data
                ],
            },
        )

    @mockserver.json_handler('/ivr-dispatcher/v1/ivr-framework/create-call')
    async def _(_):
        return web.json_response()

    async with stq3_context.pg.master_pool.acquire() as conn:
        await db_models.Call.insert_bulk(stq3_context, conn, db_calls)
        await db_models.Call.insert_bulk(stq3_context, conn, side_calls)

    await stq_runner.supportai_calls_processing.call(
        task_id='out_call_task', args=(), kwargs={'task_id': task.id},
    )

    async with stq3_context.pg.slave_pool.acquire() as conn:
        task_total_count = await db_models.Call.count_by_filters(
            stq3_context, conn, project_slug='sample_project', task_id=task.id,
        )
        task_init_count = await db_models.Call.count_by_filters(
            stq3_context,
            conn,
            project_slug='sample_project',
            task_id=task.id,
            statuses=[db_models.CallStatus.INITIATED],
        )
        side_init_count = await db_models.Call.count_by_filters(
            stq3_context,
            conn,
            project_slug='side_project_with_initiated_calls',
            statuses=[db_models.CallStatus.INITIATED],
        )

        assert task_total_count == task_planned_calls_number
        assert task_init_count == call_lines_quota
        assert side_init_count == side_calls_initiated_number


@pytest.mark.project(slug='sample_project')
async def test_reschedule_task_till_closest_queued_call(
        stq3_context, stq_runner, mockserver, patch, create_task,
):
    now = datetime.datetime.now().astimezone()
    calls_delays_hrs = [1.5, 2.5, 0.5, 3.0]
    begin_calls_at_times = [
        now + datetime.timedelta(hours=delay_hrs)
        for delay_hrs in calls_delays_hrs
    ]
    closest_call_begin_at = begin_calls_at_times[2]

    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    async def _stq_reschedule(request):
        eta = request.json['eta']
        eta_dt = datetime.datetime.fromisoformat(eta[:-1]).replace(
            tzinfo=datetime.timezone.utc,
        )
        diff = (eta_dt - closest_call_begin_at).total_seconds()
        assert abs(diff) < 5.0
        return {}

    task = create_task(
        type_='outgoing_calls_init',
        file_id=None,
        params={
            'calls_from_db': True,
            'begin_calls_at': str(now),  # just non-empty when from db
        },
    )

    calls = [
        common.get_preset_call(
            project_slug='sample_project',
            task_id=task.id,
            phone='phone',
            personal_phone_id='some_id',
            begin_at=begin_call_at,
        )
        for begin_call_at in begin_calls_at_times
    ]
    async with stq3_context.pg.master_pool.acquire() as conn:
        await db_models.Call.insert_bulk(stq3_context, conn, calls)

    await stq_runner.supportai_calls_processing.call(
        task_id='i_dont_give_a_rat_ass', args=(), kwargs={'task_id': task.id},
    )
    assert task.status == base_task.TaskStatus.PROCESSING.value

    async with stq3_context.pg.slave_pool.acquire() as conn:
        not_initiated_calls = await db_models.Call.select_by_task_id(
            stq3_context, conn, task.id,
        )

    assert len(not_initiated_calls) == 4
    for call in not_initiated_calls:
        assert call.status == db_models.CallStatus.QUEUED

    assert _stq_reschedule.times_called == 1


@pytest.mark.parametrize('with_begin_at', [True, False])
@pytest.mark.parametrize('with_end_at', [True, False])
@pytest.mark.project(slug='sample_project')
@pytest.mark.config(
    SUPPORTAI_CALLS_CONFIG={
        'call_lines_common_quota': 5,
        'delay_between_calls_in_seconds': 0,
        'projects': {'sample_project': {}},
    },
)
async def test_initiate_calls_from_interval(
        stq3_context,
        stq_runner,
        mockserver,
        patch,
        create_task,
        with_begin_at,
        with_end_at,
):
    @mockserver.json_handler('/ivr-dispatcher/v1/ivr-framework/create-call')
    async def _(_):
        return web.json_response()

    now = datetime.datetime.now().astimezone()
    chat_ids_with_deviations = [
        ('1', 1, 3),
        ('2', -1, 1),
        ('3', -3, -1),
        ('4', 3, 1),
        ('5', -1, -3),
    ]
    chat_ids_with_intervals = [
        (
            chat_id,
            now + datetime.timedelta(hours=begin_dev),
            now + datetime.timedelta(hours=end_dev),
        )
        for chat_id, begin_dev, end_dev in chat_ids_with_deviations
    ]

    should_be_initiated = ['2']
    if not with_begin_at:
        should_be_initiated += ['1', '4']
    if not with_end_at:
        should_be_initiated += ['3', '5']

    status_to_expected_chat_ids = {
        db_models.CallStatus.QUEUED: ['1', '4'] if with_begin_at else [],
        db_models.CallStatus.INITIATED: should_be_initiated,
        db_models.CallStatus.CANCELLED: ['3', '5'] if with_end_at else [],
    }

    task_params = {'calls_from_db': True}
    if with_begin_at:
        task_params['begin_calls_at'] = str(now)  # just non-empty when from db
    if with_end_at:
        task_params['end_calls_at'] = str(now)  # just non-empty when from db
    task = create_task(
        type_='outgoing_calls_init', file_id=None, params=task_params,
    )

    calls = [
        common.get_preset_call(
            project_slug='sample_project',
            task_id=task.id,
            chat_id=chat_id,
            status=db_models.CallStatus.QUEUED,
            begin_at=begin_at if with_begin_at else None,
            end_at=end_at if with_end_at else None,
        )
        for chat_id, begin_at, end_at in chat_ids_with_intervals
    ]
    async with stq3_context.pg.master_pool.acquire() as conn:
        await db_models.Call.insert_bulk(stq3_context, conn, calls)

    await stq_runner.supportai_calls_processing.call(
        task_id='some_task_name', args=(), kwargs={'task_id': task.id},
    )
    assert (
        task.status == base_task.TaskStatus.PROCESSING.value
    ), task.error_message

    async with stq3_context.pg.master_pool.acquire() as conn:
        updated_calls = await db_models.Call.select_by_task_id(
            stq3_context, conn, task.id,
        )
    assert len(updated_calls) == 5

    status_to_chat_ids = collections.defaultdict(set)
    for call in updated_calls:
        status_to_chat_ids[call.status].add(call.chat_id)

    assert len(status_to_chat_ids) == 1 + int(with_begin_at) + int(with_end_at)

    for status, chat_ids in status_to_chat_ids.items():
        assert chat_ids == set(status_to_expected_chat_ids[status])


@pytest.mark.parametrize('task_timezone_shift', [5.0, None])
@pytest.mark.parametrize('with_begin_at', [True, False])
@pytest.mark.parametrize('with_end_at', [True, False])
@pytest.mark.project(slug='sample_project')
async def test_setting_calls_interval_from_file(
        stq3_context,
        stq_runner,
        mockserver,
        patch,
        create_task,
        create_task_file,
        task_timezone_shift,
        with_begin_at,
        with_end_at,
):
    @mockserver.json_handler('/ivr-dispatcher/v1/ivr-framework/create-call')
    async def _(_):
        return web.json_response()

    phone_to_timezone_shift = {'+1': None, '+2': 1, '+3': -3}

    @mockserver.json_handler('/personal/v1/phones/bulk_store')
    async def _(_):
        return {
            'items': [
                {'id': phone_, 'value': phone_}
                for phone_ in phone_to_timezone_shift
            ],
        }

    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet('phones')
    worksheet.write(0, 0, 'phone')
    worksheet.write(0, 1, 'timezone_shift')
    for idx, (phone, timezone_shift) in enumerate(
            phone_to_timezone_shift.items(),
    ):
        worksheet.write(idx + 1, 0, phone)
        worksheet.write(idx + 1, 1, timezone_shift)
    workbook.close()
    output.seek(0)

    file = create_task_file(
        filename='calls.xlsx',
        content_type=constants.XLSX_CONTENT_TYPE,
        content=output.read(),
    )

    begin_calls_delay = 1
    end_calls_delay = 1.5
    local_now = (
        datetime.datetime.now().astimezone(
            datetime.timezone(
                offset=datetime.timedelta(hours=task_timezone_shift),
            ),
        )
        if task_timezone_shift is not None
        else datetime.datetime.now()
    )
    begin_calls_at = local_now + datetime.timedelta(hours=begin_calls_delay)
    end_calls_at = local_now + datetime.timedelta(hours=end_calls_delay)

    task_params = {}
    if with_begin_at:
        task_params['begin_calls_at'] = str(begin_calls_at)
    if with_end_at:
        task_params['end_calls_at'] = str(end_calls_at)

    task = create_task(
        type_='outgoing_calls_init', file_id=file.id, params=task_params,
    )

    await stq_runner.supportai_calls_processing.call(
        task_id='out_call_task', args=(), kwargs={'task_id': task.id},
    )
    assert (
        task.status == base_task.TaskStatus.PROCESSING.value
    ), task.error_message

    real_task_timezone_shift = task_timezone_shift or 3.0
    phone_to_expected_interval = {}
    for phone, call_timezone_shift in phone_to_timezone_shift.items():
        difference_hours = (
            0.0
            if call_timezone_shift is None
            else real_task_timezone_shift - call_timezone_shift
        )
        time_delta = datetime.timedelta(hours=difference_hours)
        phone_to_expected_interval[phone] = (
            begin_calls_at.astimezone() + time_delta,
            end_calls_at.astimezone() + time_delta,
        )

    async with stq3_context.pg.master_pool.acquire() as conn:
        calls = await db_models.Call.select_by_task_id(
            stq3_context, conn, task.id,
        )
    assert len(calls) == 3

    def _compare_timestamps(first_ts, second_ts):
        assert abs((first_ts - second_ts).total_seconds()) < 5.0

    for call in calls:
        expected_begin_at, expected_end_at = phone_to_expected_interval[
            call.phone
        ]
        if with_begin_at:
            _compare_timestamps(call.begin_at, expected_begin_at)
        else:
            assert call.begin_at is None
        if with_end_at:
            _compare_timestamps(call.end_at, expected_end_at)
        else:
            assert call.end_at is None
