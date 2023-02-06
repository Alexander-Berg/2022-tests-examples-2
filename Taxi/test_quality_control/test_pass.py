import asyncio
import datetime
import http

import pytest

from taxi.util import dates

from quality_control import consts
from quality_control import utils
from test_quality_control import utils as test_utils

URL = '/api/v1/pass'


@pytest.mark.config(QC_LAG_DELTA={'LAG_PASS_LIST': -10})
async def test_pass_list(qc_client):
    entity_count = 5
    entity_type = 'driver'
    exam_code = 'dkvu'
    # создаём entity_count сущностей типа entity_type
    prepare_entities_futures = [
        test_utils.prepare_entity(qc_client, entity_type, str(_id))
        for _id in range(entity_count)
    ]
    await asyncio.gather(*prepare_entities_futures)

    # назначаем прохождение ДКК
    set_dkk_futures = [
        qc_client.post(
            'api/v1/state',
            params={'type': entity_type, 'id': str(_id), 'exam': exam_code},
            json={'present': {'can_pass': True, 'sanctions': ['orders_off']}},
        )
        for _id in range(entity_count)
    ]

    await asyncio.gather(*set_dkk_futures)

    # проверяем passes
    response = await qc_client.get(
        'api/v1/pass/list',
        params={'entity_type': entity_type, 'limit': entity_count - 1},
    )
    assert response.status == http.HTTPStatus.OK
    data = await response.json()
    assert 'items' in data
    assert len(data['items']) == entity_count - 1


@pytest.mark.config(QC_LAG_DELTA={'LAG_PASS_LIST': -10})
async def test_pass_list_exam_in(qc_client):
    entity_type = 'driver'
    exam_code = 'dkvu'

    # создаём сущность типа entity_type
    await test_utils.prepare_entity(qc_client, entity_type, 'some_id')

    # назначаем прохождение ДКК
    await qc_client.post(
        'api/v1/state',
        params={'type': entity_type, 'id': 'some_id', 'exam': exam_code},
        json={'present': {'can_pass': True, 'sanctions': ['orders_off']}},
    )

    # проверяем passes
    async def _check_count(exam_in: str, expected_count: int):
        response = await qc_client.get(
            'api/v1/pass/list', params={'limit': 100, 'exam_in': exam_in},
        )
        assert response.status == http.HTTPStatus.OK
        data = await response.json()
        assert 'items' in data
        assert len(data['items']) == expected_count

    await _check_count(exam_code, 1)
    await _check_count('xxx,yyy', 0)
    await _check_count(f'xxx,{exam_code},yyy', 1)


async def test_pass_new(qc_client):
    entity = {'id': '1', 'type': 'driver'}
    exam_code = 'dkvu'
    await test_utils.prepare_entity(qc_client, entity['type'], entity['id'])

    # назначаем стандартное прохождение ДКВУ
    response = await qc_client.post(
        '/api/v1/state',
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={
            'present': {'can_pass': True, 'sanctions': ['orders_off']},
            'pass': {'media': ['front', 'back']},
        },
    )
    assert response.status == http.HTTPStatus.OK

    # проверяем назначение
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    assert state['present'].get('pass', {}).get('id')

    pass_id = state['present']['pass']['id']
    pass_item = await test_utils.check_pass(qc_client, pass_id)

    assert pass_item.get('id')
    assert pass_item.get('exam') == exam_code
    assert pass_item.get('status') == consts.PASS_NEW
    assert pass_item.get('expire_at') is None
    assert pass_item.get('modified')
    for idx, code in enumerate(['front', 'back']):
        media_settings = pass_item['media'][idx]
        assert media_settings['code'] == code
        assert media_settings['required'] is True


async def test_media_pending(qc_client, qc_cache):
    entity = {'id': '1', 'type': 'driver'}
    exam_code = 'dkvu'
    await test_utils.prepare_entity(qc_client, entity['type'], entity['id'])

    # назначаем стандартное прохождение ДКВУ
    response = await qc_client.post(
        '/api/v1/state',
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={
            'present': {'can_pass': True, 'sanctions': ['orders_off']},
            'pass': {'media': ['front', 'back']},
        },
    )
    assert response.status == http.HTTPStatus.OK

    # проверяем pass
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code,
    )
    pass_id = state['present']['pass']['id']
    pass_item = await test_utils.check_pass(qc_client, pass_id)
    assert pass_item['status'] == consts.PASS_NEW
    assert [x['code'] for x in pass_item['media'] if 'loaded' not in x] == [
        'front',
        'back',
    ]

    # отправляем одну фотку
    await test_utils.send_fake(qc_client, state, ['front'])

    # проверяем pass
    pass_item = await test_utils.check_pass(qc_client, pass_id)
    assert pass_item['status'] == consts.PASS_NEW
    assert [x['code'] for x in pass_item['media'] if 'loaded' not in x] == [
        'back',
    ]

    # отправкляем 2-ю фотку
    await test_utils.send_fake(qc_client, state, ['back'])

    exam_settings = qc_cache.entity_settings(entity['type'])['exams'][
        exam_code
    ]
    # проверяем pass
    pass_item = await test_utils.check_pass(qc_client, pass_id)
    assert pass_item['status'] == consts.PASS_PENDING
    assert pass_item.get('pending_expired') == utils.to_string(
        datetime.datetime.utcnow()
        + dates.parse_duration_string(exam_settings['pass']['stale']),
    )
    assert [x['code'] for x in pass_item['media'] if 'loaded' not in x] == []


async def test_pass_update(qc_client, qc_cache):
    entity = {'id': '1', 'type': 'driver'}
    exam_code = 'dkvu'
    await test_utils.prepare_entity(qc_client, entity['type'], entity['id'])

    # назначаем стандартное прохождение ДКВУ
    response = await qc_client.post(
        '/api/v1/state',
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={
            'present': {'can_pass': True, 'sanctions': ['orders_off']},
            'pass': {'media': ['front', 'back']},
        },
    )
    assert response.status == http.HTTPStatus.OK

    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code,
    )
    pass_id = state['present']['pass']['id']

    # обновляем требования media и data
    response = await qc_client.post(
        '/api/v1/pass/update',
        params={'pass_id': pass_id},
        json={'media': ['back', 'front', 'selfie'], 'data': ['test_1']},
    )
    assert response.status == http.HTTPStatus.OK

    # проверяем последовательность media
    settings = await response.json()
    exam_settings = qc_cache.entity_settings(entity['type'])['exams'][
        exam_code
    ]
    for idx, media_code in enumerate(['back', 'front', 'selfie']):
        media_settings = exam_settings['media']['items'][media_code]
        assert settings['media'][idx] == media_settings

    # проверяем pass
    pass_item = await test_utils.check_pass(qc_client, pass_id)
    assert pass_item['status'] == consts.PASS_NEW
    assert pass_item['media'] == [
        {'code': x, 'required': True} for x in ['back', 'front', 'selfie']
    ]

    assert pass_item['data'] == [{'field': 'test_1', 'required': True}]


async def test_pass_data_on_new(qc_client, qc_context):
    entity = {'id': '1', 'type': 'driver'}
    exam_code = 'dkvu'
    await test_utils.prepare_entity(qc_client, entity['type'], entity['id'])

    # назначаем стандартное прохождение ДКВУ
    response = await qc_client.post(
        '/api/v1/state',
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={
            'present': {'can_pass': True, 'sanctions': ['orders_off']},
            'pass': {'media': ['front', 'back']},
        },
    )
    assert response.status == http.HTTPStatus.OK

    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code,
    )
    pass_id = state['present']['pass']['id']

    # отправляем данные и проверяем
    await test_utils.send_data(qc_client, state, {'test_1': '1'})
    pass_item = await test_utils.check_pass(qc_client, pass_id)
    assert pass_item['status'] == consts.PASS_NEW
    assert pass_item['data'] == [
        {'field': 'test_1', 'required': False, 'value': '1'},
    ]
    await test_utils.check_pass_filter(
        qc_context, pass_item['id'], [dict(field='id', value=entity['id'])],
    )

    # обновляем требования media и data
    response = await qc_client.post(
        '/api/v1/pass/update',
        params={'pass_id': pass_id},
        json={'media': ['back', 'front', 'selfie'], 'data': ['test_2']},
    )
    assert response.status == http.HTTPStatus.OK

    # отправляем данные
    await test_utils.send_data(
        qc_client, state, {'test_1': '2'}, status=http.HTTPStatus.BAD_REQUEST,
    )
    await test_utils.send_data(qc_client, state, {'test_2': '2'})
    pass_item = await test_utils.check_pass(qc_client, pass_id)
    assert pass_item['status'] == consts.PASS_NEW
    assert pass_item['data'] == [
        {'field': 'test_2', 'value': '2', 'required': True},
    ]

    await test_utils.check_pass_filter(
        qc_context,
        pass_item['id'],
        [
            dict(field='id', value=entity['id']),
            dict(field='test_2', value='2'),
        ],
    )


async def test_default_data(qc_client):
    entity = {'id': '1', 'type': 'driver'}
    exam_code = 'dkvu'
    await test_utils.prepare_entity(
        qc_client,
        entity['type'],
        entity['id'],
        data=dict(license_pd_id='license', name='Yakov'),
    )

    # назначаем стандартное прохождение ДКВУ
    response = await qc_client.post(
        '/api/v1/state',
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={
            'present': {'can_pass': True, 'sanctions': ['orders_off']},
            'pass': {'media': ['front', 'back']},
        },
    )
    assert response.status == http.HTTPStatus.OK

    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code,
    )
    await test_utils.send_fake(qc_client, state)

    pass_id = state['present']['pass']['id']
    pass_item = await test_utils.check_pass(qc_client, pass_id)
    assert pass_item['status'] == consts.PASS_PENDING
    assert pass_item['data'] == [
        {
            'field': 'license_pd_id',
            'value': 'license',
            'required': False,
            'editable': True,
        },
        {'field': 'name', 'value': 'Yakov', 'required': False},
    ]


async def test_pass_data_on_pending(qc_client):
    entity = {'id': '1', 'type': 'driver'}
    exam_code = 'dkvu'
    await test_utils.prepare_entity(qc_client, entity['type'], entity['id'])

    # назначаем стандартное прохождение ДКВУ
    response = await qc_client.post(
        '/api/v1/state',
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={
            'present': {'can_pass': True, 'sanctions': ['orders_off']},
            'pass': {'media': ['front', 'back']},
        },
    )
    assert response.status == http.HTTPStatus.OK

    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code,
    )
    await test_utils.send_fake(qc_client, state)

    pass_id = state['present']['pass']['id']
    pass_item = await test_utils.check_pass(qc_client, pass_id)
    assert pass_item['status'] == consts.PASS_PENDING
    assert pass_item['data'] == [
        {
            'field': 'license_pd_id',
            'value': '',
            'required': False,
            'editable': True,
        },
    ]

    # если отправлять без modified, то будет ошибка
    await test_utils.send_data(
        qc_client, state, {'test_2': '3'}, status=http.HTTPStatus.BAD_REQUEST,
    )

    # если отправлять с неправильным modified, то будет конфликт
    await test_utils.send_data(
        qc_client,
        state,
        {'test_2': '3'},
        modified='test',
        status=http.HTTPStatus.CONFLICT,
    )

    await test_utils.send_data(
        qc_client, state, {'test_2': '3'}, modified=pass_item['modified'],
    )
    pass_item = await test_utils.check_pass(qc_client, pass_id)
    assert pass_item['status'] == consts.PASS_PENDING

    assert sorted(pass_item['data'], key=lambda x: x['field']) == [
        {
            'field': 'license_pd_id',
            'value': '',
            'required': False,
            'editable': True,
        },
        {'field': 'test_2', 'value': '3', 'required': False},
    ]


async def test_pass_loaded_and_required(qc_client):
    entity = {'id': '1', 'type': 'driver'}
    exam_code = 'dkvu'
    await test_utils.prepare_entity(qc_client, entity['type'], entity['id'])

    # назначаем стандартное прохождение ДКВУ
    response = await qc_client.post(
        '/api/v1/state',
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={
            'present': {'can_pass': True, 'sanctions': ['orders_off']},
            'pass': {'media': ['front', 'back', 'selfie']},
        },
    )
    assert response.status == http.HTTPStatus.OK

    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code,
    )
    pass_id = state['present']['pass']['id']

    # загружаем front и back
    await test_utils.send_fake(qc_client, state, ['front', 'back'])

    # обновляем требования media
    response = await qc_client.post(
        '/api/v1/pass/update',
        params={'pass_id': pass_id},
        json={'media': ['back', 'selfie']},
    )
    assert response.status == http.HTTPStatus.OK

    # проверяем media loaded
    pass_item = await test_utils.check_pass(qc_client, pass_id)
    assert pass_item['status'] == consts.PASS_NEW
    pass_media = {x['code']: x for x in pass_item['media']}
    assert pass_media['front'].get('required') is False
    assert pass_media['front'].get('loaded')
    assert pass_media['back'].get('loaded')
    assert pass_media['back'].get('required') is True
    assert pass_media['selfie'].get('loaded') is None
    assert pass_media['selfie'].get('required') is True

    # меняем требования - теперь все фотки загружены, data не требуется
    response = await qc_client.post(
        '/api/v1/pass/update',
        params={'pass_id': pass_id},
        json={'media': ['back', 'front']},
    )
    assert response.status == http.HTTPStatus.BAD_REQUEST

    # меняем требования - теперь все фотки загружены, data требуется
    response = await qc_client.post(
        '/api/v1/pass/update',
        params={'pass_id': pass_id},
        json={'media': ['back', 'front'], 'data': ['test_1']},
    )
    assert response.status == http.HTTPStatus.OK

    # меняем требования - теперь data не трбуется, все фотки загружены
    response = await qc_client.post(
        '/api/v1/pass/update',
        params={'pass_id': pass_id},
        json={'media': ['back', 'front'], 'data': []},
    )
    assert response.status == http.HTTPStatus.BAD_REQUEST


async def test_media_data_pending(qc_client):
    entity = {'id': '1', 'type': 'driver'}
    exam_code = 'dkvu'
    await test_utils.prepare_entity(qc_client, entity['type'], entity['id'])

    # назначаем стандартное прохождение ДКВУ
    response = await qc_client.post(
        '/api/v1/state',
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={
            'present': {'can_pass': True, 'sanctions': ['orders_off']},
            'pass': {'media': ['front', 'back']},
        },
    )
    assert response.status == http.HTTPStatus.OK

    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code,
    )
    pass_id = state['present']['pass']['id']

    # обновляем требования media и data
    response = await qc_client.post(
        '/api/v1/pass/update',
        params={'pass_id': pass_id},
        json={'media': ['back', 'front', 'selfie'], 'data': ['test_1']},
    )
    assert response.status == http.HTTPStatus.OK

    # отправляем фотки
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code,
    )
    await test_utils.send_fake(qc_client, state)

    # проверяем pass
    pass_item = await test_utils.check_pass(qc_client, pass_id)
    assert pass_item['status'] == consts.PASS_NEW

    # отправляем data без required
    await test_utils.send_data(
        qc_client, state, {'test_2': '2'}, status=http.HTTPStatus.BAD_REQUEST,
    )

    pass_item = await test_utils.check_pass(qc_client, pass_id)
    assert pass_item['status'] == consts.PASS_NEW
    assert pass_item.get('data') == [{'field': 'test_1', 'required': True}]

    # отправляем data с required
    await test_utils.send_data(qc_client, state, {'test_1': '1'})

    pass_item = await test_utils.check_pass(qc_client, pass_id)
    assert pass_item['status'] == consts.PASS_PENDING
    assert sorted(pass_item['data'], key=lambda k: k['field']) == [
        {
            'field': 'license_pd_id',
            'value': '',
            'required': False,
            'editable': True,
        },
        {'field': 'test_1', 'required': True, 'value': '1'},
    ]


async def test_resolve_nonblock_sanctions(qc_client, qc_context):
    """Проверяем, что при передачи в /api/v1/pass/resolve неблокирующих санкций
    получим need_future == True"""
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

    # загружаем media
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
        json={
            'status': consts.RESOLUTION_FAIL,
            'sanctions': ['dkk_comfort_off'],
        },
    )
    assert response.status == http.HTTPStatus.OK

    await test_utils.check_need_future(qc_context, entity, exam_code, True)


async def test_resolve_block_sanctions(qc_cache, qc_client, qc_context):
    """Проверяем, что при передачи в /api/v1/pass/resolve блокирующих санкций
    получим блок"""
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

    # загружаем media
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code=exam_code,
    )
    await test_utils.send_fake(qc_client, state)

    exam_settings = qc_cache.entity_settings(entity['type'])['exams'][
        exam_code
    ]
    response = await qc_client.post(
        '/api/v1/pass/resolve',
        params={
            'type': entity['type'],
            'id': entity['id'],
            'pass_id': state['present']['pass']['id'],
        },
        json={
            'status': consts.RESOLUTION_FAIL,
            'sanctions': ['dkk_comfort_off'] + exam_settings['block'].get(
                'sanctions', [],
            ),
        },
    )
    assert response.status == http.HTTPStatus.OK

    await test_utils.check_need_future(qc_context, entity, exam_code, False)


@pytest.mark.config(
    QC_EXAMS_PRELOADED_MEDIA={
        'is_enabled': True,
        'exams': {
            'vaccination': {
                'data_to_media': {
                    'scan_result_id': {
                        'type': 'media_storage',
                        'id': '1234567890',
                        'version': '1',
                        'bucket': 'vaccination-photo',
                    },
                },
            },
        },
    },
)
async def test_vaccination_data_pending(qc_client):
    entity = {'id': '1', 'type': 'driver'}
    exam_code = 'vaccination'
    await test_utils.prepare_entity(qc_client, entity['type'], entity['id'])

    # назначаем стандартное прохождение ДКВУ
    response = await qc_client.post(
        '/api/v1/state',
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={
            'present': {'can_pass': True, 'sanctions': ['orders_off']},
            'pass': {'media': ['front', 'back']},
        },
    )
    assert response.status == http.HTTPStatus.OK

    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code,
    )
    pass_id = state['present']['pass']['id']
    pass_item = await test_utils.check_pass(qc_client, pass_id)
    assert pass_item['status'] == consts.PASS_NEW
    assert sorted(pass_item['media'], key=lambda k: k['code']) == [
        {'code': 'back', 'required': True},
        {'code': 'front', 'required': True},
    ]
    assert not pass_item.get('data')

    # обновляем требования media и data
    response = await qc_client.post(
        '/api/v1/pass/update',
        params={'pass_id': pass_id},
        json={'media': [], 'data': ['scan_result_id']},
    )
    assert response.status == http.HTTPStatus.OK
    pass_item = await test_utils.check_pass(qc_client, pass_id)
    assert pass_item['status'] == consts.PASS_NEW
    assert sorted(pass_item['media'], key=lambda k: k['code']) == [
        {'code': 'back', 'required': True},
        {'code': 'front', 'required': True},
    ]
    assert pass_item['data'] == [{'field': 'scan_result_id', 'required': True}]

    # отправляем data
    await test_utils.send_data(
        qc_client, state, {'scan_result_id': '2'}, status=http.HTTPStatus.OK,
    )

    pass_item = await test_utils.check_pass(qc_client, pass_id)
    assert pass_item['status'] == consts.PASS_PENDING
    assert sorted(pass_item['data'], key=lambda k: k['field']) == [
        {'field': 'scan_result_id', 'value': '2', 'required': True},
    ]
    for item in pass_item['media']:
        item.pop('loaded')
    assert sorted(pass_item['media'], key=lambda k: k['code']) == [
        {
            'code': 'back',
            'required': True,
            'storage': {
                'type': 'media_storage',
                'id': '1234567890',
                'version': '1',
                'bucket': 'vaccination-photo',
            },
        },
        {
            'code': 'front',
            'required': True,
            'storage': {
                'type': 'media_storage',
                'id': '1234567890',
                'version': '1',
                'bucket': 'vaccination-photo',
            },
        },
    ]
