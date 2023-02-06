# -*- coding: utf-8 -*-
import logging

import allure
import pytest
from requests.exceptions import RequestException

from common import users
from common.client import MordaClient
from common.geobase import Regions
from common.morda import DesktopMain
from common.users import User

logger = logging.getLogger(__name__)


@allure.feature('stream')
class TestStream(object):
    @allure.story('stream_frame_deny')
    @pytest.mark.yasm(signal='morda_stream_frame_deny_{}_tttt')
    @pytest.mark.parametrize('loggedin', [False, True])
    @pytest.mark.parametrize('valid_sk', [True])
    @pytest.mark.parametrize('inframe', [False, True])
    @pytest.mark.parametrize('_from', ['morda', 'serp', 'tv', 'appsearch'])
    def test_stream_frame(self, yasm, loggedin, valid_sk, inframe, _from):
        try:
            return self._stream_frame(yasm, loggedin, valid_sk, inframe, _from)
        except RequestException:
            return

    def _stream_frame(self, yasm, loggedin, valid_sk, inframe, _from):

        morda = DesktopMain(region=Regions.MOSCOW)
        client = MordaClient(morda=morda)

        if loggedin:
            passport_host = client.cleanvars(blocks=['Mail']).send().json()['Mail']['auth_host']
            with User(users.DEFAULT) as user:
                client.login(passport_host, user['login'], user['password']).send()

        if valid_sk:
            secret_key = client.cleanvars(blocks=['sk']).send().json()['sk']
        else:
            secret_key = 'u00000000000000000000000000000000'

        print secret_key

        url = client.make_url('{}/portal/tvstream')
        params = {
            'from': _from,
            'from_block': 'channel',
            'inframe': 1 if inframe else 0,
            'url': 'https://strm.yandex.ru/dvr/ntv/ntv0.m3u8',
            'cleanvars': '$__NOTHING__%',
            'sk': secret_key,
        }
        response = client.request(url=url, params=params).send()
        is_test_passed = response.get_headers().get('X-Frame-Options', '').upper() != 'DENY'

        signal = 'morda_stream_frame_deny_test_{}_{}_{}_{}_tttt'.format(
            'login' if loggedin else 'logout',
            'oksk' if valid_sk else 'badsk',
            'inframe1' if inframe else 'inframe0',
            _from,
        )
        yasm.add_to_signal(signal, 0 if is_test_passed else 1)

        arg_str = \
            u'Обнаружен заголовок "X-Frame-Options: DENY" для in_frame стрима с параметрами: ' \
            u'loggedin={}, valid_sk={}, inframe={}, _from={}'.format(loggedin, valid_sk, inframe, _from)
        assert is_test_passed, arg_str
