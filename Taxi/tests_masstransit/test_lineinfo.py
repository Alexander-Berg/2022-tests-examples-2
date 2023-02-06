import pytest


@pytest.mark.now('2019-09-25T12:11:00+0000')
@pytest.mark.mtinfo(v2_line='mtinfo_line.json')
async def test_simple(taxi_masstransit, mockserver, load_binary, load_json):

    response = await taxi_masstransit.get(
        '/4.0/masstransit/v1/lineinfo?line_id=213_144_bus_mosgortrans',
    )
    assert response.status_code == 200
    expected_json = load_json('expected_response.json')
    response_json = response.json()
    assert expected_json['info'] == response_json['info']


@pytest.mark.now('2019-09-25T12:11:00+0000')
@pytest.mark.mtinfo(v2_line='mtinfo_line.json')
@pytest.mark.experiments3(filename='shuttle_line_color.json')
@pytest.mark.parametrize('route_available', [False, True])
@pytest.mark.parametrize(
    'stop_id,has_order',
    [('transport_stop_5_1', False), ('simple_stop_2_2', True), ('', True)],
)
async def test_shuttles(
        taxi_masstransit,
        mockserver,
        load_binary,
        load_json,
        experiments3,
        stop_id,
        has_order,
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
        return load_json('shuttle_stop_item.json')

    @mockserver.json_handler(
        '/shuttle-control/internal/shuttle-control/v1/shuttles/list',
    )
    def handler_shuttle_shuttles_list(request):
        response = load_json('shuttles_list.json')
        if 'shuttle_ids' in request.json:
            return [
                item
                for item in response
                if item['id'] in request.json['shuttle_ids']
            ]
        return response

    @mockserver.json_handler(
        '/shuttle-control/internal/shuttle-control/v1/routes/list',
    )
    def handler_shuttle_routes_list(request):
        response = load_json('shuttles_routes.json')
        if not has_order:
            response[0]['is_cyclic'] = False
        return response

    line = 'line_id=shuttle_route_1'
    stop = 'stop_id=' + stop_id
    pos = 'position=2.000001,2.000001'
    vid = 'vehicle_id=shuttle_1'
    query = '&'.join([line, stop, pos, vid])
    response = await taxi_masstransit.get(
        '/4.0/masstransit/v1/lineinfo?' + query,
        headers={'X-Yandex-UID': '11111'},
    )

    if not route_available:
        assert response.status_code == 404
        return

    assert response.status_code == 200
    expected_json = load_json('shuttle_response.json')
    response_json = response.json()
    assert expected_json['info'] == response_json['info']
    if not has_order:
        expected_json['threads'][0]['segments'].pop()
        expected_json['selected_vehicle']['stops_estimation'].pop()
    assert response_json['threads'] == expected_json['threads']
    for est in expected_json['selected_vehicle']['stops_estimation']:
        if est['stop']['id'] == stop_id:
            est['is_current'] = True
    assert (
        response_json['selected_vehicle'] == expected_json['selected_vehicle']
    )
    assert response_json['schedule'] == expected_json['schedule']
    if not has_order:
        assert response_json.get('order', False) == has_order
    else:
        assert response_json['order'] == expected_json['order']


TRANSLATIONS = {
    'shuttle_control.stops.shuttle_stop_1': {
        'ru': 'Shuttle stop 1 tanker key',
    },
    'shuttle_control.routes.to_oko': {'ru': 'To oko from tanker'},
    'shuttle_control.stops.0_0': {'ru': '0 - 0 stop'},
    'shuttle_control.stops.2_2': {'ru': '2 - 2 stop'},
    'shuttle_control.stops.5_1': {'ru': '5 - 1 stop'},
}


@pytest.mark.now('2019-09-25T12:11:00+0000')
@pytest.mark.mtinfo(v2_line='mtinfo_line.json')
@pytest.mark.parametrize('order_enabled', [False, True])
@pytest.mark.parametrize(
    'expected_line_name, expected_threads_start_stop_names, '
    'expected_thread_segments_names, expected_selected_vehicle_stop_names ',
    [
        (
            'To OKO',
            ['0 - 0'],
            ['0 - 0', '2 - 2', '5 - 1'],
            ['0 - 0', '0 - 0', '2 - 2', '5 - 1'],
        ),
        pytest.param(
            'To oko from tanker',
            ['0 - 0 stop'],
            ['0 - 0 stop', '2 - 2 stop', '5 - 1 stop'],
            ['0 - 0 stop', '0 - 0 stop', '2 - 2 stop', '5 - 1 stop'],
            marks=pytest.mark.translations(client_messages=TRANSLATIONS),
        ),
    ],
)
async def test_shuttles_translation(
        taxi_masstransit,
        mockserver,
        experiments3,
        load_binary,
        load_json,
        expected_line_name,
        expected_threads_start_stop_names,
        expected_thread_segments_names,
        expected_selected_vehicle_stop_names,
        order_enabled,
):
    experiments3.add_experiments_json(
        load_json(
            'add_shuttle_exp.json'
            if order_enabled
            else 'add_shuttle_exp_deprecated_booking.json',
        ),
    )

    # pylint: disable=unused-variable
    @mockserver.json_handler(
        '/shuttle-control/internal/shuttle-control/v1/stops/item',
    )
    def handler_shuttle_stops_item(request):
        return load_json('shuttle_stop_item.json')

    @mockserver.json_handler(
        '/shuttle-control/internal/shuttle-control/v1/shuttles/list',
    )
    def handler_shuttle_shuttles_list(request):
        return load_json('shuttles_list.json')

    @mockserver.json_handler(
        '/shuttle-control/internal/shuttle-control/v1/routes/list',
    )
    def handler_shuttle_routes_list(request):
        return load_json('shuttles_routes.json')

    line = 'line_id=shuttle_route_1'
    stop = 'stop_id=transport_stop_5_1'
    pos = 'position=2.000001,2.000001'
    vid = 'vehicle_id=shuttle_1'
    query = '&'.join([line, stop, pos, vid])
    response = await taxi_masstransit.get(
        '/4.0/masstransit/v1/lineinfo?' + query,
        headers={'X-Yandex-UID': '11111'},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['info']['name'] == expected_line_name

    order = response_json.get('order', False)
    if order_enabled:
        assert order
    else:
        assert not order

    threads_start_stop_names = sorted(
        [thread['start_stop']['name'] for thread in response_json['threads']],
    )
    assert threads_start_stop_names == expected_threads_start_stop_names

    thread_segments_names = sum(
        [
            [segment['end_stop']['name'] for segment in thread['segments']]
            for thread in response_json['threads']
        ],
        [],
    )
    thread_segments_names = sorted(thread_segments_names)
    assert thread_segments_names == expected_thread_segments_names

    selected_vehicle_stop_names = [
        stop['stop']['name']
        for stop in response_json['selected_vehicle']['stops_estimation']
    ]
    selected_vehicle_stop_names = sorted(selected_vehicle_stop_names)
    assert selected_vehicle_stop_names == expected_selected_vehicle_stop_names
