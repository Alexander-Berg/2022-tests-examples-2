import aiohttp.web
import pytest

from taxi.clients import personal

DATA = [
    {
        'kis_art_id': 'real_kis_art_id1',
        'full_name': 'Калинин Андрей Алексеевич',
        'phone': '+79115553322',
        'kis_art_status': 'requested',
        'driver_profile_id': 'dr_pr_1',
    },
    {
        'full_name': 'Малышева Анна Сергеевна',
        'phone': '+70006811011',
        'kis_art_status': 'requested',
        'driver_profile_id': 'dr_pr_2',
    },
    {
        'full_name': 'Олексеев Кто-то Там',
        'phone': '+79006667777',
        'kis_art_status': 'requested',
        'driver_profile_id': 'dr_pr_9',
    },
    {
        'kis_art_id': 'real_kis_art_id18',
        'full_name': 'Фамилия Имя Отчество',
        'phone': '+79006667777',
        'kis_art_status': 'permanent',
        'driver_profile_id': 'dr_pr_18',
    },
    {
        'full_name': 'Prosto testov',
        'kis_art_status': 'requested',
        'driver_profile_id': 'dr_pr_1',
    },
    {
        'full_name': 'gagaga Test',
        'phone': '+79009999999',
        'kis_art_status': 'requested',
        'driver_profile_id': 'dr_pr_5',
    },
    {
        'kis_art_id': 'real_kis_art_id8',
        'full_name': 'Сергеев К Д',
        'phone': '+70000000000',
        'kis_art_status': 'failed',
        'driver_profile_id': 'dr_pr_8',
    },
    {
        'kis_art_id': 'real_kis_art_7',
        'full_name': 'Михайлов Владимир Сергеевич',
        'kis_art_status': 'temporary',
        'driver_profile_id': 'dr_pr_7',
    },
    {
        'kis_art_id': 'real_kis_art_3',
        'full_name': 'Фомин Александр Николаевич',
        'kis_art_status': 'temporary',
        'driver_profile_id': 'dr_pr_3',
    },
    {
        'kis_art_id': 'real_kis_art_id_3_1',
        'full_name': 'Алексеева Алина Юрьевна',
        'phone': '+72220009988',
        'kis_art_status': 'permanent',
        'driver_profile_id': 'dr_pr_1',
    },
    {
        'kis_art_id': 'real_kis_art_id4',
        'full_name': 'Матвиенко Богдан Сергеевич',
        'kis_art_status': 'without_id',
        'driver_profile_id': 'dr_pr_4',
    },
]


@pytest.mark.parametrize(
    (
        'provider',
        'park_id',
        'driver_profiles_file',
        'phone_list',
        'kis_art_id_list',
        'main_request',
        'main_response',
    ),
    [
        (
            'yandex',
            'pid1',
            'driver_profiles.json',
            [
                {
                    'id': 'fa866b5c515a48a8b0dee01a7d74b477',
                    'phone': '+79115553322',
                },
                {
                    'id': '7da1236a76e0405eb1307e1bffc07491',
                    'phone': '+70006811011',
                },
            ],
            [{'id': 'kis_art_id1', 'deptrans_id': 'real_kis_art_id1'}],
            {
                'date': '2020-01-04',
                'kis_art_statuses': ['requested'],
                'limit': 2,
            },
            {
                'drivers': DATA[:2],
                'cursor': (
                    '0J7Qu9C10LrRgdC10LXQsiDQmtGC0L4t0'
                    'YLQviDQotCw0Lw7ZHJfcHJfOQ=='
                ),
                'drivers_count': 3,
            },
        ),
        (
            'yandex',
            'pid1',
            'driver_profiles2.json',
            [
                {
                    'id': 'fa866b5c515a48a8b0dee01a7d74b555',
                    'phone': '+79006667777',
                },
            ],
            [],
            {
                'date': '2020-01-04',
                'kis_art_statuses': ['requested'],
                'limit': 1,
                'cursor': (
                    '0J7Qu9C10LrRgdC10LXQsiDQmtGC0L4t0'
                    'YLQviDQotCw0Lw7ZHJfcHJfOQ=='
                ),
            },
            {'drivers': DATA[2:3], 'drivers_count': 3},
        ),
        (
            'yandex',
            'pid1',
            'driver_profiles3.json',
            [{'id': 'test_id', 'phone': '+79006667777'}],
            [{'id': 'kis_art_id18', 'deptrans_id': 'real_kis_art_id18'}],
            {
                'date': '2020-01-05',
                'kis_art_statuses': ['permanent'],
                'limit': 1,
                'cursor': (
                    '0KTQsNC80LjQu9C40Y8g0JjQvNGPINCe0YLRh9C10YH'
                    'RgtCy0L47ZHJfcHJfMTg='
                ),
            },
            {'drivers': DATA[3:4], 'drivers_count': 2},
        ),
        (
            'yandex',
            'pid2',
            'driver_profiles4.json',
            [{'id': 'phone_pd_id5', 'phone': '+79009999999'}],
            [],
            {
                'date': '2020-01-04',
                'kis_art_statuses': ['requested'],
                'limit': 3,
                'name_filter': 'test',
            },
            {'drivers': DATA[4:6], 'drivers_count': 2},
        ),
        (
            'yandex',
            'pid1',
            'driver_profiles5.json',
            [{'id': 'phone_pd_id8', 'phone': '+70000000000'}],
            [
                {'id': 'bhbliubl', 'deptrans_id': 'real_kis_art_id8'},
                {'id': 'temporary_7', 'deptrans_id': 'real_kis_art_7'},
                {'id': 'kis_art_id3', 'deptrans_id': 'real_kis_art_3'},
            ],
            {
                'date': '2020-01-04',
                'kis_art_statuses': ['failed', 'temporary'],
                'limit': 4,
            },
            {'drivers': [DATA[7], DATA[6], DATA[8]], 'drivers_count': 3},
        ),
        (
            'yandex',
            'pid3',
            'driver_profiles6.json',
            [{'id': 'phone_pd_id3_1', 'phone': '+72220009988'}],
            [{'id': 'kis_art_id_3_1', 'deptrans_id': 'real_kis_art_id_3_1'}],
            {
                'date': '2020-12-12',
                'kis_art_statuses': ['permanent'],
                'limit': 10,
            },
            {'drivers': [DATA[9]], 'drivers_count': 1},
        ),
        (
            'yandex_team',
            'pid3',
            'driver_profiles6.json',
            [],
            [{'id': 'kis_art_id_3_1', 'deptrans_id': 'real_kis_art_id_3_1'}],
            {
                'date': '2020-12-12',
                'kis_art_statuses': ['permanent'],
                'limit': 10,
            },
            {
                'drivers': [
                    {
                        'kis_art_id': 'real_kis_art_id_3_1',
                        'full_name': 'Алексеева Алина Юрьевна',
                        'kis_art_status': 'permanent',
                        'driver_profile_id': 'dr_pr_1',
                    },
                ],
                'drivers_count': 1,
            },
        ),
        (
            'yandex',
            'pid1',
            'driver_profiles7.json',
            [
                {
                    'id': 'fa866b5c515a48a8b0dee01a7d74b477',
                    'phone': '+79115553322',
                },
                {
                    'id': '7da1236a76e0405eb1307e1bffc07491',
                    'phone': '+70006811011',
                },
            ],
            [
                {'id': 'kis_art_id1', 'deptrans_id': 'real_kis_art_id1'},
                {'id': 'kis_art_id4', 'deptrans_id': 'real_kis_art_id4'},
            ],
            {'date': '2020-01-04', 'limit': 3},
            {
                'drivers': [DATA[0], DATA[1], DATA[10]],
                'cursor': (
                    '0JzQuNGF0LDQudC70L7QsiDQktC70LDQtNC40LzQuNGAINCh0L'
                    'XRgNCz0LXQtdCy0LjRhztkcl9wcl83'
                ),
                'drivers_count': 7,
            },
        ),
    ],
)
@pytest.mark.pgsql('fleet_reports', files=['kis_art_detailed_data.sql'])
async def tests(
        web_app_client,
        headers,
        mock_driver_profiles,
        patch,
        load_json,
        provider,
        park_id,
        driver_profiles_file,
        phone_list,
        kis_art_id_list,
        main_request,
        main_response,
):

    driver_profiles_stub = load_json(driver_profiles_file)

    @mock_driver_profiles('/v1/driver/profiles/retrieve')
    async def _v1_driver_profiles_retrieve(request):
        assert request.query == {'consumer': 'fleet-reports'}
        assert request.json == driver_profiles_stub['request']
        return aiohttp.web.json_response(driver_profiles_stub['response'])

    @patch('taxi.clients.personal.PersonalApiClient.bulk_retrieve')
    async def _bulk_retrieve(data_type, request_ids, log_extra=None):
        assert (
            data_type == personal.PERSONAL_TYPE_PHONES
            or personal.PERSONAL_TYPE_DEPTRANS_IDS
        )
        if data_type == personal.PERSONAL_TYPE_PHONES:
            return phone_list
        return kis_art_id_list

    response = await web_app_client.post(
        '/reports-api/v1/detailed/kis-art/list',
        headers={
            **headers,
            'X-Ya-User-Ticket-Provider': provider,
            'X-Park-Id': park_id,
        },
        json=main_request,
    )

    assert response.status == 200
    assert await response.json() == main_response
