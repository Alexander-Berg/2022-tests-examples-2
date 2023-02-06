import pytest


@pytest.mark.pgsql(
    'contractor_merch_integration_api', files=['insert_records.sql'],
)
@pytest.mark.parametrize(
    'data,status',
    [
        (
            {
                'payment': {
                    'status': 'payment_passed',
                    'payment_id': 'ac4ba28c-7863-473e-951c-ccb3cc154a85',
                    'updated_at': '2021-11-19T12:28:06+0000',
                    'created_at': '2021-11-19T11:28:06+0000',
                    'merchant_id': 'ac4ba28c-7863-473e-951c-ccb3cc154a85',
                    'price': '800.14',
                    'currency': 'RUB',
                    'contractor': {
                        'contractor_id': 'petia@yandex.ru',
                        'park_id': '5',
                    },
                },
            },
            200,
        ),
        (
            {
                'payment': {
                    'status': 'payment_passed',
                    'payment_id': 'ac4ba28c-7863-473e-951c-ccb3cc154a85',
                    'updated_at': '2021-11-19T12:28:06+0000',
                    'created_at': '2021-11-19T11:28:06+0000',
                    'merchant_id': 'ac4ba28c-7863-473e-951c-ccb3cc154a85',
                    'price': '800.14',
                    'contractor': {
                        'contractor_id': 'petia@yandex.ru',
                        'park_id': '5',
                    },
                },
            },
            200,
        ),
        (
            {
                'payment': {
                    'status': 'payment_failed',
                    'payment_id': 'cd2b90b1-dcd1-43bc-a99f-af192dfc69e7',
                    'updated_at': '2021-12-21T12:28:06+0000',
                    'created_at': '2021-12-19T10:28:06+0000',
                    'merchant_id': 'ac4ba28c-7863-473e-951c-ccb3cc154a85',
                    'price': '100.14',
                    'currency': 'YEN',
                    'contractor': {
                        'contractor_id': 'petia@yandex.ru',
                        'park_id': '5',
                    },
                },
            },
            500,
        ),
        (
            {
                'payment': {
                    'status': 'payment_passed',
                    'payment_id': '74bad06e-d4c3-40d3-8221-bc5e47bd72d6',
                    'updated_at': '2021-11-22T12:28:06+0000',
                    'created_at': '2021-11-20T11:28:06+0000',
                    'merchant_id': 'ac4ba28c-d4c3-473e-951c-bc5e47bd72d6',
                    'price': '5',
                    'currency': 'USD',
                    'contractor': {
                        'contractor_id': 'petia@yandex.ru',
                        'park_id': '5',
                    },
                },
            },
            404,
        ),
        (
            {
                'payment': {
                    'status': 'payment_passed',
                    'payment_id': '471c6697-e34f-4c61-8c1f-3be94755aaba',
                    'updated_at': '2021-11-29T12:28:06+0000',
                    'contractor': {
                        'contractor_id': 'petia@yandex.ru',
                        'park_id': '5',
                    },
                    'created_at': '2021-11-20T11:28:06+0000',
                    'merchant_id': 'ac4ba28c-d4c3-473e-e34f-bc5e47bd72d6',
                    'price': '19',
                    'currency': 'RUB',
                },
            },
            400,
        ),
    ],
)
async def test_notify(
        mockserver, taxi_contractor_merch_integration_api_web, data, status,
):
    @mockserver.json_handler('/mobi/transaction-mmbarcode/MMBarcodeOPGateBean')
    async def _notify_handler(request):
        body = request.json
        assert body['clientLogin'] == '5_petia@yandex.ru'
        if body.get('mmTranId') == 4:
            return mockserver.make_response(status=500)
        if body.get('mmTranId') == 10:
            return mockserver.make_response(
                status=200,
                json={
                    'signature': 'test',
                    'result': -10,
                    'resultDesc': 'limits_exceeded',
                },
            )
        return mockserver.make_response(
            status=200, json={'signature': 'test', 'result': 0},
        )

    response = await taxi_contractor_merch_integration_api_web.post(
        path='/contractor-merchants/v1/internal/v1/notify', json=data,
    )
    assert response.status == status
