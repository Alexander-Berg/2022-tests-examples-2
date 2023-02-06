import pytest


@pytest.mark.now('2019-09-25T12:11:00+0000')
@pytest.mark.translations(
    client_messages={
        'transport.card.route.arriving': {'en': 'arriving'},
        'transport.card.route.eta_min': {'en': 'min'},
        'transport.card.route.interval': {
            'en': 'every %(route_interval_in_minutes)d min',
        },
        'transport.card.route.interval_1min': {'en': 'every minute'},
        'transport.card.subtitle.stop': {'en': 'Transport Stop'},
    },
)
@pytest.mark.mtinfo(v2_stop='mtinfo_stop.json')
@pytest.mark.stops_file(filename='stops.json')
async def test_simple(taxi_masstransit, mockserver, load_binary, load_json):

    response = await taxi_masstransit.get(
        '/4.0/masstransit/v1/stopinfo?stop_id=1',
    )

    assert response.status_code == 200
    assert response.json() == load_json('expected_answer_simple.json')


@pytest.mark.now('2019-09-25T12:11:00+0000')
@pytest.mark.translations(
    client_messages={
        'transport.card.route.arriving': {'en': 'arriving'},
        'transport.card.route.eta_min': {'en': 'min'},
        'transport.card.route.interval': {
            'en': 'every %(route_interval_in_minutes)d min',
        },
        'transport.card.route.interval_1min': {'en': 'every minute'},
        'transport.card.subtitle.stop': {'en': 'Transport Stop'},
    },
)
@pytest.mark.stops_file(filename='stops.json')
@pytest.mark.mtinfo(v2_stop='mtinfo_stop.json')
@pytest.mark.parametrize('route_available', [False, True])
async def test_shuttles(
        taxi_masstransit,
        mockserver,
        load_binary,
        load_json,
        experiments3,
        route_available,
):
    experiments3.add_experiments_json(
        load_json(
            'add_shuttle_exp.json'
            if route_available
            else 'add_shuttle_exp_restricted.json',
        ),
    )

    # pylint: disable=unused-variable
    @mockserver.json_handler(
        '/shuttle-control/internal/shuttle-control/v1/stops/item',
    )
    def handler_shuttle_stops_item(request):
        return load_json('shuttle_item.json')

    response = await taxi_masstransit.get(
        '/4.0/masstransit/v1/stopinfo?stop_id=1',
    )

    assert response.status_code == 200
    assert response.json() == load_json(
        'shuttle_1.json' if route_available else 'expected_answer_simple.json',
    )
