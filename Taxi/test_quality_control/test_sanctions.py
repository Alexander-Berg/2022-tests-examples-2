import http

from quality_control import consts
from test_quality_control import utils as test_utils

URL = '/api/v1/state'


async def test_dkvu_sanctions(qc_client):
    entity = {'id': '1', 'type': 'driver'}
    await test_utils.prepare_entity(qc_client, entity['type'], entity['id'])
    exam_code = 'dkvu'

    # назначаем стандартное прохождение ДКВУ
    response = await qc_client.post(
        '/api/v1/state',
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={'present': {'can_pass': True, 'sanctions': ['orders_off']}},
    )
    assert response.status == http.HTTPStatus.OK

    # проверяем санкции
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    assert state.get('present', {}).get('sanctions') == ['orders_off']

    # отправляем фотки, для ДКВУ санкции сохраняются
    await test_utils.send_fake(qc_client, state)
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    assert state.get('present', {}).get('sanctions') == ['orders_off']
    assert state.get('present', {}).get('pass', {}).get('pending')

    # резолвим SUCCESS, санкции снимаются
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
    assert state.get('past') and state.get('present') is None
    assert state['past'].get('resolution') == consts.RESOLUTION_SUCCESS
    assert state['past'].get('reason') is None


async def test_dkk_sanctions(qc_client):
    entity = {'id': '1', 'type': 'driver'}
    await test_utils.prepare_entity(qc_client, entity['type'], entity['id'])
    exam_code = 'dkk'

    # назначаем стандартное прохождение ДКВУ
    response = await qc_client.post(
        '/api/v1/state',
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={'present': {'can_pass': True, 'sanctions': ['orders_off']}},
    )
    assert response.status == http.HTTPStatus.OK

    # проверяем санкции
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    assert state.get('present', {}).get('sanctions') == ['orders_off']

    # отправляем фотки, для ДКК санкции снимаются
    await test_utils.send_fake(qc_client, state)
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    assert state.get('present', {}).get('sanctions') != ['orders_off']
    assert state.get('present', {}).get('pass', {}).get('pending')

    # резолвим SUCCESS, санкции по-прежнему сняты
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
    assert state.get('present', {}).get('sanctions') != ['orders_off']
    assert state['past'].get('resolution') == consts.RESOLUTION_SUCCESS
    assert state['past'].get('reason') is None
