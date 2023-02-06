import pytest

DEFAULT_HEADERS = {
    'X-Yandex-UID': '999',
    'X-YaTaxi-UserId': 'test_user_id_xxx',
    'User-Agent': 'yandex-taxi/3.18.0.7675 Android/6.0 (testenv client)',
}

DEFAULT_REQUEST = {
    'order_id': '1',
    'cancel_state': 'paid',
    'allowed_changes': [{'name': 'test'}],
}


TRANSLATIONS = {
    'cancel_rules.title.driving': {'ru': 'Отменить заказ?'},
    'cancel_rules.text.driving.paid.not_cash': {'ru': 'Будешь должен'},
    'cancel_rules.text.driving.free': {'ru': 'Бесплатно'},
    'cancel_rules.cancel_button.title': {'ru': 'Назад'},
    'cancel_rules.confirm_button.title': {'ru': 'Да, отменить'},
    'cancel_rules.confirm_button.subtitle': {'ru': 'За %(value)s'},
    'allowed_change.text.test': {'ru': 'Изменить что-то'},
    'allowed_change.text.extra_test': {'ru': 'Изменить что-то ещё'},
    'cancel_rules.different_cost_popup.title': {
        'ru': 'Итого за отмену: %(value)s',
    },
    'cancel_rules.different_cost_popup.text': {
        'ru': 'Цена изменилась пока вы ждали',
    },
    'cancel_rules.different_cost_popup.confirm_button': {'ru': 'Ясно'},
}


@pytest.mark.translations(client_messages=TRANSLATIONS)
@pytest.mark.parametrize(
    'cancel_state, expected_json, pricing_times_called',
    [
        pytest.param('paid', 'expected_cancel_rules_paid.json', 1, id='paid'),
        pytest.param('free', 'expected_cancel_rules_free.json', 0, id='free'),
        pytest.param('disabled', None, 0, id='disabled'),
    ],
)
@pytest.mark.experiments3(filename='experiments3.json')
async def test_cancel_rules(
        taxi_order_parts,
        mockserver,
        load_json,
        cancel_state,
        expected_json,
        pricing_times_called,
):
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _order_core(request):
        return load_json('order_core_response.json')

    @mockserver.json_handler('/pricing-data-preparer/v2/recalc_order')
    def _pricing_data_preparer(request):
        return load_json('pricing_data_preparer_response.json')

    request = {**DEFAULT_REQUEST, 'cancel_state': cancel_state}
    response = await taxi_order_parts.post(
        '/v1/frequency/mid', json=request, headers=DEFAULT_HEADERS,
    )

    assert response.status == 200
    assert response.headers['Cache-Control'] == 'max-age=300'

    if expected_json:
        assert response.json()['cancel_rules'] == load_json(expected_json)
    else:
        assert 'cancel_rules' not in response.json()

    assert _pricing_data_preparer.times_called == pricing_times_called


@pytest.mark.translations(client_messages=TRANSLATIONS)
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.parametrize(
    'order_core_error, pricing_data_error',
    [
        pytest.param(True, False, id='order_core_error'),
        pytest.param(True, True, id='both'),
        pytest.param(False, True, id='pricing_data_error'),
    ],
)
async def test_cancel_rules_with_problem(
        taxi_order_parts,
        mockserver,
        load_json,
        order_core_error,
        pricing_data_error,
):
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _order_core(request):
        if order_core_error:
            return mockserver.make_response(
                status=500, json={'code': '500', 'message': 'some error'},
            )
        return load_json('order_core_response.json')

    @mockserver.json_handler('/pricing-data-preparer/v2/recalc_order')
    def _pricing_data_preparer(request):
        if pricing_data_error:
            return mockserver.make_response(
                status=500, json={'code': '500', 'message': 'some error'},
            )
        return load_json('pricing_data_preparer_response.json')

    response = await taxi_order_parts.post(
        '/v1/frequency/mid', json=DEFAULT_REQUEST, headers=DEFAULT_HEADERS,
    )
    if order_core_error:
        assert response.status == 500
        return

    assert response.status == 200
    assert response.headers['Cache-Control'] == 'max-age=300'
    assert response.json()['cancel_rules'] == load_json(
        'expected_cancel_rules_free.json',
    )
