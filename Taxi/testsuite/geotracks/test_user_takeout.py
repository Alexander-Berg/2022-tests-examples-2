import pytest


@pytest.mark.now('2019-04-06T12:00:00+0000')
def test_takeout(
        taxi_geotracks, redis_store, mockserver, load_binary, load_json,
):
    @mockserver.handler('/s3mds/')
    def mock_user_list(request):
        if '/spider-man/' in request.environ['QUERY_STRING']:
            return mockserver.make_response(
                '<ListBucketResult >'
                '<Name>testsuite</Name>'
                '<Prefix>history/spider-man</Prefix>'
                '<Contents>'
                '<Key>history/spider-man/20181001/07</Key>'
                '<Size>2184</Size></Contents>'
                '<Contents>'
                '<Key>history/spider-man/20181001/08</Key>'
                '<Size>2184</Size></Contents></ListBucketResult>',
                200,
            )
        else:
            return mockserver.make_response(
                '<ListBucketResult >'
                '<Name>testsuite</Name>'
                '</ListBucketResult>',
                200,
            )

    @mockserver.handler('/s3mds/history/spider-man/20181001/08')
    def mock_answer(request):
        return mockserver.make_response(
            # lon,  lat,             time,                      accuracy
            # 42,   0.4283726124352, 2018-10-01T08:00:01+00:00, 5
            # 33.5, 20.2,            2018-10-01T08:16:40+00:00, 4
            # 30,   21.5,            2018-10-01T08:33:20+00:00, 3
            load_binary('2018100107'),
            200,
        )

    @mockserver.handler('/s3mds/history/spider-man/20181001/07')
    def mock_answer2(request):
        return mockserver.make_response(
            # lon, lat, time,                      accuracy
            # 42,  0.1, 2018-10-01T07:00:01+00:00, 2
            # 32,  21,  2018-10-01T07:16:40+00:00, 1
            # 35,  28,  2018-10-01T07:33:20+00:00, 0
            load_binary('2018100107'),
            200,
        )

    # 'lon': 11.35, 'lat': 12.0, 'accuracy': 16, time: 9:14:00
    redis_store.hset(
        'history:20190406:09:spider-man',
        '1554542040',
        load_binary('2019040609'),
    )
    # 'lon': 12.0, 'lat': 13.0, 'accuracy': 14, time: 10:00:10
    redis_store.hset(
        'history:20190406:10:spider-man',
        '1554544810',
        load_binary('2019040610_1'),
    )
    # 'lon': 12.51, 'lat': 14.0, 'accuracy': 13, time: 10:00:20
    redis_store.hset(
        'history:20190406:10:spider-man',
        '1554544820',
        load_binary('2019040610_2'),
    )
    # 'lon': 12.0, 'lat': 13.0, 'accuracy': 14, time: 10:00:10
    redis_store.hset(
        'history:20190406:10:piter_parker',
        '1554544810',
        load_binary('2019040610_1'),
    )
    # 'lon': 12.51, 'lat': 14.0, 'accuracy': 13, time: 10:00:20
    redis_store.hset(
        'history:20190406:10:piter_parker',
        '1554544820',
        load_binary('2019040610_2'),
    )

    response = taxi_geotracks.post(
        'user/takeout',
        load_json('request.json'),
        headers={'YaTaxi-API-Key': 'GEOTRACKS_TAKEOUT_KEY'},
    )
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'ok'
    assert len(data['data']['track']) == 11

    eps = 1e-5
    item = data['data']['track'][0]
    assert item['lon'] == 42
    assert abs(item['lat'] - 0.1) < eps
    assert item['timestamp'] == 1538377201
    assert item['accuracy'] == 2

    response = taxi_geotracks.post(
        'user/takeout',
        load_json('request_no_data.json'),
        headers={'YaTaxi-API-Key': 'GEOTRACKS_TAKEOUT_KEY'},
    )
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'no_data'

    response = taxi_geotracks.post(
        'user/takeout',
        load_json('request_no_users.json'),
        headers={'YaTaxi-API-Key': 'GEOTRACKS_TAKEOUT_KEY'},
    )
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'no_data'


def test_takeout_api_key(taxi_geotracks, load_json):
    response = taxi_geotracks.post(
        'user/takeout',
        load_json('request_no_data.json'),
        headers={'YaTaxi-API-Key': 'GEOTRACKS-INVALID-KEY'},
    )
    assert response.status_code == 403
    response = taxi_geotracks.post(
        'user/takeout', load_json('request_no_data.json'),
    )
    assert response.status_code == 403
