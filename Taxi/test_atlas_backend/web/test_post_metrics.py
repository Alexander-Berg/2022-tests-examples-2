import pytest


async def test_post_metrics_good(
        web_app_client, db, atlas_blackbox_mock, first_metric_dict_filtered,
):
    metrics_count_before = await db.atlas_metrics_list.find().count()

    test_metric_dict = first_metric_dict_filtered
    test_metric_dict['_id'] = test_metric_dict['id'] = 'requests_share_burntt'
    test_metric_dict['target'] = 0.15

    response = await web_app_client.post(
        '/api/v2/metrics', json=test_metric_dict,
    )

    assert response.status == 201

    metrics_count_after = await db.atlas_metrics_list.find().count()
    assert metrics_count_after == metrics_count_before + 1

    new_metric = await db.atlas_metrics_list.find_one(
        {'_id': 'requests_share_burntt'},
    )
    assert new_metric['target'] == 0.15


async def test_post_metrics_bad(
        web_app_client, db, atlas_blackbox_mock, first_metric_dict_filtered,
):
    test_metric_dict = first_metric_dict_filtered

    response = await web_app_client.post(
        '/api/v2/metrics', json=test_metric_dict,
    )

    assert response.status == 400
    content = await response.json()

    assert content['code'] == 'BadRequest::MetricAlreadyExists'
    assert (
        content['message']
        == 'Metric with given "_id" already exists. Use PUT method to replace'
    )


@pytest.mark.parametrize(
    'username, expected_status',
    [('omnipotent_user', 201), ('super_user', 201), ('metrics_admin', 403)],
)
async def test_post_metrics_with_protected_edit(
        username,
        expected_status,
        web_app_client,
        atlas_blackbox_mock,
        first_metric_dict_filtered,
):
    first_metric_dict_filtered['_id'] = first_metric_dict_filtered[
        'id'
    ] = 'new_metric'
    first_metric_dict_filtered['protected_edit'] = True
    response = await web_app_client.post(
        '/api/v2/metrics', json=first_metric_dict_filtered,
    )

    assert response.status == expected_status


@pytest.mark.parametrize(
    'username, expected_status',
    [
        ('omnipotent_user', 201),
        ('metrics_admin', 201),
        ('super_user', 201),
        ('main_user', 403),
        ('nonexisted_user', 403),
    ],
)
async def test_post_metrics_permissions(
        username,
        expected_status,
        web_app_client,
        atlas_blackbox_mock,
        first_metric_dict_filtered,
):
    first_metric_dict_filtered['_id'] = first_metric_dict_filtered[
        'id'
    ] = 'requests_share_burntt'
    response = await web_app_client.post(
        '/api/v2/metrics', json=first_metric_dict_filtered,
    )

    assert response.status == expected_status


async def test_post_metric_unknown_view_group(
        web_app_client, atlas_blackbox_mock, first_metric_dict_filtered,
):
    data = first_metric_dict_filtered
    data['_id'] = data['id'] = 'new_metric_id'
    data['protected_view_group'] = 'unknown_view_group'
    response = await web_app_client.post('/api/v2/metrics', json=data)

    assert response.status == 400


async def test_post_metric_chyt(
        web_app_client, atlas_blackbox_mock, first_metric_dict_filtered,
):
    data = first_metric_dict_filtered
    data['_id'] = data['id'] = 'requests_share_burntt'
    data['connection_type'] = 'chyt'
    data['clique_alias'] = '*atlas_chyt'
    data['chyt_cluster'] = 'hahn'
    response = await web_app_client.post('/api/v2/metrics', json=data)
    assert response.status == 201


async def test_post_metric_chyt_invalid(
        web_app_client, atlas_blackbox_mock, first_metric_dict_filtered,
):
    data = first_metric_dict_filtered
    data['_id'] = data['id'] = 'requests_share_burntt'
    data['connection_type'] = 'chyt'
    data['chyt_cluster'] = 'hahn'
    response = await web_app_client.post('/api/v2/metrics', json=data)
    assert response.status == 400
