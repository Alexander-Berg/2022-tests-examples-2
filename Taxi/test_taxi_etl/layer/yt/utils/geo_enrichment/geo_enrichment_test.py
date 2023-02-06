# coding: utf-8

import os
import unittest

from mock import patch, MagicMock

from taxi_etl.layer.yt.utils import geo_enrichment as ge

TARIFF_SETTINGS_FIXTURES = [
    {
        'id': '56f968f07c0aa65c44998e33',
        'doc': {
            'city_id': 'Москва',
            'hz': 'himki'
        }
    }
]

COUNTRY_FIXTURES = [
    dict(id='rus', name_rus='Россия'),
    dict(id='kaz', name_rus='Казахстан'),
]

CITY_FIXTURES = [
    dict(id='Москва', country_id='rus'),
    dict(id='Алматы', country_id='kaz'),
]

GOOGLEDOCS_FIXTURES = [dict(country='Казахстан', regions=[" Зарубежье"])]


def read_yt_table_mock(path, *args, **kwargs):
    if '/raw/dbtaxi/tariff_settings' in path:
        return TARIFF_SETTINGS_FIXTURES
    if '/ods/mdb/country' in path:
        return COUNTRY_FIXTURES
    if '/ods/mdb/city' in path:
        return CITY_FIXTURES
    if '/raw/googledocs' in path:
        return GOOGLEDOCS_FIXTURES
    raise ValueError('path is not expected: {}'.format(path))


class TestCityAttributer(unittest.TestCase):
    @patch("dmp_suite.yt.operation.read_yt_table", read_yt_table_mock)
    @patch("taxi_etl.layer.yt.utils.geo_enrichment.CityAttributer._validate_tz2city",
           MagicMock(return_value=None))
    def setUp(self):
        self.attributer = ge.CityAttributer()

    def test_tz_city_himki(self):
        self.assertEqual(
            self.attributer.attribute(["himki_activation"]),
            "Москва"
        )

    def test_tz_city_mkad_himki(self):
        self.assertEqual(self.attributer.attribute(["mkad", "himki"]), "Москва")

    def test_tz_city_izengard(self):
        self.assertEqual(
            self.attributer.attribute(["izengard", "rivendell_activation"]),
            "unknown"
        )

    def test_tz_city_none(self):
        self.assertEqual(self.attributer.attribute([None]), "unknown")


class TestCountryAttributer(unittest.TestCase):
    @patch("dmp_suite.yt.operation.read_yt_table", read_yt_table_mock)
    @patch(("taxi_etl.layer.yt.utils.geo_enrichment."
            "CountriesAttributer._validate_city2country"),
           MagicMock(return_value=None))
    @patch(("taxi_etl.layer.yt.utils.geo_enrichment."
            "CountriesAttributer._validate_country2regions"),
           MagicMock(return_value=None))
    def setUp(self):
        self.attributer = ge.CountriesAttributer()

    def test_city_country_msk(self):
        args = ["Москва"]
        self.assertListEqual(self.attributer.attribute(*args), ["Россия"])

    def test_city_country_almati(self):
        self.assertSetEqual(
            set(self.attributer.attribute("Алматы")),
            {"Казахстан", " Зарубежье"}
        )

    def test_city_country_izengard(self):
        self.assertListEqual(self.attributer.attribute("izengard"), ["unknown"])


class TestRegionsAttributer(unittest.TestCase):
    def setUp(self):
        self.attributer = ge.RegionsAttributer.from_local_file(
            os.path.join(os.path.dirname(__file__),
                         'tariff_zones_to_regions_test_handbook.yson'))

    def test_city_country_msk(self):
        tzs = ["mkad", "himki"]
        answer = {
            "Химки",
            "Москва",
            " Регион: МО",
            " Регион: Москва + МО",
            " Регион: МО ближнее",
            " Регион: Москва + МО + Санкт-Петербург + ЛО",
        }
        self.assertSetEqual(
            set(self.attributer.attribute(tariff_zones=tzs)), answer)

    def test_city_country_unknown(self):
        tzs = []
        answer = {
            "unknown"
        }
        self.assertSetEqual(
            set(self.attributer.attribute(tariff_zones=tzs)), answer)
