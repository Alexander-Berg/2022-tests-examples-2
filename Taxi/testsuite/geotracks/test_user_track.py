import pytest


@pytest.mark.now('2018-10-01T12:00:00+0000')
def test_read(taxi_geotracks, redis_store, mockserver):
    @mockserver.handler('/s3mds/')
    def mock_user_list(request):
        return mockserver.make_response('', 200)

    user_id = 'spider-man'
    # 'lon': 12.0, 'lat': 13.0, 'accuracy': 14, time: 10:00:10
    redis_store.hset(
        'history:20181001:10:' + user_id,
        '1538388010',
        b'\x10\x00\x00\x00\x0c\x00\x18\x00\x08\x00\x0c\x00'
        b'\x10\x00\x06\x00\x0c\x00\x00\x00\x00\x00\x0e\x00'
        b'\x00\x1b\xb7\x00@]\xc6\x00*\xf0\xb1[\x00\x00\x00\x00',
    )
    # 'lon': 12.51, 'lat': 14.0, 'accuracy': 13, time: 10:00:20
    redis_store.hset(
        'history:20181001:10:' + user_id,
        '1538388020',
        b'\x10\x00\x00\x00\x0c\x00\x18\x00\x08\x00\x0c\x00'
        b'\x10\x00\x06\x00\x0c\x00\x00\x00\x00\x00\r\x000'
        b'\xe3\xbe\x00\x80\x9f\xd5\x004\xf0\xb1[\x00\x00\x00\x00',
    )
    response = taxi_geotracks.get(
        'user/track?'
        'user_id=' + user_id + '&'
        'from=2018-10-01T10:00:00Z&'
        'to=2018-10-01T10:00:10Z',
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data['track']) == 1
    assert data['user_id'] == user_id
    item = data['track'][0]

    eps = 1e-5

    assert item['lon'] - 12 < eps
    assert item['lat'] - 13 < eps
    assert item['accuracy'] == 14
    assert item['timestamp'] == 1538388010


@pytest.mark.now('2018-10-01T12:00:00+0000')
def test_read_buckets(taxi_geotracks, redis_store, mockserver):
    @mockserver.handler('/s3mds/')
    def mock_user_list(request):
        return mockserver.make_response('', 200)

    user_id = 'spider-man'
    # 'lon': 13.21, 'lat': 15.0, 'accuracy': 12, time: 7:31:00
    redis_store.hset(
        'history:20181001:07:' + user_id,
        '1538379060',
        b'\x10\x00\x00\x00\x0c\x00\x18\x00\x08\x00\x0c'
        b'\x00\x10\x00\x06\x00\x0c\x00\x00\x00\x00\x00'
        b'\x0c\x00\x90\x91\xc9\x00\xc0\xe1\xe4\x004\xcd'
        b'\xb1[\x00\x00\x00\x00',
    )
    # 'lon': 11.35, 'lat': 12.0, 'accuracy': 16, time: 9:14:00
    redis_store.hset(
        'history:20181001:09:' + user_id,
        '1538385240',
        b'\x10\x00\x00\x00\x0c\x00\x18\x00\x08\x00\x0c'
        b'\x00\x10\x00\x06\x00\x0c\x00\x00\x00\x00\x00'
        b'\x10\x00\xf0/\xad\x00\x00\x1b\xb7\x00X\xe5'
        b'\xb1[\x00\x00\x00\x00',
    )
    # 'lon': 12.0, 'lat': 13.0, 'accuracy': 14, time: 10:00:10
    redis_store.hset(
        'history:20181001:10:' + user_id,
        '1538388010',
        b'\x10\x00\x00\x00\x0c\x00\x18\x00\x08\x00\x0c\x00'
        b'\x10\x00\x06\x00\x0c\x00\x00\x00\x00\x00\x0e\x00'
        b'\x00\x1b\xb7\x00@]\xc6\x00*\xf0\xb1[\x00\x00\x00\x00',
    )
    # 'lon': 12.51, 'lat': 14.0, 'accuracy': 13, time: 10:00:20
    redis_store.hset(
        'history:20181001:10:' + user_id,
        '1538388020',
        b'\x10\x00\x00\x00\x0c\x00\x18\x00\x08\x00\x0c\x00'
        b'\x10\x00\x06\x00\x0c\x00\x00\x00\x00\x00\r\x000'
        b'\xe3\xbe\x00\x80\x9f\xd5\x004\xf0\xb1[\x00\x00\x00\x00',
    )
    response = taxi_geotracks.get(
        'user/track?'
        'user_id=' + user_id + '&'
        'from=2018-10-01T10:00:00Z&to=2018-10-01T11:00:00Z',
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data['track']) == 2
    response = taxi_geotracks.get(
        'user/track?' 'user_id=' + user_id + '&' 'last=18000',
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data['track']) == 3
    response = taxi_geotracks.get(
        'user/track?'
        'user_id=' + user_id + '&'
        'from=2018-10-01T09:00:00Z&to=2018-10-01T10:01:00Z',
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data['track']) == 3


@pytest.mark.now('2018-10-01T12:00:00+0000')
@pytest.mark.parametrize(
    'from_t, to_t, cnt',
    [
        ('1538388000', '1538388010', 1),
        ('1538388000', '1538388014', 2),
        ('1538388000', '1538388016', 3),
        ('1538388010', '1538388016', 3),
        ('1538388014', '1538388016', 3),
    ],
)
def test_read_from_one_bucket(
        taxi_geotracks, redis_store, from_t, to_t, cnt, mockserver,
):
    @mockserver.handler('/s3mds/')
    def mock_user_list(request):
        return mockserver.make_response('', 200)

    user_id = 'spider-man'
    # 'lon': 12.0, 'lat': 13.0, 'accuracy': 14, time: 10:00:10
    redis_store.hset(
        'history:20181001:10:' + user_id,
        '1538388010',
        b'\x10\x00\x00\x00\x0c\x00\x18\x00\x08\x00\x0c\x00'
        b'\x10\x00\x06\x00\x0c\x00\x00\x00\x00\x00\x0e\x00'
        b'\x00\x1b\xb7\x00@]\xc6\x00*\xf0\xb1[\x00\x00\x00\x00',
    )
    # 'lon': 13, 'lat': 15.0, 'accuracy': 10, time: 10:00:15
    redis_store.hset(
        'history:20181001:10:' + user_id,
        '1538388015',
        b'\x10\x00\x00\x00\x0c\x00\x18\x00\x08\x00\x0c\x00'
        b'\x10\x00\x06\x00\x0c\x00\x00\x00\x00\x00\n\x00@]'
        b'\xc6\x00\xc0\xe1\xe4\x00/\xf0\xb1[\x00\x00\x00\x00',
    )
    # 'lon': 12.51, 'lat': 14.0, 'accuracy': 13, time: 10:00:20
    redis_store.hset(
        'history:20181001:10:' + user_id,
        '1538388020',
        b'\x10\x00\x00\x00\x0c\x00\x18\x00\x08\x00\x0c\x00'
        b'\x10\x00\x06\x00\x0c\x00\x00\x00\x00\x00\r\x000'
        b'\xe3\xbe\x00\x80\x9f\xd5\x004\xf0\xb1[\x00\x00\x00\x00',
    )
    response = taxi_geotracks.get(
        'user/track?'
        'user_id=' + user_id + '&'
        'from=' + from_t + '&to=' + to_t,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data['track']) == cnt


@pytest.mark.now('2018-10-01T12:00:00+0000')
def test_read_mds_redis(taxi_geotracks, redis_store, mockserver):
    @mockserver.handler('/s3mds/')
    def mock_user_list(request):
        return mockserver.make_response(
            '<ListBucketResult >'
            '<Name>testsuite</Name>'
            '<Prefix>history/spider-man/20181001</Prefix>'
            '<Contents>'
            '<Key>history/spider-man/20181001/07</Key>'
            '<Size>2184</Size></Contents>'
            '<Contents>'
            '<Key>history/spider-man/20181001/08</Key>'
            '<Size>2184</Size></Contents></ListBucketResult>',
            200,
        )

    @mockserver.handler('/s3mds/history/spider-man/20181001/08')
    def mock_answer(request):
        return mockserver.make_response(
            # lon,  lat,             time,                      accuracy
            # 42,   0.4283726124352, 2018-10-01T08:00:01+00:00, 5
            # 33.5, 20.2,            2018-10-01T08:16:40+00:00, 4
            # 30,   21.5,            2018-10-01T08:33:20+00:00, 3
            b'\x1f\x8b\x08\x00\x00\x00\x00\x00\x02'
            b'\xff\x13\x60\x80\x01\x36\x06\x0e\x06'
            b'\x16\x20\xc9\x00\x24\x19\x18\x98\x81'
            b'\x38\x06\x88\x0d\xa0\xfc\x27\xff\xff'
            b'\xff\x07\x89\x36\x1c\x3e\xc9\x98\x20'
            b'\xe0\xc1\x78\xe1\xf6\xc6\x68\x98\x4e'
            b'\x1e\x06\x19\xa0\x5e\x1e\x06\x01\xa0'
            b'\x6e\x1e\xb0\x08\x0b\x43\x82\xf6\x7f'
            b'\x46\x07\x2b\x13\xc6\x17\xd7\x91\xd5'
            b'\x49\xa0\xa9\x63\x65\x68\xb8\xd7\xc0'
            b'\x14\xd2\xc9\xc6\xc0\x78\x05\xa2\x0e'
            b'\x00\xa1\x88\xc1\x52\x90\x00\x00\x00',
            200,
        )

    @mockserver.handler('/s3mds/history/spider-man/20181001/07')
    def mock_answer2(request):
        return mockserver.make_response(
            # lon, lat, time,                      accuracy
            # 42,  0.1, 2018-10-01T07:00:01+00:00, 2
            # 32,  21,  2018-10-01T07:16:40+00:00, 1
            # 35,  28,  2018-10-01T07:33:20+00:00, 0
            b'\x1f\x8b\x08\x00\x00\x00\x00\x00\x02\xff\x13\x60\x80\x01\x36\x06'
            b'\x0e\x06\x16\x20\xc9\x00\x24\x19\x18\x98\x81\x38\x05\x88\x2d\x80'
            b'\x58\x00\x88\x79\x18\x24\x80\xe2\x1c\x40\x9a\x01\x8c\x0f\xf0\x89'
            b'\x31\x31\xd8\xaf\x66\x3c\x70\x76\x63\x34\xcc\x04\x1e\x06\x19\xb0'
            b'\x0a\x01\xa0\x29\x3c\x60\x11\x46\x06\x06\x8f\x17\x8c\x0e\xf9\x0e'
            b'\x8c\x37\x4e\x22\xab\x93\x40\x53\xc7\xc4\xd0\x70\xaf\x81\x69\x41'
            b'\x1b\x23\xc3\xc7\xa3\x10\x75\x00\xee\x03\x71\x87\x98\x00'
            b'\x00\x00',
            200,
        )

    # user_id = 'spider-man'
    # 'lon': 11.35, 'lat': 12.0, 'accuracy': 16, time: 9:14:00
    redis_store.hset(
        'history:20181001:09:spider-man',
        '1538385240',
        b'\x10\x00\x00\x00\x0c\x00\x18\x00\x08\x00\x0c'
        b'\x00\x10\x00\x06\x00\x0c\x00\x00\x00\x00\x00'
        b'\x10\x00\xf0/\xad\x00\x00\x1b\xb7\x00X\xe5'
        b'\xb1[\x00\x00\x00\x00',
    )
    # 'lon': 12.0, 'lat': 13.0, 'accuracy': 14, time: 10:00:10
    redis_store.hset(
        'history:20181001:10:spider-man',
        '1538388010',
        b'\x10\x00\x00\x00\x0c\x00\x18\x00\x08\x00\x0c\x00'
        b'\x10\x00\x06\x00\x0c\x00\x00\x00\x00\x00\x0e\x00'
        b'\x00\x1b\xb7\x00@]\xc6\x00*\xf0\xb1[\x00\x00\x00\x00',
    )
    # 'lon': 12.51, 'lat': 14.0, 'accuracy': 13, time: 10:00:20
    redis_store.hset(
        'history:20181001:10:spider-man',
        '1538388020',
        b'\x10\x00\x00\x00\x0c\x00\x18\x00\x08\x00\x0c\x00'
        b'\x10\x00\x06\x00\x0c\x00\x00\x00\x00\x00\r\x000'
        b'\xe3\xbe\x00\x80\x9f\xd5\x004\xf0\xb1[\x00\x00\x00\x00',
    )
    response = taxi_geotracks.get(
        'user/track?'
        'user_id=spider-man&'
        'from=2018-10-01T07:00:00Z&'
        'to=2018-10-01T10:01:00Z',
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data['track']) == 9
    response = taxi_geotracks.get(
        'user/track?'
        'user_id=spider-man&'
        'from=2018-10-01T08:18:00Z&'
        'to=2018-10-01T10:01:00Z',
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data['track']) == 5
