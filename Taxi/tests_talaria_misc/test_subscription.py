import pytest


@pytest.mark.translations(
    client_messages={
        'talaria.error.title.passes_subscription_del': {'en': 'Title'},
        'talaria.error.subtitle.default_error': {'en': 'Subtitle'},
    },
)
@pytest.mark.parametrize(
    [
        'wind_response_status_code',
        'wind_result',
        'expected_status',
        'expected_code',
        'call_times',
    ],
    [
        pytest.param(200, 0, 200, None, 1, id='ok'),
        pytest.param(
            200,
            -141,
            404,
            'ERROR_USER_DO_NOT_HAVE_SUPER_PASS',
            1,
            id='no_subscribtion',
        ),
        pytest.param(
            200, -142, 500, 'DEFAULT_ERROR', 1, id='unexpected_result',
        ),
        pytest.param(500, 0, 500, 'DEFAULT_ERROR', 2, id='internal_error'),
    ],
)
async def test_delete_subscription(
        taxi_talaria_misc,
        mockserver,
        default_pa_headers,
        wind_user_auth_mock,
        wind_response_status_code,
        wind_result,
        expected_code,
        expected_status,
        call_times,
):
    @mockserver.json_handler('/wind/pf/v1/user/superPass/autoReload')
    def _mock_delete_subscription(request):
        return mockserver.make_response(
            status=wind_response_status_code, json={'result': wind_result},
        )

    response = await taxi_talaria_misc.delete(
        '/4.0/scooters/v1/passes/subscription', headers=default_pa_headers(),
    )

    assert _mock_delete_subscription.times_called == call_times
    assert response.status_code == expected_status
    if expected_code is None:
        assert response.json() == {}
    else:
        assert response.json() == {
            'reason': {
                'code': expected_code,
                'description': 'Subtitle',
                'title': 'Title',
            },
        }
