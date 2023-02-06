# pylint: disable=protected-access
import datetime
import io

from aiohttp import web
import openpyxl
import pytest

import supportai_calls.models as db_models
from test_supportai_calls import common


pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.pgsql('supportai_calls', files=['outgoing_calls.sql']),
]


@pytest.mark.parametrize(
    ('phone', 'chat_id', 'status', 'task_id', 'count'),
    [
        ('phone', None, None, None, 3),
        ('phone', 'chat', None, None, 2),
        (None, 'chat1', None, None, 1),
        ('+7912', None, None, None, 1),
        (None, None, 'ended', None, 1),
        (None, None, None, '1', 3),
        ('phone', None, 'queued', '1', 2),
    ],
)
async def test_get_calls(
        web_app_client, phone, chat_id, status, task_id, count,
):
    params = {
        'project_slug': 'test',
        'user_id': '34',
        'limit': 10,
        'offset': 0,
    }

    if phone:
        params['phone'] = phone
    if chat_id:
        params['chat_id'] = chat_id
    if status:
        params['status'] = status
    if task_id:
        params['task_id'] = task_id

    response = await web_app_client.get('/v1/calls', params=params)

    assert response.status == 200

    assert len((await response.json())['calls']) == count
    assert (await response.json())['total_calls_count'] == count


async def test_get_calls_older_newer_than(stq3_context, web_app_client):
    project_slug = 'test_get_calls'

    now = datetime.datetime.now().astimezone()
    deviations_min = [-10, -5, 0, 5, 10]

    eight_minutes = datetime.timedelta(minutes=8)
    newer_than = int((now - eight_minutes).timestamp() * 1000)
    older_than = int((now + eight_minutes).timestamp() * 1000)

    calls = [
        common.get_preset_call(
            project_slug, created=now + datetime.timedelta(minutes=deviation),
        )
        for deviation in deviations_min
    ]
    async with stq3_context.pg.master_pool.acquire() as conn:
        await db_models.Call.insert_bulk(stq3_context, conn, calls)

    for with_older_than in [True, False]:
        for with_newer_than in [True, False]:
            expected_count = 5
            params = {
                'project_slug': project_slug,
                'user_id': '34',
                'limit': 10,
                'offset': 0,
            }
            if with_older_than:
                params['older_than'] = older_than
                expected_count -= 1
            if with_newer_than:
                params['newer_than'] = newer_than
                expected_count -= 1

            response = await web_app_client.get('/v1/calls', params=params)
            assert response.status == 200
            assert len((await response.json())['calls']) == expected_count
            assert (await response.json())[
                'total_calls_count'
            ] == expected_count


async def test_get_calls_newest_first(stq3_context, web_app_client):
    project_slug = 'test_get_calls'

    now = datetime.datetime.now().astimezone()
    deviations_min = [-1, 1]
    calls = [
        common.get_preset_call(
            project_slug, created=now + datetime.timedelta(minutes=deviation),
        )
        for deviation in deviations_min
    ]
    async with stq3_context.pg.master_pool.acquire() as conn:
        await db_models.Call.insert_bulk(stq3_context, conn, calls)

    for newest_first in ['true', 'false', None]:
        params = {
            'project_slug': project_slug,
            'user_id': '34',
            'limit': 10,
            'offset': 0,
        }
        if newest_first:
            params['newest_first'] = newest_first
        response = await web_app_client.get('/v1/calls', params=params)
        assert response.status == 200
        response_json = await response.json()
        assert len(response_json['calls']) == 2
        first_call, second_call = response_json['calls']
        first_call_ts = datetime.datetime.strptime(
            first_call['created'], '%Y-%m-%dT%H:%M:%S.%f%z',
        )
        second_call_ts = datetime.datetime.strptime(
            second_call['created'], '%Y-%m-%dT%H:%M:%S.%f%z',
        )
        if newest_first == 'true':
            assert first_call_ts > second_call_ts
        else:
            assert first_call_ts < second_call_ts


async def test_get_calls_filter_by_direction(stq3_context, web_app_client):
    project_slug = 'test_get_calls'
    directions = ['incoming'] * 2 + ['outgoing']

    calls = [
        common.get_preset_call(
            project_slug, direction=db_models.CallDirection(direction),
        )
        for direction in directions
    ]
    async with stq3_context.pg.master_pool.acquire() as conn:
        await db_models.Call.insert_bulk(stq3_context, conn, calls)

    params = {
        'project_slug': project_slug,
        'user_id': '34',
        'limit': 10,
        'offset': 0,
    }

    response = await web_app_client.get('/v1/calls', params=params)
    assert response.status == 200

    assert len((await response.json())['calls']) == 3
    assert (await response.json())['total_calls_count'] == 3

    for direction in db_models.CallDirection:
        params['direction'] = direction.value
        response = await web_app_client.get('/v1/calls', params=params)
        assert response.status == 200
        if direction == db_models.CallDirection.OUTGOING:
            assert len((await response.json())['calls']) == 1
            assert (await response.json())['total_calls_count'] == 1
        else:
            assert len((await response.json())['calls']) == 2
            assert (await response.json())['total_calls_count'] == 2


async def test_get_calls_limit_offset(stq3_context, web_app_client):
    project_slug = 'test_get_calls'

    now = datetime.datetime.now().astimezone()
    delta = datetime.timedelta(seconds=1)

    calls = [
        common.get_preset_call(
            project_slug, chat_id=str(idx), created=now + idx * delta,
        )
        for idx in range(10)
    ]
    async with stq3_context.pg.master_pool.acquire() as conn:
        await db_models.Call.insert_bulk(stq3_context, conn, calls)

    params = {'project_slug': project_slug, 'user_id': '34', 'limit': 1}
    collected_chat_ids = set()

    for offset in range(10):
        params['offset'] = offset
        response = await web_app_client.get('/v1/calls', params=params)
        assert response.status == 200
        response_json = await response.json()
        assert response_json['total_calls_count'] == 10
        assert len(response_json['calls']) == 1
        collected_chat_ids.add(response_json['calls'][0]['chat_id'])

    assert collected_chat_ids == set(map(str, range(10)))


async def test_get_calls_status_and_statuses(stq3_context, web_app_client):
    project_slug = 'test_get_calls'

    statuses = ['queued'] + ['initiated'] * 2 + ['processing'] * 5 + ['error']

    calls = [
        common.get_preset_call(
            project_slug, status=db_models.CallStatus(status),
        )
        for status in statuses
    ]
    async with stq3_context.pg.master_pool.acquire() as conn:
        await db_models.Call.insert_bulk(stq3_context, conn, calls)

    query_status = 'queued'
    query_statuses = 'initiated,processing'

    for is_single_status in [True, False]:
        for is_multiple_statuses in [True, False]:
            params = {
                'project_slug': project_slug,
                'user_id': '34',
                'limit': 10,
                'offset': 0,
            }
            if is_single_status:
                params['status'] = query_status
            if is_multiple_statuses:
                params['statuses'] = query_statuses
            response = await web_app_client.get('/v1/calls', params=params)
            assert response.status == 200

            response_json = await response.json()
            if is_single_status:
                assert len(response_json['calls']) == 1
                assert response_json['total_calls_count'] == 1
                continue
            if is_multiple_statuses:
                assert len(response_json['calls']) == 7
                assert response_json['total_calls_count'] == 7
                continue
            assert len(response_json['calls']) == 9
            assert response_json['total_calls_count'] == 9


@pytest.mark.parametrize('expose_features', [False, True])
async def test_api_call_result(
        web_context, web_app_client, mockserver, expose_features,
):
    project_slug = 'test' if not expose_features else 'test_features_exposure'
    call_id = '2' if not expose_features else '5'

    @mockserver.json_handler('/supportai-context/v1/contexts/multiple')
    async def _(_):
        return web.json_response(
            data={
                'contexts': [
                    {
                        'created_at': '2021-04-01 10:00:00+03',
                        'chat_id': 'chat2',
                        'records': [
                            {
                                'id': '1',
                                'created_at': '2021-04-01 10:00:00+03',
                                'request': {
                                    'dialog': {
                                        'messages': [
                                            {'text': '', 'author': 'ai'},
                                        ],
                                    },
                                    'features': [
                                        {'key': 'event_type', 'value': 'dial'},
                                    ],
                                },
                                'response': {
                                    'reply': {'text': '1', 'texts': ['1']},
                                },
                            },
                            {
                                'id': '2',
                                'created_at': '2021-04-01 10:02:00+03',
                                'request': {
                                    'dialog': {
                                        'messages': [
                                            {
                                                'text': 'help help help',
                                                'author': 'user',
                                            },
                                        ],
                                    },
                                    'features': [],
                                },
                                'response': {
                                    'reply': {'text': '300', 'texts': ['300']},
                                    'features': {
                                        'probabilities': [],
                                        'features': [
                                            {
                                                'key': 'f_key',
                                                'value': 'f_value',
                                            },
                                        ],
                                    },
                                },
                            },
                        ],
                    },
                ],
                'total': 1,
            },
        )

    response = await web_app_client.get(
        f'/v1/calls/{call_id}/result?project_slug={project_slug}&user_id=34',
    )

    assert response.status == 200

    response_json = await response.json()

    assert response_json['status']
    assert len(response_json['records']) == 2

    assert response_json['records'][0]['answer'] == 'help help help'
    if expose_features:
        assert response_json['features'] == [
            {'key': 'f_key', 'value': 'f_value'},
        ]
    else:
        assert not response_json['features']


async def test_api_call_result_empty(web_context, web_app_client, mockserver):
    @mockserver.json_handler('/supportai-context/v1/contexts/multiple')
    async def _(_):
        return web.json_response(data={'contexts': []})

    response = await web_app_client.get(
        '/v1/calls/2/result?project_slug=test&user_id=34',
    )

    assert response.status == 204


async def test_cancel_calls(
        stq3_context, web_app_client, mock_tasks_handles, create_task,
):
    create_task(id_='3', type_='outgoing_calls_init')

    outgoing_calls = []
    for i in range(10):
        outgoing_calls.append(
            db_models.Call(
                id=-1,
                project_slug='test',
                direction=db_models.CallDirection.OUTGOING,
                call_service=db_models.CallService.IVR_FRAMEWORK,
                task_id='3',
                chat_id=f'does not matter {i}',
                phone='',
                personal_phone_id='',
                features='{}',
                status=db_models.CallStatus.QUEUED,
                created=datetime.datetime.now(),
                has_record=False,
                attempt_number=1,
            ),
        )
    async with stq3_context.pg.master_pool.acquire() as conn:
        await db_models.Call.insert_bulk(stq3_context, conn, outgoing_calls)

    response_cancel = await web_app_client.post(
        'v1/calls/tasks/3/cancel?project_slug=test&user_id=34',
    )
    assert response_cancel.status == 200
    assert (await response_cancel.json()) == {}

    async with stq3_context.pg.slave_pool.acquire() as conn:
        num_cancelled = await db_models.Call.count_by_filters(
            stq3_context,
            conn,
            project_slug='test',
            task_id='3',
            statuses=[db_models.CallStatus.CANCELLED],
        )

    assert num_cancelled == 10


async def test_collect_calls_statistics(
        web_context, web_app_client, mockserver,
):
    @mockserver.json_handler(
        '/supportai-statistics/supportai-statistics'
        '/v1/statistics/calls/general',
    )
    def _(_):
        return {
            'series_total': 550,
            'dials_first_attempt': 281,
            'series_dials': 412,
            'unsuccessful_series': 138,
            'calls_total': 986,
            'calls_dials': 412,
            'no_dial_calls': 574,
            'successful_calls': 191,
            'hangups': 182,
            'silent_hangups': 56,
            'forwarded_calls': 1,
            'errors_during_call': 39,
            'mean_talk_duration': 25,
        }

    response = await web_app_client.get(
        f'/v1/calls/statistics?project_slug=test_statistics&user_id=34',
    )
    assert response.status == 200

    file_content = await response.content.read()
    workbook = openpyxl.load_workbook(io.BytesIO(file_content))
    assert 'Статистика по звонкам' in workbook
    sheet = workbook['Статистика по звонкам']

    content = [(row[0].value, row[1].value) for row in sheet.iter_rows()]
    assert content == [
        ('Статистика по всем звонкам', None),
        ('Всего серий звонков', 550),
        ('Дозвонились с первого раза', 281),
        ('Дозвонились хотя бы раз', 412),
        ('Серия закончилась недозвоном', 138),
        (None, None),
        ('Всего звонков', 986),
        ('Дозвонились', 412),
        ('Не дозвонились', 574),
        ('Звонков успешно завершилось', 191),
        ('Человек положил трубку', 182),
        ('Человек молча положил трубку', 56),
        ('Звонков переведено на оператора', 1),
        ('Звонков завершилось с ошибкой', 39),
        (None, None),
        ('Среднее время разговора, с', 25),
    ]
