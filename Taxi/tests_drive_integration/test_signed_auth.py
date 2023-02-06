import pytest

PARK_ID = 'db1'
DRIVER_PROFILE_ID = 'uuid1'


@pytest.mark.parametrize(
    'issue_status', ['not_present', 'in_progress', 'active'],
)
async def test_get_auth(taxi_drive_integration, pgsql, load, issue_status):
    queries = []
    if issue_status == 'in_progress':
        queries = [load('main_in_progress.sql')]
    elif issue_status == 'active':
        queries = [load('main_issued.sql')]

    pgsql['drive_integration'].apply_queries(queries)

    response = await taxi_drive_integration.get(
        '/internal/drive-integration/v1/signed_auth',
        params={'park_id': PARK_ID, 'driver_profile_id': DRIVER_PROFILE_ID},
    )
    assert response.status_code == 200

    assert response.json()['access_status'] == issue_status
    if issue_status == 'not_present':
        assert 'signed_auth' in response.json()
