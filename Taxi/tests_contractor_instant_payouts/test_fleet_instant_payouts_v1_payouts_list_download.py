import pytest

from tests_contractor_instant_payouts import utils

ENDPOINT = '/fleet/instant-payouts/v1/payouts/list/download'
MOCK_URL = '/driver-profiles/v1/driver/profiles/retrieve'


def build_headers(
        park_id, accept_language=None, accept=None, accept_charset=None,
):
    headers = {
        **utils.SERVICE_HEADERS,
        'X-Ya-User-Ticket': 'ticket_valid1',
        'X-Ya-User-Ticket-Provider': 'yandex',
        'X-Yandex-UID': '1',
        'X-Park-ID': park_id,
    }
    if accept_language is not None:
        headers['Accept-Language'] = accept_language
    if accept is not None:
        headers['Accept'] = accept
    if accept_charset is not None:
        headers['Accept-Charset'] = accept_charset
    return headers


OK_CSV_HEADER = (
    'ID водителя;Водитель;Сумма заявки;Списано с баланса водителя;'
    'Списано со счета;Номер карты;Дата;Статус;Банк;ID транзакции'
)

OK_CSV_PARAMS = [
    (
        'park1',
        'text/csv',
        'utf-8',
        3,
        [
            (
                'contractor1;Иванов Иван Иванович;'
                '300.0101;303.0202;300.0202;************5678;'
                '2020-03-03T15:00:00+0300;Выполнена;'
                'Альфабанк;3c178bd1-f720-4daf-99b8-b8ab253f3812'
            ),
            (
                'contractor1;Иванов Иван Иванович;'
                '200.0202;202.0404;;************1234;'
                '2020-02-02T15:00:00+0300;Отклонена: Недостаточно средств;'
                'Модульбанк;3c178bd1-f720-4daf-99b8-b8ab253f3811'
            ),
            (
                'contractor1;Иванов Иван Иванович;'
                '100.0101;101.0202;100.0202;************1234;'
                '2020-01-01T15:00:00+0300;Выполнена;'
                'Модульбанк;3c178bd1-f720-4daf-99b8-b8ab253f3810'
            ),
        ],
    ),
    (
        'park1',
        'text/csv',
        None,
        7,
        [
            (
                'contractor1;Иванов Иван Иванович;'
                '300.0101;303.0202;300.0202;************5678;'
                '2020-03-03T19:00:00+0700;Выполнена;'
                'Альфабанк;3c178bd1-f720-4daf-99b8-b8ab253f3812'
            ),
            (
                'contractor1;Иванов Иван Иванович;'
                '200.0202;202.0404;;************1234;'
                '2020-02-02T19:00:00+0700;Отклонена: Недостаточно средств;'
                'Модульбанк;3c178bd1-f720-4daf-99b8-b8ab253f3811'
            ),
            (
                'contractor1;Иванов Иван Иванович;'
                '100.0101;101.0202;100.0202;************1234;'
                '2020-01-01T19:00:00+0700;Выполнена;'
                'Модульбанк;3c178bd1-f720-4daf-99b8-b8ab253f3810'
            ),
        ],
    ),
    ('park2', 'text/csv', None, 3, []),
]


@pytest.mark.now('2021-01-01T12:00:00+0000')
@pytest.mark.parametrize(
    'park_id, accept, accept_charset, tz_offset, expected_results',
    OK_CSV_PARAMS,
)
async def test_csv(
        taxi_contractor_instant_payouts,
        mockserver,
        park_id,
        accept,
        accept_charset,
        tz_offset,
        expected_results,
):
    @mockserver.json_handler(MOCK_URL)
    def _driver_profiles_handler(request):
        return {
            'profiles': [
                {
                    'data': {
                        'full_name': {
                            'first_name': 'Иван',
                            'last_name': 'Иванов',
                            'middle_name': 'Иванович',
                        },
                    },
                    'park_driver_id': park_id + '_contractor1',
                    'park_driver_profile_id': park_id + '_contractor1',
                    'revision': '0_1234567_4',
                },
            ],
        }

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_parks_list(request):
        return {
            'parks': [
                {
                    'city_id': 'city1',
                    'country_id': 'cid1',
                    'demo_mode': False,
                    'driver_partner_source': 'yandex',
                    'id': park_id,
                    'is_active': True,
                    'is_billing_enabled': False,
                    'is_franchising_enabled': False,
                    'locale': 'locale1',
                    'login': 'login1',
                    'name': 'name1',
                    'tz_offset': tz_offset,
                    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
                },
            ],
        }

    response = await taxi_contractor_instant_payouts.post(
        ENDPOINT,
        headers=build_headers(
            park_id=park_id,
            accept_language='ru',
            accept=accept,
            accept_charset=accept_charset,
        ),
    )

    assert response.status_code == 200, response.text

    results = response.text.split('\r\n')
    assert results[0] == OK_CSV_HEADER, results[0]
    for result in results[1:]:
        assert result in expected_results, result

    assert 'Content-Disposition' in response.headers
    assert (
        response.headers['Content-Disposition']
        == 'attachment; filename=\"contractor_instant_payouts_2021-01-01.csv\"'
    )


@pytest.mark.now('2021-01-01T12:00:00+0000')
async def test_xlsx(taxi_contractor_instant_payouts, mockserver):
    @mockserver.json_handler(MOCK_URL)
    def _driver_profiles_handler(request):
        return {
            'profiles': [
                {
                    'data': {
                        'full_name': {
                            'first_name': 'Иван',
                            'last_name': 'Иванов',
                            'middle_name': 'Иванович',
                        },
                    },
                    'park_driver_id': 'park1' + '_contractor1',
                    'park_driver_profile_id': 'park1' + '_contractor1',
                    'revision': '0_1234567_4',
                },
            ],
        }

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_parks_list(request):
        return {
            'parks': [
                {
                    'city_id': 'city1',
                    'country_id': 'cid1',
                    'demo_mode': False,
                    'driver_partner_source': 'yandex',
                    'id': 'park1',
                    'is_active': True,
                    'is_billing_enabled': False,
                    'is_franchising_enabled': False,
                    'locale': 'locale1',
                    'login': 'login1',
                    'name': 'name1',
                    'tz_offset': 3,
                    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
                },
            ],
        }

    response = await taxi_contractor_instant_payouts.post(
        ENDPOINT, headers=build_headers(park_id='park1', accept_language='ru'),
    )

    assert response.status_code == 200, response.text
    assert response.content is not None

    assert 'Content-Disposition' in response.headers
    assert response.headers['Content-Disposition'] == (
        'attachment; '
        'filename=\"contractor_instant_payouts_2021-01-01.xlsx\"'
    )
