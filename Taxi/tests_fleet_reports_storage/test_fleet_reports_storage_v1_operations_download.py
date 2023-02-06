import pytest

ENDPOINT = '/fleet/reports-storage/v1/operations/download'
HEADERS = {
    'X-Park-ID': 'base_park_id_0',
    'X-Yandex-UID': '0',
    'X-Ya-User-Ticket-Provider': 'yandex',
}


@pytest.mark.now('2019-01-01T01:00:00+00:00')
async def test_success(taxi_fleet_reports_storage, mockserver):
    @mockserver.handler('/tmp/base_operation_00000000000000001')
    def _mock_mds(request):
        if request.method == 'GET':
            return mockserver.make_response('OK', 200)
        return mockserver.make_response('Wrong Method', 400)

    response = await taxi_fleet_reports_storage.get(
        ENDPOINT,
        params={'operation_id': 'base_operation_00000000000000001'},
        headers=HEADERS,
    )

    assert response.status_code == 200
    assert 'link' in response.json()
    assert response.json()['file_name'] == 'report_orders.csv'


@pytest.mark.now('2019-01-01T01:00:00+00:00')
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


@pytest.mark.now('2019-01-01T01:00:00+00:00')
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


@pytest.mark.now('2019-01-03T01:00:00+00:00')
async def test_operation_in_work(taxi_fleet_reports_storage):
    response = await taxi_fleet_reports_storage.get(
        ENDPOINT,
        params={'operation_id': 'base_operation_00000000000000000'},
        headers=HEADERS,
    )

    assert response.status_code == 409
    assert response.json() == {
        'code': 'OPERATION_IN_WORK',
        'message': 'Operation in work',
    }


@pytest.mark.now('2019-01-04T01:00:00+00:00')
async def test_operation_expired(taxi_fleet_reports_storage):
    response = await taxi_fleet_reports_storage.get(
        ENDPOINT,
        params={'operation_id': 'base_operation_00000000000000000'},
        headers=HEADERS,
    )

    assert response.status_code == 404
    assert response.json() == {
        'code': 'OPERATION_NOT_FOUND',
        'message': 'Operation expired',
    }


@pytest.mark.now('2019-01-02T01:00:00+00:00')
async def test_is_not_available_for_download(
        taxi_fleet_reports_storage, testpoint,
):
    @testpoint('operation_not_available_download')
    def _operation_not_available_download(data):
        pass

    response = await taxi_fleet_reports_storage.get(
        ENDPOINT,
        params={'operation_id': 'base_operation_00000000000000001'},
        headers=HEADERS,
    )

    assert response.status_code == 404
    assert response.json() == {
        'code': 'OPERATION_NOT_FOUND',
        'message': 'Operation not found',
    }

    assert _operation_not_available_download.times_called == 1


DELETTER_CONFIG = {
    'batch_size': 10,
    'enabled': True,
    'pg_timeout': 1000,
    'work_interval': 1,
    'available_time': 24,
    'operation_time': 72,
}


@pytest.mark.now('2019-01-02T00:00:00+00:00')
@pytest.mark.config(FLEET_REPORTS_STORAGE_FILE_DELETER=DELETTER_CONFIG)
async def test_operation_and_file_were_deleted_by_uploaded_at(
        taxi_fleet_reports_storage, mockserver, pgsql,
):
    @mockserver.handler('/tmp/base_operation_00000000000000001')
    def _mock_def_id(request):
        if request.method == 'DELETE':
            return mockserver.make_response('OK', 200)
        return mockserver.make_response('Wrong method', 400)

    await taxi_fleet_reports_storage.run_task('file-deleter-component')

    assert _mock_def_id.times_called > 0

    cursor = pgsql['fleet_reports'].cursor()
    cursor.execute(
        f"""
        SELECT status
        FROM fleet_reports_storage.operations
        """,
    )
    result = list(cursor.fetchall())
    assert result == [('new',), ('deleted',), ('deleted',)]


@pytest.mark.now('2019-01-04T00:00:00+00:00')
@pytest.mark.config(FLEET_REPORTS_STORAGE_FILE_DELETER=DELETTER_CONFIG)
async def test_operation_and_file_were_deleted_by_uploaded_at_and_created_at(
        taxi_fleet_reports_storage, mockserver, pgsql,
):
    @mockserver.handler('/tmp/base_operation_00000000000000000')
    def _mock_def_id0(request):
        if request.method == 'DELETE':
            return mockserver.make_response('OK', 200)
        return mockserver.make_response('Wrong method', 400)

    @mockserver.handler('/tmp/base_operation_00000000000000001')
    def _mock_def_id1(request):
        if request.method == 'DELETE':
            return mockserver.make_response('OK', 200)
        return mockserver.make_response('Wrong method', 400)

    await taxi_fleet_reports_storage.run_task('file-deleter-component')

    assert _mock_def_id0.times_called > 0
    assert _mock_def_id1.times_called > 0

    cursor = pgsql['fleet_reports'].cursor()
    cursor.execute(
        f"""
        SELECT status
        FROM fleet_reports_storage.operations
        """,
    )
    result = list(cursor.fetchall())
    assert result == [('deleted',), ('deleted',), ('deleted',)]


@pytest.mark.now('2019-01-01T10:00:00+00:00')
@pytest.mark.config(FLEET_REPORTS_STORAGE_FILE_DELETER=DELETTER_CONFIG)
async def test_operation_and_file_were_not_deleted(
        taxi_fleet_reports_storage, mockserver,
):
    @mockserver.handler('/tmp/base_operation_00000000000000000')
    def _mock_def_id0(request):
        return mockserver.make_response('Wrong request', 400)

    @mockserver.handler('/tmp/base_operation_00000000000000001')
    def _mock_def_id1(request):
        return mockserver.make_response('Wrong request', 400)

    await taxi_fleet_reports_storage.run_task('file-deleter-component')

    assert _mock_def_id0.times_called == 0 and _mock_def_id1.times_called == 0
