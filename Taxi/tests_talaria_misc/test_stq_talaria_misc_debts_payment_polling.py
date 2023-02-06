import pytest


@pytest.mark.parametrize(
    'status', ['pending', 'failed', 'not_found', 'success'],
)
async def test_main(mockserver, stq_runner, status):
    @mockserver.json_handler('/wind/pf/server/v1/yandexPayment/topup/status')
    def _mock_wind_topups_status(request):
        assert request.query == {'operation_id': 'operation_id_value'}
        if status == 'not_found':
            return mockserver.make_response(status=404)
        return {'result': 0, 'status': status}

    kwargs = {
        'operation_id': 'operation_id_value',
        'personal_phone_id': 'personal_phone_id',
        'yandex_uid': 'yandex_uid',
        'wind_user_id': 'wind_user_id',
    }

    await stq_runner.talaria_misc_debts_payment_polling.call(
        task_id='operation_id_value', kwargs=kwargs,
    )

    assert _mock_wind_topups_status.times_called == 1
