import pytest

from . import conftest


PROFILE_REQUEST = {
    'user': {'personal_phone_id': 'personal_phone_id_123'},
    'name': 'Petya',
    'sourceid': 'cargo',
}

PROFILE_RESPONSE = {
    'dont_ask_name': False,
    'experiments': [],
    'name': 'Petya',
    'personal_phone_id': 'personal_phone_id_123',
    'user_id': 'taxi_user_id_1',
}


def _behavior_network_error(mockserver):
    raise mockserver.NetworkError()


def _behavior_500(mockserver):
    return mockserver.make_response('{}', 500, content_type='application/json')


def _behavior_400(mockserver):
    return mockserver.make_response('{}', 400, content_type='application/json')


def _behavior_401(mockserver):
    return mockserver.make_response('{}', 401, content_type='application/json')


def _behavior_404(mockserver):
    return mockserver.make_response('{}', 404, content_type='application/json')


def _behavior_406(mockserver):
    return mockserver.make_response('{}', 406, content_type='application/json')


def _behavior_429(mockserver):
    return mockserver.make_response('{}', 429, content_type='application/json')


def _predicat_has_calls(queue):
    return queue.has_calls


def _predicat_times_called_0(queue):
    return queue.times_called == 0


def _predicat_times_called_1(queue):
    return queue.times_called == 1


@pytest.mark.parametrize(
    'mock_behavior', [_behavior_network_error, _behavior_500],
)
async def test_handler_profile_problems(
        mockserver, stq_runner, mock_behavior, mock_claims_full,
):
    mock_claims_full.response['items'] = [
        {
            'id': 123,
            'extra_id': '123',
            'pickup_point': 1,
            'droppof_point': 2,
            'title': 'Холодильник карманный',
            'size': {'length': 0.1, 'width': 0.2, 'height': 0.3},
            'weight': 5,
            'quantity': 1,
            'cost_value': '10.20',
            'cost_currency': 'RUR',
        },
    ]

    @mockserver.json_handler('/int-authproxy/v1/profile')
    def _profile(request):
        assert request.json == PROFILE_REQUEST
        return mock_behavior(mockserver)

    await stq_runner.cargo_matcher_claim_estimating.call(
        task_id='claim_id_1', expect_fail=True,
    )

    assert mock_claims_full.mock.times_called == 1
    assert _profile.has_calls


@pytest.mark.parametrize(
    'mock_behavior, result_predicat, expect_fail',
    [
        (_behavior_network_error, _predicat_has_calls, True),
        (_behavior_500, _predicat_has_calls, True),
        (_behavior_400, _predicat_times_called_1, False),
        (_behavior_404, _predicat_times_called_1, False),
        (_behavior_406, _predicat_times_called_1, False),
        (_behavior_429, _predicat_times_called_1, False),
    ],
)
async def test_handler_orders_estimate_problems(
        mockserver,
        stq_runner,
        mock_claims_full,
        mock_behavior,
        result_predicat,
        expect_fail,
):
    mock_claims_full.response['items'] = [
        {
            'id': 123,
            'extra_id': '123',
            'pickup_point': 1,
            'droppof_point': 2,
            'title': 'Холодильник карманный',
            'size': {'length': 0.1, 'width': 0.2, 'height': 0.3},
            'weight': 5,
            'quantity': 1,
            'cost_value': '10.20',
            'cost_currency': 'RUR',
        },
    ]

    @mockserver.json_handler('/cargo-claims/v1/claims/finish-estimate')
    def _dummy_save_result(request):
        return {
            'id': 'claim_id_1',
            'status': 'ready_for_approval',
            'version': 1,
            'user_request_revision': '123',
            'skip_client_notify': True,
        }

    @mockserver.json_handler('/int-authproxy/v1/profile')
    def _profile(request):
        assert request.json == PROFILE_REQUEST
        return PROFILE_RESPONSE

    @mockserver.json_handler('/int-authproxy/v1/orders/estimate')
    def _orders_estimate(request):
        assert request.json == {
            'sourceid': 'cargo',
            'selected_class': 'express',
            'user': {
                'personal_phone_id': 'personal_phone_id_123',
                'user_id': 'taxi_user_id_1',
            },
            'payment': {
                'payment_method_id': 'corp-corp_client_id_12312312312312312',
                'type': 'corp',
            },
            'requirements': {'door_to_door': True},
            'route': [[37.1, 55.1], [37.2, 55.3]],
        }
        return mock_behavior(mockserver)

    await stq_runner.cargo_matcher_claim_estimating.call(
        task_id='claim_id_1', expect_fail=expect_fail,
    )

    assert mock_claims_full.mock.times_called == 1
    assert _profile.times_called == 1
    assert result_predicat(_orders_estimate)
    assert expect_fail != result_predicat(_dummy_save_result)


def _behavior_404_v2(mockserver):
    return mockserver.make_response(
        '{"code": "404", "message": "404"}',
        404,
        content_type='application/json',
    )


@pytest.mark.parametrize(
    'mock_behavior, result_predicat, expect_fail',
    [(_behavior_404_v2, _predicat_times_called_1, False)],
)
async def test_v1_tariff_corp_current_problem(
        mockserver,
        stq_runner,
        mock_claims_full,
        mock_behavior,
        result_predicat,
        expect_fail,
):
    mock_claims_full.response['items'] = [
        {
            'id': 123,
            'extra_id': '123',
            'pickup_point': 1,
            'droppof_point': 2,
            'title': 'Холодильник карманный',
            'size': {'length': 0.1, 'width': 0.2, 'height': 0.3},
            'weight': 5,
            'quantity': 1,
            'cost_value': '10.20',
            'cost_currency': 'RUR',
        },
    ]

    @mockserver.json_handler('/int-authproxy/v1/orders/estimate')
    def _orders_estimate(request):
        assert request.json == {
            'sourceid': 'cargo',
            'selected_class': 'express',
            'user': {
                'personal_phone_id': 'personal_phone_id_123',
                'user_id': 'taxi_user_id_1',
            },
            'payment': {
                'payment_method_id': 'corp-corp_client_id_12312312312312312',
                'type': 'corp',
            },
            'requirements': {'door_to_door': True},
            'route': [[37.1, 55.1], [37.2, 55.3]],
        }
        return {
            'offer': 'taxi_offer_id_1',
            'is_fixed_price': True,
            'currency_rules': conftest.get_currency_rules(),
            'service_levels': [{'class': 'express', 'price_raw': 999.001}],
        }

    @mockserver.json_handler('/cargo-claims/v1/claims/finish-estimate')
    def _dummy_save_result(request):
        return {
            'id': 'claim_id_1',
            'status': 'ready_for_approval',
            'version': 1,
            'user_request_revision': '123',
            'skip_client_notify': True,
        }

    @mockserver.json_handler('/int-authproxy/v1/profile')
    def _profile(request):
        assert request.json == PROFILE_REQUEST
        return PROFILE_RESPONSE

    await stq_runner.cargo_matcher_claim_estimating.call(
        task_id='claim_id_1', expect_fail=expect_fail,
    )

    assert expect_fail != result_predicat(_dummy_save_result)
