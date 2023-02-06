import copy

import pytest


ALGORITHMS = ['mapmatcher', 'snap', 'auto']

TRACK_PREPROCESSING_SETTINGS = [
    {},  # This is 'no preprocessing mode'
    {'no_speed': True},
]

EXTRAPOLATE_OPTIONS = [True, False]

DEFAULT_PARAMS = {'timeout': 1000000}


def _get_request_params(algorithm, timeout=None):
    """
    Returns GET-params for request.
    """
    params = DEFAULT_PARAMS.copy()
    params['algorithm'] = algorithm
    if timeout is not None:
        params['timeout'] = timeout

    return params


def _create_body(
        track,
        extrapolate=None,
        interpolate=None,
        preprocess_settings=None,
        verbose=True,
):
    """
    Generates request body.
    :param extrapolate: forces enabling/disabling of extrapolation
    :param verbose: more data will be returned, mostly about
        extrapolation and interpolation status. Also will force
        accounting  this request in statistics
    :param preprocess_settings: track will be additionally preprocessed
           before building request body. @see method _preprocess_track
           for more information
    """
    if preprocess_settings is not None:
        track = _preprocess_track(track, preprocess_settings)
    result = {'track': track, 'verbose': verbose}
    if extrapolate is not None:
        result['extrapolate'] = extrapolate
    if interpolate is not None:
        result['interpolate'] = interpolate

    return result


def _preprocess_track(track, settings):
    result = track
    if settings.get('no_speed', False):
        result = copy.deepcopy(track)
        for point in result:
            if 'speed' in point:
                del point['speed']
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


def _test_valid_but_not_adjusted(response):
    """
    Failure to adjust is not an error. It is expressed as
    list of positions, every position has is_null == true
    """
    assert response.status_code == 200
    data = response.json()
    assert 'positions' in data
    positions = data['positions']

    assert 'current_position' not in data
    assert positions
    for pos in positions:
        assert 'is_null' in pos
        assert pos['is_null'] is True


def _test_get_positions(response):
    data = response.json()
    assert 'positions' in data
    positions = data['positions']

    return positions


def _test_points_are_close(ref_point, test_point, epsilon=0.003):
    if 'is_null' in test_point:
        assert not test_point['is_null']
    assert abs(ref_point['lat'] - test_point['lat']) < epsilon
    assert abs(ref_point['lon'] - test_point['lon']) < epsilon


def _test_current_position_valid(source_track, positions, current_position):
    if all(map(lambda x: x['is_null'] is True, positions)):
        # track is unadjusted
        assert current_position is None
        return

    # track is adjusted
    assert 'timestamp' in current_position
    timestamp = current_position['timestamp']

    assert 'points' in current_position
    points = current_position['points']
    assert len(points) == 1
    current_point = points[0]

    x = current_point.copy()
    x.update({'timestamp': timestamp})
    _assert_is_position(x)

    # get last adjusted position
    last_idx = next(
        i
        for i in reversed(range(len(positions)))
        if (positions[i]['is_null'] is False)
    )
    last_adj = positions[last_idx]

    # This version of graph adjustment service returns only one
    # item in current_position and it is the last adjusted pos
    _test_points_are_close(last_adj, x, 0.00001)
    assert timestamp >= last_adj['timestamp']

    assert timestamp == source_track[-1]['timestamp']

    assert 'probability' in current_point
    probability = current_point['probability']
    assert probability >= 0
    assert probability <= 1


def _make_request_for_direction_test(
        taxi_yaga_adjust,
        load_json,
        algorithm,
        preprocess_settings,
        extrapolate,
):
    params = _get_request_params(algorithm)
    body = _create_body(
        load_json('adjustable_track1.json')['track'],
        extrapolate=extrapolate,
        preprocess_settings=preprocess_settings,
    )
    return taxi_yaga_adjust.post('adjust/track', body, params=params)


def _check_direction(response):
    assert response.status_code == 200
    data = response.json()
    assert 'positions' in data
    for adjusted_position in data['positions']:
        _assert_is_position_with_direction(adjusted_position)


@pytest.mark.parametrize('algorithm', ALGORITHMS)
@pytest.mark.parametrize('extrapolate', EXTRAPOLATE_OPTIONS)
@pytest.mark.parametrize('preprocess_settings', TRACK_PREPROCESSING_SETTINGS)
async def test_graph_adjust_without_direction_experiment(
        taxi_yaga_adjust,
        load_json,
        algorithm,
        preprocess_settings,
        extrapolate,
):
    response = await _make_request_for_direction_test(
        taxi_yaga_adjust,
        load_json,
        algorithm,
        preprocess_settings,
        extrapolate,
    )
    _check_direction(response)


@pytest.mark.parametrize('algorithm', ALGORITHMS)
@pytest.mark.parametrize('extrapolate', EXTRAPOLATE_OPTIONS)
@pytest.mark.parametrize('preprocess_settings', TRACK_PREPROCESSING_SETTINGS)
async def test_graph_adjust_track(
        taxi_yaga_adjust,
        load_json,
        algorithm,
        preprocess_settings,
        extrapolate,
):
    params = _get_request_params(algorithm)

    body = _create_body(
        load_json('adjustable_track1.json')['track'],
        extrapolate=extrapolate,
        preprocess_settings=preprocess_settings,
    )
    track = body['track']
    response = await taxi_yaga_adjust.post('adjust/track', body, params=params)

    assert response.status_code == 200
    data = response.json()
    assert 'positions' in data
    positions = data['positions']

    assert len(positions) == len(track)

    adjusted_count = 0
    for src_pos, adj_pos in zip(track, positions):
        _assert_is_position(adj_pos)

        if adj_pos['is_null'] is False:
            adjusted_count += 1
            assert src_pos['timestamp'] == adj_pos['timestamp']
            assert 'is_toll' in adj_pos
            assert not adj_pos['is_toll']

    assert adjusted_count >= 3

    ref_point = track[-1]
    last_adj_point = positions[-1]
    # last point is near the road, so we shouldn't stray far
    assert last_adj_point['lat'] - ref_point['lat'] < 0.001
    assert last_adj_point['lon'] - ref_point['lon'] < 0.001

    # Check current position
    assert 'current_position' in data
    current_position = data['current_position']
    _test_current_position_valid(track, positions, current_position)

    assert 'timestamp' in current_position


@pytest.mark.parametrize('algorithm', ALGORITHMS)
@pytest.mark.parametrize('extrapolate', EXTRAPOLATE_OPTIONS)
async def test_graph_adjust_empty_track(
        taxi_yaga_adjust, algorithm, extrapolate,
):
    params = _get_request_params(algorithm)
    response = await taxi_yaga_adjust.post(
        'adjust/track',
        _create_body(track=[], extrapolate=None),
        params=params,
    )

    assert response.status_code == 400


# @pytest.mark.parametrize('algorithm', ['mapmatcher', 'auto'])
# @pytest.mark.parametrize('extrapolate', EXTRAPOLATE_OPTIONS)
# async def test_graph_adjust_timeout(
#         taxi_yaga_adjust,
#         load_json,
#         algorithm,
#         extrapolate):
#     """
#     Both 'auto' and 'mapmatcher' algorithms should follow timeout requested
#     """
#
#     params = _get_request_params(algorithm,
#                                                    timeout=1)
#
#     body = _create_body(
#         load_json('adjustable_track1.json')['track'],
#         extrapolate=extrapolate)
#     response = await taxi_graph_adjust.post(
#         'adjust/track',
#          body,
#          params=params)
#
#     assert response.status_code == 413


@pytest.mark.parametrize('algorithm', ALGORITHMS)
@pytest.mark.parametrize('extrapolate', EXTRAPOLATE_OPTIONS)
@pytest.mark.parametrize('preprocess_settings', TRACK_PREPROCESSING_SETTINGS)
async def test_graph_adjust_track_unsorted_timestamp(
        taxi_yaga_adjust,
        load_json,
        algorithm,
        preprocess_settings,
        extrapolate,
):
    """
    Tests that track unsorted by timestamp will cause a proper error
    """
    params = _get_request_params(algorithm)

    body = _create_body(
        # Take a good track
        # and reverse it to make a bad-by-timestamps one
        list(reversed(load_json('adjustable_track1.json')['track'])),
        preprocess_settings=preprocess_settings,
        extrapolate=extrapolate,
    )

    response = await taxi_yaga_adjust.post('adjust/track', body, params=params)

    assert response.status_code == 400


@pytest.mark.parametrize('algorithm', ALGORITHMS)
@pytest.mark.parametrize('extrapolate', EXTRAPOLATE_OPTIONS)
@pytest.mark.parametrize('preprocess_settings', TRACK_PREPROCESSING_SETTINGS)
async def test_graph_adjust_position_broken_path(
        taxi_yaga_adjust,
        load_json,
        algorithm,
        preprocess_settings,
        extrapolate,
):
    """
    This test track is moving backwards one uni-directional road. As a result
    mapmatcher returns a broken path. We must not crush on such cases.
    """
    params = _get_request_params(algorithm)

    # Take a good track
    body = _create_body(
        list(reversed(load_json('broken_track.json')['track'])),
        preprocess_settings=preprocess_settings,
        extrapolate=extrapolate,
    )

    response = await taxi_yaga_adjust.post('adjust/track', body, params=params)

    assert response.status_code == 400


@pytest.mark.parametrize('preprocess_settings', TRACK_PREPROCESSING_SETTINGS)
@pytest.mark.parametrize('extrapolate', EXTRAPOLATE_OPTIONS)
async def test_mapmatcher_time_frozen(
        taxi_yaga_adjust, load_json, preprocess_settings, extrapolate,
):
    """
    Test checks that if you pass track with all same timestamp
    points, it will be handled correctly by mapmatcher
    mapmatcher will return an empty result.
    """
    params = _get_request_params('mapmatcher')
    body = _create_body(
        load_json('time_frozen_track.json')['track'],
        preprocess_settings=preprocess_settings,
        extrapolate=extrapolate,
    )

    response = await taxi_yaga_adjust.post('adjust/track', body, params=params)

    _test_valid_but_not_adjusted(response)


@pytest.mark.parametrize('preprocess_settings', TRACK_PREPROCESSING_SETTINGS)
@pytest.mark.parametrize('extrapolate', EXTRAPOLATE_OPTIONS)
async def test_mapmatcher_space_frozen(
        taxi_yaga_adjust, load_json, preprocess_settings, extrapolate,
):
    """
    Test checks that if you pass track with all proper timestamps,
    but same lat,lon then, mapmatcher will return an empty result (and not
    crush the whole server)
    """
    params = _get_request_params('mapmatcher')
    body = _create_body(
        load_json('space_frozen_track.json')['track'],
        preprocess_settings=preprocess_settings,
        extrapolate=extrapolate,
    )

    response = await taxi_yaga_adjust.post('adjust/track', body, params=params)

    # Failure to adjust is not an error.
    _test_valid_but_not_adjusted(response)


@pytest.mark.parametrize(
    'algorithm', list(filter(lambda x: x != 'mapmatcher', ALGORITHMS)),
)
@pytest.mark.parametrize('preprocess_settings', TRACK_PREPROCESSING_SETTINGS)
@pytest.mark.parametrize('extrapolate', EXTRAPOLATE_OPTIONS)
async def test_graph_adjust_space_frozen(
        taxi_yaga_adjust,
        load_json,
        algorithm,
        preprocess_settings,
        extrapolate,
):
    """
    Test checks that if you pass track with all proper timestamps,
    but same lat,lon then algorithms (except mapmatcher) will return
    correct results
    """
    params = _get_request_params(algorithm)
    body = _create_body(
        load_json('space_frozen_track.json')['track'],
        preprocess_settings=preprocess_settings,
        extrapolate=extrapolate,
    )
    track = body['track']

    response = await taxi_yaga_adjust.post('adjust/track', body, params=params)

    assert response.status_code == 200
    positions = _test_get_positions(response)
    # Any (and acutally the only) point of a track is fairly close to the
    # road
    ref_point = track[-1]
    for pos in positions:
        _test_points_are_close(ref_point, pos)
    last_point = positions[-1]
    assert last_point['timestamp'] == ref_point['timestamp']


@pytest.mark.parametrize('algorithm', ['mapmatcher', 'auto'])
@pytest.mark.parametrize('preprocess_settings', TRACK_PREPROCESSING_SETTINGS)
async def test_extrapolation(
        taxi_yaga_adjust, load_json, algorithm, preprocess_settings,
):
    track = load_json('track_extrapolation_test.json')['track']

    # Without extrapolation
    params = _get_request_params(algorithm)
    response = await taxi_yaga_adjust.post(
        'adjust/track',
        _create_body(
            track, preprocess_settings=preprocess_settings, extrapolate=False,
        ),
        params=params,
    )

    assert response.status_code == 200
    non_extrapolated = _test_get_positions(response)
    assert len(non_extrapolated) == len(track)
    assert non_extrapolated[-1]['is_null'] is True
    ref_elem = _find_first(
        reversed(non_extrapolated), lambda x: not x['is_null'],
    )

    # With extrapolation
    params = _get_request_params(algorithm)
    response = await taxi_yaga_adjust.post(
        'adjust/track',
        _create_body(
            track, preprocess_settings=preprocess_settings, extrapolate=True,
        ),
        params=params,
    )

    assert response.status_code == 200
    extrapolated = _test_get_positions(response)
    assert extrapolated[-1]['is_null'] is False
    assert extrapolated[-1]['is_extrapolated'] is True

    _test_points_are_close(ref_elem, extrapolated[-1], epsilon=0.00003)


@pytest.mark.parametrize('algorithm', ALGORITHMS)
async def test_unadjustable_track(taxi_yaga_adjust, algorithm, load_json):
    params = _get_request_params(algorithm)
    body = _create_body(
        load_json('unadjustable_track1.json')['track'],
        preprocess_settings=None,
        extrapolate=False,
    )

    response = await taxi_yaga_adjust.post('adjust/track', body, params=params)
    assert response.status_code == 200
    positions = _test_get_positions(response)

    for pos in positions:
        assert 'is_null' in pos
        assert pos['is_null']

    assert 'current_position' not in response.json()


def _find_interpolation_candidates(adjusted_track):
    """
    Returns list of indices of poinst that should be interpolated
    """

    left_end = None

    # Null points that has real point on the left, but may or may not
    # have real point on the right. When real point on the right
    # is found, null_candidaets is merged into result
    null_candidates = []
    # (left, index, right) of the null points that has real point on
    # the left and right side
    result = []

    for pos, val in enumerate(adjusted_track):
        if val['is_null'] is False:
            for x in null_candidates:
                result.append((left_end, x, pos))
            left_end = pos
            null_candidates = []
            continue

        # This is null point

        # If there is real point on the left, add to candidates
        if left_end is not None:
            null_candidates.append(pos)

    return result


@pytest.mark.parametrize('algorithm', ['mapmatcher', 'auto'])
async def test_interpolation(taxi_yaga_adjust, load_json, algorithm):
    track = load_json('track_interpolation_test.json')['track']

    # Without interpolation
    params = _get_request_params(algorithm)
    response = await taxi_yaga_adjust.post(
        'adjust/track',
        _create_body(track, extrapolate=False, interpolate=False),
        params=params,
    )

    assert response.status_code == 200
    non_interpolated = _test_get_positions(response)
    assert len(non_interpolated) == len(track)
    interpolated_candidates = _find_interpolation_candidates(non_interpolated)
    interpolated_candidates_pos = set(
        map(lambda x: x[1], interpolated_candidates),
    )
    assert interpolated_candidates

    # With interpolation
    params = _get_request_params(algorithm)
    response = await taxi_yaga_adjust.post(
        'adjust/track',
        _create_body(track, extrapolate=False, interpolate=True),
        params=params,
    )

    # Find all interpolated positions

    assert response.status_code == 200
    interpolated = _test_get_positions(response)

    for left, pos, right in interpolated_candidates:
        elem = interpolated[pos]
        assert elem['is_null'] is False
        assert elem['is_interpolated'] is True

        assert elem['timestamp'] > interpolated[left]['timestamp']
        assert elem['timestamp'] < interpolated[right]['timestamp']

    # Check that others are not interpolated
    for pos, _ in enumerate(interpolated):
        if pos in interpolated_candidates_pos:
            continue
        elem = interpolated[pos]
        assert elem['is_null'] is True or elem['is_interpolated'] is False


@pytest.mark.parametrize('algorithm', ['mapmatcher', 'auto'])
async def test_interpolation_no_experiment(
        taxi_yaga_adjust, load_json, algorithm,
):
    track = load_json('track_interpolation_test.json')['track']

    # Without interpolation
    params = _get_request_params(algorithm)
    response = await taxi_yaga_adjust.post(
        'adjust/track',
        _create_body(track, extrapolate=False, interpolate=False),
        params=params,
    )

    assert response.status_code == 200
    non_interpolated = _test_get_positions(response)
    assert len(non_interpolated) == len(track)
    interpolated_candidates = _find_interpolation_candidates(non_interpolated)
    # interpolated_candidates_pos = set(map(
    #     lambda x: x[1], interpolated_candidates))
    assert interpolated_candidates

    # With interpolation (enabled via experiment)
    params = _get_request_params(algorithm)
    response = await taxi_yaga_adjust.post(
        'adjust/track',
        _create_body(track, extrapolate=False, interpolate=None),
        params=params,
    )

    # Answer must be the same
    assert non_interpolated == _test_get_positions(response)


# This one tests that user can pass additional properties into request and
# we will correctly ignore it. Basically, it tests for conformance with
# JSON scheam additonalProperties: true
async def test_graph_adjust_track_additional_properties(
        taxi_yaga_adjust, load_json,
):
    algorithm = 'mapmatcher'
    params = _get_request_params(algorithm)
    params['__ZAdditional5'] = 'garbage'
    params['__ZAdditional7'] = 'garbage'

    body = _create_body(
        load_json('adjustable_track1.json')['track'],
        extrapolate=False,
        preprocess_settings=None,
    )
    response = await taxi_yaga_adjust.post('adjust/track', body, params=params)

    assert response.status_code == 200
    data = response.json()
    assert 'positions' in data
