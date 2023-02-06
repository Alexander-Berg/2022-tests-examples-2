import pytest


@pytest.mark.now('2018-9-17T12:40')
@pytest.mark.parametrize(
    ['extension'], [pytest.param('xls'), pytest.param('xlsx')],
)
@pytest.mark.parametrize(
    ['passport_mock', 'status', 'idempotency_token'],
    [pytest.param('client3', 200, 'export_v2_user_task_id')],
    indirect=['passport_mock'],
)
async def test_file_export(
        taxi_corp_real_auth_client,
        patch,
        passport_mock,
        status,
        idempotency_token,
        extension,
        db,
):
    @patch('taxi.stq.client.put')
    async def _put(*args, **kwargs):
        pass

    response = await taxi_corp_real_auth_client.post(
        '/2.0/users/file/export',
        params={'format': extension},
        headers={'X-Idempotency-Token': idempotency_token},
    )

    assert response.status == status
    response_json = await response.json()

    if response.status == 200:
        task_id = response_json['_id']

        db_item = await db.corp_long_tasks.find_one(
            {'_id': task_id, 'idempotency_token': idempotency_token},
        )
        assert db_item['task_args'] == {
            'format': extension,
            'department_id': 'dep1',
            'client_id': 'client3',
        }
        assert _put.calls


@pytest.mark.parametrize(
    ['passport_mock'], [pytest.param('client3')], indirect=['passport_mock'],
)
async def test_get_task(taxi_corp_real_auth_client, passport_mock):
    response = await taxi_corp_real_auth_client.get(
        '/2.0/users/export/status',
        params={'task_id': 'export_v2_user_task_id'},
    )

    assert response.status == 200
    response_json = await response.json()
    assert response_json == {
        'status': 'complete',
        'result': {
            'content_type': 'application/vnd.ms-excel',
            'file_name': 'result.xls',
            'mds_key': '598/5b1250a34b5044d7ac4525682f9a703b',
        },
    }


@pytest.mark.parametrize(
    ['passport_mock'], [pytest.param('client3')], indirect=['passport_mock'],
)
async def test_result(taxi_corp_real_auth_client, passport_mock):
    response = await taxi_corp_real_auth_client.get(
        '/2.0/users/export/result',
        params={'task_id': 'export_v2_user_task_id'},
    )

    assert response.status == 200
    assert (
        response.headers['X-Accel-Redirect']
        == '/proxy-mds/get-taxi/598/5b1250a34b5044d7ac4525682f9a703b'
    )
    assert (
        response.headers['Content-Disposition']
        == 'attachment; filename="result.xls"'
    )
    assert response.headers['Content-type'] == 'application/vnd.ms-excel'
