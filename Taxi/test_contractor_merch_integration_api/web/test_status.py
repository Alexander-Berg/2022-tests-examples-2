import pytest

from contractor_merch_integration_api.utils import operation_class


def status_handler_response(status: str):
    return {
        'payment': {
            'status': status,
            'created_at': '2021-11-29T11:44:47.790779',
            'updated_at': '2021-11-29T13:44:47.790779',
            'contractor': {'park_id': '123', 'contractor_id': '18-92'},
            'price': '123.45',
        },
    }


def refunds_handler_response(ids: list, canceled: bool):
    return {
        'refunds': [
            {
                'id': x,
                'amount': '100',
                'currency': 'RUB',
                'created_at': '2021-11-12T12:00:00+00:00',
                'metadata': {'mobi_refund_id': '111', 'is_cancel': canceled},
            }
            for x in ids
        ],
    }


FAILED_JSON_RESPONSE = {
    'signature': (
        '0a814d580c2f1b42c6008074609bf5576c17f1e0f9da81a8c182f77f07d54537'
    ),
    'result': -2,
    'resultDesc': 'transaction not found',
}

FULL_JSON_RESPONSE = {
    'result': 0,
    'opTranId': 'ac4ba28c-7863-473e-951c-ccb3cc154a85',
    'opTranTime': '2021-11-29T16:44:47.790779+03:00',
    'clientLogin': '123_18-92',
    'tranAmount': '123.45',
    'resultDesc': 'success',
    'status': 1,
}


def get_mobi_request(mobi_transaction_id: int, is_signature_correct: bool):
    json = {'operation': 'status', 'mmTranId': mobi_transaction_id}
    if is_signature_correct:
        json['signature'] = operation_class.create_signature(
            secret_key='QWERTY12345', parameters=json,
        )
    else:
        json['signature'] = '123'
    return json


@pytest.mark.pgsql(
    'contractor_merch_integration_api', files=['status_records.sql'],
)
@pytest.mark.parametrize(
    'data,result,status',
    [
        (
            get_mobi_request(1, True),
            operation_class.ResultType.SUCCESS,
            operation_class.StatusType.COMPLETED,
        ),
        (
            get_mobi_request(10, True),
            operation_class.ResultType.SUCCESS,
            operation_class.StatusType.INPROGRESS,
        ),
        (
            get_mobi_request(4, True),
            operation_class.ResultType.SUCCESS,
            operation_class.StatusType.REFUNDED,
        ),
        (
            get_mobi_request(15, True),
            operation_class.ResultType.SUCCESS,
            operation_class.StatusType.CANCELED,
        ),
        (
            get_mobi_request(20, True),
            operation_class.ResultType.TRANSACTION_NOT_FOUND,
            operation_class.StatusType.FAILED,
        ),
        (
            get_mobi_request(34, True),
            operation_class.ResultType.INTERNAL_ERROR,
            operation_class.StatusType.FAILED,
        ),
        (
            get_mobi_request(35, True),
            operation_class.ResultType.INTERNAL_ERROR,
            operation_class.StatusType.FAILED,
        ),
        (
            get_mobi_request(36, True),
            operation_class.ResultType.TRANSACTION_NOT_FOUND,
            operation_class.StatusType.FAILED,
        ),
        (
            get_mobi_request(23, True),
            operation_class.ResultType.TRANSACTION_NOT_FOUND,
            operation_class.StatusType.FAILED,
        ),
        (
            get_mobi_request(23, False),
            operation_class.ResultType.INCORRECT_SIGNATURE,
            operation_class.StatusType.FAILED,
        ),
    ],
)
async def test_status(
        mockserver,
        taxi_contractor_merch_integration_api_web,
        data,
        result,
        status,
):
    @mockserver.json_handler(
        '/contractor-merch-payments/internal/'
        'v1/contractor-merch-payments/payment/status',
    )
    async def _status_handler(request):
        if (
                request.args['payment_id']
                == 'cd2b90b1-dcd1-43bc-a99f-af192dfc69e7'
                or request.args['payment_id']
                == 'ac4ba28c-7863-473e-951c-ccb3cc154a85'
                or request.args['payment_id']
                == 'd9d519e2-a637-43b5-aba4-ffe370204869'
                or request.args['payment_id']
                == '1543eeab-aaaa-4625-b80f-8fa416b90263'
        ):
            return mockserver.make_response(
                status=200,
                json=status_handler_response(status='payment_passed'),
            )

        if (
                request.args['payment_id']
                == '471c6697-e34f-4c61-8c1f-3be94755aaba'
        ):
            return mockserver.make_response(
                status=200,
                json=status_handler_response(
                    status='pending_payment_execution',
                ),
            )

        if (
                request.args['payment_id']
                == '34ceeee0-dd8c-4625-b80f-8fa416b90263'
        ):
            return mockserver.make_response(
                status=404,
                json={'code': '404', 'message': 'transaction not found'},
            )
        if (
                request.args['payment_id']
                == '73decba0-dd8c-4625-b80f-8fa416b90263'
        ):
            return mockserver.make_response(status=500, json={})
        return mockserver.make_response(
            status=200, json=status_handler_response(status='payment_passed'),
        )

    @mockserver.json_handler(
        '/contractor-merch-payments/internal/'
        'contractor-merch-payments/v1/payment/refunds',
    )
    async def _refunds_handler(request):
        if (
                request.args['payment_id']
                == 'cd2b90b1-dcd1-43bc-a99f-af192dfc69e7'
        ):
            return mockserver.make_response(
                status=200,
                json=refunds_handler_response(['123', '234'], canceled=False),
            )
        if (
                request.args['payment_id']
                == 'd9d519e2-a637-43b5-aba4-ffe370204869'
        ):
            return mockserver.make_response(
                status=200,
                json=refunds_handler_response(['123', '234'], canceled=True),
            )
        if (
                request.args['payment_id']
                == '10eacba0-aaaa-4625-b80f-8fa416b90263'
        ):
            return mockserver.make_response(status=500, json={})
        if (
                request.args['payment_id']
                == '1543eeab-aaaa-4625-b80f-8fa416b90263'
        ):
            return mockserver.make_response(
                status=404,
                json={'code': '404', 'message': 'transaction not found'},
            )
        return mockserver.make_response(
            status=200, json=refunds_handler_response([], canceled=False),
        )

    response = await taxi_contractor_merch_integration_api_web.post(
        path='/contractor-merchants/v1/external/v1/operation', json=data,
    )
    assert response.status == 200
    if int(result) < 0:
        assert (await response.json())['result'] == int(result)
    else:
        assert (await response.json())['status'] == int(status)
        assert (await response.json())['result'] == int(result)
    if data.get('mmTranId') == 1:
        FULL_JSON_RESPONSE['signature'] = operation_class.create_signature(
            secret_key='QWERTY12345', parameters=FULL_JSON_RESPONSE,
        )
        assert (await response.json()) == FULL_JSON_RESPONSE
    elif data.get('mmTranId') == 23 and int(status) == -2:
        assert (await response.json()) == FAILED_JSON_RESPONSE
