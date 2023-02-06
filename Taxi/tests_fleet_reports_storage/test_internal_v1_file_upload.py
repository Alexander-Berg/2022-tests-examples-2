ENDPOINT = '/internal/v1/file/upload'
FILE_DATA = bytes('file_string_data', encoding='utf-8')


async def test_success(
        taxi_fleet_reports_storage, mockserver, pgsql, testpoint,
):
    @mockserver.handler('/tmp/base_operation_00000000000000000')
    def _mock_mds(request):
        assert request.content_type == 'application/pdf'
        if request.method == 'PUT':
            return mockserver.make_response('OK', 200)
        return mockserver.make_response('Wrong Method', 400)

    @testpoint('call_stq_notifications')
    def _call_stq_notifications(data):
        pass

    response = await taxi_fleet_reports_storage.put(
        ENDPOINT,
        params={
            'operation_id': 'base_operation_00000000000000000',
            'content_type': 'application/pdf',
        },
        data=FILE_DATA,
    )

    assert response.status_code == 200

    cursor = pgsql['fleet_reports'].cursor()
    cursor.execute(
        f"""
        SELECT status
        FROM fleet_reports_storage.operations
        WHERE id = \'base_operation_00000000000000000\'
        """,
    )
    assert cursor.fetchone()[0] == 'uploaded'

    assert _call_stq_notifications.times_called == 1


async def test_operation_not_found(taxi_fleet_reports_storage):
    response = await taxi_fleet_reports_storage.put(
        ENDPOINT,
        params={'operation_id': 'base_operation_10000000000000000'},
        data=FILE_DATA,
    )

    assert response.status_code == 404
    assert response.json() == {
        'code': 'OPERATION_NOT_FOUND',
        'message': 'Operation not found',
    }


async def test_operation_already_uploaded(
        taxi_fleet_reports_storage, testpoint,
):
    @testpoint('resend_request')
    def _resend_request(data):
        pass

    response = await taxi_fleet_reports_storage.put(
        ENDPOINT,
        params={'operation_id': 'base_operation_00000000000000001'},
        data=FILE_DATA,
    )

    assert response.status_code == 200

    assert _resend_request.times_called == 1


async def test_operation_is_not_new(taxi_fleet_reports_storage, testpoint):
    response = await taxi_fleet_reports_storage.put(
        ENDPOINT,
        params={'operation_id': 'base_operation_00000000000000002'},
        data=FILE_DATA,
    )

    assert response.status_code == 409
    assert response.json() == {
        'code': 'NOT_ALLOWED_STATUS',
        'message': 'Current status = "deleted". Need = "new"',
    }
