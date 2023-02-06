import pytest


@pytest.mark.parametrize(
    'range_results_override, user_exists',
    [
        pytest.param(
            False,
            True,
            marks=(pytest.mark.pgsql('talaria_misc', files=['users.sql'])),
            id='no_range_results_override',
        ),
        pytest.param(
            True,
            True,
            marks=(
                pytest.mark.experiments3(
                    filename='config3_wind_yango_ride_history_settings.json',
                ),
                pytest.mark.pgsql('talaria_misc', files=['users.sql']),
            ),
            id='with_range_results_override',
        ),
        pytest.param(False, False, id='user_does_not_exist'),
    ],
)
async def test_ride_history_list(
        mockserver,
        load_json,
        taxi_talaria_misc,
        get_users_form_db,
        range_results_override,
        user_exists,
):
    @mockserver.json_handler('/wind/pf/v1/boardRides')
    def _mock_wind_boards_finsh_ride_response(request):
        expected_limit = '5' if range_results_override else '1'
        assert request.query['limit'] == expected_limit
        return load_json('wind_ride_history_response.json')

    request = {
        'yandex_user_info': {
            'yandex_uid': 'yandex_uid',
            'personal_phone_id': 'personal_phone_id',
        },
        'range': {'results': 1},
    }
    response = await taxi_talaria_misc.post(
        '/talaria/v1/ride-history/list', json=request,
    )
    assert response.status_code == 200
    response_body = response.json()
    if user_exists:
        assert response_body == load_json('expected_response.json')
        assert _mock_wind_boards_finsh_ride_response.times_called == 1
    else:
        assert response_body == {'orders': []}
        assert _mock_wind_boards_finsh_ride_response.times_called == 0


@pytest.mark.translations(
    client_messages={
        'talaria.ride_history.payment_method.card': {'en': 'Card'},
        'talaria.ride_history.bill_item.riding': {'en': 'Riding'},
        'talaria.ride_history.bill_item.reservation': {'en': 'Reservation'},
        'talaria.ride_history.bill_item.unlock': {'en': 'Unlocking'},
    },
)
@pytest.mark.pgsql('talaria_misc', files=['users.sql'])
async def test_ride_history_item(
        mockserver, load_json, taxi_talaria_misc, get_users_form_db,
):
    order_id = 'some_ride_id'

    @mockserver.json_handler(f'/wind/pf/v1/boardRides/{order_id}')
    def _mock_wind_board_ride_response(request):
        return load_json('wind_board_ride_response.json')

    request = {
        'yandex_user_info': {
            'yandex_uid': 'yandex_uid',
            'personal_phone_id': 'personal_phone_id',
        },
        'order_id': order_id,
    }
    response = await taxi_talaria_misc.post(
        '/talaria/v1/ride-history/item',
        json=request,
        headers={'Accept-Language': 'en'},
    )
    assert response.status_code == 200
    assert response.json() == load_json('item_expected_response.json')
