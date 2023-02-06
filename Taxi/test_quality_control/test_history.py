# pylint: disable=too-many-lines
import http

import pytest

from quality_control import consts
from test_quality_control import utils as test_utils

# поскольку мы не можем зафризить время в монге, не нужно фризить время:
# балковые ручки не вернут данные после апдейта, т.к. now стоит на месте
# pylint: disable=invalid-name
pytestmark = pytest.mark.dontfreeze


async def test_history(qc_client, qc_context):
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

    await test_utils.check_pass_filter(
        qc_context, pass_id, [dict(field='id', value=entity['id'])],
    )

    # Отправляем фотки повторно
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    pass_id = state['present']['pass']['id']

    # Отправляем data
    await test_utils.send_data(
        qc_client, state, {'test_1': '1', 'test_2': '2'},
    )

    await test_utils.send_fake(qc_client, state)

    await test_utils.check_pass_filter(
        qc_context,
        pass_id,
        [
            dict(field='id', value=entity['id']),
            dict(field='test_2', value='2'),
        ],
    )

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

    # проверяем всю историю
    response = await qc_client.post(
        '/api/v1/pass/history',
        params={'type': entity['type'], 'exam': exam_code},
        json={'filter': dict(id=entity['id'])},
    )

    assert response.status == http.HTTPStatus.OK
    response_data = await response.json()
    assert len(response_data['items']) == 2

    # проверяем историю с фильтром по data
    response = await qc_client.post(
        '/api/v1/pass/history',
        params={'type': entity['type'], 'exam': exam_code},
        json={'filter': dict(id=entity['id'], test_2='2')},
    )

    assert response.status == http.HTTPStatus.OK
    response_data = await response.json()
    assert len(response_data['items']) == 1


async def test_history_data_changes_on_resolve(qc_client, qc_context):
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

    # Отправляем data
    await test_utils.send_data(
        qc_client, state, {'test_1': '1', 'test_2': '2'},
    )

    await test_utils.send_fake(qc_client, state)

    await test_utils.check_pass_filter(
        qc_context,
        pass_id,
        [
            dict(field='id', value=entity['id']),
            dict(field='test_2', value='2'),
        ],
    )

    # проверяем, что в истории есть проверка
    # проверяем всю историю
    response = await qc_client.post(
        '/api/v1/pass/history',
        params={'type': entity['type'], 'exam': exam_code},
        json={'filter': dict(id=entity['id'], test_2='2')},
    )

    assert response.status == http.HTTPStatus.OK
    response_data = await response.json()
    assert len(response_data['items']) == 1

    # резолвим меняя данные
    response = await qc_client.post(
        '/api/v1/pass/resolve',
        params={
            'type': entity['type'],
            'id': entity['id'],
            'pass_id': pass_id,
        },
        json={'status': consts.RESOLUTION_SUCCESS, 'data': dict(test_2='3')},
    )
    assert response.status == http.HTTPStatus.OK

    # проверяем историю с фильтром
    response = await qc_client.post(
        '/api/v1/pass/history',
        params={'type': entity['type'], 'exam': exam_code},
        json={'filter': dict(id=entity['id'], test_2='2')},
    )

    assert response.status == http.HTTPStatus.OK
    response_data = await response.json()
    assert not response_data['items']

    # проверяем историю с фильтром
    response = await qc_client.post(
        '/api/v1/pass/history',
        params={'type': entity['type'], 'exam': exam_code},
        json={'filter': dict(id=entity['id'], test_2='3')},
    )

    assert response.status == http.HTTPStatus.OK
    response_data = await response.json()
    assert len(response_data['items']) == 1
