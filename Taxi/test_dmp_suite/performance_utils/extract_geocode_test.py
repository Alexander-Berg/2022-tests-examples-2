# coding: utf-8
from unittest import TestCase

from dmp_suite.performance_utils import extract_geocode


class ExtractGeocodeTest(TestCase):
    def test_extract_geocode(self):
        self.assertEqual(
            extract_geocode('ma_kz-akm-ast_generic_android.23352130'),
            'kz-akm-ast'
        )
        self.assertEqual(
            extract_geocode('ma_brand_msk_yandex.taxi_android.15158921'),
            None
        )
        self.assertEqual(
            extract_geocode('dt_ru-per-all_comp_exp.27499820'),
            'ru-per-all'
        )
        self.assertEqual(
            extract_geocode('brand-ekb_mobile-yandex.taxi_iphone'),
            None
        )
        self.assertEqual(
            extract_geocode('копия driver_rabota_ru-che-che_brand_lptest'),
            'ru-che-che'
        )
        self.assertEqual(
            extract_geocode('sdfsdfsdf_ua-51-ode_'),
            'ua-51-ode'
        )
        self.assertEqual(
            extract_geocode('by-min-_'),
            'by-min-'
        )
        self.assertEqual(
            extract_geocode('ma_ru-rus-all_uretention_rsya_android_exp [oplata kartoj].31066269'),
            'ru-rus-all'
        )
        self.assertEqual(
            extract_geocode('ma_ru-ore-ors_generic_android.31015615'),
            'ru-ore-ors'
        )
        self.assertEqual(
            extract_geocode('ma_ru-tve-tve_generic_iphone.30917683'),
            'ru-tve-tve'
        )
        self.assertEqual(
            extract_geocode('ru-sve-ntag_rt'),
            'ru-sve-ntag'
        )
        self.assertEqual(
            extract_geocode('ru-mow-msk_dom-rabota_exp (6102320324057)'),
            'ru-mow-msk'
        )
        self.assertEqual(
            extract_geocode('dt_dua-goal_il-m-rlz_promo-post_reach'),
            'il-m-rlz'
        )
        self.assertEqual(
            extract_geocode('lavka-ios-remarketing'),
            None
        )
