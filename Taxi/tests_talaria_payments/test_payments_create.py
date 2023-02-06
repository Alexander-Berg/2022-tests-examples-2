import pytest


@pytest.mark.now('2022-01-01T00:00:00+00:00')
@pytest.mark.parametrize(
    [
        'invoice_create_response',
        'invoice_update_response',
        'invoice_case',
        'expected_response',
    ],
    [
        (200, 200, None, 200),
        (200, 400, None, 500),
        (400, None, None, 500),
        (200, 404, None, 500),
        (409, 200, 'no_conflict', 200),
        (200, 409, 'no_conflict', 200),
        (409, None, 'payment_method_id_mismatch', 409),
        (200, 409, 'items_mismatch', 409),
        (409, 409, 'items_mismatch', 409),
    ],
)
async def test_main(
        taxi_talaria_payments,
        mockserver,
        load_json,
        invoice_create_response: int,
        invoice_update_response: int,
        invoice_case: str,
        expected_response: int,
):
    @mockserver.json_handler('/transactions-ng/v2/invoice/create')
    def invoice_create(request):
        assert request.json == load_json('invoice_create_request.json')

        if invoice_create_response == 200:
            response = {}
        else:
            response = {'code': 'code', 'message': 'message'}

        return mockserver.make_response(
            status=invoice_create_response, json=response,
        )

    @mockserver.json_handler('/transactions-ng/v2/invoice/update')
    def invoice_update(request):
        assert request.json == load_json('invoice_update_request.json')
        if invoice_update_response == 200:
            response = {}
        else:
            response = {'code': 'code', 'message': 'message'}

        return mockserver.make_response(
            status=invoice_update_response, json=response,
        )

    @mockserver.json_handler('/transactions-ng/v2/invoice/retrieve')
    def invoice_retrieve(request):
        assert request.json == load_json('invoice_retrieve_request.json')
        return load_json(f'invoice_retrieve_response_{invoice_case}.json')

    @mockserver.json_handler(
        '/talaria-misc/talaria/v1/wind-user-to-yandex-user',
    )
    def wind_user_to_yandex_user(request):
        assert request.query == {'wind_user_id': 'wind_user_id'}
        return {
            'yandex_uid': 'another_yandex_uid',
            'personal_phone_id': 'personal_phone_id',
        }

    response = await taxi_talaria_payments.post(
        '/talaria-payments/v1/payments/create',
        json=load_json('payments_create_request.json'),
        headers={'x-api-key': 'wind_api_key', 'X-Real-IP': '1.1.1.1'},
    )
    assert response.status_code == expected_response

    assert wind_user_to_yandex_user.times_called == 1

    if expected_response not in [200, 500]:
        assert response.json()['code'] == invoice_case

    assert invoice_create.times_called == 1

    if invoice_update_response is not None:
        assert invoice_update.times_called == 1
    else:
        assert invoice_update.times_called == 0

    if invoice_case is not None:
        if invoice_create_response == 409 and invoice_update_response == 409:
            assert invoice_retrieve.times_called == 2
        else:
            assert invoice_retrieve.times_called == 1
    else:
        assert invoice_retrieve.times_called == 0


@pytest.mark.now('2022-01-01T00:00:00+00:00')
@pytest.mark.config(
    TALARIA_PAYMENTS_CHARGE_TYPE_SETTINGS_MAP={
        '__default__': {'user_state_flow': 'order'},
        'topup': {
            'user_state_flow': 'topup',
            'user_state_flow_fallbacks': ['order', 'free_pass'],
        },
    },
)
@pytest.mark.parametrize(
    ['yandex_uid_found', 'flows_found', 'expected_flow', 'expected_response'],
    [
        (True, ['topup', 'order'], 'topup', 200),
        (True, ['tips', 'free_pass', 'order'], 'order', 200),
        (True, ['tips', 'free_pass'], 'free_pass', 200),
        (False, ['topup', 'order'], None, 404),
        (True, ['tips'], None, 404),
    ],
)
async def test_without_optional_params(
        taxi_talaria_payments,
        mockserver,
        load_json,
        yandex_uid_found: bool,
        flows_found: list,
        expected_flow: str,
        expected_response: int,
):
    @mockserver.json_handler('/transactions-ng/v2/invoice/create')
    def invoice_create(request):
        assert request.json == load_json('invoice_create_request_short.json')
        return {}

    @mockserver.json_handler('/transactions-ng/v2/invoice/update')
    def invoice_update(request):
        assert request.json == load_json('invoice_update_request.json')
        return {}

    @mockserver.json_handler(
        '/talaria-misc/talaria/v1/wind-user-to-yandex-user',
    )
    def wind_user_to_yandex_user(request):
        assert request.query == {'wind_user_id': 'wind_user_id'}
        if yandex_uid_found:
            return {
                'yandex_uid': 'yandex_uid',
                'personal_phone_id': 'personal_phone_id',
            }
        return mockserver.make_response(status=404)

    @mockserver.json_handler('/user-state/internal/v1/last-payment-methods')
    def user_state(request):
        assert request.query == {'service': 'scooters'}
        flows = []
        for flow in flows_found:
            flow_data = {'flow_type': flow}
            if flow == expected_flow:
                flow_data['payment_method'] = {
                    'type': 'card',
                    'id': 'payment_method_id',
                }
            else:
                flow_data['payment_method'] = {
                    'type': 'applepay',
                    'id': 'unexpected_payment_method_id',
                }
            flows.append(flow_data)
        return {'flows': flows}

    response = await taxi_talaria_payments.post(
        '/talaria-payments/v1/payments/create',
        json=load_json('payments_create_request_short.json'),
        headers={'x-api-key': 'wind_api_key', 'X-Real-IP': '1.1.1.1'},
    )

    assert response.status_code == expected_response

    if expected_response != 200:
        resp_body = response.json()
        if not yandex_uid_found:
            assert resp_body['code'] == 'user_not_found'
        elif not expected_flow:
            assert resp_body['code'] == 'payment_method_not_found'

    assert wind_user_to_yandex_user.times_called == 1

    if yandex_uid_found:
        assert user_state.times_called == 1
    else:
        assert user_state.times_called == 0

    if expected_response == 200:
        assert invoice_create.times_called == 1
        assert invoice_update.times_called == 1
    else:
        assert invoice_create.times_called == 0
        assert invoice_update.times_called == 0


@pytest.mark.now('2022-01-01T00:00:00+00:00')
@pytest.mark.parametrize(
    ['is_payment_allowed'],
    [
        pytest.param(
            True,
            marks=pytest.mark.experiments3(
                filename='exp3_payment_restrictions_allowed.json',
            ),
        ),
        pytest.param(
            False,
            marks=pytest.mark.experiments3(
                filename='exp3_payment_restrictions_not_allowed.json',
            ),
        ),
    ],
)
async def test_payment_restriction(
        taxi_talaria_payments, mockserver, load_json, is_payment_allowed: bool,
):
    @mockserver.json_handler('/transactions-ng/v2/invoice/create')
    def invoice_create(request):
        assert request.json == load_json('invoice_create_request.json')
        return {}

    @mockserver.json_handler('/transactions-ng/v2/invoice/update')
    def invoice_update(request):
        assert request.json == load_json('invoice_update_request.json')
        return {}

    # @mockserver.json_handler('/transactions-ng/v2/invoice/retrieve')
    # def invoice_retrieve(request):
    #     assert request.json == load_json('invoice_retrieve_request.json')
    #     return load_json(f'invoice_retrieve_response_no_conflict.json')

    @mockserver.json_handler(
        '/talaria-misc/talaria/v1/wind-user-to-yandex-user',
    )
    def wind_user_to_yandex_user(request):
        assert request.query == {'wind_user_id': 'wind_user_id'}
        return {
            'yandex_uid': 'yandex_uid',
            'personal_phone_id': 'personal_phone_id',
        }

    response = await taxi_talaria_payments.post(
        '/talaria-payments/v1/payments/create',
        json=load_json('payments_create_request.json'),
        headers={'x-api-key': 'wind_api_key', 'X-Real-IP': '1.1.1.1'},
    )
    if is_payment_allowed:
        assert response.status_code == 200
        assert wind_user_to_yandex_user.times_called == 1
        # assert invoice_retrieve.times_called == 1
        assert invoice_create.times_called == 1
        assert invoice_update.times_called == 1
    else:
        assert response.status_code == 500
        assert wind_user_to_yandex_user.times_called == 1
        assert invoice_create.times_called == 0
        assert invoice_update.times_called == 0
