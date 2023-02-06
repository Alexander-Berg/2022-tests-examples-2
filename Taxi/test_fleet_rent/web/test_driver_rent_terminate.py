from fleet_rent.use_cases import driver_rent_terminate


USE_CASE_CALL = (
    'fleet_rent.use_cases.driver_rent_terminate.'
    'DriverRentTerminate.terminate'
)


async def test_terminate_404(web_app_client, driver_auth_headers, patch):
    @patch(USE_CASE_CALL)
    async def _terminate(rent_id: str, driver_id: str, driver_park_id: str):
        assert rent_id == 'bad_id'
        assert driver_id == 'driver_id'
        assert driver_park_id == 'driver_park_id'
        raise driver_rent_terminate.RentNotFound()

    response404 = await web_app_client.post(
        '/driver/v1/periodic-payments/rent/terminate',
        params={'rent_id': 'bad_id'},
        headers=driver_auth_headers,
    )
    assert response404.status == 404


async def test_terminate_409(web_app_client, driver_auth_headers, patch):
    @patch(USE_CASE_CALL)
    async def _terminate(rent_id: str, driver_id: str, driver_park_id: str):
        assert rent_id == 'rejected_record_id'
        assert driver_id == 'driver_id'
        assert driver_park_id == 'driver_park_id'
        raise driver_rent_terminate.RentCannotBeTerminated()

    response409 = await web_app_client.post(
        '/driver/v1/periodic-payments/rent/terminate',
        params={'rent_id': 'rejected_record_id'},
        headers=driver_auth_headers,
    )
    assert response409.status == 409


async def test_terminate_200(web_app_client, driver_auth_headers, patch):
    @patch(USE_CASE_CALL)
    async def _terminate(rent_id: str, driver_id: str, driver_park_id: str):
        assert rent_id == 'record_id'
        assert driver_id == 'driver_id'
        assert driver_park_id == 'driver_park_id'

    response200 = await web_app_client.post(
        '/driver/v1/periodic-payments/rent/terminate',
        params={'rent_id': 'record_id'},
        headers=driver_auth_headers,
    )
    assert response200.status == 200
