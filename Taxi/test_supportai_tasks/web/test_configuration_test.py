import pytest


@pytest.mark.pgsql('supportai_tasks', files=['sample_projects.sql'])
@pytest.mark.parametrize(
    ('task_id', 'num_rows', 'total_records'),
    [(7, 10, 12), (8, 1, 1), (20, 0, 0)],
)
async def test_smoke_get_configuration_test(
        web_app_client, task_id, num_rows, total_records,
):
    response = await web_app_client.get(
        f'/v1/configuration_test?task_id={task_id}&user_id=34&offset=0&limit=10',  # noqa: E501
    )
    assert response.status == 200

    response_json = await response.json()

    assert len(response_json['test_records']) == num_rows
    assert response_json['total_records'] == total_records


@pytest.mark.pgsql('supportai_tasks', files=['sample_projects.sql'])
async def test_get_not_equal_configuration_test(web_app_client):
    response = await web_app_client.get(
        '/v1/configuration_test?'
        'task_id=7&user_id=34&offset=0&limit=10&is_equal=false',
    )
    assert response.status == 200

    response_json = await response.json()

    assert len(response_json['test_records']) == 4
    assert response_json['total_records'] == 4


@pytest.mark.pgsql('supportai_tasks', files=['sample_projects.sql'])
async def test_configuration_test_record(web_app_client):
    response = await web_app_client.get(
        f'/v1/configuration_test?task_id=8&user_id=34&offset=0&limit=10',
    )
    assert response.status == 200

    response_json = await response.json()
    records = response_json['test_records']
    assert records

    record = records[0]

    assert record['id']
    assert record['task_id']
    assert record['request_text']
    assert record['is_equal']
    assert record['chat_id'] == '1'
    assert record.get('diff') is None


@pytest.mark.pgsql('supportai_tasks', files=['sample_projects.sql'])
async def test_configuration_test_diff(web_app_client):
    response = await web_app_client.get(
        f'/v1/configuration_test?task_id=9&user_id=34&offset=0&limit=10',
    )
    assert response.status == 200

    response_json = await response.json()
    records = response_json['test_records']
    assert records

    record = records[0]

    assert not record['is_equal']
    assert record.get('diff') is not None
    assert record['diff']['release']
    assert record['diff']['draft']
    assert record.get('chat_id') is None
