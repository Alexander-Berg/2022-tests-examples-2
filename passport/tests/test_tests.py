# -*- coding: utf-8 -*-
from passport.backend.libs_checker import library_tests
import yatest.common as yc


class TestGeobaseTest(library_tests.geobase_checker.TestGeobase):
    @classmethod
    def setUpClass(cls):
        cls.geobase = library_tests.geobase_checker.Lookup(yc.work_path('test_data/geodata4.bin'))


class TestLibIpregTest(library_tests.ipreg_checker.TestLibIpreg):
    @classmethod
    def setUpClass(cls):
        cls.ipreg = library_tests.ipreg_checker.init_ipreg(yc.work_path('test_data/layout-passport-ipreg.json'))


class TestUATraitsTest(library_tests.uatraits_checker.TestUATraits):
    @classmethod
    def setUpClass(cls):
        cls.BROWSER_ENCODE, cls.BROWSER_DECODE = library_tests.uatraits_checker.init_browsers(
            yc.work_path('test_data/dict_BrowserName.json'),
        )
        cls.OS_ENCODE, cls.OS_DUMB_ENCODE, cls.OS_DECODE = library_tests.uatraits_checker.init_oses(
            yc.work_path('test_data/dict_OSFamily_OSVersion_OSName.json'),
        )
