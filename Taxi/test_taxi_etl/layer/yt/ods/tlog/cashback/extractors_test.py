import pytest
from unittest import TestCase

from taxi_etl.layer.yt.ods.tlog.cashback.loader import cashback_type_extractor, plus_flg_extractor


class TestExtractors(TestCase):
    def test_cashback_type_extractor(self):
        assert cashback_type_extractor('any_cashback_value', 'econom') == 'any_cashback_value'
        assert cashback_type_extractor(None, 'econom') == 'transaction'
        assert cashback_type_extractor(None, 'any_tariff') == 'agent'
        assert cashback_type_extractor(None, None) == 'transaction'

        assert cashback_type_extractor(1, 'econom') == 1
        assert cashback_type_extractor('', 1) == ''
        assert cashback_type_extractor(None, 1) == 'agent'
        assert cashback_type_extractor(None, '') == 'agent'

    def test_plus_flg_extractor(self):
        assert plus_flg_extractor(True) is True
        assert plus_flg_extractor(False) is False
        assert plus_flg_extractor('true') is True
        assert plus_flg_extractor('trUE') is True
        assert plus_flg_extractor('any_other_text_except_true') is False
        assert plus_flg_extractor(None) is False

        # for any other data type except bool or str
        with pytest.raises(TypeError):
            plus_flg_extractor(1)
