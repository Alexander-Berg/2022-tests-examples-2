import pytest

from protocol.yauber import yauber


DRIVERTAG = 'c457f916dad5ed96dcc05e150df711ad5fdf0f7239a355531b07c45cabff7ef9'


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.parametrize('use_choices_handler', [False, True])
def test_tow_regular(
        taxi_protocol,
        mockserver,
        tracker,
        now,
        config,
        use_choices_handler,
        dummy_choices,
):
    @mockserver.json_handler('/driver-ratings/v2/driver/rating')
    def _get_rating(request):
        return {'unique_driver_id': 'driver_id', 'rating': '4.927'}

    config.set_values(
        dict(USE_FEEDBACK_RETRIEVE_CHOICES_HANDLER=use_choices_handler),
    )

    tracker.set_position(
        '999012_a5709ce56c2740d9a536650f5390de0b',
        now,
        55.73341076871702,
        37.58917997300821,
    )

    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
        headers=yauber.headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content['status'] == 'waiting'
    assert content['tariff']['class'] == 'uberx'
    assert content['driver'] == {
        'car': [37.58917997300821, 55.73341076871702],
        'color': 'фиолетовый',
        'color_code': '4A2197',
        'model': 'Skoda Fabia',
        'name': 'Бородач Исак Арнольдович',
        'overdue': False,
        'phone': '+79321259615',
        'need_request_driver_phone': True,
        'plates': 'Х492НК77',
        'way_time': 0,
        'yellow_car_number': False,
        'photo_url': (
            'https://tc.mobile.yandex.net/static/images/'
            '41007/54630f09-1f14-4bf3-8c24-04fdd7059107'
        ),
        'rating': '4.92',
        'tag': DRIVERTAG,
    }
    assert dummy_choices.was_called() == use_choices_handler
