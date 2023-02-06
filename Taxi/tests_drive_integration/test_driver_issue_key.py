import pytest

PARK_ID = 'db1'
DRIVER_PROFILE_ID = 'uuid1'
DRIVE_ID = 'drive_id1'

DRIVE_ENCODED_JWT = (
    'eyJhbGciOiJFUzM4NCIsInR5cCI6IkpXVCJ9.'
    'eyJwYXJrX2lkIjoiZGIxIiwiZHJpdmVyX3Byb'
    '2ZpbGVfaWQiOiJ1dWlkMSIsImRyaXZlX3VzZX'
    'JfaWQiOiJkcml2ZV9pZDEifQ.mHMSROvu7EwA'
    'sFtKngq3aM9eWVUaoziPjq7iypufXCl-hW3tJ'
    '8-tQg7y9QrTy53aMpma12BFnvRQ-Sr9BbxKu2'
    'ZNp4UWpGDBfdluUT9dyqVkHTyf4WG86nvuDV5'
    'doMTy'
)

HEADERS = {
    'X-Request-Application': 'taximeter',
    'X-Request-Platform': 'android',
    'X-Request-Application-Version': '9.07',
    'X-YaTaxi-Park-Id': PARK_ID,
    'X-YaTaxi-Driver-Profile-Id': DRIVER_PROFILE_ID,
    'Accept-Language': 'ru',
}


@pytest.mark.parametrize('drive_state', ['active', 'blocked'])
@pytest.mark.parametrize('is_new_driver', [True, False])
async def test_issue_key(
        taxi_drive_integration,
        stq,
        pgsql,
        load,
        mockserver,
        drive_state,
        is_new_driver,
):
    @mockserver.json_handler('admin-yandex-drive/user/info')
    def _mock_driver_info(request):
        return mockserver.make_response(
            json={'status': drive_state}, status=200,
        )

    queries = []
    if not is_new_driver:
        queries = [load('main.sql')]
    pgsql['drive_integration'].apply_queries(queries)

    response = await taxi_drive_integration.post(
        '/driver/v1/drive-integration/v1/issue_key',
        headers=HEADERS,
        json={'jwt': DRIVE_ENCODED_JWT},
    )

    if drive_state != 'active':
        assert response.status_code == 403
        assert response.json()['message'] == 'User is forbidden'
        assert stq.drive_integration_key_issue.times_called == 0
        return

    assert response.status_code == 200
    if is_new_driver:
        assert stq.drive_integration_key_issue.times_called == 1

        stq_data = stq.drive_integration_key_issue.next_call()
        assert stq_data['queue'] == 'drive_integration_key_issue'
        assert (
            stq_data['id']
            == PARK_ID + '_' + DRIVER_PROFILE_ID + '_' + DRIVE_ID + '_issue'
        )

        del stq_data['kwargs']['log_extra']
        assert stq_data['kwargs'] == {
            'park_id': PARK_ID,
            'driver_profile_id': DRIVER_PROFILE_ID,
            'yandex_drive_id': DRIVE_ID,
        }
    else:
        assert stq.drive_integration_key_issue.times_called == 0


async def test_issue_key_existing_driver(
        taxi_drive_integration, stq, pgsql, load, mockserver,
):
    @mockserver.json_handler('admin-yandex-drive/user/info')
    def _mock_driver_info(request):
        return mockserver.make_response(json={'status': 'active'}, status=200)

    queries = [load('main_existing.sql')]
    pgsql['drive_integration'].apply_queries(queries)

    response = await taxi_drive_integration.post(
        '/driver/v1/drive-integration/v1/issue_key',
        headers=HEADERS,
        json={'jwt': DRIVE_ENCODED_JWT},
    )

    assert response.status_code == 409
    assert response.json()['message'] == 'Access is already given to user'
    assert stq.drive_integration_key_issue.times_called == 0
