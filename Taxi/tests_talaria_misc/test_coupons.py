import pytest


@pytest.mark.parametrize(
    [
        'wind_response_status_code',
        'wind_result',
        'expected_status',
        'expected_reason',
        'call_times',
    ],
    [
        pytest.param(200, 0, 200, None, 1, id='ok'),
        pytest.param(
            200,
            -500,
            404,
            {
                'code': 'ERROR_PROMOTION_CODE_NOT_EXIST',
                'description': 'Not exist',
                'title': 'Title',
            },
            1,
            id='not_exist',
        ),
        pytest.param(
            200,
            -501,
            404,
            {
                'code': 'ERROR_PROMOTION_CODE_IS_EXPIRED',
                'description': 'Expired',
                'title': 'Title',
            },
            1,
            id='expired',
        ),
        pytest.param(
            200,
            -503,
            404,
            {
                'code': 'ERROR_ALREADY_HAVE_PROMOTION_CODE',
                'description': 'Already have',
                'title': 'Title',
            },
            1,
            id='already_have',
        ),
        pytest.param(
            200,
            -504,
            404,
            {
                'code': 'ERROR_PROMOTION_CODE_TYPE_ERROR',
                'description': 'Type error',
                'title': 'Title',
            },
            1,
            id='type_error',
        ),
        pytest.param(
            500,
            0,
            500,
            {
                'code': 'DEFAULT_ERROR',
                'description': 'Subtitle',
                'title': 'Title',
            },
            2,
            id='500',
        ),
    ],
)
@pytest.mark.translations(
    client_messages={
        'talaria.error.title.default_error': {'en': 'Title'},
        'talaria.error.subtitle.default_error': {'en': 'Subtitle'},
        'talaria.error.subtitle.coupons_activate_post.'
        'error_promotion_code_not_exist': {'en': 'Not exist'},
        'talaria.error.subtitle.coupons_activate_post.'
        'error_promotion_code_is_expired': {'en': 'Expired'},
        'talaria.error.subtitle.coupons_activate_post.'
        'error_already_have_promotion_code': {'en': 'Already have'},
        'talaria.error.subtitle.coupons_activate_post.'
        'error_promotion_code_type_error': {'en': 'Type error'},
    },
)
async def test_coupons_activate(
        taxi_talaria_misc,
        mockserver,
        default_pa_headers,
        wind_user_auth_mock,
        wind_response_status_code,
        wind_result,
        expected_reason,
        expected_status,
        call_times,
):
    @mockserver.json_handler('/wind/pf/v1/promotionCodes/records')
    def _mock_use_promocode(request):
        assert 'authentication' in request.headers
        return mockserver.make_response(
            status=wind_response_status_code, json={'result': wind_result},
        )

    response = await taxi_talaria_misc.post(
        '/4.0/scooters/v1/coupons/activate',
        json={'promotion_code': 'code'},
        headers=default_pa_headers(),
    )

    assert _mock_use_promocode.times_called == call_times
    assert response.status_code == expected_status
    if expected_reason is None:
        assert response.json() == {}
    else:
        assert response.json()['reason'] == expected_reason
