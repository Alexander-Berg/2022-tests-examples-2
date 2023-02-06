# pylint: disable=redefined-outer-name

import datetime

import pytest

from taxi.clients import integration_api


NOW = datetime.datetime(2020, 9, 10, 9, 18, 40)
SBER_CLIENTS_SETTINGS = {
    'ввб нгосб/транспорт': {'client_id': 'client1', 'class': 'econom'},
}

IN_PROGRESS_REQUEST = {'СБ_ID': 'e1', 'ИДЕНТИФИКАТОР': 'order_id_1'}


@pytest.mark.now(NOW.isoformat())
@pytest.mark.pgsql('sber_int_api', files=('claims.sql',))
@pytest.mark.config(SBER_CLIENTS_SETTINGS=SBER_CLIENTS_SETTINGS)
@pytest.mark.parametrize(
    'order_proc, expected_response, expected_claim',
    [
        pytest.param(
            {
                '_id': 'order_id_1',
                'order': {
                    'status': 'complete',
                    'taxi_status': 'complete',
                    'cost': 50,
                },
                'created': NOW,
            },
            {
                'DONE': {
                    'ID': '1',
                    'ВЫПОЛНЕНО': '2020-09-10 12:18:40',
                    'ЗАРЕГИСТРИРОВАНО': '2020-09-10 12:18:40',
                    'ИДЕНТИФИКАТОР': 'order_id_1',
                    'КОД_ЗАКРЫТИЯ': '1',
                    'НАЧАЛО РАБОТ': '2020-09-10 12:18:40',
                    'РЕШЕНИЕ': None,
                    'СБ_ID': 'e1',
                    'СТАТУС': '7',
                    'PRICE': '50.00',
                },
            },
            {
                'external_id': 'e1',
                'status': 'complete',
                'close_status': 'complete',
                'taxi_order_id': 'order_id_1',
                'personal_phone_id': 'defee2e75b2039c74d9cfbc068d0aef7',
                'route': (
                    '['
                    '"Москва, улица Вавилова, 19", '
                    '"Москва, Кутузовский проспект, 32"'
                    ']'
                ),
                'error_reason': None,
            },
            id='min',
        ),
        pytest.param(
            {
                '_id': 'order_id_1',
                'order': {
                    'status': 'complete',
                    'taxi_status': 'complete',
                    'calc_info': {'waiting_time': 4},
                    'taximeter_receipt': {'total_distance': 55600.0},
                },
                'created': NOW,
                'order_info': {
                    'statistics': {
                        'setcared': NOW + datetime.timedelta(minutes=1),
                        'travel_time': 56,
                        'start_transporting_time': NOW + datetime.timedelta(
                            minutes=3,
                        ),
                        'complete_time': NOW + datetime.timedelta(minutes=4),
                        'status_updates': [
                            {
                                't': 'waiting',
                                'c': NOW + datetime.timedelta(minutes=2),
                            },
                            {
                                't': 'complete',
                                'p': {
                                    'updated': NOW + datetime.timedelta(
                                        minutes=5,
                                    ),
                                    'geopoint': [37.642756, 55.735483],
                                },
                            },
                        ],
                    },
                },
                'payment_tech': {'without_vat_to_pay': {'ride': 6660000}},
                'performer': {'driver_id': 'driver_id_1'},
                'candidates': [
                    {
                        'driver_id': 'driver_id_1',
                        'phone': '+70003660056',
                        'car_model': 'BMW X6',
                        'car_number': 'У008УУ88',
                        'car_color': 'желтый',
                        'name': 'Рябов Кирилл Чеславович',
                    },
                ],
            },
            {
                'DONE': {
                    'ID': '1',
                    'KILOM': '55.6',
                    'LAGTIME_50': '00:04:00',
                    'NOLAG_RADIUS_50': '00:00:56',
                    'PRICE': '666.00',
                    'ВРЕМЯ_ЗАВЕРШЕНИЯ_ПОЕЗДКИ': '2020-09-10 12:22:40',
                    'ВРЕМЯ_НАЧАЛА_ПОЕЗДКИ': '2020-09-10 12:21:40',
                    'ВЫПОЛНЕНО': '2020-09-10 12:20:40',
                    'ЗАРЕГИСТРИРОВАНО': '2020-09-10 12:18:40',
                    'ИДЕНТИФИКАТОР': 'order_id_1',
                    'КОД_ЗАКРЫТИЯ': '1',
                    'МАРШРУТ': '55.735483:37.642756',
                    'НАЧАЛО РАБОТ': '2020-09-10 12:19:40',
                    'РЕШЕНИЕ': (
                        'BMW X6 желтый У008УУ88 +70003660056, Рябов Кирилл '
                        'Чеславович'
                    ),
                    'СБ_ID': 'e1',
                    'СТАТУС': '7',
                    'ТАЙМИНГ_ПОЕЗДКИ': '2020-09-10 12:23:40',
                },
            },
            {
                'external_id': 'e1',
                'status': 'complete',
                'close_status': 'complete',
                'taxi_order_id': 'order_id_1',
                'personal_phone_id': 'defee2e75b2039c74d9cfbc068d0aef7',
                'route': (
                    '['
                    '"Москва, улица Вавилова, 19", '
                    '"Москва, Кутузовский проспект, 32"'
                    ']'
                ),
                'error_reason': None,
            },
            id='max',
        ),
    ],
)
async def test_in_progress_handler(
        patch,
        cron_context,
        order_archive_mock,
        handler,
        order_proc,
        expected_response,
        expected_claim,
):
    order_archive_mock.set_order_proc(order_proc)

    @patch(
        'client_integration_api.components.IntegrationAPIClient.order_search',
    )
    async def _order_search(*args, **kwargs):
        return integration_api.APIResponse(
            status=200,
            data={'orders': [{'vehicle': {'location': [1, 2]}}]},
            headers={},
        )

    response = await handler('IN_PROGRESS', IN_PROGRESS_REQUEST)
    assert response == expected_response

    async with cron_context.pg.master.acquire() as conn:
        new_claim = await conn.fetchrow(
            cron_context.postgres_queries['fetch_claim_by_id.sql'], 'e1',
        )
    new_claim = dict(new_claim)
    assert new_claim == expected_claim


@pytest.mark.now(NOW.isoformat())
@pytest.mark.pgsql('sber_int_api', files=('claims.sql',))
@pytest.mark.config(SBER_CLIENTS_SETTINGS=SBER_CLIENTS_SETTINGS)
async def test_in_progress_order_archive_500(order_archive_mock, handler):
    order_archive_mock.set_order_proc_retrieve_500()

    response = await handler('IN_PROGRESS', IN_PROGRESS_REQUEST)
    assert response == {}
