# pylint: disable=redefined-outer-name
# pylint: disable=too-many-lines
import datetime

from aiohttp import web
import bson
import pandas  # noqa: fixes freezegun import
import pytest

from taxi.util import dates

from taxi_accelerometer_metrics.generated.cron import run_cron

GRAPHITE_PREFIX = 'taxi_accelerometer_metrics_cron.road_accident_check.'


def make_tp(point, timestamp):
    return dict(point=point, timestamp=timestamp, bearing=300, speed=40)


@pytest.mark.config(
    ACCELEROMETER_METRICS_JOBS_SETTINGS=dict(
        __default__=dict(enabled=False),
        road_accident_check=dict(enabled=False, limit=1, sleep=0),
    ),
)
async def test_disable_job(patch, mock_driver_trackstory, mock_safety_center):
    @mock_driver_trackstory('/legacy/gps-storage/get')
    def _geotracks_handler(request):
        assert False

    @mock_safety_center('/v1/accidents')
    def _safety_center_handler(request):
        assert False

    @patch('taxi.util.graphite.send_taxi_cluster_metric')
    async def graphite_mock(metric, value, timestamp):
        pass

    # crontask
    await run_cron.main(
        [
            'taxi_accelerometer_metrics.crontasks.road_accident_check',
            '-t',
            '0',
        ],
    )

    graphite_calls = graphite_mock.calls
    assert len(graphite_calls) == 2


CONFIRMED_ACCIDENT_TRACK = [
    make_tp([39.68, 47.05], 1568203061),  # far from accident (before)
    make_tp([39.68, 47.21], 1568203120),  # close to accident (before)
    # close to accident (after, not confirmed)
    make_tp([39.68, 47.25], 1568203211),
    make_tp([39.68, 47.22], 1568203361),  # close to accident (after)
]


@pytest.mark.now('2019-09-11T13:00:00+0000')
# accident timestamp is 1568203161
@pytest.mark.config(
    ACCELEROMETER_METRICS_JOBS_SETTINGS=dict(
        __default__=dict(enabled=False),
        road_accident_check=dict(enabled=True, limit=1, sleep=0),
    ),
    ROAD_ACCIDENT_CHECK_SAFETY_CENTER_ENABLED=True,
    ROAD_ACCIDENT_CHECK_TIME_BEFORE=250,  # 1568202911
    ROAD_ACCIDENT_CHECK_TIME_AFTER=250,  # 1568203411
    ROAD_ACCIDENT_CHECK_CONFIRM_GEOTRACKS_POINTS_AFTER_TIME=150,  # 1568203311
    ROAD_ACCIDENT_CHECK_MAX_DISTANCE_BEFORE=3000,
    ROAD_ACCIDENT_CHECK_MAX_DISTANCE_AFTER=3000,
)
@pytest.mark.parametrize(
    'status, track',
    [
        ('confirmed', CONFIRMED_ACCIDENT_TRACK),
        # no confirmed point after accident
        (
            'unconfirmed',
            [
                make_tp(
                    [39.68, 47.05], 1568203061,
                ),  # far from accident (before)
                make_tp(
                    [39.68, 47.17], 1568203120,
                ),  # close to accident (before)
                # close to accident (after, not confirmed)
                make_tp([39.68, 47.25], 1568203211),
            ],
        ),
        # far point after accident
        (
            'unconfirmed',
            [
                make_tp(
                    [39.68, 47.05], 1568203061,
                ),  # far from accident (before)
                make_tp(
                    [39.68, 47.17], 1568203120,
                ),  # close to accident (before)
                # close to accident (after, not confirmed)
                make_tp([39.68, 47.25], 1568203211),
                # far from accident
                make_tp([39.68, 47.45], 1568203361),
            ],
        ),
        # far point after accident (not confirmed)
        (
            'unconfirmed',
            [
                make_tp(
                    [39.68, 47.05], 1568203061,
                ),  # far from accident (before)
                make_tp(
                    [39.68, 47.17], 1568203120,
                ),  # close to accident (before)
                # close to accident (after, not confirmed)
                make_tp([39.68, 47.25], 1568203211),
                # far from accident (after, not confirmed)
                make_tp([39.68, 47.45], 1568203300),
                make_tp(
                    [39.68, 47.22], 1568203361,
                ),  # close to accident (after)
            ],
        ),
        # no far points before accident
        (
            'unconfirmed',
            [
                make_tp(
                    [39.68, 47.21], 1568203120,
                ),  # close to accident (before)
                # close to accident (after, not confirmed)
                make_tp([39.68, 47.25], 1568203211),
                make_tp(
                    [39.68, 47.22], 1568203361,
                ),  # close to accident (after)
            ],
        ),
        # no points before accident
        (
            'unconfirmed',
            [
                # close to accident (after, not confirmed)
                make_tp([39.68, 47.25], 1568203211),
                make_tp(
                    [39.68, 47.22], 1568203361,
                ),  # close to accident (after)
            ],
        ),
        # no points after accident
        (
            'unconfirmed',
            [
                make_tp(
                    [39.68, 47.05], 1568203061,
                ),  # far from accident (before)
                make_tp(
                    [39.68, 47.21], 1568203120,
                ),  # close to accident (before)
            ],
        ),
    ],
)
async def test_road_accident_check(
        db, patch, mock_driver_trackstory, mock_safety_center, status, track,
):
    @mock_driver_trackstory('/legacy/gps-storage/get')
    def _geotracks_handler(request):
        return web.json_response(
            data=dict(
                tracks=[
                    dict(
                        db_id=x['db_id'],
                        driver_id=x['driver_id'],
                        req_id=x['req_id'],
                        track=track,
                    )
                    for x in request.json['params']
                ],
            ),
        )

    @mock_safety_center('/v1/accidents')
    def _safety_center_handler(request):
        assert status == 'confirmed'
        return web.json_response(data=dict(accident_id='sc_id'))

    @patch('taxi.util.graphite.send_taxi_cluster_metric')
    async def graphite_mock(metric, value, timestamp):
        pass

    now = datetime.datetime.utcnow().replace(second=0, microsecond=0)
    ts_to = dates.timestamp_us(now)

    # crontask
    await run_cron.main(
        [
            'taxi_accelerometer_metrics.crontasks.road_accident_check',
            '-t',
            '0',
        ],
    )

    graphite_calls = graphite_mock.calls
    assert len(graphite_calls) == 6

    if status == 'confirmed':
        assert _safety_center_handler.times_called == 1
    else:
        assert _safety_center_handler.times_called == 0

    graphite_requests = [
        dict(metric=GRAPHITE_PREFIX + 'job.total', value=1, timestamp=ts_to),
        dict(metric=GRAPHITE_PREFIX + 'total', value=1, timestamp=ts_to),
        dict(
            metric=GRAPHITE_PREFIX + f'job.{status}', value=1, timestamp=ts_to,
        ),
        dict(metric=GRAPHITE_PREFIX + status, value=1, timestamp=ts_to),
    ]

    graphite_requests = sorted(graphite_requests, key=lambda k: k['metric'])
    graphite_calls = sorted(graphite_calls, key=lambda k: k['metric'])

    assert graphite_calls[2:] == graphite_requests

    road_accidents = await db.road_accidents.find(
        {},
        {
            '_id': 0,
            'status': 1,
            'safety_center_id': 1,
            'geotracks_check.status': 1,
        },
    ).to_list(length=None)

    db_check = dict(status=status, geotracks_check=dict(status='Checked'))
    if status == 'confirmed':
        db_check['safety_center_id'] = 'sc_id'

    assert road_accidents == [db_check]


@pytest.mark.now('2019-09-11T13:00:00+0000')
# accident timestamp is 1568203161
@pytest.mark.config(
    ACCELEROMETER_METRICS_JOBS_SETTINGS=dict(
        __default__=dict(enabled=False),
        road_accident_check=dict(enabled=True, limit=1, sleep=0),
    ),
    ROAD_ACCIDENT_CHECK_SAFETY_CENTER_ENABLED=True,
    ROAD_ACCIDENT_CHECK_TIME_BEFORE=250,  # 1568202911
    ROAD_ACCIDENT_CHECK_TIME_AFTER=250,  # 1568203411
    ROAD_ACCIDENT_CHECK_CONFIRM_GEOTRACKS_POINTS_AFTER_TIME=150,  # 1568203311
    ROAD_ACCIDENT_CHECK_MAX_DISTANCE_BEFORE=3000,
    ROAD_ACCIDENT_CHECK_MAX_DISTANCE_AFTER=3000,
)
@pytest.mark.parametrize('track', [CONFIRMED_ACCIDENT_TRACK])
async def test_no_order_for_alias_id(
        db, patch, mock_driver_trackstory, mock_safety_center, track,
):
    @mock_driver_trackstory('/legacy/gps-storage/get')
    def _geotracks_handler(request):
        return web.json_response(
            data=dict(
                tracks=[
                    dict(
                        db_id=x['db_id'],
                        driver_id=x['driver_id'],
                        req_id=x['req_id'],
                        track=track,
                    )
                    for x in request.json['params']
                ],
            ),
        )

    @mock_safety_center('/v1/accidents')
    def _safety_center_handler(request):
        return web.json_response(
            status=404, data=dict(code='no_order_for_alias_id'),
        )

    @patch('taxi.util.graphite.send_taxi_cluster_metric')
    async def graphite_mock(metric, value, timestamp):
        pass

    now = datetime.datetime.utcnow().replace(second=0, microsecond=0)
    ts_to = dates.timestamp_us(now)

    # crontask
    await run_cron.main(
        [
            'taxi_accelerometer_metrics.crontasks.road_accident_check',
            '-t',
            '0',
        ],
    )

    graphite_calls = graphite_mock.calls
    assert len(graphite_calls) == 6

    assert _safety_center_handler.times_called == 1

    graphite_requests = [
        dict(metric=GRAPHITE_PREFIX + 'job.total', value=1, timestamp=ts_to),
        dict(metric=GRAPHITE_PREFIX + 'total', value=1, timestamp=ts_to),
        dict(
            metric=GRAPHITE_PREFIX + f'job.missing', value=1, timestamp=ts_to,
        ),
        dict(metric=GRAPHITE_PREFIX + 'missing', value=1, timestamp=ts_to),
    ]

    graphite_requests = sorted(graphite_requests, key=lambda k: k['metric'])
    graphite_calls = sorted(graphite_calls, key=lambda k: k['metric'])

    assert graphite_calls[2:] == graphite_requests

    road_accidents = await db.road_accidents.find(
        {},
        {
            '_id': 0,
            'status': 1,
            'safety_center_id': 1,
            'geotracks_check.status': 1,
        },
    ).to_list(length=None)

    db_check = dict(status='confirmed', geotracks_check=dict(status='Checked'))

    assert road_accidents == [db_check]


@pytest.mark.now('2019-09-11T13:00:00+0000')
# accident timestamp is 1568203161
@pytest.mark.config(
    ACCELEROMETER_METRICS_JOBS_SETTINGS=dict(
        __default__=dict(enabled=False),
        road_accident_check=dict(enabled=True, limit=1, sleep=0),
    ),
    ROAD_ACCIDENT_CHECK_SAFETY_CENTER_ENABLED=False,
    ROAD_ACCIDENT_CHECK_TIME_BEFORE=250,  # 1568202911
    ROAD_ACCIDENT_CHECK_TIME_AFTER=250,  # 1568203411
    ROAD_ACCIDENT_CHECK_CONFIRM_GEOTRACKS_POINTS_AFTER_TIME=150,  # 1568203311
    ROAD_ACCIDENT_CHECK_MAX_DISTANCE_BEFORE=3000,
    ROAD_ACCIDENT_CHECK_MAX_DISTANCE_AFTER=3000,
)
async def test_disabled_safety_center(
        db, mock_driver_trackstory, mock_safety_center,
):
    @mock_driver_trackstory('/legacy/gps-storage/get')
    def _geotracks_handler(request):
        track = CONFIRMED_ACCIDENT_TRACK
        return web.json_response(
            data=dict(
                tracks=[
                    dict(
                        db_id=x['db_id'],
                        driver_id=x['driver_id'],
                        req_id=x['req_id'],
                        track=track,
                    )
                    for x in request.json['params']
                ],
            ),
        )

    @mock_safety_center('/v1/accidents')
    def _safety_center_handler(request):
        return web.json_response(data={})

    # crontask
    await run_cron.main(
        [
            'taxi_accelerometer_metrics.crontasks.road_accident_check',
            '-t',
            '0',
        ],
    )

    assert _safety_center_handler.times_called == 0
    road_accidents = await db.road_accidents.find(
        {},
        {
            '_id': 0,
            'status': 1,
            'safety_center_id': 1,
            'geotracks_check.status': 1,
        },
    ).to_list(length=None)

    db_check = dict(status='confirmed', geotracks_check=dict(status='Checked'))
    assert road_accidents == [db_check]


@pytest.mark.now('2019-09-11T13:00:00+0000')
@pytest.mark.config(
    ACCELEROMETER_METRICS_JOBS_SETTINGS=dict(
        __default__=dict(enabled=False),
        road_accident_check=dict(enabled=True, limit=1, sleep=0),
    ),
)
async def test_road_accident_check_no_tracks(
        db, patch, mock_driver_trackstory, mock_safety_center,
):
    @mock_driver_trackstory('/legacy/gps-storage/get')
    def _geotracks_handler(request):
        return web.json_response(
            data=dict(
                tracks=[
                    dict(
                        db_id=x['db_id'],
                        driver_id=x['driver_id'],
                        req_id=x['req_id'],
                        track=[],
                    )
                    for x in request.json['params']
                ],
            ),
        )

    @mock_safety_center('/v1/accidents')
    def _safety_center_handler(request):
        assert False

    # crontask
    await run_cron.main(
        [
            'taxi_accelerometer_metrics.crontasks.road_accident_check',
            '-t',
            '0',
        ],
    )

    road_accidents = await db.road_accidents.find(
        {}, {'_id': 0, 'status': 1, 'geotracks_check.status': 1},
    ).to_list(length=None)

    db_check = dict(
        status='unconfirmed', geotracks_check=dict(status='NoTrackError'),
    )

    assert road_accidents == [db_check]


@pytest.mark.filldb(road_accidents='throttler')
@pytest.mark.now('2019-09-11T13:00:00+0000')
@pytest.mark.config(
    ACCELEROMETER_METRICS_JOBS_SETTINGS=dict(
        __default__=dict(enabled=False),
        road_accident_check=dict(enabled=True, limit=3, sleep=0),
    ),
    ROAD_ACCIDENT_CHECK_NO_ORDERS=True,
)
async def test_road_accident_check_throttler(
        db, freeze, patch, mock_driver_trackstory, mock_safety_center,
):
    @mock_driver_trackstory('/legacy/gps-storage/get')
    def _geotracks_handler(request):
        return web.json_response(
            data=dict(
                tracks=[
                    dict(
                        db_id=x['db_id'],
                        driver_id=x['driver_id'],
                        req_id=x['req_id'],
                        track=[],
                    )
                    for x in request.json['params']
                ],
            ),
        )

    @mock_safety_center('/v1/accidents')
    def _safety_center_handler(request):
        assert False

    @patch('taxi.util.graphite.send_taxi_cluster_metric')
    async def graphite_mock(metric, value, timestamp):
        pass

    @patch(
        'taxi_accelerometer_metrics.helpers.db.'
        'RoadAccidents.set_accidents_resolution',
    )
    async def set_accidents_resolution(accidents):
        freeze.tick(delta=datetime.timedelta(minutes=1))
        for accident in accidents:
            await db.road_accidents.update(
                dict(_id=accident.accident_id),
                {'$set': dict(status=accident.status)},
            )

    start = datetime.datetime.utcnow().replace(second=0, microsecond=0)
    start_ts = dates.timestamp_us(start)
    # crontask
    await run_cron.main(
        [
            'taxi_accelerometer_metrics.crontasks.road_accident_check',
            '-t',
            '0',
        ],
    )

    assert len(set_accidents_resolution.calls) == 2

    graphite_calls = graphite_mock.calls
    assert len(graphite_calls) == 8

    ts_plus_one = dates.timestamp_us(start + datetime.timedelta(minutes=1))
    ts_plus_two = dates.timestamp_us(start + datetime.timedelta(minutes=2))

    graphite_requests = [
        dict(
            metric=GRAPHITE_PREFIX + 'job.total',
            value=5,
            timestamp=ts_plus_two,
        ),
        dict(
            metric=GRAPHITE_PREFIX + 'job.unconfirmed',
            value=5,
            timestamp=ts_plus_two,
        ),
        dict(metric=GRAPHITE_PREFIX + 'total', value=3, timestamp=start_ts),
        dict(
            metric=GRAPHITE_PREFIX + 'unconfirmed',
            value=3,
            timestamp=start_ts,
        ),
        dict(metric=GRAPHITE_PREFIX + 'total', value=2, timestamp=ts_plus_one),
        dict(
            metric=GRAPHITE_PREFIX + 'unconfirmed',
            value=2,
            timestamp=ts_plus_one,
        ),
    ]

    graphite_requests = sorted(
        graphite_requests, key=lambda k: (k['metric'], k['timestamp']),
    )
    graphite_calls = sorted(
        graphite_calls, key=lambda k: (k['metric'], k['timestamp']),
    )

    assert graphite_calls[2:] == graphite_requests


@pytest.mark.now('2019-09-11T13:00:00+0000')
@pytest.mark.config(
    ACCELEROMETER_METRICS_JOBS_SETTINGS=dict(
        __default__=dict(enabled=False),
        road_accident_check=dict(enabled=True, limit=1, sleep=0),
    ),
    ROAD_ACCIDENT_CHECK_SAFETY_CENTER_ENABLED=True,
    ROAD_ACCIDENT_CHECK_CATBOOST_MODEL_ENABLED=True,
)
@pytest.mark.parametrize(
    'confidence',
    [
        pytest.param(64, marks=pytest.mark.filldb(road_accidents='positive')),
        pytest.param(0, marks=pytest.mark.filldb(road_accidents='negative')),
    ],
)
async def test_road_accident_check_catboost_model(
        db,
        patch,
        load_binary,
        mock_safety_center,
        mock_driver_trackstory,
        confidence,
):
    @patch('taxi_accelerometer_metrics.helpers.sandbox.download')
    async def _load_model(*args, **kwargs):
        return load_binary('model.cbm')

    @mock_driver_trackstory('/legacy/gps-storage/get')
    def _geotracks_handler(request):
        assert False

    @mock_safety_center('/v1/accidents')
    def _safety_center_handler(request):
        return web.json_response(data=dict(accident_id='sc_id'))

    await run_cron.main(
        [
            'taxi_accelerometer_metrics.crontasks.road_accident_check',
            '-t',
            '0',
        ],
    )

    if confidence:
        assert _safety_center_handler.times_called == 1
        call = await _safety_center_handler.wait_call()
        assert call['request'].json['confidence'] == confidence
    else:
        assert _safety_center_handler.times_called == 0


@pytest.mark.now('2019-09-11T13:00:00+0000')
@pytest.mark.config(
    ACCELEROMETER_METRICS_JOBS_SETTINGS=dict(
        __default__=dict(enabled=False),
        road_accident_check=dict(enabled=True, limit=1, sleep=0),
    ),
    ROAD_ACCIDENT_CHECK_SAFETY_CENTER_ENABLED=True,
    ROAD_ACCIDENT_CHECK_STATUS_FILTERING_ENABLED=True,
    ROAD_ACCIDENT_CHECK_STATUSES_TO_SEND=['transporting'],
    ROAD_ACCIDENT_CHECK_TIME_BEFORE=250,  # 1568202911
    ROAD_ACCIDENT_CHECK_TIME_AFTER=250,  # 1568203411
    ROAD_ACCIDENT_CHECK_CONFIRM_GEOTRACKS_POINTS_AFTER_TIME=150,  # 1568203311
    ROAD_ACCIDENT_CHECK_MAX_DISTANCE_BEFORE=3000,
    ROAD_ACCIDENT_CHECK_MAX_DISTANCE_AFTER=3000,
)
@pytest.mark.parametrize(
    'order_status, should_call', [('transporting', True), ('driving', False)],
)
async def test_road_accident_check_filter_by_order_status(
        db,
        mock_safety_center,
        mock_driver_trackstory,
        mockserver,
        order_status,
        should_call,
):
    @mock_driver_trackstory('/legacy/gps-storage/get')
    def _geotracks_handler(request):
        return web.json_response(
            data=dict(
                tracks=[
                    dict(
                        db_id=x['db_id'],
                        driver_id=x['driver_id'],
                        req_id=x['req_id'],
                        track=CONFIRMED_ACCIDENT_TRACK,
                    )
                    for x in request.json['params']
                ],
            ),
        )

    @mock_safety_center('/v1/accidents')
    def _safety_center_handler(request):
        return web.json_response(data=dict(accident_id='sc_id'))

    @mockserver.handler(
        '/order-core/internal/processing/v1/order-proc/get-fields',
    )
    def _get_fields(req):
        return mockserver.make_response(
            status=200,
            content_type='application/bson',
            response=bson.BSON.encode(
                {
                    'document': {
                        'order_info': {
                            'statistics': {
                                'status_updates': [
                                    {
                                        'c': datetime.datetime(2018, 1, 1),
                                        't': order_status,
                                    },
                                ],
                            },
                        },
                    },
                    'revision': {},
                },
            ),
        )

    await run_cron.main(
        [
            'taxi_accelerometer_metrics.crontasks.road_accident_check',
            '-t',
            '0',
        ],
    )

    assert _safety_center_handler.has_calls == should_call

    road_accident = await db.road_accidents.find_one({}, {'order_status': 1})
    assert road_accident.get('order_status') == order_status


@pytest.mark.now('2019-09-11T13:00:00+0000')
@pytest.mark.config(
    ACCELEROMETER_METRICS_JOBS_SETTINGS=dict(
        __default__=dict(enabled=False),
        road_accident_check=dict(enabled=True, limit=1, sleep=0),
    ),
    ROAD_ACCIDENT_CHECK_SAFETY_CENTER_ENABLED=True,
    ROAD_ACCIDENT_CHECK_STATUS_FILTERING_ENABLED=True,
    ROAD_ACCIDENT_CHECK_STATUSES_TO_SEND=['transporting'],
    ROAD_ACCIDENT_CHECK_TIME_BEFORE=250,  # 1568202911
    ROAD_ACCIDENT_CHECK_TIME_AFTER=250,  # 1568203411
    ROAD_ACCIDENT_CHECK_CONFIRM_GEOTRACKS_POINTS_AFTER_TIME=150,  # 1568203311
    ROAD_ACCIDENT_CHECK_MAX_DISTANCE_BEFORE=3000,
    ROAD_ACCIDENT_CHECK_MAX_DISTANCE_AFTER=3000,
)
async def test_road_accident_check_filter_by_order_status_order_not_found(
        db, mock_safety_center, mock_driver_trackstory, mockserver,
):
    @mock_driver_trackstory('/legacy/gps-storage/get')
    def _geotracks_handler(request):
        return web.json_response(
            data=dict(
                tracks=[
                    dict(
                        db_id=x['db_id'],
                        driver_id=x['driver_id'],
                        req_id=x['req_id'],
                        track=CONFIRMED_ACCIDENT_TRACK,
                    )
                    for x in request.json['params']
                ],
            ),
        )

    @mock_safety_center('/v1/accidents')
    def _safety_center_handler(request):
        return web.json_response(data=dict(accident_id='sc_id'))

    @mockserver.handler(
        '/order-core/internal/processing/v1/order-proc/get-fields',
    )
    def _get_fields(req):
        return mockserver.make_response(
            status=404,
            json=dict(code='no_such_order', message='no such order'),
        )

    await run_cron.main(
        [
            'taxi_accelerometer_metrics.crontasks.road_accident_check',
            '-t',
            '0',
        ],
    )

    assert not _safety_center_handler.has_calls

    road_accident = await db.road_accidents.find_one({}, {'order_status': 1})
    assert road_accident.get('order_status') is None
