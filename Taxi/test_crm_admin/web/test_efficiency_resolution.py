import pytest

from crm_admin import storage


@pytest.mark.parametrize(
    'experiment_id, group_name, resolution, status',
    [('e1', 'g1', 'approved', 200), ('e2', 'g1', 'rejected', 200)],
)
async def test_efficiency_resolution(
        web_context,
        web_app_client,
        experiment_id,
        group_name,
        resolution,
        status,
):
    params = [
        {
            'experiment_id': experiment_id,
            'group_name': group_name,
            'resolution': resolution,
        },
    ]
    response = await web_app_client.post(
        '/v1/efficiency/resolution', json=params,
    )
    assert response.status == status

    if status == 200:
        db_resolutions = storage.DbResolution(web_context)
        saved_resolution = await db_resolutions.fetch_pushed_resolution(
            experiment_id, group_name,
        )
        assert saved_resolution == resolution
