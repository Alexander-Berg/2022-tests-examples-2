import pytest


@pytest.mark.pgsql(
    'supportai_tasks', files=['sample_projects.sql', 'sample_results.sql'],
)
async def test_get_clustering_results(web_app_client):
    response = await web_app_client.get(
        '/v1/clustering/overview?'
        'user_id=34&project_slug=ya_market&header_count=1',
    )

    assert response.status == 200
    response_json = await response.json()

    assert len(response_json['clusters']) == 2
    assert {1} == {
        len(response_json['clusters'][0]['cluster_items']),
        len(response_json['clusters'][1]['cluster_items']),
    }
    assert {1, 2} == {
        response_json['clusters'][0]['total_items'],
        response_json['clusters'][1]['total_items'],
    }

    response = await web_app_client.get(
        '/v1/clustering/results?'
        'user_id=34&project_slug=ya_market&cluster_number=1&offset=1&limit=2',
    )

    assert response.status == 200
    response_json = await response.json()

    assert len(response_json['cluster_items']) == 1
    assert response_json['cluster_items'][0]['id'] == '3'

    response = await web_app_client.get(
        '/v1/clustering/results?'
        'user_id=34&project_slug=ya_market&cluster_number=2&offset=1&limit=2',
    )

    assert response.status == 200
    response_json = await response.json()

    assert not response_json['cluster_items']


@pytest.mark.pgsql(
    'supportai_tasks', files=['sample_projects.sql', 'sample_results.sql'],
)
async def test_clustering_can_run(web_app_client):
    response = await web_app_client.get(
        '/v1/clustering/overview?'
        'user_id=34&project_slug=ya_market&header_count=1',
    )

    assert response.status == 200
    response_json = await response.json()

    assert len(response_json['clusters']) == 2
    assert response_json['can_run'] is False
    assert response_json['created_at'] == '2021-01-01T15:00:00+03:00'
