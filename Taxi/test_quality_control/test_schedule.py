import datetime
import http

import freezegun
import pytest

from taxi.util import dates

from quality_control import consts
from quality_control import utils
from test_quality_control import utils as test_utils


@pytest.mark.now('2020-01-01T00:00:00')
async def test_dkk_future(qc_client):
    entity = {'id': '1', 'type': 'driver'}
    exam_code = 'dkk'
    await test_utils.prepare_entity(qc_client, entity['type'], entity['id'])

    # назначаем прохождение ДКК
    response = await qc_client.post(
        'api/v1/state',
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={'present': {'can_pass': True, 'sanctions': ['orders_off']}},
    )
    assert response.status == http.HTTPStatus.OK

    future = datetime.datetime.utcnow() + datetime.timedelta(hours=12)

    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code,
    )
    # отправляем фотки
    await test_utils.send_fake(qc_client, state)

    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code,
    )

    assert state.get('present')
    assert state.get('future') is None

    mistake_future = datetime.datetime.utcnow() - datetime.timedelta(hours=1)
    # устанавливаем future через schedule

    response = await qc_client.post(
        '/api/v1/schedule',
        params={
            'type': entity['type'],
            'id': entity['id'],
            'exam': exam_code,
            'modified': state['modified'],
        },
        json={
            'future': [
                {
                    'begin': utils.to_string(mistake_future),
                    'can_pass': True,
                    'sanctions': ['orders_off'],
                },
            ],
        },
    )

    # нельзя установить future в прошлое
    assert response.status == http.HTTPStatus.BAD_REQUEST

    # устанавливаем future через schedule
    response = await qc_client.post(
        '/api/v1/schedule',
        params={
            'type': entity['type'],
            'id': entity['id'],
            'exam': exam_code,
            'modified': state['modified'],
        },
        json={
            'future': [
                {
                    'begin': utils.to_string(future),
                    'can_pass': True,
                    'sanctions': ['orders_off', 'dkk_comfort_off'],
                },
            ],
        },
    )

    assert response.status == http.HTTPStatus.OK

    # проверяем состояние сейчас
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )

    assert state.get('present') and state.get('future')
    future_begin = dates.parse_timestring(state['future']['begin'], 'UTC')
    assert set(state['future'].get('sanctions')) == {
        'orders_off',
        'dkk_comfort_off',
    }
    assert future_begin == future


async def test_pass_after_schedule(qc_client, task_current_state):
    entity = {'id': '1', 'type': 'driver'}
    exam_code = 'dkk'
    await test_utils.prepare_entity(qc_client, entity['type'], entity['id'])

    # назначаем ДКК пройденным
    response = await qc_client.post(
        'api/v1/state',
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={'present': {'can_pass': True}},
    )
    assert response.status == http.HTTPStatus.OK

    # загружаем media и ставим резолюцию
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    await test_utils.send_fake(qc_client, state)
    response = await qc_client.post(
        '/api/v1/pass/resolve',
        params={
            'type': entity['type'],
            'id': entity['id'],
            'pass_id': state['present']['pass']['id'],
        },
        json={'status': consts.RESOLUTION_SUCCESS},
    )
    assert response.status == http.HTTPStatus.OK

    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )

    # устанавливаем future через schedule
    future = datetime.datetime.utcnow() + datetime.timedelta(hours=12)

    response = await qc_client.post(
        '/api/v1/schedule',
        params={
            'type': entity['type'],
            'id': entity['id'],
            'exam': exam_code,
            'modified': state['modified'],
        },
        json={
            'future': [
                {
                    'begin': utils.to_string(future),
                    'can_pass': True,
                    'sanctions': ['orders_off'],
                },
            ],
        },
    )
    assert response.status == http.HTTPStatus.OK

    # наступает future
    with freezegun.freeze_time(future):
        await task_current_state()

    # проверяем состояние
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    assert state.get('present')
    assert state['present'].get('pass', {}).get('id')
    assert state['present'].get('pass', {}).get('pending') is None

    # загружаем media
    await test_utils.send_fake(qc_client, state)

    # проверяем состояние
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    assert state['present'].get('pass', {}).get('pending')


@pytest.mark.ticked_time
async def test_dkk_modified_change(qc_client):
    entity = {'id': '1', 'type': 'driver'}
    exam_code = 'dkk'
    await test_utils.prepare_entity(qc_client, entity['type'], entity['id'])

    # назначаем ДКК пройденным
    response = await qc_client.post(
        'api/v1/state',
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={'present': {'can_pass': True}},
    )
    assert response.status == http.HTTPStatus.OK

    # загружаем media и ставим резолюцию
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    await test_utils.send_fake(qc_client, state)

    # получаем время загрузки фоток
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    load_modified_date = dates.parse_timestring(state['modified'], 'UTC')

    response = await qc_client.post(
        '/api/v1/pass/resolve',
        params={
            'type': entity['type'],
            'id': entity['id'],
            'pass_id': state['present']['pass']['id'],
        },
        json={'status': consts.RESOLUTION_SUCCESS},
    )
    assert response.status == http.HTTPStatus.OK

    # получаем время резолюции
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    resolve_modified_date = dates.parse_timestring(state['modified'], 'UTC')

    # устанавливаем future через schedule
    future = datetime.datetime.utcnow() + datetime.timedelta(hours=12)
    response = await qc_client.post(
        '/api/v1/schedule',
        params={
            'type': entity['type'],
            'id': entity['id'],
            'exam': exam_code,
            'modified': state['modified'],
        },
        json={
            'future': [
                {
                    'begin': utils.to_string(future),
                    'can_pass': True,
                    'sanctions': ['orders_off'],
                },
            ],
        },
    )
    assert response.status == http.HTTPStatus.OK

    # получаем время после планирования future
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    future_modified_date = dates.parse_timestring(state['modified'], 'UTC')

    # resolve_modified_date НЕ должен изениться т.к.
    # экзамен с release: AFTER_PASS
    assert load_modified_date == resolve_modified_date
    assert resolve_modified_date < future_modified_date


@pytest.mark.ticked_time
async def test_dkvu_modified_change(qc_client):
    entity = {'id': '1', 'type': 'driver'}
    exam_code = 'dkvu'
    await test_utils.prepare_entity(qc_client, entity['type'], entity['id'])

    # назначаем ДКК пройденным
    response = await qc_client.post(
        'api/v1/state',
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={'present': {'can_pass': True}},
    )
    assert response.status == http.HTTPStatus.OK

    # загружаем media и ставим резолюцию
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    await test_utils.send_fake(qc_client, state)

    # получаем время загрузки фоток
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    load_modified_date = dates.parse_timestring(state['modified'], 'UTC')

    response = await qc_client.post(
        '/api/v1/pass/resolve',
        params={
            'type': entity['type'],
            'id': entity['id'],
            'pass_id': state['present']['pass']['id'],
        },
        json={'status': consts.RESOLUTION_SUCCESS},
    )
    assert response.status == http.HTTPStatus.OK

    # получаем время резолюции
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    resolve_modified_date = dates.parse_timestring(state['modified'], 'UTC')

    # устанавливаем future через schedule
    future = datetime.datetime.utcnow() + datetime.timedelta(hours=12)
    response = await qc_client.post(
        '/api/v1/schedule',
        params={
            'type': entity['type'],
            'id': entity['id'],
            'exam': exam_code,
            'modified': state['modified'],
        },
        json={
            'future': [
                {
                    'begin': utils.to_string(future),
                    'can_pass': True,
                    'sanctions': ['orders_off'],
                },
            ],
        },
    )
    assert response.status == http.HTTPStatus.OK

    # получаем время после планирования future
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    future_modified_date = dates.parse_timestring(state['modified'], 'UTC')

    # resolve_modified_date должен изениться т.к.
    # экзамен с release: AFTER_RESOLVE
    assert load_modified_date < resolve_modified_date
    assert resolve_modified_date < future_modified_date
