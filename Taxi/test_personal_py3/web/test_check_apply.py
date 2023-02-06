import pytest
import yt.wrapper.errors as yt_errors


ROBOT = 'robot-taxi-tst-32415'


@pytest.mark.yt(static_table_data=['yt_pd_input_table.yaml'])
async def test_check(taxi_personal_py3_web, yt_client, yt_apply):
    try:
        yt_client.create('user', attributes={'name': ROBOT})
    except yt_errors.YtHttpResponseError:
        pass
    yt_client.set(
        '//home/taxi/unittests/services/personal-py3/@acl',
        [{'action': 'allow', 'subjects': [ROBOT], 'permissions': 'write'}],
    )
    response = await taxi_personal_py3_web.post(
        '/v1/check',
        json={
            'export_data_items': [
                {
                    'export_type': 'from_id_to_value',
                    'data_type': 'phones',
                    'yt_column_name': 'phone',
                },
            ],
            'ticket': 'testticket-1',
            'input_yt_table': '//home/testsuite/yt_pd_input_table',
            'output_table_ttl': 10,
        },
        headers={'X-Yandex-Login': 'test_login'},
    )
    assert response.status == 200


async def test_check_no_table(taxi_personal_py3_web):
    response = await taxi_personal_py3_web.post(
        '/v1/check',
        json={
            'export_data_items': [
                {
                    'export_type': 'from_id_to_value',
                    'data_type': 'phones',
                    'yt_column_name': 'phone',
                },
            ],
            'ticket': 'TESTTICKET-1',
            'input_yt_table': 'no_such_table',
        },
        headers={'X-Yandex-Login': 'test_login'},
    )
    assert response.status == 400
    body = await response.json()
    assert body['code'] == 'INPUT_TABLE_NOT_FOUND'


@pytest.mark.yt(static_table_data=['yt_pd_input_table.yaml'])
async def test_check_folder_instead_table(taxi_personal_py3_web):
    response = await taxi_personal_py3_web.post(
        '/v1/check',
        json={
            'export_data_items': [
                {
                    'export_type': 'from_id_to_value',
                    'data_type': 'phones',
                    'yt_column_name': 'phone',
                },
            ],
            'ticket': 'TESTTICKET-1',
            'input_yt_table': '//home/testsuite',
        },
        headers={'X-Yandex-Login': 'test_login'},
    )
    assert response.status == 400
    body = await response.json()
    assert body['code'] == 'WRONG_CYPRESS_TYPE'


@pytest.mark.yt(static_table_data=['yt_pd_input_table.yaml'])
async def test_check_no_column_in_table(taxi_personal_py3_web):
    response = await taxi_personal_py3_web.post(
        '/v1/check',
        json={
            'export_data_items': [
                {
                    'export_type': 'from_id_to_value',
                    'data_type': 'phones',
                    'yt_column_name': 'one_more_wrong_column',
                },
                {
                    'export_type': 'from_id_to_value',
                    'data_type': 'phones',
                    'yt_column_name': 'wrong_column_name',
                },
            ],
            'ticket': 'TESTTICKET-1',
            'input_yt_table': '//home/testsuite/yt_pd_input_table',
        },
        headers={'X-Yandex-Login': 'test_login'},
    )
    assert response.status == 400
    body = await response.json()
    assert body['code'] == 'COLUMNS_NOT_FOUND'


@pytest.mark.yt(static_table_data=['yt_pd_input_table.yaml'])
async def test_check_lack_of_permissions(
        taxi_personal_py3_web, yt_client, yt_apply,
):
    try:
        yt_client.create('user', attributes={'name': ROBOT})
    except yt_errors.YtHttpResponseError:
        pass
    yt_client.set(
        '//home/taxi/unittests/services/personal-py3/@acl',
        [{'action': 'allow', 'subjects': [ROBOT], 'permissions': 'read'}],
    )
    response = await taxi_personal_py3_web.post(
        '/v1/check',
        json={
            'export_data_items': [
                {
                    'export_type': 'from_id_to_value',
                    'data_type': 'phones',
                    'yt_column_name': 'phone',
                },
            ],
            'ticket': 'TESTTICKET-1',
            'input_yt_table': '//home/testsuite/yt_pd_input_table',
        },
        headers={'X-Yandex-Login': 'test_login'},
    )
    assert response.status == 403
    body = await response.json()
    assert body['code'] == 'LACK_OF_PERMISSIONS_TO_WRITE'


async def test_apply(taxi_personal_py3_web, yt_client, yt_apply, web_context):
    result = await web_context.pg.master_pool.fetch(
        'select * from personal_export.export_info '
        'where yandex_login = \'test_login\'',
    )
    assert not result

    column_data1 = {
        'export_type': 'from_id_to_value',
        'data_type': 'phones',
        'yt_column_name': 'column1',
    }
    column_data2 = {
        'export_type': 'from_id_to_value',
        'data_type': 'driver_licenses',
        'yt_column_name': 'column2',
    }
    response = await taxi_personal_py3_web.post(
        '/v1/apply',
        json={
            'export_data_items': [column_data1, column_data2],
            'ticket': 'TESTTICKET-1',
            'input_yt_table': '//home/testsuite/yt_pd_input_table',
            'output_table_ttl': 10,
        },
        headers={'X-Yandex-Login': 'test_login'},
    )
    result = await web_context.pg.master_pool.fetchrow(
        'select * from personal_export.export_info '
        'where yandex_login = \'test_login\'',
    )
    assert result['id'] == 1
    assert result['yandex_login'] == 'test_login'
    assert result['ticket'] == 'TESTTICKET-1'
    assert result['input_yt_table'] == '//home/testsuite/yt_pd_input_table'
    assert result['output_table_ttl'] == 10
    assert result['need_duplicate_columns']
    assert not result['show_export_status_column']

    columns_export_data = await web_context.pg.master_pool.fetch(
        'select export_type, data_type, yt_column_name '
        'from personal_export.export_columns_data '
        f'where export_id = {result["id"]} order by yt_column_name',
    )
    assert len(columns_export_data) == 2
    columns_list = [dict(item) for item in columns_export_data]
    assert columns_list[0] == column_data1
    assert columns_list[1] == column_data2
    assert response.status == 200


async def test_apply_wrong_ticket_format(taxi_personal_py3_web):
    response = await taxi_personal_py3_web.post(
        '/v1/apply',
        json={
            'export_data_items': [
                {
                    'export_type': 'from_id_to_value',
                    'data_type': 'phones',
                    'yt_column_name': 'test_yt_column_name',
                },
            ],
            'ticket': 'ticket_with_wrong_format_name',
            'input_yt_table': '//home/testsuite/yt_pd_input_table',
            'output_table_ttl': 10,
        },
        headers={'X-Yandex-Login': 'test_login'},
    )
    assert response.status == 400


async def test_apply_too_big_output_table_ttl(taxi_personal_py3_web):
    response = await taxi_personal_py3_web.post(
        '/v1/apply',
        json={
            'export_data_items': [
                {
                    'export_type': 'from_id_to_value',
                    'data_type': 'phones',
                    'yt_column_name': 'test_yt_column_name',
                },
            ],
            'ticket': 'TESTTICKET-1',
            'input_yt_table': '//home/testsuite/yt_pd_input_table',
            'output_table_ttl': 15,
        },
        headers={'X-Yandex-Login': 'test_login'},
    )
    assert response.status == 400


async def test_apply_too_small_output_table_ttl(taxi_personal_py3_web):
    response = await taxi_personal_py3_web.post(
        '/v1/apply',
        json={
            'export_data_items': [
                {
                    'export_type': 'from_id_to_value',
                    'data_type': 'phones',
                    'yt_column_name': 'test_yt_column_name',
                },
            ],
            'ticket': 'TESTTICKET-1',
            'input_yt_table': '//home/testsuite/yt_pd_input_table',
            'output_table_ttl': 0,
        },
        headers={'X-Yandex-Login': 'test_login'},
    )
    assert response.status == 400
