import pytest

from dmp_suite import geohash as py_geohash

try:
    from dmp_suite.speedups.geo import geohash as c_geohash
    speedups_not_loaded = False
except ImportError:
    speedups_not_loaded = True


@pytest.mark.skipif(speedups_not_loaded, reason='speedups not loaded')
@pytest.mark.parametrize(
    'lon,lat,precision,ghash', [
        (59.5091, -46.2127, 1, 'f'),
        (-63.6645, -26.663, 2, '5k'),
        (-2.9399, -24.6031, 3, '7rq'),
        (-118.6321, -32.2144, 4, '5210'),
        (2.2313, 55.455, 5, 't0rkt'),
        (-115.0377, 11.6319, 6, 'h20208'),
        (20.6213, 87.9812, 7, 'tgwt61c'),
        (-8.4516, 7.5221, 8, 'knmrgjmm'),
        (-157.2564, -84.2913, 9, '40h01bhbn'),
        (144.8119, 72.8488, 10, 'vxgzcxyzup'),
        (-136.8144, 46.623, 11, 'j010hbjb48h'),
        (-5.5482, -38.6052, 12, '7ph83tbx3ss3')
    ]
)
def test_encode(lon, lat, precision, ghash):
    assert py_geohash.encode(lon, lat, precision) == ghash
    assert c_geohash.encode(lon, lat, precision) == ghash


@pytest.mark.skipif(speedups_not_loaded, reason='speedups not loaded')
@pytest.mark.parametrize(
    'ghash, lat, lon, lat_err, lon_err', [
        ('f', 67.5, -67.5, 22.5, 22.5),
        ('5k', -64.6875, -28.125, 2.8125, 5.625),
        ('7rq', -3.515625, -24.609375, 0.703125, 0.703125),
        ('5210', -89.912109375, -32.16796875, 0.087890625, 0.17578125),
        ('t0rkt', 2.21923828125, 55.43701171875, 0.02197265625, 0.02197265625),
        ('h20208', -89.99725341796875, 11.6290283203125, 0.00274658203125, 0.0054931640625),
        ('tgwt61c', 20.620651245117188, 87.98057556152344, 0.0006866455078125, 0.0006866455078125),
        ('knmrgjmm', -8.451662063598633, 7.522029876708984, 8.58306884765625e-05, 0.000171661376953125),
        ('40h01bhbn', -89.99997854232788, -84.29129362106323, 2.1457672119140625e-05, 2.1457672119140625e-05),
        ('vxgzcxyzup', 89.99999731779099, 72.84880220890045, 2.682209014892578e-06, 5.364418029785156e-06),
        ('j010hbjb48h', -89.99999932944775, 46.62299998104572, 6.705522537231445e-07, 6.705522537231445e-07),
        ('7ph83tbx3ss3', -5.548200057819486, -38.60520014539361, 8.381903171539307e-08, 1.6763806343078613e-07),
    ]
)
def test_decode_exactly(ghash, lat, lon, lat_err, lon_err):

    def compare_result(x_lat, x_lon, x_lat_err, x_lon_err):
        assert x_lat == pytest.approx(lat)
        assert x_lon == pytest.approx(lon)
        assert x_lat_err == pytest.approx(lat_err)
        assert x_lon_err == pytest.approx(lon_err)

    compare_result(*py_geohash.decode_exactly(ghash))
    compare_result(*c_geohash.decode_exactly(ghash))
