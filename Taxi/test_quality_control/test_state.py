# pylint: disable=too-many-lines
import datetime
import http
import json

import freezegun
import pytest

from taxi.util import dates

from quality_control import utils
from test_quality_control import utils as test_utils

URL = '/api/v1/state'
URL_MANY = '/api/v1/state/list'


async def test_init_exam_state(qc_client):
    entity = {'id': '1', 'type': 'driver'}
    exam_code = 'dkvu'
    await test_utils.prepare_entity(qc_client, entity['type'], entity['id'])

    # экзамен сначала не назначен
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    assert state is None

    # проверяем, что также ничего не вернеться c флагом показывать выключенные
    state = await test_utils.check_state(
        qc_client,
        entity['type'],
        entity['id'],
        exam_code=exam_code,
        show_disabled=True,
    )
    assert state is None


async def test_init_second_exam_state(qc_client):
    entity = {'id': '1', 'type': 'driver'}
    await test_utils.prepare_entity(qc_client, entity['type'], entity['id'])

    # Назначаем любой экзамен
    response = await qc_client.post(
        URL,
        params={'type': entity['type'], 'id': entity['id'], 'exam': 'dkvu'},
        json={'present': {'can_pass': True, 'sanctions': ['orders_off']}},
    )
    assert response.status == http.HTTPStatus.OK

    # Проверяем "несуществующий" экзамен
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code='identity',
    )
    assert state is None

    # Проверяем "несуществующий" экзамен с флагом show_disabled
    state = await test_utils.check_state(
        qc_client,
        entity['type'],
        entity['id'],
        exam_code='identity',
        show_disabled=True,
    )
    assert state is None


async def test_hard_call(qc_client, qc_context):
    entity = {'id': '1', 'type': 'driver'}
    exam_code = 'dkvu'
    await test_utils.prepare_entity(qc_client, entity['type'], entity['id'])

    # назначаем стандартное прохождение ДКВУ
    response = await qc_client.post(
        URL,
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={'present': {'can_pass': True, 'sanctions': ['orders_off']}},
    )
    assert response.status == http.HTTPStatus.OK

    # проверяем назначение
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    assert state['code'] == exam_code
    assert 'present' in state
    assert 'past' not in state
    assert 'future' not in state
    assert state['present'].get('sanctions') == ['orders_off']
    assert 'pass' in state['present']

    pass_item = state['present']['pass']
    assert 'id' in pass_item
    assert 'pending' not in pass_item
    assert 'media' in pass_item
    assert [x['code'] for x in pass_item['media']] == ['front', 'back']
    # проверяем, что фильтр по entity_id уже создан для пасса

    await test_utils.check_pass_filter(
        qc_context, pass_item['id'], [dict(field='id', value=entity['id'])],
    )


@pytest.mark.now('2020-01-01T00:00:00')
async def test_soft_call(qc_client, task_current_state):
    entity = {'id': '1', 'type': 'driver'}
    exam_code = 'dkvu'
    await test_utils.prepare_entity(qc_client, entity['type'], entity['id'])

    # назначаем отложенное прохождение ДКВУ
    future_begin_1 = datetime.datetime.utcnow() + datetime.timedelta(minutes=1)
    future_begin_2 = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
    response = await qc_client.post(
        URL,
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={
            'present': {'can_pass': False},
            'future': [
                {'begin': utils.to_string(future_begin_1), 'can_pass': True},
                {
                    'begin': utils.to_string(future_begin_2),
                    'can_pass': True,
                    'sanctions': ['orders_off'],
                },
            ],
        },
    )
    assert response.status == http.HTTPStatus.OK

    # проверяем, что сейчас экзамен сдавать не надо, санкций нет и
    # future будет сразу смотреть на future_begin_2
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    assert state.get('present') is None
    assert state.get('future')
    assert state['future'].get('begin') == utils.to_string(future_begin_2)
    assert state['future'].get('sanctions') == ['orders_off']

    # проверяем, что после begin 1 можно сдавать экзамен,
    # после begin_2 будут санкции
    with freezegun.freeze_time(future_begin_1):
        await task_current_state()

    state_after_begin_1 = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )

    assert state_after_begin_1.get('present')
    assert state_after_begin_1['present'].get('pass')
    assert state_after_begin_1['present'].get('sanctions') is None
    assert state_after_begin_1.get('future')
    assert state_after_begin_1['future'].get('begin') == utils.to_string(
        future_begin_2,
    )
    assert state_after_begin_1['future'].get('sanctions')

    # проверяем, что после begin 2 нужно сдавать экзамен, есть санкции
    with freezegun.freeze_time(future_begin_2):
        await task_current_state()

    state_after_begin_2 = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )

    assert state_after_begin_2.get('present')
    assert state_after_begin_2['present'].get('pass')
    assert state_after_begin_2['present'].get('sanctions')
    assert state_after_begin_2.get('future') is None


async def test_dkvu_with_extra_media(qc_client, qc_cache):
    entity = {'id': '1', 'type': 'driver'}
    exam_code = 'dkvu'
    await test_utils.prepare_entity(qc_client, entity['type'], entity['id'])

    # назначаем прохождение ДКВУ с селфи
    response = await qc_client.post(
        URL,
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={
            'present': {'can_pass': True, 'sanctions': ['orders_off']},
            'pass': {'media': ['front', 'back', 'selfie']},
        },
    )
    assert response.status == http.HTTPStatus.OK

    # проверяем media
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    assert state['present']['pass'].get('media')

    exam_settings = qc_cache.entity_settings(entity['type'])['exams'][
        exam_code
    ]
    for idx, media_code in enumerate(['front', 'back', 'selfie']):
        media_settings = exam_settings['media']['items'][media_code]
        assert state['present']['pass']['media'][idx] == media_settings


async def test_dkvu_media_order(qc_client, qc_cache):
    entity = {'id': '1', 'type': 'driver'}
    exam_code = 'dkvu'
    await test_utils.prepare_entity(qc_client, entity['type'], entity['id'])

    # назначаем прохождение ДКВУ с обратным порядком media
    response = await qc_client.post(
        URL,
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={
            'present': {'can_pass': True, 'sanctions': ['orders_off']},
            'pass': {'media': ['back', 'front']},
        },
    )
    assert response.status == http.HTTPStatus.OK

    # проверяем последовательность media
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    exam_settings = qc_cache.entity_settings(entity['type'])['exams'][
        exam_code
    ]
    for idx, media_code in enumerate(['back', 'front']):
        media_settings = exam_settings['media']['items'][media_code]
        assert state['present']['pass']['media'][idx] == media_settings


async def test_dkk_future(qc_client, task_current_state, qc_cache):
    entity = {'id': '1', 'type': 'driver'}
    exam_code = 'dkk'
    await test_utils.prepare_entity(qc_client, entity['type'], entity['id'])

    # назначаем прохождение ДКК
    response = await qc_client.post(
        URL,
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={'present': {'can_pass': True, 'sanctions': ['orders_off']}},
    )
    assert response.status == http.HTTPStatus.OK
    # проверяем состояние: только present
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    assert state.get('present') and state.get('future') is None

    # отправляем фотки
    await test_utils.send_fake(qc_client, state)

    # проверяем состояние сейчас: только future
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    pass_date = dates.parse_timestring(state['modified'], 'UTC')

    assert state.get('present')
    assert state.get('future') is None
    assert state['present'].get('sanctions') is None
    assert state['present'].get('pass', {}).get('pending')

    # планируем future
    with freezegun.freeze_time(pass_date):
        future1_delta = dates.parse_duration_string('9d12h')
        future2_delta = dates.parse_duration_string('12h')

        await test_utils.schedule_future(
            qc_client,
            entity['type'],
            entity['id'],
            exam_code,
            ['orders_off'],
            future1_delta,
            future2_delta,
        )

    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )

    future_begin = dates.parse_timestring(state['future']['begin'], 'UTC')
    assert state['future'].get('sanctions') == ['orders_off']
    assert future_begin == pass_date + future1_delta + future2_delta

    # резолвим проверку
    response = await qc_client.post(
        '/api/v1/pass/resolve',
        params={
            'type': entity['type'],
            'id': entity['id'],
            'pass_id': state['present']['pass']['id'],
        },
        json={'status': 'SUCCESS'},
    )
    assert response.status == http.HTTPStatus.OK

    # снова проверяем состояние сейчас: past и future
    # все пройдено
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    assert state.get('present') is None
    assert state.get('past') and state.get('future')

    future_begin = dates.parse_timestring(state['future']['begin'], 'UTC')
    assert state['future'].get('sanctions') == ['orders_off']
    assert future_begin == pass_date + future1_delta + future2_delta

    # проверяем след. состояние: past, present и future
    # можно проходить экзамен, скоро блокировка
    with freezegun.freeze_time(pass_date + future1_delta):
        await task_current_state()

    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    assert state.get('present') and state.get('future')
    assert state['present'].get('sanctions') is None
    assert state['present'].get('pass', {}).get('media')
    assert state['future'].get('sanctions') == ['orders_off']

    # проверяем след. состояние: только present, нужно проходить экзамен,
    # блокировка
    with freezegun.freeze_time(future_begin):
        await task_current_state()

    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    assert state.get('present') and state.get('future') is None
    assert state['present'].get('sanctions') == ['orders_off']
    assert state['present'].get('pass', {}).get('media')


@pytest.mark.now('2020-01-01T00:00:00')
async def test_dkk_future_not_set(qc_client, task_current_state):
    entity = {'id': '1', 'type': 'driver'}
    exam_code = 'dkk'

    await test_utils.prepare_entity(qc_client, entity['type'], entity['id'])

    # назначаем прохождение ДКК
    response = await qc_client.post(
        URL,
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={'present': {'can_pass': True, 'sanctions': ['orders_off']}},
    )
    assert response.status == http.HTTPStatus.OK
    # проверяем состояние: только present
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    assert state.get('present') and state.get('future') is None

    # отправляем фотки
    await test_utils.send_fake(qc_client, state)

    # проверяем состояние сейчас: только present
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    assert state.get('present') and state.get('future') is None
    assert state['present'].get('sanctions') is None
    assert state['present'].get('pass', {}).get('pending')

    # резолвим проверку
    response = await qc_client.post(
        '/api/v1/pass/resolve',
        params={
            'type': entity['type'],
            'id': entity['id'],
            'pass_id': state['present']['pass']['id'],
        },
        json={'status': 'SUCCESS'},
    )
    assert response.status == http.HTTPStatus.OK

    # снова проверяем состояние сейчас: past
    # все пройдено
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    assert state.get('present') is None
    assert state.get('future') is None
    assert state.get('past')

    future_begin_1 = datetime.datetime.utcnow() + datetime.timedelta(hours=12)
    future_begin_2 = datetime.datetime.utcnow() + datetime.timedelta(hours=13)
    # устанавливаем future через schedule
    response = await qc_client.post(
        '/api/v1/schedule',
        params={
            'type': entity['type'],
            'id': entity['id'],
            'exam': exam_code,
            'modified': state.get('modified'),
        },
        json={
            'future': [
                {'begin': utils.to_string(future_begin_1), 'can_pass': True},
                {
                    'begin': utils.to_string(future_begin_2),
                    'can_pass': True,
                    'sanctions': ['orders_off'],
                },
            ],
        },
    )
    assert response.status == http.HTTPStatus.OK

    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    assert state.get('present') is None
    assert state.get('past') and state.get('future')

    future_begin = dates.parse_timestring(state['future']['begin'], 'UTC')
    assert state['future'].get('sanctions') == ['orders_off']
    assert future_begin == future_begin_2

    # проверяем след. состояние: past, present и future
    # можно проходить экзамен, скоро блокировка
    with freezegun.freeze_time(future_begin_1):
        await task_current_state()

    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    assert state.get('present') and state.get('future')
    assert state['present'].get('sanctions') is None
    assert state['present'].get('pass', {}).get('media')
    assert state['future'].get('sanctions') == ['orders_off']

    # проверяем след. состояние: только present, нужно проходить экзамен,
    # блокировка
    with freezegun.freeze_time(future_begin_2):
        await task_current_state()

    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    assert state.get('present') and state.get('future') is None
    assert state['present'].get('sanctions') == ['orders_off']
    assert state['present'].get('pass', {}).get('media')


async def test_enable_on_without_state(qc_client):
    entity = {'id': '1', 'type': 'driver'}
    exam_code = 'dkvu'
    await test_utils.prepare_entity(qc_client, entity['type'], entity['id'])

    # включаем экзамен без установки состояния
    response = await qc_client.post(
        URL,
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={'enabled': True},
    )
    assert response.status == http.HTTPStatus.OK

    # проверяем состояние
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    assert (state or {}).get('present')
    assert state['present'].get('sanctions') == ['orders_off']
    assert state['present'].get('pass')
    assert state['present']['pass'].get('id')
    assert [x['code'] for x in state['present']['pass'].get('media', [])] == [
        'front',
        'back',
    ]


async def test_enable_off_when_not_passed(qc_client):
    entity = {'id': '1', 'type': 'driver'}
    exam_code = 'dkvu'
    await test_utils.prepare_entity(qc_client, entity['type'], entity['id'])

    # назначаем стандартное прохождение ДКВУ
    response = await qc_client.post(
        URL,
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={'present': {'can_pass': True, 'sanctions': ['orders_off']}},
    )
    assert response.status == http.HTTPStatus.OK
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )

    # сейчас назначена проверка, есть тест на это
    pass_id = state['present']['pass']['id']

    # теперь отменяем экзамен
    response = await qc_client.post(
        URL,
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={'enabled': False},
    )
    assert response.status == http.HTTPStatus.OK

    # экзамен должен быть выключен
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    assert state is None

    # включаем экзамен обратно
    response = await qc_client.post(
        URL,
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={'enabled': True},
    )
    assert response.status == http.HTTPStatus.OK

    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )

    assert state['present']['pass'].get('id') == pass_id


async def test_enable_off_when_passed(qc_client):
    entity = {'id': '1', 'type': 'driver'}
    exam_code = 'dkvu'
    await test_utils.prepare_entity(qc_client, entity['type'], entity['id'])

    # устанавливаем ДКВУ пройденным
    response = await qc_client.post(
        URL,
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={'present': {'can_pass': False}},
    )
    assert response.status == http.HTTPStatus.OK
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )

    # проверки нет, санкций нет
    assert state.get('present') is None

    # выключаем экзамен
    response = await qc_client.post(
        URL,
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={'enabled': False},
    )
    assert response.status == http.HTTPStatus.OK

    # экзамен должен быть выключен
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    assert state is None

    # включаем экзамен обратно
    response = await qc_client.post(
        URL,
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={'enabled': True},
    )
    assert response.status == http.HTTPStatus.OK

    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )

    # снова проверки нет, санкций нет
    assert state.get('present') is None


async def test_enable_off_update(qc_client):
    entity = {'id': '1', 'type': 'driver'}
    exam_code = 'dkvu'
    await test_utils.prepare_entity(qc_client, entity['type'], entity['id'])

    # устанавливаем ДКВУ пройденным
    response = await qc_client.post(
        URL,
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={'present': {'can_pass': False}},
    )
    assert response.status == http.HTTPStatus.OK

    # проверки нет, санкций нет
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    assert state.get('present') is None

    # выключаем экзамен
    response = await qc_client.post(
        URL,
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={'enabled': False},
    )
    assert response.status == http.HTTPStatus.OK

    # сбрасываем прохождение, но оставляем выключенным
    response = await qc_client.post(
        URL,
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={
            'enabled': False,
            'present': {'can_pass': True, 'sanctions': ['orders_off']},
        },
    )
    assert response.status == http.HTTPStatus.OK

    # экзамен еще выключен
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    assert state is None

    # включаем экзамен и проверяем санкции
    response = await qc_client.post(
        URL,
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={'enabled': True},
    )
    assert response.status == http.HTTPStatus.OK

    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    assert state['present'].get('pass')
    assert state['present'].get('sanctions') == ['orders_off']


@pytest.mark.ticked_time
async def test_modified_after_enable(qc_client):
    entity = {'id': '1', 'type': 'driver'}
    exam_code = 'dkk'
    await test_utils.prepare_entity(qc_client, entity['type'], entity['id'])
    # назначаем стандартное прохождение ДКК
    response = await qc_client.post(
        URL,
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={'present': {'can_pass': True, 'sanctions': ['orders_off']}},
    )
    assert response.status == http.HTTPStatus.OK

    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    first_modified = dates.parse_timestring(state['modified'], 'UTC')
    assert first_modified

    # отключаем экзамен
    response = await qc_client.post(
        URL,
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={'enabled': False},
    )
    assert response.status == http.HTTPStatus.OK

    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    assert state is None

    # включаем снова
    response = await qc_client.post(
        URL,
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={'enabled': True},
    )
    assert response.status == http.HTTPStatus.OK

    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    second_modified = dates.parse_timestring(state['modified'], 'UTC')
    assert second_modified > first_modified


async def test_null_state(qc_client):
    entity = {'id': '1', 'type': 'driver'}
    exam_code = 'dkvu'
    await test_utils.prepare_entity(qc_client, entity['type'], entity['id'])

    # enabled = false
    response = await qc_client.post(
        URL,
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json=json.loads(
            '{"enabled": false, "present": null, "future":null, "pass": null}',
        ),
    )
    assert response.status == http.HTTPStatus.OK

    # enabled = true
    response = await qc_client.post(
        URL,
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json=json.loads(
            '{"enabled": true, "present": null, "future":null, "pass": null}',
        ),
    )
    assert response.status == http.HTTPStatus.OK


async def test_state_reason(qc_client):
    entity = {'id': '1', 'type': 'driver'}
    exam_code = 'dkvu'
    await test_utils.prepare_entity(qc_client, entity['type'], entity['id'])

    # назначаем стандартное ДКВУ с reason
    reason = {
        'code': 'code1',
        'source': 'source1',
        'login': 'login1',
        'comment': 'Test1',
        'number': 'number1',
    }
    response = await qc_client.post(
        'api/v1/state',
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={
            'present': {'can_pass': True, 'sanctions': ['orders_off']},
            'reason': reason,
        },
    )
    assert response.status == http.HTTPStatus.OK

    # Проверяем state
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )

    assert state['present'].get('reason') == reason


async def test_stale_media(qc_client, qc_cache):
    entity = {'id': '1', 'type': 'driver'}
    await test_utils.prepare_entity(qc_client, entity['type'], entity['id'])

    exam_code = 'dkvu'
    exam_settings = qc_cache.entity_settings(entity['type'])['exams'][
        exam_code
    ]

    # назначаем стандартное прохождение ДКВУ
    response = await qc_client.post(
        URL,
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={'present': {'can_pass': True, 'sanctions': ['orders_off']}},
    )
    assert response.status == http.HTTPStatus.OK

    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )

    assert [
        x['code']
        for x in state.get('present', {}).get('pass', {}).get('media', [])
    ] == exam_settings['media']['default']

    # загрузим только 1 медиа
    media_to_load = state['present']['pass']['media'][:1]
    media_to_skip = state['present']['pass']['media'][1:]
    state['present']['pass']['media'] = media_to_load
    await test_utils.send_fake(qc_client, state)

    # Проверяем, что загрузили
    state_now = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )

    modified = next(
        iter(
            dates.parse_timestring(x['loaded'], 'UTC')
            for x in state_now['present']['pass']['media']
        ),
        None,
    )
    media_stale = dates.parse_duration_string(exam_settings['media']['stale'])
    with freezegun.freeze_time(modified + media_stale):
        state_future = await test_utils.check_state(
            qc_client, entity['type'], entity['id'], exam_code=exam_code,
        )

    loaded_media = next(iter(media_to_load), None)
    media_now = dict(
        (x['code'], x) for x in state_now['present']['pass']['media']
    )
    media_future = dict(
        (x['code'], x) for x in state_future['present']['pass']['media']
    )

    assert loaded_media
    assert media_now.get(loaded_media['code'], {}).get('loaded')
    assert media_future.get(loaded_media['code'], {}).get('loaded') is None

    # Загружаем остальные фотки через время stale => не переходим в PENDING
    with freezegun.freeze_time(modified + media_stale):
        state['present']['pass']['media'] = media_to_skip
        await test_utils.send_fake(qc_client, state)

    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )

    assert state['present']['pass'].get('pending') is None
    assert all('loaded' in x for x in state['present']['pass']['media'])

    # Загружаем остальные фотки сейчас => переходим в PENDING
    state['present']['pass']['media'] = media_to_skip
    await test_utils.send_fake(qc_client, state)

    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )

    assert state['present']['pass'].get('pending')
    assert state['present']['pass'].get('media', []) == []


async def test_old_flow(qc_client):
    entity = {'id': '1', 'type': 'driver'}
    response = await qc_client.post(
        '/api/v1/data',
        params={'type': entity['type'], 'id': entity['id'], 'flow': 'old'},
        json={'park_id': '1'},
    )
    assert response.status == http.HTTPStatus.OK

    exam_code = 'dkvu'
    # назначаем стандартное прохождение ДКВУ
    response = await qc_client.post(
        URL,
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={'present': {'can_pass': True, 'sanctions': ['orders_off']}},
    )
    assert response.status == http.HTTPStatus.OK

    # проверяем состояние по старому flow
    response = await qc_client.get(
        '/api/v1/state',
        params={
            'type': entity['type'],
            'id': entity['id'],
            'exam': exam_code,
            'flow': 'old',
        },
    )
    assert response.status == http.HTTPStatus.OK
    result = await response.json()
    assert len(result.get('items', [])) == 1

    exam_state = result['items'][0]
    assert exam_state.get('id') == entity['id']
    assert exam_state.get('type') == entity['type']
    assert len(exam_state.get('exams', [])) == 1


async def test_old_flow_by_default(qc_client):
    entity = {'id': '1', 'type': 'driver'}
    exam_code = 'dkvu'
    await test_utils.prepare_entity(qc_client, entity['type'], entity['id'])

    response = await qc_client.get(
        '/api/v1/state',
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
    )

    result = await response.json()
    assert len(result.get('items', [])) == 1


async def test_enabled_in_state_one(qc_client):
    entity = {'id': '1', 'type': 'driver'}
    await test_utils.prepare_entity(qc_client, entity['type'], entity['id'])

    exam_code = 'dkk'
    # вызываем на ДКК
    await test_utils.prepare_exam(
        qc_client,
        entity['type'],
        entity['id'],
        exam_code,
        test_utils.STATES.CALL,
    )
    state_enabled = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code, show_disabled=True,
    )
    assert state_enabled
    assert state_enabled.get('enabled') is True
    assert state_enabled.get('code') == exam_code
    assert state_enabled.get('present')

    state_default = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code,
    )
    assert state_default
    assert state_default.get('enabled') is None
    assert state_default.get('code') == exam_code
    assert state_default.get('present')

    # выключаем на ДКК
    await test_utils.prepare_exam(
        qc_client,
        entity['type'],
        entity['id'],
        exam_code,
        test_utils.STATES.DISABLE,
    )

    state_disabled = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code, show_disabled=True,
    )
    assert state_disabled
    assert state_disabled.get('enabled') is False
    assert state_disabled.get('code') == exam_code
    assert state_disabled.get('present')

    state_default = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code,
    )
    assert state_default is None


@pytest.mark.dontfreeze
async def test_enabled_in_state_many(qc_client):
    entity_jack = {'id': '1', 'type': 'driver'}
    entity_alice = {'id': '2', 'type': 'driver'}
    await test_utils.prepare_entity(
        qc_client, entity_jack['type'], entity_jack['id'],
    )
    await test_utils.prepare_entity(
        qc_client, entity_alice['type'], entity_alice['id'],
    )

    exam_code = 'dkk'
    # вызываем на ДКК
    await test_utils.prepare_exam(
        qc_client,
        entity_jack['type'],
        entity_jack['id'],
        exam_code,
        test_utils.STATES.CALL,
    )
    await test_utils.prepare_exam(
        qc_client,
        entity_alice['type'],
        entity_alice['id'],
        exam_code,
        test_utils.STATES.CALL,
    )

    states_enabled = await test_utils.check_states(
        qc_client, 'driver', exam_code, True,
    )
    assert len(states_enabled.get('items', [])) == 2
    for item in states_enabled['items']:
        assert len(item.get('exams', [])) == 1
        assert item['exams'][0].get('code') == exam_code
        assert item['exams'][0].get('enabled') is True
        assert item['exams'][0].get('present')

    states_default = await test_utils.check_states(
        qc_client, 'driver', exam_code,
    )
    assert len(states_default.get('items', [])) == 2
    for item in states_default['items']:
        assert len(item.get('exams', [])) == 1
        assert item['exams'][0].get('code') == exam_code
        assert item['exams'][0].get('enabled') is None
        assert item['exams'][0].get('present')

    # выключаем ДКК
    await test_utils.prepare_exam(
        qc_client,
        entity_jack['type'],
        entity_jack['id'],
        exam_code,
        test_utils.STATES.DISABLE,
    )
    await test_utils.prepare_exam(
        qc_client,
        entity_alice['type'],
        entity_alice['id'],
        exam_code,
        test_utils.STATES.DISABLE,
    )

    states_disabled = await test_utils.check_states(
        qc_client, 'driver', exam_code, True,
    )
    assert len(states_disabled.get('items', [])) == 2
    for item in states_disabled['items']:
        assert len(item.get('exams', [])) == 1
        assert item['exams'][0].get('code') == exam_code
        assert item['exams'][0].get('enabled') is False
        assert item['exams'][0].get('present')

    states_default = await test_utils.check_states(
        qc_client, 'driver', exam_code,
    )
    assert len(states_default.get('items', [])) == 2
    for item in states_default['items']:
        assert not item.get('exams')


@pytest.mark.parametrize('delay, sanctions', [(9, None), (15, ['orders_off'])])
async def test_block_release(qc_client, delay, sanctions, task_current_state):
    """
    В тесте назначается 2 будущих состояния: одно - after_pass,
    другое - after_resolve. После этого первый тест ждёт наступления первого
    состояния, а второй - второго. Далее отправляются фото и проверяется,
    что в первом случае (after_pass) мы сразу получили ок, а во втором
    случае ок не получен и висят санкции.
    """
    entity = {'id': '1', 'type': 'driver'}
    exam_code = 'dkvu'
    await test_utils.prepare_entity(qc_client, entity['type'], entity['id'])

    # назначаем ДКВУ с двумя состояниями в будущем
    future_begin_1 = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
    future_begin_2 = datetime.datetime.utcnow() + datetime.timedelta(hours=15)
    response = await qc_client.post(
        URL,
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={
            'present': {
                'can_pass': True,
                'sanctions': ['orders_off'],
                'release': 'after_pass',
            },
            'future': [
                {
                    'begin': utils.to_string(future_begin_1),
                    'can_pass': True,
                    'release': 'after_pass',
                },
                {
                    'begin': utils.to_string(future_begin_2),
                    'can_pass': True,
                    'sanctions': ['orders_off'],
                    'release': 'after_resolve',
                },
            ],
        },
    )
    assert response.status == http.HTTPStatus.OK

    # отправку фото делаем спустя delay_time
    delay_time = datetime.datetime.utcnow() + datetime.timedelta(
        hours=delay, minutes=10,
    )
    with freezegun.freeze_time(delay_time):
        await task_current_state()

    # Отправляем фотки
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    await test_utils.send_fake(qc_client, state)

    # Проверяем блокировки или их отсутствие
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    assert state['present']['pass'].get('id')
    assert state['present']['pass'].get('pending')
    assert state['present'].get('sanctions') == sanctions


async def test_media_settings(qc_client, qc_cache):
    media_settings = {
        'some_id': 12345,
        'mask_code': 'rectangle_mask',
        'orientation': 'landscape',
        'frame_processor': {'type': 'face', 'settings_id': 'biometry_base'},
    }

    entity = {'id': '1', 'type': 'driver'}
    exam_code = 'dkk'

    # обновляем настройки медиа в кэше
    exam_settings = qc_cache.entity_settings(entity['type'])['exams'][
        exam_code
    ]
    exam_settings['media']['items']['front']['settings'] = media_settings

    await test_utils.prepare_entity(qc_client, entity['type'], entity['id'])

    # назначаем прохождение ДКК
    response = await qc_client.post(
        URL,
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={'present': {'can_pass': True, 'sanctions': ['orders_off']}},
    )
    assert response.status == http.HTTPStatus.OK

    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )

    # должны вернуться точно такие-же настройки медиа, которые лежали в кэше
    front_settings = [
        x for x in state['present']['pass']['media'] if x['code'] == 'front'
    ]
    assert len(front_settings) == 1

    assert front_settings[0]['settings'] == media_settings
