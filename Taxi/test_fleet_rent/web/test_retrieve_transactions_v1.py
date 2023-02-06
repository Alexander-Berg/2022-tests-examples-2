import aiohttp.web
import pytest

TAXIMETER_BACKEND_FLEET_RENT = {
    'transaction.withhold': {
        'ru': 'Запланировано списание №{serial_id} с водителя за {asset}',
    },
    'transaction.withdraw': {
        'ru': 'Списание №{serial_id} с водителя за {asset}',
    },
    'transaction.cancel_wo_user': {
        'ru': 'Отмена задолженности по списанию №{serial_id} {date} в {time}',
    },
    'transaction.cancel_with_user': {
        'ru': (
            'Отмена задолженности по списанию №{serial_id} '
            'Пользователь {user} {date} в {time}'
        ),
    },
    'rent_asset_other_chair': {'ru': 'Кресло'},
    'rent_asset_other_deposit': {'ru': 'Депозит'},
    'rent_asset_other_device': {'ru': 'Устройство'},
    'rent_asset_other_misc': {'ru': 'Прочее'},
}
TARIFF = {
    'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$$CURRENCY$'},
    'currency_sign.rub': {'ru': '₽'},
}
CITIES = {'Москва': {'ru': 'Москва'}}


@pytest.mark.parametrize(
    'rent_id,service_file,'
    'billing_reports_balances_stub_file,billing_reports_journal_stub_file',
    [
        [
            'a0068704940d49fe80e3bb2e04ad5d73',
            'service_success.json',
            'billing_reports_balances_success.json',
            'billing_reports_journal_success.json',
        ],
        [
            '2114fa2747f8484ab0560fa35bb8b501',
            'service_success_fixed_order_id.json',
            'billing_reports_balances_success_fixed_order_id.json',
            'billing_reports_journal_success_fixed_order_id.json',
        ],
        [
            '2114fa2747f8484ab0560fa35bb8b501',
            'service_success_cancel_data.json',
            'billing_reports_balances_success_fixed_order_id.json',
            'billing_reports_journal_success_cancel_data.json',
        ],
        [
            'a0068704940d49fe80e3bb2e04ad5d73',
            'service_success_empty_cursor.json',
            'billing_reports_balances_success.json',
            'billing_reports_journal_success_empty_cursor.json',
        ],
    ],
)
@pytest.mark.translations(
    taximeter_backend_fleet_rent=TAXIMETER_BACKEND_FLEET_RENT,
    tariff=TARIFF,
    cities=CITIES,
)
@pytest.mark.pgsql('fleet_rent', files=['init_db.sql'])
@pytest.mark.now('2020-07-17T14:31:01.467800+03:00')
async def test_success(
        web_app_client,
        load_json,
        mock_billing_reports,
        mock_dispatcher_access_control,
        mock_fleet_vehicles,
        mock_fleet_parks,
        mock_parks_replica,
        mock_billing_replication,
        rent_id,
        service_file,
        billing_reports_balances_stub_file,
        billing_reports_journal_stub_file,
        patch,
):
    @patch(
        'fleet_rent.components.currency_provider.'
        'CurrencyProvider.get_park_external_currency',
    )
    async def _get_park_external_currency(park_id: str, now):
        return 'RUB'

    service_stub = load_json(service_file)
    billing_reports_balances_stub = load_json(
        billing_reports_balances_stub_file,
    )
    billing_reports_journal_stub = load_json(billing_reports_journal_stub_file)

    @mock_billing_reports('/v1/balances/select')
    async def _v1_balances_select(request):
        assert request.json == billing_reports_balances_stub['request']
        return aiohttp.web.json_response(
            billing_reports_balances_stub['response'],
        )

    @mock_billing_reports('/v2/journal/select')
    async def _v1_journal_select(request):
        assert request.json == billing_reports_journal_stub['request']
        return aiohttp.web.json_response(
            billing_reports_journal_stub['response'],
        )

    @mock_fleet_vehicles('/v1/vehicles/retrieve')
    async def _v1_vehicles_retrieve(request):
        return {
            'vehicles': [
                {
                    'data': {'brand': 'Volvo', 'model': 'XC60'},
                    'park_id_car_id': (
                        '7ad36bc7560449998acbe2c57a75c293_car_id1'
                    ),
                },
            ],
        }

    @mock_fleet_parks('/v1/parks/list')
    async def _v1_parks_list(request):
        return {
            'parks': [
                {
                    'id': '7ad36bc7560449998acbe2c57a75c293',
                    'login': 'park_login',
                    'name': 'Sea',
                    'is_active': True,
                    'city_id': 'Gotham',
                    'locale': 'ru',
                    'is_billing_enabled': True,
                    'is_franchising_enabled': True,
                    'country_id': 'RUR',
                    'demo_mode': False,
                    'provider_config': {'type': 'none', 'clid': '555'},
                    'tz_offset': 5,
                    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
                },
            ],
        }

    @mock_fleet_parks('/v1/parks/contacts/retrieve')
    async def _v1_parks_contacts_retrieve(request):
        return {
            'drivers': {
                'address': 'address',
                'address_coordinates': {'lon': '1.2', 'lat': '2.1'},
                'email': 'email',
                'phone': 'phone',
            },
        }

    @mock_parks_replica('/v1/parks/billing_client_id/retrieve')
    async def _v1_parks_billing_client_id_retrieve(request):
        return {'billing_client_id': 'p_billing_client_id'}

    @mock_billing_replication('/person/')
    async def _person(request):
        return [{'ID': 'person_id', 'inn': 'my_inn'}]

    @mock_dispatcher_access_control('/v1/parks/users/list')
    async def _dac_park_users_list(request):
        assert request.json == {
            'offset': 0,
            'limit': 1,
            'query': {
                'park': {'id': '7ad36bc7560449998acbe2c57a75c293'},
                'user': {'passport_uid': ['some_passport_uid']},
            },
        }
        return {
            'users': [
                {
                    'id': 'some',
                    'is_confirmed': True,
                    'is_enabled': True,
                    'is_superuser': False,
                    'is_usage_consent_accepted': True,
                    'park_id': request.json['query']['park']['id'],
                    'passport_uid': 'some_passport_uid',
                    'display_name': 'Hellow Orld!',
                },
            ],
            'offset': 0,
            'limit': 1,
        }

    response = await web_app_client.post(
        '/fleet/rent/v1/park/rents/transactions',
        headers={
            'Accept-Language': 'ru',
            'X-Ya-User-Ticket': 'user_ticket',
            'X-Ya-User-Ticket-Provider': 'yandex',
            'X-Yandex-Login': 'abacaba',
            'X-Yandex-UID': '123',
            'X-Park-Id': '7ad36bc7560449998acbe2c57a75c293',
            'X-Real-IP': '127.0.0.1',
        },
        json=service_stub['request'],
    )

    assert response.status == 200, await response.text()

    data = await response.json()
    assert data == service_stub['response']


@pytest.mark.pgsql('fleet_rent', files=['init_db.sql'])
async def test_not_found(
        web_app_client, load_json, mock_billing_reports, patch,
):
    @patch(
        'fleet_rent.components.currency_provider.'
        'CurrencyProvider.get_park_external_currency',
    )
    async def _get_park_external_currency(park_id: str, now):
        return 'RUB'

    response = await web_app_client.post(
        '/fleet/rent/v1/park/rents/transactions',
        headers={
            'Accept-Language': 'ru',
            'X-Ya-User-Ticket': 'user_ticket',
            'X-Ya-User-Ticket-Provider': 'yandex',
            'X-Yandex-Login': 'abacaba',
            'X-Yandex-UID': '123',
            'X-Park-Id': 'park_id',
            'X-Real-IP': '127.0.0.1',
        },
        json={'limit': 25, 'rent_id': 'rent_id'},
    )

    assert response.status == 404, await response.text()


@pytest.mark.parametrize(
    'rent_id,service_file,'
    'billing_reports_balances_stub_file,billing_reports_journal_stub_file',
    [
        [
            'a0068704940d49fe80e3bb2e04ad5d73',
            'service_success_empty_cursor.json',
            'billing_reports_balances_success.json',
            'billing_reports_journal_success_empty_cursor.json',
        ],
    ],
)
@pytest.mark.translations(
    taximeter_backend_fleet_rent=TAXIMETER_BACKEND_FLEET_RENT,
    tariff=TARIFF,
    cities=CITIES,
)
@pytest.mark.pgsql('fleet_rent', files=['init_db_misc.sql'])
@pytest.mark.now('2020-07-17T14:31:01.467800+03:00')
async def test_success_misc(
        web_app_client,
        load_json,
        mock_billing_reports,
        mock_dispatcher_access_control,
        mock_fleet_vehicles,
        mock_fleet_parks,
        mock_parks_replica,
        mock_billing_replication,
        rent_id,
        service_file,
        billing_reports_balances_stub_file,
        billing_reports_journal_stub_file,
        patch,
):
    @patch(
        'fleet_rent.components.currency_provider.'
        'CurrencyProvider.get_park_external_currency',
    )
    async def _get_park_external_currency(park_id: str, now):
        return 'RUB'

    service_stub = load_json(service_file)
    descr_withdraw = 'Списание №5701 с водителя за непонятно что Прочее'
    descr_withhold = (
        'Запланировано списание №5701 с водителя за непонятно что Прочее'
    )
    tranactions = service_stub['response']['transactions']
    tranactions[0]['description'] = descr_withdraw
    tranactions[1]['description'] = descr_withdraw
    tranactions[3]['description'] = descr_withhold

    billing_reports_balances_stub = load_json(
        billing_reports_balances_stub_file,
    )
    billing_reports_journal_stub = load_json(billing_reports_journal_stub_file)

    @mock_billing_reports('/v1/balances/select')
    async def _v1_balances_select(request):
        assert request.json == billing_reports_balances_stub['request']
        return aiohttp.web.json_response(
            billing_reports_balances_stub['response'],
        )

    @mock_billing_reports('/v2/journal/select')
    async def _v1_journal_select(request):
        assert request.json == billing_reports_journal_stub['request']
        return aiohttp.web.json_response(
            billing_reports_journal_stub['response'],
        )

    @mock_fleet_vehicles('/v1/vehicles/retrieve')
    async def _v1_vehicles_retrieve(request):
        return {
            'vehicles': [
                {
                    'data': {'brand': 'Volvo', 'model': 'XC60'},
                    'park_id_car_id': (
                        '7ad36bc7560449998acbe2c57a75c293_car_id1'
                    ),
                },
            ],
        }

    @mock_fleet_parks('/v1/parks/list')
    async def _v1_parks_list(request):
        return {
            'parks': [
                {
                    'id': '7ad36bc7560449998acbe2c57a75c293',
                    'login': 'park_login',
                    'name': 'Sea',
                    'is_active': True,
                    'city_id': 'Gotham',
                    'locale': 'ru',
                    'is_billing_enabled': True,
                    'is_franchising_enabled': True,
                    'country_id': 'RUR',
                    'demo_mode': False,
                    'provider_config': {'type': 'none', 'clid': '555'},
                    'tz_offset': 5,
                    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
                },
            ],
        }

    @mock_fleet_parks('/v1/parks/contacts/retrieve')
    async def _v1_parks_contacts_retrieve(request):
        return {
            'drivers': {
                'address': 'address',
                'address_coordinates': {'lon': '1.2', 'lat': '2.1'},
                'email': 'email',
                'phone': 'phone',
            },
        }

    @mock_parks_replica('/v1/parks/billing_client_id/retrieve')
    async def _v1_parks_billing_client_id_retrieve(request):
        return {'billing_client_id': 'p_billing_client_id'}

    @mock_billing_replication('/person/')
    async def _person(request):
        return [{'ID': 'person_id', 'inn': 'my_inn'}]

    @mock_dispatcher_access_control('/v1/parks/users/list')
    async def _dac_park_users_list(request):
        assert request.json == {
            'offset': 0,
            'limit': 1,
            'query': {
                'park': {'id': '7ad36bc7560449998acbe2c57a75c293'},
                'user': {'passport_uid': ['some_passport_uid']},
            },
        }
        return {
            'users': [
                {
                    'id': 'some',
                    'is_confirmed': True,
                    'is_enabled': True,
                    'is_superuser': False,
                    'is_usage_consent_accepted': True,
                    'park_id': request.json['query']['park']['id'],
                    'passport_uid': 'some_passport_uid',
                    'display_name': 'Hellow Orld!',
                },
            ],
            'offset': 0,
            'limit': 1,
        }

    response = await web_app_client.post(
        '/fleet/rent/v1/park/rents/transactions',
        headers={
            'Accept-Language': 'ru',
            'X-Ya-User-Ticket': 'user_ticket',
            'X-Ya-User-Ticket-Provider': 'yandex',
            'X-Yandex-Login': 'abacaba',
            'X-Yandex-UID': '123',
            'X-Park-Id': '7ad36bc7560449998acbe2c57a75c293',
            'X-Real-IP': '127.0.0.1',
        },
        json=service_stub['request'],
    )

    assert response.status == 200, await response.text()

    data = await response.json()
    assert data == service_stub['response']
