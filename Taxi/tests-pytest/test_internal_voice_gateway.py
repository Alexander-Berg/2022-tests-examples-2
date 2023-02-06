import datetime
import json

import pytest

from taxi.core import async
from taxi.internal import voice_gateway as ivgw
from taxi.external import voice_gateway as evgw

MP3DATA = 'mp3-data'


@pytest.mark.filldb(_specified=True, voice_gateways='')
@pytest.inline_callbacks
def test__get_all_gateways():
    gateways = yield ivgw._get_all_gateways()
    # we have 3 in db
    assert len(gateways) == 3


@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_get_all_talks(load, patch):

    @patch('taxi.internal.voice_gateway._get_all_gateways')
    @async.inline_callbacks
    def _get_all_gateways():
        yield
        async.return_value(json.loads(load('db_voice_gateways.json')))

    @patch('taxi.external.voice_gateway.get_talk_list')
    @async.inline_callbacks
    def get_talk_list(host, token, start, end, verify=False):
        yield
        if (not isinstance(host, basestring) or
                not isinstance(token, basestring) or
                not isinstance(start, datetime.datetime) or
                not isinstance(end, datetime.datetime) or
                start >= end):
            raise Exception('Invalid params')
        if 'MTT' in token:
            async.return_value(json.loads(load('get_talks_mtt.json')))
        elif 'ZEBRA' in token:
            async.return_value(json.loads(load('get_talks_zebra.json')))
        else:
            raise evgw.RequestError('Error')

    start = datetime.datetime(2015, 11, 29)
    end = datetime.datetime(2015, 11, 30)
    talk_list = yield ivgw.get_all_talks(start, end)
    assert len(talk_list) == 2
    for talk in talk_list:
        if talk['gateway_id'] == 'zebra':
            assert (talk['redirectionid'] ==
                    '16854835a60c455554130b6e3d81ec50user4drv')
        elif talk['gateway_id'] == 'mtt':
            assert (talk['redirectionid'] ==
                    '7b99469c1f55551f81073f3f8f73405fuser4drv')
