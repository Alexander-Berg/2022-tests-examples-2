import datetime

import aiohttp.web
import pytest

from fleet_fines.generated.stq3 import stq_context as context
from fleet_fines.stq import poll_ym_request


@pytest.mark.pgsql(
    'taxi_fleet_fines',
    queries=[
        """
    INSERT INTO fleet_fines.documents_vc
        (park_id, car_id, vc_original, vc_normalized, is_normalized, is_valid)
    VALUES
        ('p1', 'с1', '1234567890', '1234567890', TRUE, TRUE),
        ('p1', 'с2', '0987654321', '0987654321', TRUE, TRUE);
    """,
    ],
)
async def test_poll_vc(stq3_context: context.Context, mockserver):
    @mockserver.json_handler('/yamoney_fines/getFines')
    async def _poll(request):
        fines_data = {
            'status': 'success',
            'result': {
                'fines': [
                    {
                        'type': 'VEHICLE_REG_CERTIFICATE',
                        'number': '1234567890',
                        'uin': '1',
                        'paymentLink': 'https://money.yandex.ru/payme1',
                        'fine': {
                            'billDate': '2019-10-30T06:38:26+03:00',
                            'sum': 500.00,
                            'discountedSum': 250.00,
                            'discountDate': '2019-11-19T00:00:00+03:00',
                            'articleCode': '12.9ч.2',
                            'location': 'Краснодарский край',
                        },
                    },
                    {
                        'type': 'VEHICLE_REG_CERTIFICATE',
                        'number': '0987654321',
                        'uin': '2',
                        'paymentLink': 'https://money.yandex.ru/payme2',
                        'fine': {
                            'billDate': '2019-10-28T20:29:27+03:00',
                            'sum': 500.00,
                            'articleCode': '12.9ч.2',
                            'location': 'Вологодская область',
                        },
                    },
                ],
            },
        }
        return aiohttp.web.json_response(fines_data)

    await poll_ym_request.task(
        stq3_context,
        'req_1',
        [],
        ['1234567890', '0987654321'],
        datetime.datetime(2020, 1, 1),
    )
    fines = await stq3_context.pg.main.fetch(
        'SELECT * FROM fleet_fines.fines_vc',
    )
    assert len(fines) == 2
    docs = await stq3_context.pg.main.fetch(
        'SELECT * FROM fleet_fines.documents_vc',
    )
    for doc in docs:
        last_check_date = doc.get('last_check_date')
        last_successful_check = doc.get('last_successful_check')
        assert last_check_date and last_check_date == last_successful_check


@pytest.mark.pgsql(
    'taxi_fleet_fines',
    queries=[
        """
    INSERT INTO fleet_fines.documents_dl
        (park_id, driver_id, dl_pd_id_original, dl_pd_id_normalized,
         is_normalized, is_valid)
    VALUES
        ('p1', 'd1', '1234567890', '1234567890',
         TRUE, TRUE),
        ('p1', 'd2', '0987654321', '0987654321',
         TRUE, TRUE);
    """,
    ],
)
async def test_poll_dl(stq3_context: context.Context, mockserver, patch):
    @mockserver.json_handler('/yamoney_fines/getFines')
    async def _poll(request):
        fines_data = {
            'status': 'success',
            'result': {
                'fines': [
                    {
                        'type': 'DRIVER_LICENSE',
                        'number': 'wqeq1231',
                        'uin': '1',
                        'paymentLink': 'https://money.yandex.ru/payme1',
                        'fine': {
                            'billDate': '2019-10-30T06:38:26.123+03:00',
                            'sum': 500.00,
                            'discountedSum': 250.00,
                            'discountDate': '2019-11-19T00:00:00+03:00',
                            'articleCode': '12.9ч.2',
                            'location': 'Краснодарский край',
                        },
                    },
                    {
                        'type': 'DRIVER_LICENSE',
                        'number': 'f32e2332',
                        'uin': '2',
                        'paymentLink': 'https://money.yandex.ru/payme2',
                        'fine': {
                            'billDate': '2019-10-28T20:29:27.12+03:00',
                            'sum': 500.00,
                            'articleCode': '12.9ч.2',
                            'location': 'Вологодская область',
                        },
                    },
                ],
            },
        }
        return aiohttp.web.json_response(fines_data)

    @patch('taxi.clients.personal.PersonalApiClient.bulk_store')
    async def _store_pd(*args, **kwargs):
        return [
            {'license': 'wqeq1231', 'id': '1234567890'},
            {'license': 'f32e2332', 'id': '0987654321'},
        ]

    await poll_ym_request.task(
        stq3_context,
        'req_1',
        ['1234567890', '0987654321'],
        [],
        datetime.datetime(2020, 1, 1),
    )
    data = await stq3_context.pg.main.fetch(
        'SELECT * FROM fleet_fines.fines_dl',
    )
    assert len(data) == 2
    docs = await stq3_context.pg.main.fetch(
        'SELECT * FROM fleet_fines.documents_dl',
    )
    for doc in docs:
        last_check_date = doc.get('last_check_date')
        last_successful_check = doc.get('last_successful_check')
        assert last_check_date and last_check_date == last_successful_check


@pytest.mark.pgsql(
    'taxi_fleet_fines',
    queries=[
        """
    INSERT INTO fleet_fines.documents_vc
        (park_id, car_id, vc_original, vc_normalized, is_normalized, is_valid)
    VALUES
        ('p1', 'с1', '0987654321', '0987654321', TRUE, TRUE);
    """,
    ],
)
async def test_poll_drop_single(stq3_context: context.Context, mockserver):
    @mockserver.json_handler('/yamoney_fines/getFines')
    async def _poll(request):
        return aiohttp.web.json_response({}, status=503)

    await poll_ym_request.task(
        stq3_context,
        'req_1',
        [],
        ['0987654321'],
        datetime.datetime(2020, 1, 1),
    )
    fines = await stq3_context.pg.main.fetch(
        'SELECT * FROM fleet_fines.fines_vc',
    )
    assert not fines
    docs = await stq3_context.pg.main.fetch(
        'SELECT * FROM fleet_fines.documents_vc',
    )
    assert docs[0].get('last_check_date')
    assert not docs[0].get('last_successful_check')


@pytest.mark.pgsql(
    'taxi_fleet_fines',
    queries=[
        """
    INSERT INTO fleet_fines.documents_vc
        (park_id, car_id, vc_original, vc_normalized,
         is_normalized, is_valid, last_check_date)
    VALUES
        ('p1', 'с1', '1234567890', '1234567890',
         TRUE, TRUE, NULL),
        ('p1', 'с2', '0987654321', '0987654321',
         TRUE, TRUE, NULL);
        """,
        """
    INSERT INTO fleet_fines.fines_vc
        (uin, vc_normalized, loaded_at, sum, bill_date, payment_link)
    VALUES
        ('2', '0987654321', NOW(), 500.00, NOW(),
        'https://money.yandex.ru/payme2')
        """,
    ],
)
async def test_poll_disappeared(stq3_context: context.Context, mockserver):
    @mockserver.json_handler('/yamoney_fines/getFines')
    async def _poll(request):
        fines_data = {
            'status': 'success',
            'result': {
                'fines': [
                    {
                        'type': 'VEHICLE_REG_CERTIFICATE',
                        'number': '1234567890',
                        'uin': '1',
                        'paymentLink': 'https://money.yandex.ru/payme1',
                        'fine': {
                            'billDate': '2019-10-30T06:38:26+03:00',
                            'sum': 500.00,
                            'discountedSum': 250.00,
                            'discountDate': '2019-11-19T00:00:00+03:00',
                            'articleCode': '12.9ч.2',
                            'location': 'Краснодарский край',
                        },
                    },
                ],
            },
        }
        return aiohttp.web.json_response(fines_data)

    await poll_ym_request.task(
        stq3_context,
        'req_1',
        [],
        ['1234567890', '0987654321'],
        datetime.datetime(2020, 1, 1),
    )
    fines = await stq3_context.pg.main.fetch(
        'SELECT * FROM fleet_fines.fines_vc',
    )
    assert len(fines) == 2
    assert not fines[0].get('disappeared_at')
    assert fines[1].get('disappeared_at')

    docs = await stq3_context.pg.main.fetch(
        'SELECT * FROM fleet_fines.documents_vc',
    )
    assert docs[0].get('last_check_date')
    assert docs[1].get('last_check_date')
