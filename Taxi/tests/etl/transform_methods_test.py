from __future__ import absolute_import

import decimal

import etl.transform_methods.common as common


class TestLatLon2QuadkeyCheckNone(object):
    def test_none(self):
        assert common.latlon2quadkeychecknone(None, None) is None
        assert common.latlon2quadkeychecknone(None, 0) is None
        assert common.latlon2quadkeychecknone(0, None) is None

    def test_zoom(self):
        zoomed_value = '12120113010021330020'
        assert common.latlon2quadkeychecknone(55.123, 55.234, 20) == zoomed_value
        assert common.latlon2quadkeychecknone(55.123, 55.234) == zoomed_value[:15]
        assert common.latlon2quadkeychecknone(55.123, 55.234, 10) == zoomed_value[:10]

    def test_decimal(self):
        dec_lat = decimal.Decimal('55.123')
        dec_lon = decimal.Decimal('55.234')
        assert common.latlon2quadkeychecknone(dec_lat, dec_lon) == '121201130100213'
        assert common.latlon2quadkeychecknone(dec_lat, 55.234) == '121201130100213'
        assert common.latlon2quadkeychecknone(55.123, dec_lon) == '121201130100213'


class TestToFloatConverter(object):
    def test_none(self):
        assert common.to_float_converter(None) is None

    def test_float(self):
        assert common.to_float_converter(0.0123) == 0.0123

    def test_str(self):
        assert common.to_float_converter('0.0123'), 0.0123

    def test_int(self):
        assert common.to_float_converter(123), 123.0

    def test_decimal(self):
        dec = decimal.Decimal('0.0123')
        float_value = common.to_float_converter(dec)
        assert isinstance(float_value, float)
        assert float_value, 0.0123
