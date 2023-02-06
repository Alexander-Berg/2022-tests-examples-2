from unittest import TestCase

from taxi_etl.layer.yt.ods.zendesk_hiring.common.impl import normalize_phone_number


class TestNormalizePhoneNumber(TestCase):
    def test_removes_non_digits(self):
        self.assertEqual(
            normalize_phone_number('+7 (916) 123-45-67 (мобильный)'),
            u'+79161234567'
        )

    def test_adds_leading_plus(self):
        self.assertEqual(
            normalize_phone_number('79161234567'),
            u'+79161234567'
        )

    def test_is_none_when_no_digits(self):
        self.assertEqual(
            normalize_phone_number('абракадабра'),
            None
        )
