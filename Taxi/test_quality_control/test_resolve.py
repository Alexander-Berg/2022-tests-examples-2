# pylint: disable=too-many-lines
import datetime
import http

import freezegun

from taxi.util import dates

from quality_control import consts
from test_quality_control import utils as test_utils


async def test_upload(qc_client):
    entity = {'id': '1', 'type': 'driver'}
    exam_code = 'dkvu'
    await test_utils.prepare_entity(qc_client, entity['type'], entity['id'])

    # назначаем стандартное прохождение ДКВУ
    response = await qc_client.post(
        'api/v1/state',
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={
            'present': {
                'can_pass': True,
                'sanctions': [consts.BLOCK_ORDERS_OFF],
            },
        },
    )
    assert response.status == http.HTTPStatus.OK

    # проверяем назначение
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    assert 'media' in state['present']['pass']

    # загружаем media
    await test_utils.send_fake(qc_client, state)

    # проверяем состояние
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    assert 'pending' in state['present']['pass']
    assert 'media' not in state['present']['pass']

    reason = {'text': 'Плохие фото'}
    identity = {'login': 'test'}
    # резолвим FALSE
    response = await qc_client.post(
        '/api/v1/pass/resolve',
        params={
            'type': entity['type'],
            'id': entity['id'],
            'pass_id': state['present']['pass']['id'],
        },
        json={
            'status': consts.RESOLUTION_FAIL,
            'reason': reason,
            'identity': identity,
        },
    )
    assert response.status == http.HTTPStatus.OK

    # проверяем повторное назначение
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    assert 'media' in state['present']['pass']
    assert 'sanctions' in state['present']
    assert state['present'].get('sanctions') == [consts.BLOCK_ORDERS_OFF]
    assert state['past'].get('resolution') == consts.RESOLUTION_FAIL
    assert state['present'].get('reason') == reason
    assert state['present'].get('identity') == identity


async def test_bad_media(qc_client):
    entity = {'id': '1', 'type': 'driver'}
    exam_code = 'dkvu'
    await test_utils.prepare_entity(qc_client, entity['type'], entity['id'])

    # назначаем стандартное прохождение ДКВУ
    response = await qc_client.post(
        'api/v1/state',
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={
            'present': {
                'can_pass': True,
                'sanctions': [consts.BLOCK_ORDERS_OFF],
            },
        },
    )
    assert response.status == http.HTTPStatus.OK
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )

    pass_item = state['present']['pass']
    await test_utils.send_fake(qc_client, state)

    # частично резолвим
    reason = {'text': 'Плохие фото'}
    identity = {'login': 'test'}
    response = await qc_client.post(
        '/api/v1/pass/resolve',
        params={
            'type': entity['type'],
            'id': entity['id'],
            'pass_id': pass_item['id'],
        },
        json={
            'status': consts.RESOLUTION_FAIL,
            'reason': reason,
            'identity': identity,
            'media': [{'status': consts.RESOLUTION_FAIL, 'code': 'front'}],
        },
    )
    assert response.status == http.HTTPStatus.OK

    # Проверяем sate
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    assert 'past' in state
    assert state['past'].get('id') == pass_item['id']
    assert state['past'].get('resolution') == consts.RESOLUTION_FAIL
    assert 'present' in state
    assert state['present'].get('sanctions') == [consts.BLOCK_ORDERS_OFF]
    assert state['present'].get('reason') == reason
    assert state['present'].get('identity') == identity
    media_codes = [x['code'] for x in state['present']['pass']['media']]
    assert media_codes == ['front']


async def test_repass_one_media(qc_client):
    entity = {'id': '1', 'type': 'driver'}
    exam_code = 'dkvu'
    await test_utils.prepare_entity(qc_client, entity['type'], entity['id'])

    # назначаем ДКВУ с 1-й фоткой
    response = await qc_client.post(
        'api/v1/state',
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={
            'present': {
                'can_pass': True,
                'sanctions': [consts.BLOCK_ORDERS_OFF],
            },
            'pass': {'media': ['front']},
        },
    )
    assert response.status == http.HTTPStatus.OK

    # Проверяем state
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )

    pass_item = state['present']['pass']
    assert [x['code'] for x in pass_item['media']] == ['front']
    await test_utils.send_fake(qc_client, state)

    # Резолвим в статусе FAIL
    response = await qc_client.post(
        '/api/v1/pass/resolve',
        params={
            'type': entity['type'],
            'id': entity['id'],
            'pass_id': pass_item['id'],
        },
        json={'status': consts.RESOLUTION_FAIL, 'reason': 'Плохие фото'},
    )
    assert response.status == http.HTTPStatus.OK

    # Проверяем state
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )

    pass_item = state['present']['pass']
    assert [x['code'] for x in pass_item['media']] == ['front']


async def test_resolve_with_null(qc_client):
    entity = {'id': '1', 'type': 'driver'}
    exam_code = 'dkvu'
    await test_utils.prepare_entity(qc_client, entity['type'], entity['id'])

    # назначаем стандартное прохождение ДКВУ
    response = await qc_client.post(
        'api/v1/state',
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={
            'present': {
                'can_pass': True,
                'sanctions': [consts.BLOCK_ORDERS_OFF],
            },
        },
    )
    assert response.status == http.HTTPStatus.OK

    # проверяем назначение
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )

    # загружаем media
    await test_utils.send_fake(qc_client, state)

    # резолвим SUCCESS
    response = await qc_client.post(
        '/api/v1/pass/resolve',
        params={
            'type': entity['type'],
            'id': entity['id'],
            'pass_id': state['present']['pass']['id'],
        },
        json={
            'status': 'SUCCESS',
            'reason': None,
            'media': None,
            'data': None,
        },
    )
    assert response.status == http.HTTPStatus.OK

    # Проверяем state
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )

    assert state.get('present') is None
    assert state.get('past')
    assert state['past'].get('reason') is None
    assert state['past'].get('resolution') == consts.RESOLUTION_SUCCESS


async def test_stale_pass_when_passed(qc_client, qc_cache, task_stale_pass):
    entity = {'id': '1', 'type': 'driver'}
    exam_code = 'dkk'
    await test_utils.prepare_entity(qc_client, entity['type'], entity['id'])

    # назначаем стандартное прохождение ДКК
    response = await qc_client.post(
        'api/v1/state',
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={
            'present': {
                'can_pass': True,
                'sanctions': [consts.BLOCK_ORDERS_OFF],
            },
        },
    )
    assert response.status == http.HTTPStatus.OK

    # проверяем назначение
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    # загружаем media
    await test_utils.send_fake(qc_client, state)
    # планируем future
    await test_utils.schedule_future(
        qc_client,
        entity['type'],
        entity['id'],
        exam_code,
        [consts.BLOCK_ORDERS_OFF],
    )

    # проверяем назначение
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    assert state['present']['pass'].get('pending')
    assert state['present']['pass'].get('id')
    assert state['present'].get('sanctions') is None
    assert state.get('past') is None
    assert state.get('future')

    pass_id = state['present']['pass']['id']
    pending_time = dates.parse_timestring(
        state['present']['pass']['pending'], 'UTC',
    )

    exam_settings = qc_cache.entity_settings(entity['type'])['exams'][
        exam_code
    ]
    stale_time = pending_time + dates.parse_duration_string(
        exam_settings['pass']['stale'],
    )

    # проверяем состояние до истечения срока проверки
    with freezegun.freeze_time(stale_time - datetime.timedelta(seconds=1)):
        await task_stale_pass()

    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    assert state.get('present')

    # проверяем состояние после истечения срока проверки
    with freezegun.freeze_time(stale_time):
        await task_stale_pass()

    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    assert state.get('present') is None
    assert state['past'].get('resolution') == consts.RESOLUTION_CANCEL
    assert state['past'].get('reason') is None
    assert state['past'].get('id') == pass_id


async def test_stale_pass_when_not_passed(
        qc_client, qc_cache, task_stale_pass,
):
    entity = {'id': '1', 'type': 'driver'}
    exam_code = 'dkvu'
    await test_utils.prepare_entity(qc_client, entity['type'], entity['id'])

    # назначаем стандартное прохождение ДКВУ
    response = await qc_client.post(
        'api/v1/state',
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={
            'present': {
                'can_pass': True,
                'sanctions': [consts.BLOCK_ORDERS_OFF],
            },
            'pass': {'media': ['selfie']},
        },
    )
    assert response.status == http.HTTPStatus.OK

    # проверяем назначение
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    # загружаем media
    await test_utils.send_fake(qc_client, state)

    # проверяем назначение
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    assert state['present']['pass'].get('pending')
    assert state['present']['pass'].get('id')
    assert state['present'].get('sanctions') == [consts.BLOCK_ORDERS_OFF]
    assert state.get('past') is None
    assert state.get('future') is None

    pass_id = state['present']['pass']['id']
    pending_time = dates.parse_timestring(
        state['present']['pass']['pending'], 'UTC',
    )

    exam_settings = qc_cache.entity_settings(entity['type'])['exams'][
        exam_code
    ]
    stale_time = pending_time + dates.parse_duration_string(
        exam_settings['pass']['stale'],
    )

    # проверяем состояние до истечения срока проверки
    with freezegun.freeze_time(stale_time - datetime.timedelta(seconds=1)):
        await task_stale_pass()

    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    assert state['present']['pass'].get('pending')

    # проверяем состояние до истечения срока проверки
    with freezegun.freeze_time(stale_time):
        await task_stale_pass()

    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    assert state.get('present')
    assert state['present']['pass'].get('pending') is None
    assert state['present']['pass'].get('id') != pass_id
    assert [x['code'] for x in state['present']['pass']['media']] == ['selfie']
    assert state['past'].get('resolution') == consts.RESOLUTION_CANCEL
    assert state['past'].get('reason') is None
    assert state['past'].get('id') == pass_id


async def test_reason(qc_client):
    entity = {'id': '1', 'type': 'driver'}
    exam_code = 'dkvu'
    await test_utils.prepare_entity(qc_client, entity['type'], entity['id'])

    # назначаем стандартное ДКВУ
    response = await qc_client.post(
        'api/v1/state',
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={
            'present': {
                'can_pass': True,
                'sanctions': [consts.BLOCK_ORDERS_OFF],
            },
        },
    )
    assert response.status == http.HTTPStatus.OK

    # Отправляем фотки
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    pass_id = state['present']['pass']['id']
    await test_utils.send_fake(qc_client, state)

    # резолвим FAIL со сложной причиной
    reason_complex = {
        'code': 'code1',
        'source': 'source1',
        'login': 'login1',
        'comment': 'Test1',
        'number': 'number1',
    }

    response = await qc_client.post(
        '/api/v1/pass/resolve',
        params={
            'type': entity['type'],
            'id': entity['id'],
            'pass_id': pass_id,
        },
        json={'status': consts.RESOLUTION_FAIL, 'reason': reason_complex},
    )
    assert response.status == http.HTTPStatus.OK

    # Проверяем state
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )

    assert state['present'].get('reason') == reason_complex
    assert state['present'].get('identity') is None
    assert state['past'].get('reason') == reason_complex.get('comment')
    assert state['past'].get('id')

    # проверяем pass
    pass_item = await test_utils.check_pass(qc_client, state['past'].get('id'))
    assert pass_item.get('resolution')
    assert pass_item['resolution'].get('reason') == {
        'text': reason_complex.get('comment'),
    }
    assert pass_item['resolution'].get('identity') is None

    # Отправляем еще раз фотки
    await test_utils.send_fake(qc_client, state)

    # резолвим FAIL с детальной причиной
    reason = {'text': 'Test2'}
    identity = {'yandex_team': {'yandex_login': 'login'}}

    response = await qc_client.post(
        '/api/v1/pass/resolve',
        params={
            'type': entity['type'],
            'id': entity['id'],
            'pass_id': state['present']['pass']['id'],
        },
        json={
            'status': consts.RESOLUTION_FAIL,
            'reason': reason,
            'identity': identity,
        },
    )
    assert response.status == http.HTTPStatus.OK

    # Проверяем state
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )

    assert state['present'].get('reason') == reason
    assert state['present'].get('identity') == identity
    assert state['past'].get('reason') == reason.get('text')
    assert state['past'].get('id')

    # проверяем pass
    pass_item = await test_utils.check_pass(qc_client, state['past'].get('id'))
    assert pass_item.get('resolution')
    assert pass_item['resolution'].get('reason') == reason
    assert pass_item['resolution'].get('identity') == identity


async def test_resolve_sanctions_success(qc_client, task_current_state):
    entity = {'id': '1', 'type': 'driver'}
    exam_code = 'dkk'
    await test_utils.prepare_entity(qc_client, entity['type'], entity['id'])

    # назначаем стандартное прохождение
    response = await qc_client.post(
        'api/v1/state',
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={
            'present': {
                'can_pass': True,
                'sanctions': [consts.BLOCK_ORDERS_OFF],
            },
        },
    )
    assert response.status == http.HTTPStatus.OK

    # Отправляем фотки
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    pass_id = state['present']['pass']['id']
    await test_utils.send_fake(qc_client, state)

    # резолвим
    response = await qc_client.post(
        '/api/v1/pass/resolve',
        params={
            'type': entity['type'],
            'id': entity['id'],
            'pass_id': pass_id,
        },
        json={'status': consts.RESOLUTION_SUCCESS},
    )
    assert response.status == http.HTTPStatus.OK

    # планируем future
    await test_utils.schedule_future(
        qc_client,
        entity['type'],
        entity['id'],
        exam_code,
        [consts.BLOCK_ORDERS_OFF],
    )

    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    assert state.get('present') is None
    assert state.get('future')
    assert state['future'].get('sanctions') == [consts.BLOCK_ORDERS_OFF]

    # переходим в будущее и проверяем санкции
    await test_utils.goto_future(task_current_state, state)

    # проверяем блокировку
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    assert state.get('present')
    assert state['present'].get('sanctions') == [consts.BLOCK_ORDERS_OFF]


async def test_resolve_sanctions_fail(qc_client):
    entity = {'id': '1', 'type': 'driver'}
    exam_code = 'dkk'
    await test_utils.prepare_entity(qc_client, entity['type'], entity['id'])

    # назначаем стандартное прохождение
    response = await qc_client.post(
        'api/v1/state',
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={
            'present': {
                'can_pass': True,
                'sanctions': [consts.BLOCK_ORDERS_OFF],
            },
        },
    )
    assert response.status == http.HTTPStatus.OK

    # Отправляем фотки
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    pass_id = state['present']['pass']['id']
    await test_utils.send_fake(qc_client, state)

    # резолвим
    response = await qc_client.post(
        '/api/v1/pass/resolve',
        params={
            'type': entity['type'],
            'id': entity['id'],
            'pass_id': pass_id,
        },
        json={'status': consts.RESOLUTION_FAIL, 'sanctions': ['new']},
    )
    assert response.status == http.HTTPStatus.OK

    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    assert state.get('present')
    assert state['present'].get('sanctions') == ['new']


async def test_after_pass(qc_client, qc_context):
    entity = {'id': '1', 'type': 'driver'}
    exam_code = 'dkk'
    await test_utils.prepare_entity(qc_client, entity['type'], entity['id'])

    # назначаем стандартное прохождение
    response = await qc_client.post(
        'api/v1/state',
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={
            'present': {
                'can_pass': True,
                'sanctions': [consts.BLOCK_ORDERS_OFF],
            },
        },
    )
    assert response.status == http.HTTPStatus.OK

    # Отправляем фотки
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    pass_id = state['present']['pass']['id']
    await test_utils.send_fake(qc_client, state)

    # Проверяем отсутсвие блокировки
    await test_utils.check_need_future(qc_context, entity, exam_code, True)
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    assert state['present']['pass'].get('id')
    assert state['present']['pass'].get('pending')
    assert state['present'].get('sanctions') is None

    # резолвим
    response = await qc_client.post(
        '/api/v1/pass/resolve',
        params={
            'type': entity['type'],
            'id': entity['id'],
            'pass_id': pass_id,
        },
        json={'status': consts.RESOLUTION_FAIL},
    )
    assert response.status == http.HTTPStatus.OK

    # Отправляем фотки повторно
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    pass_id = state['present']['pass']['id']
    await test_utils.send_fake(qc_client, state)

    # Проверяем блокировку
    await test_utils.check_need_future(qc_context, entity, exam_code, False)
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    assert state['present']['pass'].get('id')
    assert state['present']['pass'].get('pending')
    assert state['present'].get('sanctions') == [consts.BLOCK_ORDERS_OFF]

    # резолвим
    response = await qc_client.post(
        '/api/v1/pass/resolve',
        params={
            'type': entity['type'],
            'id': entity['id'],
            'pass_id': pass_id,
        },
        json={'status': consts.RESOLUTION_SUCCESS},
    )
    assert response.status == http.HTTPStatus.OK

    # Проверяем отсутсвие блокировки
    await test_utils.check_need_future(qc_context, entity, exam_code, True)
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    assert state.get('present') is None


async def test_after_pass_restore(qc_client, qc_context, task_current_state):
    entity = {'id': '1', 'type': 'driver'}
    exam_code = 'dkk'
    await test_utils.prepare_entity(qc_client, entity['type'], entity['id'])

    # назначаем стандартное прохождение
    response = await qc_client.post(
        'api/v1/state',
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={
            'present': {
                'can_pass': True,
                'sanctions': [consts.BLOCK_ORDERS_OFF],
            },
        },
    )
    assert response.status == http.HTTPStatus.OK

    # Отправляем фотки
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    pass_id = state['present']['pass']['id']
    await test_utils.send_fake(qc_client, state)

    # резолвим FAIL
    response = await qc_client.post(
        '/api/v1/pass/resolve',
        params={
            'type': entity['type'],
            'id': entity['id'],
            'pass_id': pass_id,
        },
        json={'status': consts.RESOLUTION_FAIL},
    )
    assert response.status == http.HTTPStatus.OK

    # Отправляем фотки повторно
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    pass_id = state['present']['pass']['id']
    await test_utils.send_fake(qc_client, state)

    # резолвим SUCCESS
    response = await qc_client.post(
        '/api/v1/pass/resolve',
        params={
            'type': entity['type'],
            'id': entity['id'],
            'pass_id': pass_id,
        },
        json={'status': consts.RESOLUTION_SUCCESS},
    )
    assert response.status == http.HTTPStatus.OK

    # планируем future и переходим
    await test_utils.schedule_future(
        qc_client,
        entity['type'],
        entity['id'],
        exam_code,
        [consts.BLOCK_ORDERS_OFF],
    )
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    await test_utils.goto_future(task_current_state, state)

    # Отправляем фотки
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    await test_utils.send_fake(qc_client, state)

    # Проверяем блокировку
    await test_utils.check_need_future(qc_context, entity, exam_code, True)
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    assert state['present']['pass'].get('id')
    assert state['present']['pass'].get('pending')
    assert state['present'].get('sanctions') is None


async def test_after_pass_recall(qc_client, qc_context):
    entity = {'id': '1', 'type': 'driver'}
    exam_code = 'dkk'
    await test_utils.prepare_entity(qc_client, entity['type'], entity['id'])

    # назначаем стандартное прохождение
    response = await qc_client.post(
        'api/v1/state',
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={
            'present': {
                'can_pass': True,
                'sanctions': [consts.BLOCK_ORDERS_OFF],
            },
        },
    )
    assert response.status == http.HTTPStatus.OK

    # Отправляем фотки
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    pass_id = state['present']['pass']['id']
    await test_utils.send_fake(qc_client, state)

    # Проверяем блокировку
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    assert state['present']['pass'].get('id')
    assert state['present']['pass'].get('pending')
    assert state['present'].get('sanctions') is None

    # резолвим FAIL
    response = await qc_client.post(
        '/api/v1/pass/resolve',
        params={
            'type': entity['type'],
            'id': entity['id'],
            'pass_id': pass_id,
        },
        json={'status': consts.RESOLUTION_FAIL},
    )
    assert response.status == http.HTTPStatus.OK

    # Перевызываем
    response = await qc_client.post(
        'api/v1/state',
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={
            'present': {
                'can_pass': True,
                'sanctions': [consts.BLOCK_ORDERS_OFF],
            },
        },
    )
    assert response.status == http.HTTPStatus.OK

    # Отправляем фотки
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    pass_id = state['present']['pass']['id']
    await test_utils.send_fake(qc_client, state)

    # Проверяем блокировку
    await test_utils.check_need_future(qc_context, entity, exam_code, False)
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    assert state['present']['pass'].get('id')
    assert state['present']['pass'].get('pending')
    assert state['present'].get('sanctions') == [consts.BLOCK_ORDERS_OFF]


async def test_after_resolve(qc_client, qc_context):
    entity = {'id': '1', 'type': 'driver'}
    exam_code = 'dkvu'
    await test_utils.prepare_entity(qc_client, entity['type'], entity['id'])

    # назначаем стандартное прохождение
    response = await qc_client.post(
        'api/v1/state',
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={
            'present': {
                'can_pass': True,
                'sanctions': [consts.BLOCK_ORDERS_OFF],
            },
        },
    )
    assert response.status == http.HTTPStatus.OK

    # Отправляем фотки
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    pass_id = state['present']['pass']['id']
    await test_utils.send_fake(qc_client, state)

    # Проверяем блокировку
    await test_utils.check_need_future(qc_context, entity, exam_code, False)
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    assert state['present']['pass'].get('id')
    assert state['present']['pass'].get('pending')
    assert state['present'].get('sanctions') == [consts.BLOCK_ORDERS_OFF]

    # резолвим
    response = await qc_client.post(
        '/api/v1/pass/resolve',
        params={
            'type': entity['type'],
            'id': entity['id'],
            'pass_id': pass_id,
        },
        json={'status': consts.RESOLUTION_FAIL},
    )
    assert response.status == http.HTTPStatus.OK

    # Отправляем фотки повторно
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    pass_id = state['present']['pass']['id']
    await test_utils.send_fake(qc_client, state)

    # Проверяем блокировку
    await test_utils.check_need_future(qc_context, entity, exam_code, False)
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    assert state['present']['pass'].get('id')
    assert state['present']['pass'].get('pending')
    assert state['present'].get('sanctions') == [consts.BLOCK_ORDERS_OFF]

    # резолвим
    response = await qc_client.post(
        '/api/v1/pass/resolve',
        params={
            'type': entity['type'],
            'id': entity['id'],
            'pass_id': pass_id,
        },
        json={'status': consts.RESOLUTION_SUCCESS},
    )
    assert response.status == http.HTTPStatus.OK

    # Проверяем отсутсвие блокировки
    await test_utils.check_need_future(qc_context, entity, exam_code, True)
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    assert state.get('present') is None


async def test_data_confirmed_empty(qc_client):
    entity = {'id': '1', 'type': 'driver'}
    exam_code = 'dkvu'
    await test_utils.prepare_entity(qc_client, entity['type'], entity['id'])

    # проверяем подтвержденное состояние
    confirmed = await test_utils.check_confirmed(
        qc_client, entity['type'], entity['id'], exam_code,
    )
    assert confirmed == {}

    # назначаем стандартное прохождение
    response = await qc_client.post(
        'api/v1/state',
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={
            'present': {
                'can_pass': True,
                'sanctions': [consts.BLOCK_ORDERS_OFF],
            },
        },
    )
    assert response.status == http.HTTPStatus.OK

    # Отправляем фотки
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    pass_id = state['present']['pass']['id']
    await test_utils.send_fake(qc_client, state)

    # проверяем подтвержденное состояние
    confirmed = await test_utils.check_confirmed(
        qc_client, entity['type'], entity['id'], exam_code,
    )
    assert confirmed == {}

    # резолвим
    response = await qc_client.post(
        '/api/v1/pass/resolve',
        params={
            'type': entity['type'],
            'id': entity['id'],
            'pass_id': pass_id,
        },
        json={'status': consts.RESOLUTION_SUCCESS},
    )
    assert response.status == http.HTTPStatus.OK

    # проверяем подтвержденное состояние
    pass_item = await test_utils.check_pass(qc_client, pass_id)
    confirmed = await test_utils.check_confirmed(
        qc_client, entity['type'], entity['id'], exam_code,
    )
    assert confirmed == {
        'data': {'license_pd_id': ''},
        'pass_id': pass_id,
        'modified': pass_item['modified'],
    }


async def test_data_confirmed_change(qc_client):
    entity = {'id': '1', 'type': 'driver'}
    exam_code = 'dkvu'
    await test_utils.prepare_entity(qc_client, entity['type'], entity['id'])

    # проверяем подтвержденное состояние
    confirmed = await test_utils.check_confirmed(
        qc_client, entity['type'], entity['id'], exam_code,
    )
    assert confirmed == {}

    # назначаем стандартное прохождение
    response = await qc_client.post(
        'api/v1/state',
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={
            'present': {
                'can_pass': True,
                'sanctions': [consts.BLOCK_ORDERS_OFF],
            },
        },
    )
    assert response.status == http.HTTPStatus.OK

    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    pass_id = state['present']['pass']['id']

    # Обновляем требования
    response = await qc_client.post(
        '/api/v1/pass/update',
        params={'pass_id': pass_id},
        json={'data': ['test_1']},
    )
    assert response.status == http.HTTPStatus.OK

    # Отправляем данные и фотки
    await test_utils.send_fake(qc_client, state)
    await test_utils.send_data(
        qc_client, state, data={'test_1': '1', 'test_2': '2'},
    )

    # проверяем подтвержденное состояние
    confirmed = await test_utils.check_confirmed(
        qc_client, entity['type'], entity['id'], exam_code,
    )
    assert confirmed == {}

    # резолвим
    response = await qc_client.post(
        '/api/v1/pass/resolve',
        params={
            'type': entity['type'],
            'id': entity['id'],
            'pass_id': pass_id,
        },
        json={
            'status': consts.RESOLUTION_SUCCESS,
            'data': {'test_2': '22', 'test_3': '33'},
        },
    )
    assert response.status == http.HTTPStatus.OK

    # проверяем подтвержденное состояние
    pass_item = await test_utils.check_pass(qc_client, pass_id)
    confirmed = await test_utils.check_confirmed(
        qc_client, entity['type'], entity['id'], exam_code,
    )

    assert confirmed.get('pass_id') == pass_item['id']
    assert confirmed.get('modified') == pass_item['modified']
    assert confirmed.get('data')
    assert confirmed['data'].get('test_1') == '1'
    assert confirmed['data'].get('test_2') == '22'
    assert confirmed['data'].get('test_3') == '33'

    pass_data = {x['field']: x for x in pass_item['data']}
    assert pass_data['test_1'].get('required') is True
    assert pass_data['test_1'].get('value') == '1'
    assert pass_data['test_2'].get('required') is False
    assert pass_data['test_2'].get('value') == '22'
    assert pass_data['test_2'].get('prev_value') == '2'
    assert pass_data['test_3'].get('required') is False
    assert pass_data['test_3'].get('value') == '33'
    assert pass_data['test_3'].get('prev_value') is None


async def test_data_confirmed_multiple(qc_client):
    entity = {'id': '1', 'type': 'driver'}
    exam_code = 'dkvu'
    await test_utils.prepare_entity(qc_client, entity['type'], entity['id'])

    # назначаем стандартное прохождение
    response = await qc_client.post(
        'api/v1/state',
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={
            'present': {
                'can_pass': True,
                'sanctions': [consts.BLOCK_ORDERS_OFF],
            },
        },
    )
    assert response.status == http.HTTPStatus.OK

    # Отправляем данные и фотки и резолвим
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    pass_id_1 = state['present']['pass']['id']
    await test_utils.send_fake(qc_client, state)

    response = await qc_client.post(
        '/api/v1/pass/resolve',
        params={
            'type': entity['type'],
            'id': entity['id'],
            'pass_id': pass_id_1,
        },
        json={'status': consts.RESOLUTION_SUCCESS, 'data': {'test_1': '1'}},
    )
    assert response.status == http.HTTPStatus.OK

    # проверяем подтвержденные данные
    confirmed = await test_utils.check_confirmed(
        qc_client, entity['type'], entity['id'], exam_code,
    )
    assert confirmed['pass_id'] == pass_id_1
    assert confirmed['data'] == {'license_pd_id': '', 'test_1': '1'}

    # опять вызываем на ДКВУ
    response = await qc_client.post(
        'api/v1/state',
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={
            'present': {
                'can_pass': True,
                'sanctions': [consts.BLOCK_ORDERS_OFF],
            },
        },
    )
    assert response.status == http.HTTPStatus.OK

    # Отправляем данные и фотки и резолвим
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    pass_id_2 = state['present']['pass']['id']
    await test_utils.send_fake(qc_client, state)

    response = await qc_client.post(
        '/api/v1/pass/resolve',
        params={
            'type': entity['type'],
            'id': entity['id'],
            'pass_id': pass_id_2,
        },
        json={'status': consts.RESOLUTION_SUCCESS, 'data': {'test_2': '2'}},
    )
    assert response.status == http.HTTPStatus.OK

    # проверяем подтвержденные данные
    confirmed = await test_utils.check_confirmed(
        qc_client, entity['type'], entity['id'], exam_code,
    )
    assert confirmed['pass_id'] == pass_id_2
    assert confirmed['data'] == {'license_pd_id': '', 'test_2': '2'}


async def test_set_pass_policy(qc_client, qc_context):
    entity = {'id': '1', 'type': 'driver'}
    # берём экзамен 'after_pass'
    exam_code = 'dkk'
    await test_utils.prepare_entity(qc_client, entity['type'], entity['id'])

    # назначаем прохождение с политикой 'after_resolve'
    response = await qc_client.post(
        'api/v1/state',
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={
            'present': {
                'can_pass': True,
                'sanctions': [consts.BLOCK_ORDERS_OFF],
                'release': 'after_resolve',
            },
        },
    )
    assert response.status == http.HTTPStatus.OK

    # Отправляем фотки
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    await test_utils.send_fake(qc_client, state)

    # проверяем, что экзамен не пройден
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )

    assert state['present'].get('sanctions') == [consts.BLOCK_ORDERS_OFF]


async def test_data_value_array(qc_client):
    entity = {'id': '1', 'type': 'driver'}
    exam_code = 'dkvu'
    await test_utils.prepare_entity(qc_client, entity['type'], entity['id'])

    # назначаем стандартное прохождение
    response = await qc_client.post(
        'api/v1/state',
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={
            'present': {
                'can_pass': True,
                'sanctions': [consts.BLOCK_ORDERS_OFF],
            },
        },
    )
    assert response.status == http.HTTPStatus.OK

    # Отправляем данные и фотки и резолвим
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    pass_id_1 = state['present']['pass']['id']
    await test_utils.send_fake(qc_client, state)

    response = await qc_client.post(
        '/api/v1/pass/resolve',
        params={
            'type': entity['type'],
            'id': entity['id'],
            'pass_id': pass_id_1,
        },
        json={
            'status': consts.RESOLUTION_SUCCESS,
            'data': {'array_field': ['value_1', 'value_2'], 'empty_array': []},
        },
    )
    assert response.status == http.HTTPStatus.OK

    # проверяем подтвержденные данные
    confirmed = await test_utils.check_confirmed(
        qc_client, entity['type'], entity['id'], exam_code,
    )
    assert confirmed['pass_id'] == pass_id_1
    assert confirmed['data'] == {
        'license_pd_id': '',
        'array_field': ['value_1', 'value_2'],
        'empty_array': [],
    }
