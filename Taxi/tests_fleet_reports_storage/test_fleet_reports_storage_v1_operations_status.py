ENDPOINT = '/fleet/reports-storage/v1/operations/status'
HEADERS = {
    'X-Park-ID': 'base_park_id_0',
    'X-Yandex-UID': '0',
    'X-Ya-User-Ticket-Provider': 'yandex',
}


async def test_success(taxi_fleet_reports_storage):
    response = await taxi_fleet_reports_storage.get(
        ENDPOINT,
        params={'operation_id': 'base_operation_00000000000000000'},
        headers=HEADERS,
    )

    assert response.status_code == 200
    assert response.json() == {'status': 'new'}


async def test_operation_not_found(taxi_fleet_reports_storage, testpoint):
    @testpoint('operation_not_found')
    def _operation_not_found(data):
        pass

    response = await taxi_fleet_reports_storage.get(
        ENDPOINT,
        params={'operation_id': 'base_operation_10000000000000000'},
        headers=HEADERS,
    )

    assert response.status_code == 404
    assert response.json() == {
        'code': 'OPERATION_NOT_FOUND',
        'message': 'Operation not found',
    }

    assert _operation_not_found.times_called == 1


async def test_user_is_not_operation_owner(
        taxi_fleet_reports_storage, testpoint,
):
    @testpoint('user_no_access_operation')
    def _user_no_access_operation(data):
        pass

    headers = HEADERS.copy()
    headers['X-Park-ID'] = '123'

    response = await taxi_fleet_reports_storage.get(
        ENDPOINT,
        params={'operation_id': 'base_operation_00000000000000000'},
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json() == {
        'code': 'OPERATION_NOT_FOUND',
        'message': 'Operation not found',
    }

    assert _user_no_access_operation.times_called == 1
