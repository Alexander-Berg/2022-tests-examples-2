import pytest

from tests_signal_device_api_admin import utils
from tests_signal_device_api_admin import web_common

TEXT_CSV = 'text/csv'

URL_TEMPLATE = (
    'https://fleet.yandex-team.ru/signalq/stream/{}/{}?grouping={}&park_id={}'
)

ALL_EVENTS_BY_VEHICLE = (
    'время события,тип события,скорость,водитель,номер устройства,резолюция,'
    'номер автомобиля,позывной автомобиля,ссылка на событие'
    '\r\n2020-02-26T23:55:00,на легком чилле,,Петров Иван,AB2,,'
    'О122КХ178,test,'
    'https://fleet.yandex-team.ru/signalq/stream/'
    'all/'
    '7f5a516f-29ff-4ebe-93eb-465bf0124e85'
    '?grouping=vehicles'
    '&park_id=p1'
    '\r\n2020-02-27T11:02:00,хз где,89.437895,Иванов Петр,AB2,,,,'
    'https://fleet.yandex-team.ru/signalq/stream/'
    'all/'
    '5f5a516f-29ff-4ebe-93eb-465bf0124e85'
    '?grouping=vehicles'
    '&park_id=p1'
    '\r\n2020-02-27T11:05:00,хз где,89.437895,Иванов Петр,AB1,,,,'
    'https://fleet.yandex-team.ru/signalq/stream/'
    'all/'
    '6f5a516f-29ff-4ebe-93eb-465bf0124e85'
    '?grouping=vehicles'
    '&park_id=p1'
    '\r\n2020-02-27T12:00:00,на чилле,34.437895,Иванов Петр,AB1,это кто,,,'
    'https://fleet.yandex-team.ru/signalq/stream/'
    'all/'
    '3f5a516f-29ff-4ebe-93eb-465bf0124e85'
    '?grouping=vehicles'
    '&park_id=p1'
    '\r\n2020-02-27T12:00:00,на чилле,34.437895,Петров Иван,AB2,,,,'
    'https://fleet.yandex-team.ru/signalq/stream/'
    'all/'
    '8f5a516f-29ff-4ebe-93eb-465bf0124e85'
    '?grouping=vehicles'
    '&park_id=p1'
    '\r\n2020-02-27T12:00:00,на чилле,34.437895,,AB3,privet!,,,'
    'https://fleet.yandex-team.ru/signalq/stream/'
    'all/'
    '9f5a516f-29ff-4ebe-93eb-465bf0124e85'
    '?grouping=vehicles'
    '&park_id=p1'
    '\r\n2020-02-27T13:02:00,хз где,89.437895,Иванов Петр,AB1,'
    'все норм,,,'
    'https://fleet.yandex-team.ru/signalq/stream/'
    'all/'
    '4f5a516f-29ff-4ebe-93eb-465bf0124e85'
    '?grouping=vehicles'
    '&park_id=p1'
)

ALL_EVENTS_BY_DRIVER = (
    'время события,тип события,скорость,водитель,номер устройства,резолюция,'
    'номер автомобиля,позывной автомобиля,ссылка на событие'
    '\r\n2020-02-26T23:55:00,на легком чилле,,Петров Иван,AB2,,'
    'О122КХ178,test,'
    'https://fleet.yandex-team.ru/signalq/stream/'
    'all/'
    '7f5a516f-29ff-4ebe-93eb-465bf0124e85'
    '?grouping=drivers'
    '&park_id=p1'
    '\r\n2020-02-27T11:02:00,хз где,89.437895,Иванов Петр,AB2,,,,'
    'https://fleet.yandex-team.ru/signalq/stream/'
    'all/'
    '5f5a516f-29ff-4ebe-93eb-465bf0124e85'
    '?grouping=drivers'
    '&park_id=p1'
    '\r\n2020-02-27T11:05:00,хз где,89.437895,Иванов Петр,AB1,,,,'
    'https://fleet.yandex-team.ru/signalq/stream/'
    'all/'
    '6f5a516f-29ff-4ebe-93eb-465bf0124e85'
    '?grouping=drivers'
    '&park_id=p1'
    '\r\n2020-02-27T12:00:00,на чилле,34.437895,Иванов Петр,AB1,это кто,,,'
    'https://fleet.yandex-team.ru/signalq/stream/'
    'all/'
    '3f5a516f-29ff-4ebe-93eb-465bf0124e85'
    '?grouping=drivers'
    '&park_id=p1'
    '\r\n2020-02-27T12:00:00,на чилле,34.437895,Петров Иван,AB2,,,,'
    'https://fleet.yandex-team.ru/signalq/stream/'
    'all/'
    '8f5a516f-29ff-4ebe-93eb-465bf0124e85'
    '?grouping=drivers'
    '&park_id=p1'
    '\r\n2020-02-27T12:00:00,на чилле,34.437895,,AB3,privet!,,,'
    'https://fleet.yandex-team.ru/signalq/stream/'
    'all/'
    '9f5a516f-29ff-4ebe-93eb-465bf0124e85'
    '?grouping=drivers'
    '&park_id=p1'
    '\r\n2020-02-27T13:02:00,хз где,89.437895,Иванов Петр,AB1,'
    'все норм,,,'
    'https://fleet.yandex-team.ru/signalq/stream/'
    'all/'
    '4f5a516f-29ff-4ebe-93eb-465bf0124e85'
    '?grouping=drivers'
    '&park_id=p1'
)


PETROV_EVENTS = (
    'время события,тип события,скорость,водитель,номер устройства,резолюция,'
    'номер автомобиля,позывной автомобиля,ссылка на событие'
    '\r\n2020-02-26T23:55:00,на легком чилле,,Петров Иван,AB2,,'
    'О122КХ178,test,'
    'https://fleet.yandex-team.ru/signalq/stream/'
    'ZDJ8fGQ1OGU3NTNjNDRlNTQ4Y2U5ZWRhZWMwZTBlZjljOGMx/'
    '7f5a516f-29ff-4ebe-93eb-465bf0124e85'
    '?grouping=drivers'
    '&park_id=p1'
    '\r\n2020-02-27T12:00:00,на чилле,34.437895,Петров Иван,AB2,,,,'
    'https://fleet.yandex-team.ru/signalq/stream/'
    'ZDJ8fGQ1OGU3NTNjNDRlNTQ4Y2U5ZWRhZWMwZTBlZjljOGMx/'
    '8f5a516f-29ff-4ebe-93eb-465bf0124e85'
    '?grouping=drivers'
    '&park_id=p1'
)


DEVICE_1_EVENTS = (
    'время события,тип события,скорость,водитель,номер устройства,резолюция,'
    'номер автомобиля,позывной автомобиля,ссылка на событие'
    '\r\n2020-02-27T11:05:00,хз где,89.437895,Иванов Петр,AB1,,,,'
    'https://fleet.yandex-team.ru/signalq/stream/'
    'fHxlNThlNzUzYzQ0ZTU0OGNlOWVkYWVjMGUwZWY5YzhjMQ/'
    '6f5a516f-29ff-4ebe-93eb-465bf0124e85'
    '?grouping=vehicles'
    '&park_id=p1'
    '\r\n2020-02-27T12:00:00,на чилле,34.437895,Иванов Петр,AB1,это кто,,,'
    'https://fleet.yandex-team.ru/signalq/stream/'
    'fHxlNThlNzUzYzQ0ZTU0OGNlOWVkYWVjMGUwZWY5YzhjMQ/'
    '3f5a516f-29ff-4ebe-93eb-465bf0124e85'
    '?grouping=vehicles'
    '&park_id=p1'
    '\r\n2020-02-27T13:02:00,хз где,89.437895,Иванов Петр,AB1,'
    'все норм,,,'
    'https://fleet.yandex-team.ru/signalq/stream/'
    'fHxlNThlNzUzYzQ0ZTU0OGNlOWVkYWVjMGUwZWY5YzhjMQ/'
    '4f5a516f-29ff-4ebe-93eb-465bf0124e85'
    '?grouping=vehicles'
    '&park_id=p1'
)


EMPTY_REPORT = (
    'время события,тип события,скорость,водитель,номер устройства,резолюция,'
    'номер автомобиля,позывной автомобиля,ссылка на событие'
)


FLEET_VEHICLES_RESPONSE = {
    'vehicles': [
        {
            'data': {'car_id': 'car1', 'number': 'О122КХ777'},
            'park_id_car_id': 'p1_car1',
            'revision': '0_1574328384_71',
        },
        {
            'data': {
                'car_id': 'c2',
                'number': 'О122КХ178',
                'callsign': 'test',
            },
            'park_id_car_id': 'p1_c2',
            'revision': '0_1574328384_71',
        },
    ],
}


@pytest.mark.pgsql('signal_device_api_meta_db', files=['events.sql'])
@pytest.mark.config(
    SIGNAL_DEVICE_API_ADMIN_EVENTS_EXPORT_SETTINGS_V3={
        'max_depth_days': 5000,
        'url_template': URL_TEMPLATE,
    },
)
@pytest.mark.parametrize(
    'req, accept, expected_response',
    [
        (
            {
                'start_at': '2010-02-27T00:00:00+03',
                'end_at': '2022-02-27T00:00:00+03',
                'tz_offset': 0,
            },
            TEXT_CSV,
            ALL_EVENTS_BY_VEHICLE,
        ),
        (
            {
                'start_at': '2010-02-27T00:00:00+03',
                'end_at': '2022-02-27T00:00:00+03',
                'tz_offset': 0,
                'group_by': 'driver_profile_id',
            },
            None,
            ALL_EVENTS_BY_DRIVER,
        ),
        (
            {
                'start_at': '2010-02-27T00:00:00+03',
                'end_at': '2022-02-27T00:00:00+03',
                'driver_profile_id': 'd2',
                'tz_offset': 0,
            },
            TEXT_CSV,
            PETROV_EVENTS,
        ),
        (
            {
                'start_at': '2010-02-27T00:00:00+03',
                'end_at': '2022-02-27T00:00:00+03',
                'driver_profile_id': 'd2',
                'tz_offset': 0,
            },
            TEXT_CSV,
            PETROV_EVENTS,
        ),
        (
            {
                'start_at': '2010-02-27T00:00:00+03',
                'end_at': '2022-02-27T00:00:00+03',
                'device_id': 'e58e753c44e548ce9edaec0e0ef9c8c1',
                'tz_offset': 0,
            },
            TEXT_CSV,
            DEVICE_1_EVENTS,
        ),
        (
            {
                'start_at': '2010-02-27T00:00:00+03',
                'end_at': '2022-02-27T00:00:00+03',
                'device_id': 'lol_228',
                'tz_offset': 0,
            },
            TEXT_CSV,
            EMPTY_REPORT,
        ),
        (
            {
                'start_at': '2010-02-27T00:00:00+03',
                'end_at': '2022-02-27T00:00:00+03',
                'tz_offset': 0,
            },
            'text/xlsx',
            None,
        ),
        (
            {
                'start_at': '2010-02-27T00:00:00+03',
                'end_at': '2022-02-27T00:00:00+03',
                'tz_offset': 0,
                'group_by': 'driver_profile_id',
            },
            'text/xlsx',
            None,
        ),
        (
            {
                'start_at': '2010-02-27T00:00:00+03',
                'end_at': '2022-02-27T00:00:00+03',
                'driver_profile_id': 'd2',
                'tz_offset': 0,
            },
            'text/xlsx',
            None,
        ),
        (
            {
                'start_at': '2010-02-27T00:00:00+03',
                'end_at': '2022-02-27T00:00:00+03',
                'driver_profile_id': 'd2',
                'tz_offset': 0,
            },
            'text/xlsx',
            None,
        ),
        (
            {
                'start_at': '2010-02-27T00:00:00+03',
                'end_at': '2022-02-27T00:00:00+03',
                'device_id': 'e58e753c44e548ce9edaec0e0ef9c8c1',
                'tz_offset': 0,
            },
            'text/xlsx',
            None,
        ),
        (
            {
                'start_at': '2010-02-27T00:00:00+03',
                'end_at': '2022-02-27T00:00:00+03',
                'device_id': 'lol_228',
                'tz_offset': 0,
            },
            'text/xlsx',
            None,
        ),
    ],
)
async def test_v1_events_export_csv(
        taxi_signal_device_api_admin,
        mockserver,
        fleet_vehicles,
        req,  # Имя request – служебное))))
        accept,
        expected_response,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_parks(request):
        return {
            'parks': [
                {
                    'city_id': 'CITY_ID',
                    'country_id': 'rus',
                    'demo_mode': False,
                    'id': 'p1',
                    'is_active': True,
                    'is_billing_enabled': True,
                    'is_franchising_enabled': False,
                    'locale': 'ru',
                    'login': 'LOGIN',
                    'name': 'NAME',
                    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
                    'specifications': ['signalq'],
                },
            ],
        }

    fleet_vehicles.set_fleet_vehicles_response(FLEET_VEHICLES_RESPONSE)

    headers = {
        **web_common.YA_TEAM_HEADERS,
        'X-Park-Id': 'p1',
        'Accept-Language': 'ru',
    }
    if accept:
        headers['Accept'] = accept

    response = await taxi_signal_device_api_admin.post(
        '/fleet/signal-device-api-admin/v1/events/export',
        json=req,
        headers=headers,
    )

    assert response.status_code == 200, response.text
    if accept == TEXT_CSV:
        assert response.text == expected_response
        return

    assert response.content is not None
    assert 'Content-Disposition' in response.headers


DEMO_REPORT = (
    'время события,тип события,скорость,водитель,номер устройства,резолюция,'
    'номер автомобиля,позывной автомобиля,ссылка на событие'
    '\r\n2019-02-26T08:00:00,third eye,,,77777,,,,'
    'https://fleet.yandex-team.ru/signalq/stream/'
    'all/'
    f'{utils.get_encoded_events_cursor("2019-02-26T08:00:00+00:00", "e7")}'
    '?grouping=vehicles'
    '&park_id=no_such_park'
    '\r\n2019-02-25T08:00:00,seatbelt,,,11111,,Y777GD,,'
    'https://fleet.yandex-team.ru/signalq/stream/'
    'all/'
    f'{utils.get_encoded_events_cursor("2019-02-25T08:00:00+00:00", "e1")}'
    '?grouping=vehicles'
    '&park_id=no_such_park'
    '\r\n2019-02-24T08:00:00,tired,,Maresov Roman,77777,,,,'
    'https://fleet.yandex-team.ru/signalq/stream/'
    'all/'
    f'{utils.get_encoded_events_cursor("2019-02-24T08:00:00+00:00", "e2")}'
    '?grouping=vehicles'
    '&park_id=no_such_park'
)


@pytest.mark.now('2022-01-11T00:00:00+03:00')
@pytest.mark.config(
    SIGNAL_DEVICE_API_ADMIN_EVENTS_EXPORT_SETTINGS_V3={
        'max_depth_days': 3,
        'url_template': URL_TEMPLATE,
    },
    SIGNAL_DEVICE_API_ADMIN_DEMO_SETTINGS_V2={
        'timings': {
            'working_day_start': 8,
            'working_day_end': 20,
            'working_days_amount': 7,
        },
        'comments': ['Комментарий 1', 'Комментарий 2', 'Комментарий 3'],
        'media': {'__default__': {}},
        'devices': web_common.DEMO_DEVICES,
        'events': web_common.DEMO_EVENTS,
        'vehicles': web_common.DEMO_VEHICLES,
        'groups': web_common.DEMO_GROUPS,
        'drivers': web_common.DEMO_DRIVERS,
    },
    SIGNAL_DEVICE_API_ADMIN_EVENTS_WEB_WHITELIST_V2=web_common.get_demo_whitelist(),  # noqa: E501 line too long
)
@pytest.mark.parametrize(
    'req, accept, expected_response',
    [
        (
            {
                'start_at': '2019-02-24T00:00:00+03',
                'end_at': '2022-02-27T00:00:00+03',
                'tz_offset': 0,
            },
            TEXT_CSV,
            DEMO_REPORT,
        ),
    ],
)
async def test_demo_v1_events_export_csv(
        taxi_signal_device_api_admin,
        mockserver,
        req,
        accept,
        expected_response,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_fleet_parks(request):
        return {
            'parks': [
                {
                    **web_common.get_fleet_parks_info('no_such_park'),
                    'specifications': ['taxi'],
                },
            ],
        }

    headers = {
        **web_common.YA_TEAM_HEADERS,
        'X-Park-Id': 'no_such_park',
        'Accept-Language': 'ru',
    }
    if accept:
        headers['Accept'] = accept

    response = await taxi_signal_device_api_admin.post(
        '/fleet/signal-device-api-admin/v1/events/export',
        json=req,
        headers=headers,
    )

    assert response.status_code == 200, response.text
    if accept == TEXT_CSV:
        assert response.text == expected_response
        return

    assert response.content is not None
    assert 'Content-Disposition' in response.headers
