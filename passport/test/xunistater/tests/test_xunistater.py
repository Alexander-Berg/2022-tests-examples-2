# coding=utf-8
from json import loads

from passport.backend.core.test.xunistater.xunistater import XunistaterChecker
import pytest
import yatest.common as yc


@pytest.fixture(scope='module')
def xunistater():
    return XunistaterChecker(
        config_path=yc.source_path() + '/passport/backend/core/test/xunistater/tests/xunistater.conf',
        cs_id2parser_id_map={
            'ufo_status.rps': 'statbox.log',
            'ufo_failed.rps': 'statbox.log',
        }
    )


@pytest.mark.parametrize(
    'parser_id, condition_set_id, stdin, stdout_expected',
    [
        ('statbox.log', 'ufo_status.rps', 'tskv\taction=ufo_profile_checked\tmode=any_auth\tkind=ufo\tufo_status=0', '[["profile.ufo.ufo_status.0_dmmm",1]]'),
        ('statbox.log', 'ufo_failed.rps', 'tskv\taction=ufo_profile_checked\tmode=any_auth\tdecision_source=ufo_failed\tkind=ufo', '[["ufo_failed.rps_dmmm",1]]'),
    ])
def test_xunistater_signal_parser_with_product_config(xunistater, parser_id, condition_set_id, stdin, stdout_expected):
    """Проверка возможности чека tskv парсеров из конфига xunistarter'а по одному"""
    result = xunistater.check_xunistater_signal(parser_id, condition_set_id, stdin)
    assert result == loads(stdout_expected)


def test_xunistater_signals_parser_with_product_config(xunistater):
    """Проверка метода пакетной проверки генерации сигналов"""
    stdin = '''
        tskv\taction=ufo_profile_checked\tmode=any_auth\tkind=ufo\tufo_status=0
        tskv\taction=ufo_profile_checked\tmode=any_auth\tdecision_source=ufo_failed\tkind=ufo
        tskv\taction=ufo_profile_checked\tmode=any_auth\tkind=ufo\tufo_status=1
        tskv\taction=ufo_profile_checked\tmode=any_auth\tkind=ufo\tufo_status=0
    '''
    expected_signals = {
        'profile.ufo.ufo_status.0_dmmm': 2,
        'profile.ufo.ufo_status.1_dmmm': 1,
        'ufo_failed.rps_dmmm': 1,
        }
    used_condition_set_ids = ['ufo_status.rps', 'ufo_failed.rps']

    xunistater.check_xunistater_signals(stdin, used_condition_set_ids, expected_signals)
