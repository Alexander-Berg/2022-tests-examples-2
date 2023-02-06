#! -*- coding: utf-8 -*-
import unittest

from geobase6 import Lookup
from passport.backend.libs_checker.environment import StagingEnvironment


COUNTRY_REGION_TYPE = 3
CITY_REGION_TYPE = 6


def get_countries(geobase):
    countries = {}
    for region in geobase.get_regions_by_type(COUNTRY_REGION_TYPE):
        countries[region['short_en_name']] = region
    return countries


def get_first_parent_by_condition(region_id, condition, geobase):
    region = geobase.get_region_by_id(region_id)
    if condition(region):
        return region

    for parent_id in geobase.get_parents_ids(region_id):
        region = geobase.get_region_by_id(parent_id)
        if condition(region):
            return region


class TestGeobase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.geobase = Lookup(StagingEnvironment.env['libgeobase']['geodata'])

    def test_country_codes(self):
        results = [
            ('RU', True),
            ('na', False),
            ('notselected', False),
            ('fake', False),
            ('AH', False),
            ('ИК', False),
        ]
        countries = get_countries(self.geobase)
        for code, expected_result in results:
            assert (code in countries) is expected_result, '{} is {} geobase'.format(
                code,
                'missing from' if expected_result else 'present in'
            )

    def test_region_by_bad_ip(self):
        self.assertRaises(RuntimeError, self.geobase.get_region_by_ip, '127.0.0.300')

    def test_get_country_by_ip(self):
        region = get_first_parent_by_condition(
            self.geobase.get_region_by_ip('95.108.173.106')['id'],  # московский офис Яндекса
            lambda r: r['type'] == COUNTRY_REGION_TYPE,
            geobase=self.geobase,
        )
        assert region['short_en_name'] == 'RU'

    def test_get_city_by_ip(self):
        region = get_first_parent_by_condition(
            self.geobase.get_region_by_ip('95.108.173.106')['id'],  # московский офис Яндекса
            lambda r: r['type'] == CITY_REGION_TYPE,
            geobase=self.geobase,
        )
        assert region['short_en_name'] == 'MSK'

    def test_get_first_parent_by_condition(self):
        assert get_first_parent_by_condition(225, lambda r: r['id'] == 1, self.geobase) is None
        assert get_first_parent_by_condition(225, lambda r: r['id'] == 10000, self.geobase)['name'] == 'Земля'
        assert get_first_parent_by_condition(10000, lambda r: r['id'] == 10000, self.geobase)['name'] == 'Земля'

    def test_get_region_by_id(self):
        assert self.geobase.get_region_by_id(213)['id'] == 213

    def test_region_name(self):
        assert self.geobase.get_region_by_id(213)['name'] == 'Москва'

    def test_region_linguistics(self):
        assert self.geobase.get_linguistics(213, 'en').nominative == 'Moscow'
