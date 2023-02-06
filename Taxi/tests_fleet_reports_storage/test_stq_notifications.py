import aiohttp.web


async def test_success(stq_runner, mockserver, testpoint):
    @testpoint('operation_not_found')
    def _tp_operation_not_found(data):
        pass

    @mockserver.json_handler('/dispatcher-access-control/v1/parks/users/list')
    async def _mock_dac(request):
        return aiohttp.web.json_response(
            {
                'users': [
                    {
                        'id': 'user_id_0',
                        'park_id': 'park_id_0',
                        'is_enabled': True,
                        'is_confirmed': True,
                        'is_superuser': False,
                        'is_usage_consent_accepted': False,
                        'email': 'test@yandex.ru',
                    },
                ],
                'limit': 1,
                'offset': 0,
            },
        )

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    async def _mock_fleet_parks(request):
        return {
            'parks': [
                {
                    'id': 'park_id_0',
                    'login': 'login',
                    'is_active': True,
                    'city_id': 'city',
                    'locale': 'en',
                    'is_billing_enabled': True,
                    'is_franchising_enabled': True,
                    'demo_mode': False,
                    'country_id': 'country_id',
                    'name': 'some park name',
                    'tz_offset': 4,
                    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
                },
            ],
        }

    @mockserver.json_handler('/personal/v1/emails/store')
    async def _mock_personal(request):
        return aiohttp.web.json_response(
            {'id': 'personal_id', 'value': 'personal_value'},
        )

    @mockserver.json_handler('/sticker/send/')
    async def _mock_sticker(request):
        return aiohttp.web.json_response()

    @mockserver.json_handler('/fleet-notifications/v1/notifications/create')
    async def _mock_notifications(request):
        return aiohttp.web.json_response()

    await stq_runner.fleet_reports_storage_notifications.call(
        task_id='1', args=['base_operation_00000000000000001'],
    )

    assert _tp_operation_not_found.times_called == 0
    assert _mock_sticker.times_called == 1


async def test_operation_not_found(stq_runner, testpoint):
    @testpoint('operation_not_found')
    def _operation_not_found(data):
        pass

    await stq_runner.fleet_reports_storage_notifications.call(
        task_id='1', args=['1'],
    )

    assert _operation_not_found.times_called == 1


async def test_operation_is_not_uploaded(stq_runner, testpoint):
    @testpoint('operation_is_not_uploaded')
    def _operation_is_not_uploaded(data):
        pass

    await stq_runner.fleet_reports_storage_notifications.call(
        task_id='1',
        args=['base_operation_00000000000000000'],
        expect_fail=True,
    )

    assert _operation_is_not_uploaded.times_called == 1


async def test_user_not_found(stq_runner, mockserver, testpoint):
    @testpoint('user_not_found')
    def _user_not_found(data):
        pass

    @mockserver.json_handler('/dispatcher-access-control/v1/parks/users/list')
    async def _mock_dac(request):
        return aiohttp.web.json_response(
            {'users': [], 'limit': 1, 'offset': 0},
        )

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    async def _mock_fleet_parks(request):
        return {
            'parks': [
                {
                    'id': 'park_id_0',
                    'login': 'login',
                    'is_active': True,
                    'city_id': 'city',
                    'locale': 'en',
                    'is_billing_enabled': True,
                    'is_franchising_enabled': True,
                    'demo_mode': False,
                    'country_id': 'country_id',
                    'name': 'some park name',
                    'tz_offset': 4,
                    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
                },
            ],
        }

    await stq_runner.fleet_reports_storage_notifications.call(
        task_id='1', args=['base_operation_00000000000000001'],
    )

    assert _user_not_found.times_called == 1


async def test_user_no_have_email(stq_runner, mockserver, testpoint):
    @testpoint('user_no_have_email')
    def _user_no_have_email(data):
        pass

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    async def _mock_fleet_parks(request):
        return {
            'parks': [
                {
                    'id': 'park_id_0',
                    'login': 'login',
                    'is_active': True,
                    'city_id': 'city',
                    'locale': 'en',
                    'is_billing_enabled': True,
                    'is_franchising_enabled': True,
                    'demo_mode': False,
                    'country_id': 'country_id',
                    'name': 'some park name',
                    'tz_offset': 4,
                    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
                },
            ],
        }

    @mockserver.json_handler('/dispatcher-access-control/v1/parks/users/list')
    async def _mock_dac(request):
        return aiohttp.web.json_response(
            {
                'users': [
                    {
                        'id': 'user_id_0',
                        'park_id': 'park_id_0',
                        'is_enabled': True,
                        'is_confirmed': True,
                        'is_superuser': False,
                        'is_usage_consent_accepted': False,
                    },
                ],
                'limit': 1,
                'offset': 0,
            },
        )

    await stq_runner.fleet_reports_storage_notifications.call(
        task_id='1', args=['base_operation_00000000000000001'],
    )

    assert _user_no_have_email.times_called == 1


async def test_park_not_found(stq_runner, mockserver, testpoint):
    @testpoint('park_not_found')
    def _park_not_found(data):
        pass

    @mockserver.json_handler('/dispatcher-access-control/v1/parks/users/list')
    async def _mock_dac(request):
        return aiohttp.web.json_response(
            {
                'users': [
                    {
                        'id': 'user_id_0',
                        'park_id': 'park_id_0',
                        'is_enabled': True,
                        'is_confirmed': True,
                        'is_superuser': False,
                        'is_usage_consent_accepted': False,
                        'email': 'test@yandex.ru',
                    },
                ],
                'limit': 1,
                'offset': 0,
            },
        )

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    async def _mock_fleet_parks(request):
        return {'parks': []}

    await stq_runner.fleet_reports_storage_notifications.call(
        task_id='1', args=['base_operation_00000000000000001'],
    )

    assert _park_not_found.times_called == 1


async def test_saas_no_notifications(stq_runner, mockserver, testpoint):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    async def _mock_fleet_parks(request):
        return {
            'parks': [
                {
                    'id': 'park_id_0',
                    'login': 'login',
                    'is_active': True,
                    'city_id': 'city',
                    'locale': 'en',
                    'is_billing_enabled': True,
                    'is_franchising_enabled': True,
                    'demo_mode': False,
                    'country_id': 'country_id',
                    'name': 'some park name',
                    'tz_offset': 4,
                    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
                    'specifications': ['saas'],
                },
            ],
        }

    @mockserver.json_handler('/dispatcher-access-control/v1/parks/users/list')
    async def _mock_dac(request):
        return aiohttp.web.json_response()

    @mockserver.json_handler('/personal/v1/emails/store')
    async def _mock_personal(request):
        return aiohttp.web.json_response()

    @mockserver.json_handler('/sticker/send/')
    async def _mock_sticker(request):
        return aiohttp.web.json_response()

    @mockserver.json_handler('/fleet-notifications/v1/notifications/create')
    async def _mock_notifications(request):
        return aiohttp.web.json_response()

    await stq_runner.fleet_reports_storage_notifications.call(
        task_id='1', args=['base_operation_00000000000000001'],
    )

    assert _mock_fleet_parks.times_called == 1
    assert _mock_dac.times_called == 0
    assert _mock_personal.times_called == 0
    assert _mock_sticker.times_called == 0
    assert _mock_notifications.times_called == 0
