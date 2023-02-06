import pytest


async def test_put_metric(
        web_app_client, db, atlas_blackbox_mock, first_metric_dict_filtered,
):
    documents_count_before = await db.atlas_metrics_list.find().count()

    test_metric_dict = first_metric_dict_filtered
    test_metric_dict['table'] = 'new_table_name'
    del test_metric_dict['database']

    response = await web_app_client.put(
        '/api/v2/metrics/requests_share_burnt', json=test_metric_dict,
    )

    assert response.status == 204

    documents_count_after = await db.atlas_metrics_list.find().count()
    assert documents_count_after == documents_count_before

    changed_document = await db.atlas_metrics_list.find_one(
        {'_id': 'requests_share_burnt'},
    )
    assert changed_document['table'] == 'new_table_name'


async def test_put_metric_nonexists(
        web_app_client, atlas_blackbox_mock, first_metric_dict_filtered,
):
    test_metric_dict = first_metric_dict_filtered
    test_metric_dict['_id'] = 'requests_share_burntt'

    response = await web_app_client.put(
        '/api/v2/metrics/requests_share_burntt', json=test_metric_dict,
    )

    assert response.status == 400
    content = await response.json()
    assert content['code'] == 'NotFound'
    assert content['message'] == 'Metric was not found'


async def test_put_metric_differ_id(
        web_app_client, atlas_blackbox_mock, first_metric_dict_filtered,
):
    test_metric_dict = first_metric_dict_filtered
    test_metric_dict['_id'] = 'requests_share_burntt'

    response = await web_app_client.put(
        '/api/v2/metrics/requests_share_burnt', json=test_metric_dict,
    )

    assert response.status == 400
    content = await response.json()
    assert content['code'] == 'BadRequest::QueryAndBodyMetricIDMismatch'
    assert (
        content['message'] == 'different "_id" provided in query path and body'
    )


@pytest.mark.config(
    ATLAS_METRICS_RESTRICTION_GROUPS={
        'view_groups': [
            {'en_name': 'CI+KD', 'id': 'ci_kd', 'ru_name': 'CI+KD'},
        ],
    },
)
@pytest.mark.parametrize(
    'username, protected_edit, view_group, expected_status',
    [
        ('omnipotent_user', False, None, 204),
        ('metrics_admin', False, None, 204),
        ('super_user', False, None, 204),
        ('main_user', False, None, 403),
        ('nonexisted_user', False, None, 403),
        ('super_user', True, None, 204),
        ('super_user', False, 'ci_kd', 204),
        ('metrics_admin', True, None, 403),
        ('metrics_admin', False, 'ci_kd', 403),
    ],
)
async def test_put_metrics_permissions(
        username,
        protected_edit,
        view_group,
        expected_status,
        web_app_client,
        atlas_blackbox_mock,
        first_metric_dict_filtered,
):
    data = first_metric_dict_filtered
    data['protected_edit'] = protected_edit
    data['protected_view_group'] = view_group
    response = await web_app_client.put(
        '/api/v2/metrics/requests_share_burnt', json=data,
    )

    assert response.status == expected_status


@pytest.mark.parametrize(
    'username, expected_status',
    [
        ('omnipotent_user', 204),
        ('metrics_admin', 403),
        ('super_user', 204),
        ('main_user', 403),
        ('nonexisted_user', 403),
        ('metrics_edit_protected_user', 204),
    ],
)
async def test_put_metric_edit_protected(
        username,
        expected_status,
        web_app_client,
        atlas_blackbox_mock,
        first_metric_dict_filtered,
):
    data = first_metric_dict_filtered
    data['_id'] = data['id'] = 'z_edit_protected_metric'
    response = await web_app_client.put(
        '/api/v2/metrics/z_edit_protected_metric', json=data,
    )

    assert response.status == expected_status


async def test_put_metric_unknown_view_group(
        web_app_client, atlas_blackbox_mock, first_metric_dict_filtered,
):
    data = first_metric_dict_filtered
    data['protected_view_group'] = 'unknown_view_group'
    response = await web_app_client.put(
        '/api/v2/metrics/requests_share_burnt',
        json=first_metric_dict_filtered,
    )
    assert response.status == 400
