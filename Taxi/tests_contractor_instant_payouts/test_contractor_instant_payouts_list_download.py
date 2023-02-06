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
        'UTF-8',
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
    ('park2', 'text/csv', None, []),
]


@pytest.mark.now('2021-01-01T12:00:00+0000')
@pytest.mark.parametrize(
    'park_id, accept, accept_charset, expected_results', OK_CSV_PARAMS,
)
async def test_ok(
        stq_runner,
        mockserver,
        park_id,
        accept,
        accept_charset,
        expected_results,
):
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
                    'tz_offset': 3,
                    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
                },
            ],
        }

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

    @mockserver.json_handler('/fleet-reports-storage/internal/v1/file/upload')
    async def _mock_frs(request):
        return None

    await stq_runner.contractor_instant_payouts_list_download_async.call(
        task_id='1',
        kwargs={
            'park_id': park_id,
            'operation_id': '6c5c10956c2bbe505bb8c42201efe5ef',
            'accept_language': 'ru',
            'accept_charset': 'utf-8',
            'accept': accept,
        },
    )
