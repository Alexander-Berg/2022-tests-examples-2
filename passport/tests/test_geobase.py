# -*- coding: utf-8 -*-
import unittest

from nose.tools import (
    assert_raises,
    eq_,
)
from passport.backend.core.geobase import (
    get_country_code_by_ip,
    get_first_parent_by_condition,
    get_geobase,
    is_valid_country_code,
    Region,
)
from passport.backend.core.test.test_utils import with_settings
from passport.backend.utils.string import smart_unicode


@with_settings()
class TestGeobase(unittest.TestCase):
    def test_get_country_by_tld(self):
        results = [
            ('org', 'ru'),
            ('com.tr', 'tr'),
            ('kz', 'kz'),
            ('by', 'by'),
            ('', 'ru'),
            ('az', 'az'),
            ('com.am', 'am'),
            ('com.ge', 'ge'),
            ('co.il', 'il'),
            ('kg', 'kg'),
            ('lt', 'lt'),
            ('lv', 'lv'),
            ('md', 'md'),
            ('tj', 'tj'),
            ('tm', 'tm'),
            ('uz', 'uz'),
            ('fr', 'fr'),
            ('ee', 'ee'),
        ]
        for tld, code in results:
            eq_(Region(tld=tld).country['short_en_name'].lower(), code, [tld, code])

    def test_is_valid_country_code(self):
        results = [
            ('RU', True),
            ('ru', True),
            ('gg', False),
            ('na', True),
            ('notselected', False),
            ('fake', False),
            ('AH', False),
            (u'ИК', False),
        ]

        for code, expected_result in results:
            eq_(is_valid_country_code(code), expected_result, code)

    def test_get_country_by_ip(self):
        eq_(Region(ip='127.0.0.1').country, None)
        eq_(Region(ip='95.108.173.106').country['short_en_name'], 'RU')  # московский офис Яндекса

        # country вычисляется 1 раз, после чего отдается один и тот же объект
        region = Region(ip='95.108.173.106')
        eq_(id(region.country), id(region.country))

    def test_get_country_code_by_ip(self):
        for ip, code in (
            ('95.108.173.106', 'RU'),  # московский офис Яндекса
            ('127.0.0.1', None),
        ):
            eq_(get_country_code_by_ip(ip), code)

    def test_get_city_by_ip(self):
        eq_(Region(ip='127.0.0.1').city, None)
        eq_(Region(ip='95.108.173.106').city['short_en_name'], 'MSK')  # московский офис Яндекса

        # city вычисляется 1 раз, после чего отдается один и тот же объект
        region = Region(ip='95.108.173.106')
        eq_(id(region.city), id(region.city))

    def test_get_as_list_by_ip(self):
        eq_(Region(ip='127.0.0.1').AS_list, [])
        eq_(Region(ip='87.250.235.4').AS_list, ['AS13238'])  # passportdev-python

        # AS_list вычисляется 1 раз, после чего отдается один и тот же объект
        region = Region(ip='87.250.235.4')
        eq_(id(region.AS_list), id(region.AS_list))

    def test_get_timezone_by_ip(self):
        eq_(Region(ip='127.0.0.1').timezone, None)
        eq_(Region(ip='95.108.173.106').timezone, 'Europe/Moscow')  # московский офис Яндекса
        eq_(Region(ip='8.8.8.8').timezone, 'America/New_York')

    def test_get_first_parent_by_condition(self):
        eq_(get_first_parent_by_condition(225, lambda r: r['id'] == 1), None)
        eq_(smart_unicode(get_first_parent_by_condition(225, lambda r: r['id'] == 10000)['name']).capitalize(), u'Земля')
        eq_(smart_unicode(get_first_parent_by_condition(10000, lambda r: r['id'] == 10000)['name']).capitalize(), u'Земля')

    def test_get_region_by_id(self):
        eq_(Region(id=213).id, 213)
        eq_(Region().id, None)

    def test_region_name(self):
        eq_(smart_unicode(Region(id=213).name).capitalize(), u'Москва')
        eq_(Region().name, '')

    def test_region_coordinates(self):
        eq_(Region(id=213).lat, 55.755768)
        eq_(Region(id=213).lon, 37.617671)
        eq_(Region().lat, None)
        eq_(Region().lon, None)

    def test_region_linguistics(self):
        eq_(Region(id=213).linguistics('en').nominative.capitalize(), 'Moscow')
        eq_(Region().linguistics('en'), None)

    def test_geobase_asset(self):
        geobase = get_geobase()

        with assert_raises(RuntimeError):
            geobase.asset('127.0.0.1')

        eq_(geobase.asset('95.108.173.106'), 'AS13238')
