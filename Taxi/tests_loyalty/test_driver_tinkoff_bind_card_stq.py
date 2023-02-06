import pytest


STQ_KWARGS = {
    'bank_id': 'bank_id',
    'bank_driver_id': 'bank_driver_id',
    'contract_number': 'contract_number',
    'park_id': 'park_id',
    'driver_profile_id': 'driver_profile_id',
    'taximeter_app': 'Taximeter 8.80 (562)',
    'accept_language': 'ru',
}


@pytest.mark.parametrize(
    'tinkoff_response_code,tinkoff_response_status,push_message,push_count',
    [
        pytest.param(0, 200, 'tinkoff_bind_card_successfull', 1, id='ok'),
        pytest.param(
            -2210,
            200,
            'tinkoff_bind_card_already_bound',
            1,
            id='card already bound',
        ),
        pytest.param(
            -2211,
            200,
            'tinkoff_bind_card_contract_missmatch',
            1,
            id='failed to find contract id',
        ),
        pytest.param(
            -2212,
            200,
            'tinkoff_bind_card_bind_exist',
            1,
            id='another card bind already',
        ),
        pytest.param(
            666,
            200,
            'tinkoff_bind_card_failed',
            1,
            id='unexpected response code',
        ),
        pytest.param(
            -100, 400, 'tinkoff_bind_card_failed', 1, id='Validation error',
        ),
        pytest.param(-300, 500, None, 0, id='Internal server error'),
        pytest.param(0, 500, None, 0, id='Timeout'),
    ],
)
async def test_process_tinkoff_loyalty_responses(
        stq_runner,
        mockserver,
        taxi_loyalty,
        tinkoff_response_code,
        tinkoff_response_status,
        push_message,
        push_count,
):
    @mockserver.json_handler('/tinkoff-loyalty/api/ya_taxi/v1/set_ean')
    def _tinkoff_loyalty_set_ean(request):
        if tinkoff_response_status:
            return mockserver.make_response(
                status=tinkoff_response_status,
                json={'code': tinkoff_response_code, 'message': ''},
                headers={'X-Error-Reason': 'conflict'},
            )
        raise mockserver.TimeoutError()

    @mockserver.json_handler('/client-notify/v2/push')
    def _mock_notification_push(request):
        assert request.json['notification']['text'] == push_message
        return {}

    await stq_runner.loyalty_bind_driver_card.call(
        task_id=f'some_id',
        args=[],
        kwargs=STQ_KWARGS,
        expect_fail=tinkoff_response_status == 500,
    )

    assert _mock_notification_push.times_called == push_count


async def test_tinkoff_signature_equal(stq_runner, mockserver, taxi_loyalty):
    sign = '1387470a54fa5890c37e1c5d46ae7043e07238be4fef9691b42e0ab14e38efae'

    @mockserver.json_handler('/tinkoff-loyalty/api/ya_taxi/v1/set_ean')
    def _tinkoff_loyalty_set_ean(request):
        assert request.headers['X-Body-Signature'] == sign
        return {'code': 0, 'message': ''}

    @mockserver.json_handler('/client-notify/v2/push')
    def _mock_notification_push(request):
        return {}

    await stq_runner.loyalty_bind_driver_card.call(
        task_id=f'some_id',
        args=[],
        kwargs={
            **STQ_KWARGS,
            'bank_driver_id': 'ean',
            'contract_number': '123',
        },
    )
    assert _mock_notification_push.times_called == 1


async def test_tinkoff_downtime(stq, stq_runner, mockserver, taxi_loyalty):
    @mockserver.json_handler('/tinkoff-loyalty/api/ya_taxi/v1/set_ean')
    def _tinkoff_loyalty_set_ean(request):
        raise mockserver.TimeoutError()

    @mockserver.json_handler('/client-notify/v2/push')
    def _mock_notification_push(request):
        assert (
            request.json['notification']['text'] == 'tinkoff_bind_card_failed'
        )
        return {}

    for exc in range(12):
        await stq_runner.loyalty_bind_driver_card.call(
            task_id=f'some_id',
            args=[],
            kwargs=STQ_KWARGS,
            expect_fail=exc < 11,
            exec_tries=exc,
        )

    assert _mock_notification_push.times_called == 1
