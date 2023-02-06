import pytest


async def test_delete_metric(web_app_client, db, atlas_blackbox_mock):
    all_count_before = await db.atlas_metrics_list.find().count()

    response = await web_app_client.delete(
        '/api/v2/metrics/requests_share_found',
    )

    assert response.status == 204

    deleted_count = await db.atlas_metrics_list.find(
        {'_id': 'requests_share_found'},
    ).count()
    all_count_after = await db.atlas_metrics_list.find().count()

    assert deleted_count == 0
    assert all_count_after == all_count_before - 1


@pytest.mark.parametrize(
    'username, expected_status',
    [
        ('omnipotent_user', 204),
        ('metrics_admin', 204),
        ('super_user', 204),
        ('main_user', 403),
        ('nonexisted_user', 403),
    ],
)
async def test_delete_metrics_permissions(
        username, expected_status, web_app_client, atlas_blackbox_mock,
):
    response = await web_app_client.delete(
        '/api/v2/metrics/requests_share_found',
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
async def test_delete_protected_edit_metric(
        username, expected_status, web_app_client, atlas_blackbox_mock,
):
    response = await web_app_client.delete(
        '/api/v2/metrics/z_edit_protected_metric',
    )

    assert response.status == expected_status
