import time

import pytest


@pytest.mark.config(GEOTRACKS_USER_ARCHIVER_ENABLE=True)
@pytest.mark.now('2018-10-01T12:00:00+0000')
def test_user_archiver(
        taxi_geotracks, redis_store, testpoint, mockserver, config,
):
    stats = {'s3_calls': 0}

    @mockserver.handler('/s3mds/', prefix=True)
    def mock_mds(request):
        stats['s3_calls'] += 1
        return mockserver.make_response('', 200)

    redis_store.hset(
        'history:20181001:12:spider-man',
        '1538396400',
        b'\x10\x00\x00\x00\x0c\x00\x18\x00\x08\x00\x0c\x00'
        b'\x10\x00\x06\x00\x0c\x00\x00\x00\x00\x00\x0e\x00'
        b'\x00\x1b\xb7\x00@]\xc6\x00\xf0\x10\xb2[\x00\x00\x00'
        b'\x00',
    )
    redis_store.hset(
        'history:20181001:11:spider-man',
        '1538392800',
        b'\x10\x00\x00\x00\x0c\x00\x18\x00\x08\x00\x0c\x00'
        b'\x10\x00\x06\x00\x0c\x00\x00\x00\x00\x00\x0e\x00'
        b'\x00\x1b\xb7\x00@]\xc6\x00\xe0\x02\xb2[\x00\x00\x00'
        b'\x00',
    )
    redis_store.hset(
        'history:20181001:10:spider-man',
        '1538389200',
        b'\x10\x00\x00\x00\x0c\x00\x18\x00\x08\x00\x0c\x00'
        b'\x10\x00\x06\x00\x0c\x00\x00\x00\x00\x00\x0e\x00'
        b'\x00\x1b\xb7\x00@]\xc6\x00\xd0\xf4\xb1[\x00\x00\x00'
        b'\x00',
    )
    redis_store.hset(
        'history:20181001:09:spider-man',
        '1538385600',
        b'\x10\x00\x00\x00\x0c\x00\x18\x00\x08\x00\x0c\x00'
        b'\x10\x00\x06\x00\x0c\x00\x00\x00\x00\x00\x0e\x00'
        b'\x00\x1b\xb7\x00@]\xc6\x00\xc0\xe6\xb1[\x00\x00\x00'
        b'\x00',
    )
    redis_store.hset(
        'history:20181001:08:spider-man',
        '1538382000',
        b'\x10\x00\x00\x00\x0c\x00\x18\x00\x08\x00\x0c\x00'
        b'\x10\x00\x06\x00\x0c\x00\x00\x00\x00\x00\x0e\x00'
        b'\x00\x1b\xb7\x00@]\xc6\x00\xb0\xd8\xb1[\x00\x00\x00'
        b'\x00',
    )
    redis_store.hset(
        'history:20181001:08:wonder-woman',
        '1538382000',
        b'\x10\x00\x00\x00\x0c\x00\x18\x00\x08\x00\x0c\x00'
        b'\x10\x00\x06\x00\x0c\x00\x00\x00\x00\x00\x0e\x00'
        b'\x00\x1b\xb7\x00@]\xc6\x00\xb0\xd8\xb1[\x00\x00\x00'
        b'\x00',
    )
    redis_store.hset(
        'history:20181001:08:batman',
        '1538382000',
        b'\x10\x00\x00\x00\x0c\x00\x18\x00\x08\x00\x0c\x00'
        b'\x10\x00\x06\x00\x0c\x00\x00\x00\x00\x00\x0e\x00'
        b'\x00\x1b\xb7\x00@]\xc6\x00\xb0\xd8\xb1[\x00\x00\x00'
        b'\x00',
    )
    redis_store.hset(
        'history:20181001:07:batman',
        '1538378400',
        b'\x10\x00\x00\x00\x0c\x00\x18\x00\x08\x00\x0c\x00'
        b'\x10\x00\x06\x00\x0c\x00\x00\x00\x00\x00\x0e\x00'
        b'\x00\x1b\xb7\x00@]\xc6\x00\xa0\xca\xb1[\x00\x00\x00'
        b'\x00',
    )
    redis_store.hset(
        'history:20181001:06:batman',
        '1538374800',
        b'\x10\x00\x00\x00\x0c\x00\x18\x00\x08\x00\x0c\x00'
        b'\x10\x00\x06\x00\x0c\x00\x00\x00\x00\x00\x0e\x00'
        b'\x00\x1b\xb7\x00@]\xc6\x00\x90\xbc\xb1[\x00\x00\x00'
        b'\x00',
    )

    taxi_geotracks.get('ping')

    @testpoint('geohistory::archive::DoWork')
    def work(_):
        pass

    cnt = 0
    while stats['s3_calls'] != 6 and cnt != 6:
        work.wait_call(1)
        cnt += 1

    redis_store.delete('geotracks:user_archive:jobs')

    config.set_values({'GEOTRACKS_USER_ARCHIVER_ENABLE': False})
    taxi_geotracks.invalidate_caches()

    time.sleep(0.5)

    assert stats['s3_calls'] == 6
    assert redis_store.hgetall('history:20181001:07:batman') == {}
    assert redis_store.hgetall('history:20181001:06:batman') != {}
