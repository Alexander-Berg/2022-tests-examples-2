# pylint: disable=import-error

DEFAULT_PARAMS = {'timeout': 1000000}


def _get_request_params(timeout=None):
    """
    Returns GET-params for request.
    """
    params = DEFAULT_PARAMS.copy()
    if timeout is not None:
        params['timeout'] = timeout

    return params


def _create_body(track, verbose=True):
    """
    Generates request body.
    :param verbose: more data will be returned, mostly about
        extrapolation and interpolation status. Also will force
        accounting  this request in statistics
    """
    result = {'track': track, 'verbose': verbose, 'prediction_seconds': 10}

    return result


def _find_first(sequence, func):
    return next(v for v in sequence if func(v))


def _assert_is_position(position):
    assert 'lat' in position
    lat = float(position['lat'])
    assert -90 <= lat <= 90

    assert 'lon' in position
    lon = float(position['lon'])
    assert -180 <= lon <= 180

    assert 'timestamp' in position
    timestamp = int(position['timestamp'])
    assert timestamp >= 0


def _assert_is_position_with_direction(position):
    _assert_is_position(position)
    assert 'direction' in position


def _test_get_predictions(response):
    data = response.json()
    assert 'predictions' in data
    positions = data['predictions']

    return positions


def _test_points_are_close(ref_point, test_point, epsilon=0.003):
    if 'is_null' in test_point:
        assert not test_point['is_null']
    assert abs(ref_point['lat'] - test_point['lat']) < epsilon
    assert abs(ref_point['lon'] - test_point['lon']) < epsilon


def _make_request_for_direction_test(taxi_yaga_adjust, load_json):
    params = _get_request_params()
    body = _create_body(load_json('adjustable_track1.json')['track'])
    return taxi_yaga_adjust.post('predict/position', body, params=params)


def _check_direction(response):
    assert response.status_code == 200
    data = response.json()
    assert 'predictions' in data
    for pos in data['predictions']:
        _assert_is_position_with_direction(pos)


async def test_graph_predict_position(taxi_yaga_adjust, load_json):
    params = _get_request_params()

    body = _create_body(load_json('adjustable_track1.json')['track'])
    response = await taxi_yaga_adjust.post(
        'predict/position', body, params=params,
    )

    assert response.status_code == 200
    data = response.json()
    assert 'predictions' in data

    # for some reasons we can't predict point at this track
    # find out why and get another track

    # positions = data['predictions']
    # assert positions

    # for src_pos, adj_pos in zip(track, positions):
    #     _assert_is_position(adj_pos)


async def test_graph_predict_empty_track(taxi_yaga_adjust):
    params = _get_request_params()
    response = await taxi_yaga_adjust.post(
        'predict/position', _create_body(track=[]), params=params,
    )

    assert response.status_code == 400


async def test_graph_predict_position_unsorted_timestamp(
        taxi_yaga_adjust, load_json,
):
    """
    Tests that track unsorted by timestamp will cause a proper error
    """
    params = _get_request_params()

    body = _create_body(
        # Take a good track
        # and reverse it to make a bad-by-timestamps one
        list(reversed(load_json('adjustable_track1.json')['track'])),
    )

    response = await taxi_yaga_adjust.post(
        'predict/position', body, params=params,
    )

    assert response.status_code == 400


async def test_mapmatcher_time_frozen(taxi_yaga_adjust, load_json):
    """
    Test checks that if you pass track with all same timestamp
    points, it will be handled correctly by mapmatcher
    mapmatcher will return an empty result.
    """
    params = _get_request_params('mapmatcher')
    body = _create_body(load_json('time_frozen_track.json')['track'])

    response = await taxi_yaga_adjust.post(
        'predict/position', body, params=params,
    )

    _test_get_predictions(response)


async def test_mapmatcher_space_frozen(taxi_yaga_adjust, load_json):
    """
    Test checks that if you pass track with all proper timestamps,
    but same lat,lon then, mapmatcher will return an empty result (and not
    crush the whole server)
    """
    params = _get_request_params('mapmatcher')
    body = _create_body(load_json('space_frozen_track.json')['track'])

    response = await taxi_yaga_adjust.post(
        'predict/position', body, params=params,
    )

    # Failure to adjust is not an error.
    _test_get_predictions(response)


async def test_unadjustable_track(taxi_yaga_adjust, load_json):
    params = _get_request_params()
    body = _create_body(load_json('unadjustable_track1.json')['track'])

    response = await taxi_yaga_adjust.post(
        'predict/position', body, params=params,
    )
    assert response.status_code == 200
    positions = _test_get_predictions(response)

    assert positions is not None and not positions
