import datetime

import pytest


_NOW = datetime.datetime.utcnow().replace(microsecond=0)
_CLIENT_ID = 'client1'
_DEFAULT_HEADERS = {
    'Accept-Language': 'ru-RU',
    'X-Idempotency-Token': '123',
    'X-Real-IP': '127.0.0.1',
    'X-Yandex-UID': 'user1_uid',
    'X-Yandex-Login': 'user1',
}


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.config(LOCALES_CORP_SUPPORTED=['ru', 'he'])
async def test_act_reports_generate(web_app_client, db, stq, mock_personal):
    contract_id = 322223
    task_id = 'ce84e967cfe4bbc9f81a2abc72b8fb17'
    response = await web_app_client.post(
        '/corp-reports/v1/reports/act-generate',
        params={'client_id': _CLIENT_ID},
        json={'contract_id': contract_id, 'act_date': '2021-02'},
        headers=_DEFAULT_HEADERS,
    )
    assert response.status == 200
    assert (await response.json()) == {'task_id': task_id}

    assert stq.corp_generate_orders_report.times_called == 1
    task = stq.corp_generate_orders_report.next_call()
    assert task['id'] == task_id
    assert task['args'] == []
    assert task['kwargs'] == {'report_id': task_id}

    db_report = await db.corp_reports.find_one({'_id': task_id})
    assert db_report == {
        '_id': task_id,
        'client_id': _CLIENT_ID,
        'status': 'new',
        'report_type': 'acts_report',
        'requested_by': {
            'ip': '127.0.0.1',
            'passport_uid': 'user1_uid',
            'yandex_login_pd_id': 'user1_pd_id',
        },
        'request_data': {
            'contract_id': contract_id,
            'act_date': '2021-02',
            'department_id': None,
            'locale': 'ru',
        },
        'report_file': None,
        'created': _NOW,
        'updated': _NOW,
    }


@pytest.mark.now(_NOW.isoformat())
async def test_idempotency(web_app_client, db, stq, mock_personal):
    task_id = '74ba277042f8a3f833a10e383bffe266'
    response = await web_app_client.post(
        '/corp-reports/v1/reports/act-generate',
        params={'client_id': _CLIENT_ID},
        json={'contract_id': 2333, 'act_date': '2021-03'},
        headers=_DEFAULT_HEADERS,
    )
    assert response.status == 200
    assert (await response.json()) == {'task_id': task_id}

    assert stq.corp_generate_orders_report.times_called == 0

    db_report = await db.corp_reports.find_one({'_id': task_id})
    assert db_report['status'] == 'complete'
