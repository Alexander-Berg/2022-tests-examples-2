from unittest import TestCase
from functools import partial

from dmp_suite.performance_utils import normalize_utm


class TestNormalizeUtm(TestCase):
    def test_normalize_utm(self):
        utm_parameters_raw = [
            '[yt]МА_ua-goal_ru-yev-brb_android_cpc-07-03-2019'.encode('utf8'),  # rus
            '[yt]МА_ua-goal_ru-yev-brb_android_cpc-07-03-2019',  # rus
            '[yt]ма_ua-goal_ru-yev-brb_android_cpc-07-03-2019'.encode('utf8'),
            '[yt]ма_ua-goal_ru-yev-brb_android_cpc-07-03-2019',
            '[yt]MA_ua-goal_ru-yev-brb_android_cpc-07-03-2019'.encode('utf8'),  # eng
            '[yt]MA_ua-goal_ru-yev-brb_android_cpc-07-03-2019',  # eng
            '[yt]ma_ua-goal_ru-yev-brb_android_cpc-07-03-2019'.encode('utf8'),
            '[yt]ma_ua-goal_ru-yev-brb_android_cpc-07-03-2019',
            '[yt]ma_ua-goal_ru-yev-brb_android_cpc-07-03-2019  '.encode('utf8'),
            '[yt]ma_ua-goal_ru-yev-brb_android_cpc-07-03-2019  ',
        ]
        expected_utm_parameters_normalized = 10 * [u'[yt]ma_ua-goal_ru-yev-brb_android_cpc-07-03-2019']

        actual_utm_parameters_normalized = list(map(normalize_utm, utm_parameters_raw))

        self.assertListEqual(
            expected_utm_parameters_normalized,
            actual_utm_parameters_normalized,
            msg='Expected parameters are different from actual:\nexpected\n{},\nactual\n{}'.format(
                expected_utm_parameters_normalized,
                actual_utm_parameters_normalized
            )
        )

    def test_normalize_utm_wo_transliteration(self):
        utm_parameters_raw = [
            '  стать водителем uber'.encode('utf8'),
            '  стать водителем uber',
            'СТАТЬ ВОДИТЕЛЕМ UBER  '.encode('utf8'),
            'СТАТЬ ВОДИТЕЛЕМ UBER  ',
        ]
        expected_utm_parameters_normalized = 4 * [u'стать водителем uber']

        actual_utm_parameters_normalized = list(map(partial(normalize_utm, transliterate_flg=False), utm_parameters_raw))

        self.assertListEqual(
            expected_utm_parameters_normalized,
            actual_utm_parameters_normalized,
            msg='Expected parameters are different from actual:\nexpected\n{},\nactual\n{}'.format(
                expected_utm_parameters_normalized,
                actual_utm_parameters_normalized
            )
        )
