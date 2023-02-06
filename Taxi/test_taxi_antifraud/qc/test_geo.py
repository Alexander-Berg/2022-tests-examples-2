from taxi_antifraud.qc import geo


def test_geohash():
    assert geo.geohash_encode(55.75, 37.616667, 10) == 'ucftpuzx7c'
    assert geo.geohash_encode(59.95, 30.316667, 10) == 'udtt1cefj9'
    assert geo.geohash_encode(48.472207, 135.066546, 10) == 'z085c807nd'
