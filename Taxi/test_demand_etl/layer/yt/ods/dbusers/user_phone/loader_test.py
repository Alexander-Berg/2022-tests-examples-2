import unittest

import pytest
from nile.api.v1.clusters import MockCluster
from nile.drivers.common.progress import CommandFailedError

from test_dmp_suite.testing_utils import NileJobTestCase

from demand_etl.layer.yt.ods.dbusers.user_phone.loader import load
from demand_etl.layer.yt.ods.dbusers.user_phone.impl import extract_registration, is_russian_phone_num


class TestOdsUserPhone(NileJobTestCase):
    def setUp(self):
        self.job = MockCluster().job()
        load(None, raw_stream=self.job.table('').label('raw_user_phones')).label('ods_user_phone')

    def test_load(self):
        self.assertCorrectLocalRun(
            self.job,
            sources={
                'raw_user_phones': 'raw_user_phones.json',
            },
            expected_sinks={
                'ods_user_phone': 'ods_user_phone.json',
            }
        )

    def test_fail_fix_phone_pd_id(self):
        for input_file in (
                'raw_user_phones_w_different_not_normalized_phones.json',
                'raw_user_phones_w_equal_normalized_phones.json'
        ):
            self.assertRaisesRegex(
                CommandFailedError,
                'Multiple phone_pd_id for records',
                self._local_run,
                self.job,
                sources={'raw_user_phones': input_file},
                sinks={'ods_user_phone': 'ods_user_phone.json'}
            )

    def test_fail_fix_user_phone_id(self):
        self.assertRaisesRegex(
            CommandFailedError,
            'Strange phone_source_name for',
            self._local_run,
            self.job,
            sources={'raw_user_phones': 'raw_user_phones_fail_fix_user_phone_id.json'},
            sinks={'ods_user_phone': 'ods_user_phone.json'}
        )


class TestExtractRegistration(unittest.TestCase):
    def test_extract_registration(self):
        self.assertEqual(
            extract_registration('5d827f53211473c8c3529755'), '2019-09-18 19:02:43'
        )
        self.assertEqual(
            extract_registration('5c968ae8d253f1c435e35a10'), '2019-03-23 19:37:12'
        )
        self.assertEqual(
            extract_registration('5c1d4566d253f1c4359173b4'), '2018-12-21 19:56:22'
        )


@pytest.mark.parametrize('phone_number, expected',
                         [('+79150032222', True),
                          ('+76857684756', False),
                          ('+77857684756', False),
                          ('+7857684756', False),
                          ('+44685768456', False),
                          ('+79219166889', True),
                          ('+', False),
                          ('', False),
                          (None, False)
                          ])
def test_russian_flg_extractor(phone_number, expected):
    assert is_russian_phone_num(phone_number) == expected
