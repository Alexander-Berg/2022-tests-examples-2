# -*- coding: utf-8 -*-
import logging

import allure
import pytest

from common.client import MordaClient
from common.geobase import Regions
from common.morda import TouchMain, DesktopMain

logger = logging.getLogger(__name__)


def get_ua(key):
    SAFARI_9 = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/601.5.13 (KHTML, like Gecko) ' \
                    'Version/9.1 Safari/601.5.13.'
    clients = {
        'msk': MordaClient(morda=DesktopMain(region=Regions.MOSCOW)),
        'spb': MordaClient(morda=DesktopMain(region=Regions.SAINT_PETERSBURG)),
        'ptrpav': MordaClient(morda=DesktopMain(region=Regions.PETROPAVLOVSK)),
        'ukr': MordaClient(morda=DesktopMain(region=Regions.UKRAINE)),
        'bad_ua': MordaClient(morda=DesktopMain(region=Regions.MOSCOW, user_agent=SAFARI_9)),
        'touch_msk': MordaClient(morda=TouchMain(region=Regions.MOSCOW)),
        'touch_spb': MordaClient(morda=TouchMain(region=Regions.SAINT_PETERSBURG)),
    }
    clients['whitelist'] = clients['msk']
    return clients[key]


def get_stream_data(key):
    ua = get_ua(key)
    if key == 'whitelist':
        response = ua.export('stream_channels_whitelist3').send()
    else:
        response = ua.cleanvars(blocks=['Stream', 'TV']).send()

    assert response.is_ok(), u'Не удалось получить данные для {}'.format(key)

    data = response.json()

    assert data, u'Нет данныx в ответе для {}'.format(key)

    return data


@allure.feature('stream')
class TestStream(object):

    @allure.story('stream_entry')
    @pytest.mark.yasm(signal='morda_stream_entrypoints_{}_tttt')
    def test_stream_desktop_no_data_ua(self, yasm):
        data = get_stream_data('ukr')

        no_data_in_ua = 'show' not in data['Stream'] or data['Stream'] == 0

        yasm.add_to_signal('morda_stream_entrypoints_failed_ua_has_data_tttt', 1 if not no_data_in_ua else 0)

        assert no_data_in_ua, u'Не должно быть стрима на Украине'

    @allure.story('stream_entry')
    @pytest.mark.yasm(signal='morda_stream_entrypoints_{}_tttt')
    def test_stream_desktop_no_data_bad_ua(self, yasm):
        data = get_stream_data('bad_ua')

        no_data_fro_bad_ua = 'show' not in data['Stream'] or data['Stream']['show'] == 0

        yasm.add_to_signal('morda_stream_entrypoints_failed_bad_ua_has_data_tttt', 1 if not no_data_fro_bad_ua else 0)

        assert no_data_fro_bad_ua, u'Не должно быть стрима для ua из фильтра'

    @allure.story('stream_entry')
    @pytest.mark.yasm(signal='morda_stream_entrypoints_{}_tttt')
    def test_stream_desktop_entry_no_channels(self, yasm):
        data = get_stream_data('msk')

        has_channels = 'channels' in data['Stream'] and len(data['Stream']['channels'])

        logger.debug(u'Кол-во каналов в мск - {}'.format(len(data['Stream']['channels'])))

        yasm.add_to_signal('morda_stream_entrypoints_failed_no_channels_tttt', 1 if not has_channels else 0)

        assert has_channels, u'Нет каналов для десктопной ru морды'

    @allure.story('stream_entry')
    @pytest.mark.yasm(signal='morda_stream_entrypoints_{}_tttt')
    def test_stream_desktop_entry_tv_button(self, yasm):
        data = get_stream_data('msk')

        has_tv_stream_button = 'TV' in data and 'stream_default_channel' in data['TV'] and \
                               data['TV']['stream_default_channel']

        yasm.add_to_signal('morda_stream_entrypoints_no_tv_button_tttt', 1 if not has_tv_stream_button else 0)

        assert has_tv_stream_button, u'Нет кнопки "Тв онлайн" на морде'

    @allure.story('stream_entry')
    @pytest.mark.yasm(signal='morda_stream_entrypoints_{}_tttt')
    def test_stream_desktop_no_data_media_stream(self, yasm):
        data = get_stream_data('msk')
        MIN_CHANNELS = 9

        has_media_stream = 'show' in data['Stream'] and data['Stream']['show'] == 1 and \
                           len(data['Stream']['channels']) >= MIN_CHANNELS

        logger.debug(u'Кол-во каналов - {}, нужно минимум - {}'
                     .format(len(data['Stream']['channels']), MIN_CHANNELS))

        yasm.add_to_signal('morda_stream_entrypoints_failed_no_media_stream_tttt', 1 if not has_media_stream else 0)

        assert has_media_stream, u'Нет блока с каналами (онлайн передачами) в футере'

    # Тачи
    @allure.story('stream_entry')
    @pytest.mark.yasm(signal='morda_stream_entrypoints_{}_tttt')
    def test_stream_touch_no_stream_intro(self, yasm):
        data = get_stream_data('touch_msk')
        MIN_CHANNELS_TOUCH = 2

        has_touch_stream_intro = 'show' in data['Stream'] and data['Stream']['show'] == 1 \
                                 and len(data['Stream']['channels']) > MIN_CHANNELS_TOUCH

        logger.debug(u'Кол-во каналов - {}, нужно минимум - {}'
                     .format(len(data['Stream']['channels']), MIN_CHANNELS_TOUCH))

        yasm.add_to_signal('morda_stream_entrypoints_failed_touch_no_stream_tttt',
                           1 if not has_touch_stream_intro else 0)

        assert has_touch_stream_intro, u'Нет блока stream-intro на таче'

    @allure.story('stream_entry')
    @pytest.mark.yasm(signal='morda_stream_entrypoints_{}_tttt')
    def test_stream_touch_no_stream_intro_title(self, yasm):
        data = get_stream_data('touch_msk')

        has_touch_stream_title = 'show' in data['Stream'] and data['Stream']['show'] == 1 \
                                 and 'default_channel' in data['Stream'] and\
                                 data['Stream']['default_channel']

        yasm.add_to_signal('morda_stream_entrypoints_failed_touch_no_default_channel_tttt',
                           1 if not has_touch_stream_title else 0)

        assert has_touch_stream_title, u'Нет default channel для открытия с заголовка'

    @allure.story('stream_entry')
    @pytest.mark.yasm(signal='morda_stream_online_{}_tttt')
    def test_stream_online(self, yasm):
        data = get_ua('msk').tvstream_online_data()
        assert 'set' in data, u'online handler responded'
        if 'warning' in data:
            logger.debug(u'Some warning, lets see detail')
            for key in data['warning']:
                logger.debug('WARNING:' + key)
                yasm.add_to_signal('morda_stream_online_' + key + '_tttt', data['warning'][key])

        else:
            logger.debug(u'No warnings in response-- good!')
