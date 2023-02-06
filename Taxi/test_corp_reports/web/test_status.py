import pytest

_CLIENT = 'client1'
_TASK_ID = '466a6158ae043734c53bc655e1474339'

_GET_CLIENT_RESPONSE = {'id': _CLIENT, 'tz': 'Europe/Moscow'}


async def test_base(web_app_client, mock_corp_clients, mock_personal):
    mock_corp_clients.data.get_client_response = _GET_CLIENT_RESPONSE

    response = await web_app_client.post(
        '/corp-reports/v1/reports/status',
        params={'client_id': _CLIENT},
        json={'task_id': _TASK_ID},
    )
    assert response.status == 200
    assert (await response.json()) == {
        'task_id': _TASK_ID,
        'status': 'complete',
        'request': {
            'service': 'taxi',
            'department_id': 'd1_1',
            'locale': 'ru',
            'since': '2020-01-01T03:00:00+03:00',
            'till': '2020-02-01T03:00:00+03:00',
        },
        'url': f'/api/1.0/client/client1/reports/report?report_id={_TASK_ID}',
        'created_at': '2020-02-05T15:34:00+03:00',
    }


async def test_with_author(web_app_client, mock_personal, mock_corp_clients):
    mock_corp_clients.data.get_client_response = _GET_CLIENT_RESPONSE

    task_id = '56d8cef306e974e25d38d7d85108475c'

    response = await web_app_client.post(
        '/corp-reports/v1/reports/status',
        params={'client_id': _CLIENT},
        json={'task_id': task_id},
    )
    assert response.status == 200
    assert response.headers['X-Yandex-Login'] == 'manager1_login'


@pytest.mark.parametrize(
    'task_id, client_id',
    [{'not_existed_id', _CLIENT}, {_TASK_ID, 'not_existed_client'}],
)
async def test_404(task_id, client_id, web_app_client):
    response = await web_app_client.post(
        '/corp-reports/v1/reports/status',
        params={'client_id': client_id},
        json={'task_id': task_id},
    )
    assert response.status == 404


async def test_new(web_app_client, mock_corp_clients, mock_personal):
    mock_corp_clients.data.get_client_response = _GET_CLIENT_RESPONSE

    response = await web_app_client.post(
        '/corp-reports/v1/reports/status',
        params={'client_id': _CLIENT},
        json={'task_id': '3334cef306e974e25d38d7d851084333'},
    )
    assert response.status == 200
    assert (await response.json())['status'] == 'new'


async def test_default_tz(web_app_client, mock_corp_clients, mock_personal):
    # Ответ без таймзоны
    mock_corp_clients.data.get_client_response = {'id': _CLIENT}

    response = await web_app_client.post(
        '/corp-reports/v1/reports/status',
        params={'client_id': _CLIENT},
        json={'task_id': _TASK_ID},
    )

    assert response.status == 200
    assert (await response.json())['request'] == {
        'service': 'taxi',
        'department_id': 'd1_1',
        'locale': 'ru',
        'since': '2020-01-01T03:00:00+03:00',
        'till': '2020-02-01T03:00:00+03:00',
    }


async def test_act(web_app_client, mock_corp_clients, mock_personal):
    task_id = '74ba277042f8a3f833a10e383bffe266'
    mock_corp_clients.data.get_client_response = _GET_CLIENT_RESPONSE

    response = await web_app_client.post(
        '/corp-reports/v1/reports/status',
        params={'client_id': _CLIENT},
        json={'task_id': task_id},
    )
    assert response.status == 200
    assert (await response.json()) == {
        'task_id': task_id,
        'status': 'complete',
        'request': {
            'act_date': '2021-03',
            'contract_id': 2333,
            'department_id': 'd1_1',
            'locale': 'ru',
        },
        'url': f'/api/1.0/client/client1/reports/report?report_id={task_id}',
        'created_at': '2020-02-05T15:35:00+03:00',
    }
