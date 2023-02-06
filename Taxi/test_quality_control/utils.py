import datetime
import http
import logging

import bson
import freezegun

from taxi.util import dates

from quality_control import utils
from quality_control.repository import storage
from test_quality_control import plugins


logger = logging.getLogger(__name__)


async def prepare_entity(qc_client, entity_type, entity_id, data=None):
    data = data or {}
    data.update(dict(park_id='1'))
    response = await qc_client.post(
        '/api/v1/data',
        params={'type': entity_type, 'id': entity_id, 'flow': 'new'},
        json=data,
    )
    assert response.status == http.HTTPStatus.OK


async def prepare_exam(qc_client, entity_type, entity_id, exam_code, body):
    response = await qc_client.post(
        '/api/v1/state',
        params={'type': entity_type, 'id': entity_id, 'exam': exam_code},
        json=body,
    )
    assert response.status == http.HTTPStatus.OK


async def check_states(qc_client, entity_type, exam_code, show_disabled=False):
    params = {'type': entity_type, 'exam': exam_code}

    if show_disabled:
        params['disabled'] = 'true'

    response = await qc_client.get('/api/v1/state/list', params=params)
    assert response.status == http.HTTPStatus.OK
    return await response.json()


async def check_confirmed(qc_client, entity_type, entity_id, exam_code):
    params = {'type': entity_type, 'id': entity_id, 'exam': exam_code}

    response = await qc_client.get('/api/v1/data/confirmed', params=params)
    assert response.status == http.HTTPStatus.OK
    return await response.json()


async def check_state(
        qc_client, entity_type, entity_id, exam_code, show_disabled=False,
):
    params = {
        'type': entity_type,
        'id': entity_id,
        'exam': exam_code,
        'flow': 'new',
    }

    if show_disabled:
        params['disabled'] = 'true'

    response = await qc_client.get('/api/v1/state', params=params)
    assert response.status == http.HTTPStatus.OK
    return next(iter((await response.json())['exams']), None)


async def check_pass(qc_client, pass_id, with_urls=False):
    params = {'pass_id': pass_id}

    if with_urls:
        params['options'] = 'urls'

    response = await qc_client.get('/api/v1/pass', params=params)
    assert response.status == http.HTTPStatus.OK
    return await response.json()


async def check_need_future(qc_context, entity, exam_code, value_should_be):
    db_entity = await storage.get_entity(
        qc_context,
        {
            'entity_type': entity['type'],
            'entity_id': entity['id'],
            'state.exams.code': exam_code,
        },
        ['state.exams'],
    )
    assert db_entity['state']['exams'][0]['need_future'] is value_should_be


async def check_pass_filter(qc_context, pass_id, value_should_be):
    db_pass = await storage.get_pass(
        qc_context, where={'_id': bson.ObjectId(pass_id)}, select=['filter'],
    )

    assert db_pass['filter'] == value_should_be


async def send_fake(
        qc_client, state, media_codes=None, status=http.HTTPStatus.OK,
):
    pass_item = state['present']['pass']
    if not media_codes:
        media_codes = [x['code'] for x in pass_item['media']]
    for media_code in media_codes:
        response = await qc_client.post(
            '/api/v1/pass/media',
            params={'pass_id': pass_item['id'], 'media_code': media_code},
            data=plugins.BINARY_IMAGE,
            headers={
                'Content-Type': 'image/jpeg',
                'X-File-Name': f'{media_code}.jpg',
            },
        )
        assert response.status == status


async def check_watermarks(qc_client, state, x_yandex_login):
    pass_item = state['present']['pass']
    pass_id = pass_item['id']

    for media in pass_item['media']:
        media_code = media['code']
        response = await qc_client.get(
            '/admin/qc/v1/pass/media/',
            params={'pass_id': pass_id, 'media_code': media_code},
            headers={'X-Yandex-Login': x_yandex_login},
        )
        assert response.status == http.HTTPStatus.OK


async def send_data(
        qc_client, state, data, modified=None, status=http.HTTPStatus.OK,
):
    pass_item = state['present']['pass']
    json = dict(data=data)
    if modified:
        json.update(modified=modified)

    response = await qc_client.post(
        '/api/v1/pass/data', params={'pass_id': pass_item['id']}, json=json,
    )
    assert response.status == status


async def schedule_future(
        qc_client,
        entity_type,
        entity_id,
        exam_code,
        sanctions,
        future1_delta=None,
        future2_delta=None,
):
    future1_delta = future1_delta or datetime.timedelta(days=4, hours=12)
    future1_begin = datetime.datetime.utcnow() + future1_delta

    future2_delta = future2_delta or datetime.timedelta(hours=12)
    future2_begin = future1_begin + future2_delta
    state = await check_state(
        qc_client, entity_type, entity_id, exam_code=exam_code,
    )
    response = await qc_client.post(
        '/api/v1/schedule',
        params={
            'type': entity_type,
            'id': entity_id,
            'exam': exam_code,
            'modified': state['modified'],
        },
        json={
            'future': [
                {'begin': utils.to_string(future1_begin), 'can_pass': True},
                {
                    'begin': utils.to_string(future2_begin),
                    'can_pass': True,
                    'sanctions': sanctions,
                },
            ],
        },
    )
    assert response.status == http.HTTPStatus.OK


async def goto_future(task_current_state, state):
    future_date = dates.parse_timestring(state['future']['begin'], 'UTC')
    with freezegun.freeze_time(future_date):
        await task_current_state()


class STATES:
    CALL = {'present': {'can_pass': True, 'sanctions': ['orders_off']}}

    DISABLE = {'enabled': False}

    ENABLE = {'enabled': True}
