import copy
import datetime

import pytest


_NOW = datetime.datetime.utcnow().replace(microsecond=0)
_CLIENT = 'client'
_USER_LOGIN = 'user1_login'
_USER_LOGIN_PD_ID = 'user1_login_pd_id'
_USER_UID = 'user1_uid'
_IDEMPOTENCY_TOKEN = '123'

_REQUEST_DATA = {
    'service': 'taxi',
    'since_date': '2020-05-01',
    'till_date': '2020-05-31',
}
_DEFAULT_HEADERS = {
    'X-Idempotency-Token': _IDEMPOTENCY_TOKEN,
    'X-Real-IP': '127.0.0.1',
    'X-Request-Language': 'he',
    'X-Yandex-Login': _USER_LOGIN,
    'X-Yandex-UID': _USER_UID,
}
_GET_CLIENT_RESPONSE = {'id': _CLIENT, 'tz': 'Europe/Moscow'}


@pytest.mark.now(_NOW.isoformat())
async def test_base(web_app_client, mock_personal, mock_corp_clients, db, stq):
    mock_corp_clients.data.get_client_response = _GET_CLIENT_RESPONSE
    report_id = '477e95476660a2f4359a53a56edca30c'

    response = await web_app_client.post(
        '/corp-reports/v1/reports/generate',
        params={'client_id': _CLIENT},
        json=_REQUEST_DATA,
        headers=_DEFAULT_HEADERS,
    )
    assert response.status == 200
    assert (await response.json()) == {'task_id': report_id}

    assert stq.corp_generate_orders_report.times_called == 1
    task = stq.corp_generate_orders_report.next_call()
    assert task['id'] == report_id
    assert task['args'] == []
    assert task['kwargs'] == {'report_id': report_id}

    db_report = await db.corp_reports.find_one({'_id': report_id})
    assert db_report == {
        '_id': report_id,
        'client_id': _CLIENT,
        'status': 'new',
        'report_type': 'orders_report',
        'requested_by': {
            'ip': '127.0.0.1',
            'passport_uid': _USER_UID,
            'yandex_login_pd_id': _USER_LOGIN_PD_ID,
        },
        'request_data': {
            'service': 'taxi',
            'department_id': None,
            'locale': 'he',
            'since': datetime.datetime(2020, 4, 30, 21, 0),
            'till': datetime.datetime(2020, 5, 31, 21, 0),
        },
        'report_file': None,
        'created': _NOW,
        'updated': _NOW,
    }


@pytest.mark.now(_NOW.isoformat())
async def test_idempotency(
        web_app_client, mock_personal, mock_corp_clients, db, stq,
):
    mock_corp_clients.data.get_client_response = _GET_CLIENT_RESPONSE

    report_id = '466a6158ae043734c53bc655e1474339'
    headers = copy.deepcopy(_DEFAULT_HEADERS)
    headers.pop('X-Idempotency-Token')
    headers['X-Idempotency-Token'] = '456'

    response = await web_app_client.post(
        '/corp-reports/v1/reports/generate',
        params={'client_id': _CLIENT},
        json=_REQUEST_DATA,
        headers=headers,
    )
    assert response.status == 200
    assert (await response.json()) == {'task_id': report_id}

    assert stq.corp_generate_orders_report.times_called == 0

    db_report = await db.corp_reports.find_one({'_id': report_id})
    assert db_report['status'] == 'complete'


@pytest.mark.now(_NOW.isoformat())
async def test_default_tz(
        web_app_client, mock_personal, mock_corp_clients, db,
):
    # Ответ без таймзоны
    mock_corp_clients.data.get_client_response = {'id': _CLIENT}
    report_id = '477e95476660a2f4359a53a56edca30c'

    response = await web_app_client.post(
        '/corp-reports/v1/reports/generate',
        params={'client_id': _CLIENT},
        json=_REQUEST_DATA,
        headers=_DEFAULT_HEADERS,
    )
    assert response.status == 200
    assert (await response.json()) == {'task_id': report_id}

    db_report = await db.corp_reports.find_one({'_id': report_id})
    assert db_report['request_data'] == {
        'service': 'taxi',
        'department_id': None,
        'locale': 'he',
        'since': datetime.datetime(2020, 4, 30, 21, 0),
        'till': datetime.datetime(2020, 5, 31, 21, 0),
    }


@pytest.mark.now(_NOW.isoformat())
async def test_acceptlang(
        web_app_client, mock_personal, mock_corp_clients, db, stq,
):
    mock_corp_clients.data.get_client_response = _GET_CLIENT_RESPONSE
    report_id = 'ca1b158f2a9a0d51e48065ca76e90e9f'
    headers = copy.deepcopy(_DEFAULT_HEADERS)
    headers.pop('X-Request-Language')
    headers['Accept-Language'] = 'en-US'

    response = await web_app_client.post(
        '/corp-reports/v1/reports/generate',
        params={'client_id': _CLIENT},
        json=_REQUEST_DATA,
        headers=headers,
    )
    assert response.status == 200
    assert (await response.json()) == {'task_id': report_id}

    assert stq.corp_generate_orders_report.times_called == 1

    db_report = await db.corp_reports.find_one({'_id': report_id})
    assert db_report['request_data']['locale'] == 'en'
