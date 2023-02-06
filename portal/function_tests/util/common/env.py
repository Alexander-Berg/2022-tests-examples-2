# -*- coding: utf-8 -*-
import logging
import re

from portal.function_tests.util.common.params import PytestConfig

DESKTOP_UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) ' \
             'Chrome/55.0.2883.95 YaBrowser/17.1.0.2186 Yowser/2.5 Safari/537.36'

TOUCH_UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2 like Mac OS X) AppleWebKit/601.1.37 (KHTML, like Gecko) ' \
           'Version/8.0 Mobile/13A4293g Safari/600.1.4'

TOUCH_WP_UA = 'Mozilla/5.0 (compatible; MSIE 11.0; Windows Phone 8.1; Trident/6.0; IEMobile/11.0; ARM; ' \
              'Touch; NOKIA; Lumia 920)'

PDA_UA = 'Opera/9.80 (J2ME/MIDP; Opera Mini/9.80 (S60; SymbOS; Opera Mobi/23.334; U; id) Presto/2.5.25 Version/10.54'

TEL_UA = 'Nokia6300/2.0 (04.20) Profile/MIDP-2.0 Configuration/CLDC-1.1 UNTRUSTED/1.0'

logger = logging.getLogger(__name__)


def get_morda_url_pattern(env):
    def get_yaru_host_pattern(env):
        if env == 'production':
            return '((www.)?ya.ru)'
        if env == 'rc':
            return '((www-)?rc.ya.ru)'
        return '(www-{}.ya.ru)'.format(env)

    morda_url_pattern = '((www|aile|family|avg|beta|hw|m|op|firefox){}.yandex.(ru|ua|kz|by|com|com.tr))'

    if env == 'production':
        return morda_url_pattern.format('') + '|' + get_yaru_host_pattern(env)
    else:
        return morda_url_pattern.format('-' + env) + '|' + get_yaru_host_pattern(env)


def retry_count():
    return int(PytestConfig(None).config.getoption('retry_count'))


def morda_env():
    if is_monitoring():
        return 'production'
    return PytestConfig(None).config.getoption('morda_env', 'production')


def is_monitoring():
    return PytestConfig(None).config.getoption('monitoring') != '0'


def desktop_ua():
    return PytestConfig(None).config.getoption('desktop_ua', DESKTOP_UA)


def touch_ua():
    return PytestConfig(None).config.getoption('touch_ua', TOUCH_UA)


def touch_wp_ua():
    return PytestConfig(None).config.getoption('touch_wp_ua', TOUCH_WP_UA)


def pda_ua():
    return PytestConfig(None).config.getoption('pda_ua', PDA_UA)


def tel_ua():
    return PytestConfig(None).config.getoption('tel_ua', TEL_UA)


def dns_override():
    morda_dns = PytestConfig(None).config.getoption('dns_morda', None)

    res = {get_morda_url_pattern(morda_env()): morda_dns} if morda_dns else {}
    res[r'(www\.|m\.|tel\.|)yandex\.ua'] = '2a02:6b8:a::a'  # FIX UA PROD CLEANVARS

    override = PytestConfig(None).config.getoption('dns_override', [])

    pattern = re.compile('([^;=,]+)=([^,]+)')
    args = {i: j for i, j in pattern.findall(override)}

    try:
        [re.compile(e) for e in args.keys()]
    except Exception:
        logger.exception('Failed to parse dns_override property')
        raise

    res.update(args)
    return res


def rate_limit():
    return PytestConfig(None).config.getoption('rate_limit')


def get_tests_path():
    return PytestConfig(None).config.getoption('tests_path')
