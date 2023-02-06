# -*- coding: utf-8 -*-

from passport.backend.logbroker_client.core.handlers.utils import MessageChunk
from passport.backend.logbroker_client.passport_toloka import events
from passport.backend.logbroker_client.passport_toloka.handler import AdhocFilter


HEADER = {
    'topic': 'rt3.iva--passport--cleanweb-toloka-testing',
    'server': 'pass-dd-i84.sezam.yandex.net',
    'partition': '0',
    'offset': '0'
}


class TestEvents(object):
    def test_toloka_event(self):
        log_data = '{' \
                   '"name": "media_toloka_porno",' \
                   '"subsource": "custom-toloka",' \
                   '"value": true,' \
                   '"entity": "image",' \
                   '"source": "clean-web",' \
                   '"key": "comment-gotthit-4",' \
                   '"data": "{\\"avatar_key\\": \\"key\\", \\"uid\\": 2345}"' \
                   '}\n'
        message = MessageChunk(HEADER, log_data)
        events_filter = AdhocFilter([events.TolokaEvent])
        events_res = events_filter.filter(message)

        assert len(events_res) == 1
        assert events_res[0].resolution == 'media_toloka_porno'
        assert events_res[0].value is True
        assert events_res[0].entity == 'image'
        assert events_res[0].data == dict(uid=2345, avatar_key='key')
