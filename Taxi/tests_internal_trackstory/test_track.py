# pylint: disable=import-error
import datetime as dt

import flatbuffers
import internal_trackstory.GeoPoint as GeoPoint
import internal_trackstory.GpsPointFb as GpsPointFb
import internal_trackstory.GpsRouteFb as GpsRouteFb
import pytest


def make_point(builder, lon, lat, bearing, speed, timepoint):

    GpsPointFb.GpsPointFbStart(builder)
    GpsPointFb.GpsPointFbAddBearing(builder, bearing)
    point = GeoPoint.CreateGeoPoint(builder, lon, lat)
    GpsPointFb.GpsPointFbAddPoint(builder, point)
    GpsPointFb.GpsPointFbAddSpeed(builder, speed * 3.6)
    GpsPointFb.GpsPointFbAddUpdate(builder, timepoint * 1000000)

    return GpsPointFb.GpsPointFbEnd(builder)


def make_bucket(points):
    builder = flatbuffers.Builder(0)

    fbs_points = [
        make_point(
            builder,
            p['lon'],
            p['lat'],
            p['direction'],
            p['speed'],
            p['timestamp'],
        )
        for p in points
    ]

    GpsRouteFb.GpsRouteFbStartItemsVector(builder, len(points))
    for point in reversed(fbs_points):
        builder.PrependUOffsetTRelative(point)
    fbs_points = builder.EndVector(len(points))

    GpsRouteFb.GpsRouteFbStart(builder)
    GpsRouteFb.GpsRouteFbAddItems(builder, fbs_points)
    route = GpsRouteFb.GpsRouteFbEnd(builder)

    builder.Finish(route)
    return bytes(builder.Output())


def make_bucket_name(prefix, pipeline, dbid, uuid, timestamp):
    date = dt.datetime.utcfromtimestamp(timestamp)
    date_str = date.strftime('%Y%m%d')
    bucket = str(date.hour)
    return f'/mds-s3/{prefix}/{pipeline}/{dbid}/{uuid}/{date_str}/{bucket}'


def to_unix_time(timestamp):
    date = dt.datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S%z')
    return int(date.timestamp())


@pytest.fixture(name='mds_s3_storage', autouse=True)
def _mds_s3_storage():
    """
    Copy-paste from media-storage service
    """

    class FakeMdsClient:
        storage = {}

        def put_object(self, key, body):
            self.storage[key] = bytearray(body)

        def get_object(self, key) -> bytearray:
            return self.storage.get(key)

        def set_points(self, prefix, pipeline, dbid, uuid, points):
            sorted_points = {}

            for point in points:
                bucket = make_bucket_name(
                    prefix, pipeline, dbid, uuid, point['timestamp'],
                )
                if bucket not in sorted_points:
                    sorted_points[bucket] = []

                sorted_points[bucket] += [point]

            for key in sorted_points:
                self.storage[key] = bytearray(make_bucket(sorted_points[key]))

    client = FakeMdsClient()

    return client


@pytest.fixture(name='mds_s3', autouse=True)
def _mds_s3(mockserver, mds_s3_storage):
    @mockserver.handler('/mds-s3', prefix=True)
    def _mock_all(request):
        if request.method == 'PUT':
            mds_s3_storage.put_object(request.path, request.get_data())
            return mockserver.make_response('OK', 200)
        if request.method == 'GET':
            data = mds_s3_storage.get_object(request.path)
            if data:
                return mockserver.make_response(data, 200)
        return mockserver.make_response('Not found or invalid method', 404)

    return mds_s3_storage


def _format_point(point):
    res = {
        'geodata': [
            {
                'positions': [
                    {
                        # 'direction': p['direction'],
                        'speed': pytest.approx(point['speed'], 1e-6),
                        'position': [point['lon'], point['lat']],
                    },
                ],
                'time_shift': 0,
            },
        ],
        'sensors': [],
        'timestamp': point['timestamp'] * 1000,
    }
    if 'direction' in point:
        res['geodata'][0]['positions'][0]['direction'] = point['direction']
    if 'accuracy' in point:
        res['geodata'][0]['positions'][0]['accuracy'] = float(
            point['accuracy'],
        )
    return res


def _format_points(points):
    return [_format_point(p) for p in points]


async def test_single_point(taxi_internal_trackstory_adv, mds_s3):
    await taxi_internal_trackstory_adv.update_service_config(
        'pipeline_config.json',
    )

    points = [
        {
            'lon': 10,
            'lat': 20,
            'direction': 5,
            'speed': 10,
            'timestamp': to_unix_time('2022-01-01T00:00:05Z'),  # 1640995205
        },
    ]

    mds_s3.set_points('data', 'test', '$none', 'abc', points)

    request_body = {
        'from_time': '2022-01-01T00:00:00Z',
        'to_time': '2022-01-01T10:00:00Z',
        'sources': ['Verified'],
    }
    response = await taxi_internal_trackstory_adv.post(
        'test/track', json=request_body, params={'uuid': 'abc'},
    )

    assert response.status_code == 200
    data = response.json()
    assert data == [
        {'contractor': {'uuid': 'abc'}, 'Verified': _format_points(points)},
    ]


async def test_multiple_points(taxi_internal_trackstory_adv, mds_s3):
    await taxi_internal_trackstory_adv.update_service_config(
        'pipeline_config.json',
    )

    points = [
        {
            'lon': 10,
            'lat': 20,
            'direction': 5,
            'speed': 10,
            'timestamp': to_unix_time('2022-01-01T00:00:05Z'),
        },
        {
            'lon': 11,
            'lat': 22,
            'direction': 2,
            'speed': 5,
            'timestamp': to_unix_time('2022-01-01T00:01:05Z'),
        },
        {
            'lon': 13,
            'lat': 23,
            'direction': 3,
            'speed': 20,
            'timestamp': to_unix_time('2022-01-01T02:01:05Z'),
        },
    ]

    mds_s3.set_points('data', 'test', '$none', 'abc', points)

    request_body = {
        'from_time': '2022-01-01T00:00:00Z',
        'to_time': '2022-01-01T10:00:00Z',
        'sources': ['Verified'],
    }
    response = await taxi_internal_trackstory_adv.post(
        'test/track', json=request_body, params={'uuid': 'abc'},
    )

    assert response.status_code == 200
    data = response.json()
    assert data == [
        {'contractor': {'uuid': 'abc'}, 'Verified': _format_points(points)},
    ]


async def test_multiple_points_some_wrong(
        taxi_internal_trackstory_adv, mds_s3,
):
    await taxi_internal_trackstory_adv.update_service_config(
        'pipeline_config.json',
    )

    other_points = [
        {
            'lon': 10,
            'lat': 20,
            'direction': 5,
            'speed': 10,
            'timestamp': to_unix_time('2022-01-01T00:00:05Z'),
        },
    ]

    correct_points = [
        {
            'lon': 11,
            'lat': 22,
            'direction': 2,
            'speed': 5,
            'timestamp': to_unix_time('2022-01-01T00:01:05Z'),
        },
        {
            'lon': 13,
            'lat': 23,
            'direction': 3,
            'speed': 20,
            'timestamp': to_unix_time('2022-01-01T02:01:05Z'),
        },
    ]

    points = other_points + correct_points

    mds_s3.set_points('data', 'test', '$none', 'abc', points)

    request_body = {
        'from_time': '2022-01-01T00:01:00Z',
        'to_time': '2022-01-01T10:00:00Z',
        'sources': ['Verified'],
    }
    response = await taxi_internal_trackstory_adv.post(
        'test/track', json=request_body, params={'uuid': 'abc'},
    )

    assert response.status_code == 200
    data = response.json()
    assert data == [
        {
            'contractor': {'uuid': 'abc'},
            'Verified': _format_points(correct_points),
        },
    ]


@pytest.mark.now('2022-01-01T02:01:20Z')
async def test_multiple_points_some_wrong_shorttracks(
        taxi_internal_trackstory_adv, mds_s3, shorttrack_payload_sender, now,
):

    await taxi_internal_trackstory_adv.update_service_config(
        'pipeline_config.json',
    )

    other_points = [
        {
            'lon': 10,
            'lat': 20,
            'direction': 5,
            'speed': 10,
            'timestamp': to_unix_time('2022-01-01T00:00:05Z'),
        },
    ]

    shorttrack_points = [
        {
            'lon': 14,
            'lat': 24,
            'speed': 5,
            'direction': 2,
            'timestamp': to_unix_time('2022-01-01T02:01:10Z'),
        },
        {
            'lon': 14,
            'lat': 24,
            'speed': 5,
            'direction': 2,
            'timestamp': to_unix_time('2022-01-01T02:01:15Z'),
        },
    ]

    correct_points = [
        {
            'lon': 11,
            'lat': 22,
            'direction': 2,
            'speed': 5,
            'timestamp': to_unix_time('2022-01-01T00:01:05Z'),
        },
        {
            'lon': 13,
            'lat': 23,
            'direction': 3,
            'speed': 20,
            'timestamp': to_unix_time('2022-01-01T02:01:05Z'),
        },
    ]

    points = other_points + correct_points

    mds_s3.set_points('data', 'test', '$none', 'abc', points)

    await shorttrack_payload_sender.send_universal_signals_payload(
        shorttrack_points, 'Verified', '$none_abc', 'test$signals$@0',
    )

    request_body = {
        'from_time': '2022-01-01T00:01:00Z',
        'to_time': '2022-01-01T10:00:00Z',
        'sources': ['Verified'],
    }
    response = await taxi_internal_trackstory_adv.post(
        'test/track', json=request_body, params={'uuid': 'abc'},
    )

    assert response.status_code == 200
    data = response.json()
    assert data == [
        {
            'contractor': {'uuid': 'abc'},
            'Verified': _format_points(correct_points + shorttrack_points),
        },
    ]


async def test_wrong_pipeline(taxi_internal_trackstory_adv, mds_s3):
    await taxi_internal_trackstory_adv.update_service_config(
        'pipeline_config.json',
    )

    request_body = {
        'from_time': '2022-01-01T00:01:00Z',
        'to_time': '2022-01-01T10:00:00Z',
        'sources': ['Verified'],
    }
    response = await taxi_internal_trackstory_adv.post(
        'wrong_pipeline/track', json=request_body, params={'uuid': 'abc'},
    )

    assert response.status_code == 400


@pytest.mark.now('2022-01-01T02:01:20Z')
@pytest.mark.config(
    INTERNAL_TRACKSTORY_CLICKHOUSE_USAGE={
        'test': {'request_percentage': 100, 'enable_response': True},
    },
)
@pytest.mark.clickhouse(
    dbname='internal_trackstory', files=['clickhouse_data.sql'],
)
async def test_clickhouse(taxi_internal_trackstory_adv):
    await taxi_internal_trackstory_adv.update_service_config(
        'pipeline_config.json',
    )

    points = [
        {
            'lon': 20,
            'lat': 30,
            'speed': 10,
            'timestamp': to_unix_time('2022-01-01T00:00:05Z'),  # 1640995205
        },
    ]

    request_body = {
        'from_time': '2022-01-01T00:00:00Z',
        'to_time': '2022-01-01T10:00:00Z',
        'sources': ['Verified'],
    }

    response = await taxi_internal_trackstory_adv.post(
        'test/track',
        json=request_body,
        params={'uuid': 'uuid1', 'dbid': 'dbid1'},
    )

    assert response.status_code == 200
    data = response.json()
    assert data == [
        {
            'contractor': {'uuid': 'uuid1', 'dbid': 'dbid1'},
            'Verified': _format_points(points),
        },
    ]


@pytest.mark.now('2022-01-01T02:01:20Z')
@pytest.mark.config(
    INTERNAL_TRACKSTORY_CLICKHOUSE_USAGE={
        'test': {
            'request_percentage': 100,
            'enable_response': True,
            'use_http_client': True,
        },
    },
)
async def test_clickhouse_http(taxi_internal_trackstory_adv, mockserver):
    await taxi_internal_trackstory_adv.update_service_config(
        'pipeline_config.json',
    )

    @mockserver.handler('/clickhouse', prefix=True)
    def mock_clickhouse(request):
        ts0 = to_unix_time('2022-01-01T00:00:05Z') * 1000000
        ts1 = to_unix_time('2022-01-01T00:00:06Z') * 1000000
        data = (
            f'{ts0}\t20\t30\t\\N\t\\N\t10\t\\N\n'
            f'{ts1}\t21\t31\t\\N\t\\N\t11\t\\N'.encode()
        )
        return mockserver.make_response(data, 200)

    points = [
        {
            'lon': 20,
            'lat': 30,
            'speed': 10,
            'timestamp': to_unix_time('2022-01-01T00:00:05Z'),  # 1640995205
        },
        {
            'lon': 21,
            'lat': 31,
            'speed': 11,
            'timestamp': to_unix_time('2022-01-01T00:00:06Z'),  # 1640995206
        },
    ]

    request_body = {
        'from_time': '2022-01-01T00:00:00Z',
        'to_time': '2022-01-01T10:00:00Z',
        'sources': ['Verified'],
    }

    response = await taxi_internal_trackstory_adv.post(
        'test/track',
        json=request_body,
        params={'uuid': 'uuid1', 'dbid': 'dbid1'},
    )

    assert response.status_code == 200
    data = response.json()
    assert data == [
        {
            'contractor': {'uuid': 'uuid1', 'dbid': 'dbid1'},
            'Verified': _format_points(points),
        },
    ]
    assert mock_clickhouse.times_called == 1
