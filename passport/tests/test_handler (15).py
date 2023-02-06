# -*- coding: utf-8 -*-
from functools import partial
import json

from passport.backend.core.builders.xunistater.faker.fake_xunistater import (
    FakeXunistater,
    TEST_XUNISTATER_OK_RESPONSE,
)
from passport.backend.library.configurator import Configurator
from passport.backend.logbroker_client.xiva.exceptions import (
    XivaPersistentError,
    XivaRequestError,
    XivaTemporaryError,
)
from passport.backend.logbroker_client.xiva.fake import FakeXiva
from passport.backend.logbroker_client.xiva.handler import (
    MailHandler,
    MailHandlerException,
)
from passport.backend.utils.logging_mock import LoggingMock
import pytest


events_classes = [
    'passport.backend.logbroker_client.core.events.events.AccountGlogoutEvent',
    'passport.backend.logbroker_client.core.events.events.AccountDisableEvent',
    'passport.backend.logbroker_client.core.events.events.SessionKillEvent',
    'passport.backend.logbroker_client.core.events.events.TokenInvalidateEvent',
    'passport.backend.logbroker_client.core.events.events.TokenInvalidateAllEvent',
    'passport.backend.logbroker_client.core.events.events.AccountDefaultAvatarEvent',
    'passport.backend.logbroker_client.core.events.events.AccountKarmaEvent',
]

HEADER_WITH_EVENT_FILE = {
    'sourceid': 'base64:tTOfUD6sTFy9l4a_mIq8WQ',
    'seqno': '509549082',
    'topic': 'rt3.iva--historydb--raw',
    'path': '/var/log/yandex/passport-api/historydb/event.log',
    'server': 'pass-dd-i84.sezam.yandex.net',
    'partition': '7',
    'offset': '535729'
}

HEADER_WITH_AUTH_FILE = {
    'sourceid': 'base64:tTOfUD6sTFy9l4a_mIq8WQ',
    'seqno': '509549082',
    'topic': 'rt3.iva--historydb--raw',
    'path': '/var/log/yandex/passport-api/historydb/auth.log',
    'server': 'pass-dd-i84.sezam.yandex.net',
    'partition': '7',
    'offset': '535729'
}

HEADER_WITH_OAUTH_FILE = {
    'sourceid': 'base64:tTOfUD6sTFy9l4a_mIq8WQ',
    'seqno': '509549082',
    'topic': 'rt3.iva--historydb--raw',
    'path': '/var/log/yandex/passport-api/historydb/oauth.event.log',
    'server': 'pass-dd-i84.sezam.yandex.net',
    'partition': '7',
    'offset': '535729'
}

NO_APPROPRIATE_EVENTS_DATA = \
    "1 1970-01-01T05:01:27.697373+04 43 passport 123456789 info.ena 5 211.212.213.214 33.33.44.55 123142415 - -\n" + \
    "1 2014-09-04T15:34:27.676785+04 DE bb 21181453 - - oauthcheck successful clid=6b01dea51b6b456db5425564228f1abb 83.220.239.240 - - - - -\n" + \
    "1 2014-09-04T15:34:27.679551+04 DE bb 108941866 andkudrus - web ses_update aid=1406012378000:eF922Q:12;ttl=5;host=.yandex.ru; 217.118.95.107 - - - - -\n" + \
    "1 2014-09-04T15:34:27.690270+04 DE bb 46829208 - - oauthcheck successful clid=6b01dea51b6b456db5425564228f1abb 95.108.242.91 - - - - -\n" + \
    "1 2014-09-04T15:34:27.709845+04 DE bb 156487455 - - oauthcheck successful clid=82e7f4a4fbc044078a75c05e86bc9f82 141.101.241.104 - - - - -\n" + \
    "1 2014-09-04T15:34:27.729418+04 DE bb 211249453 - - oauthcheck successful clid=6b01dea51b6b456db5425564228f1abb 2a02:6b8:0:1424::89 - - - - -\n" + \
    "1 2014-09-04T15:34:27.739590+04 DE bb 3703290 - - oauthcheck successful clid=197f6527da4b48a4bde884cd03fca56f 84.52.73.190 - - - - -\n"
GOOD_EVENTS_DATA = \
    "1 1970-01-01T05:01:27.697373+04 43 passport 123456789 info.ena 0 211.212.213.214 33.33.44.55 123142415 - -\n" + \
    "1 1970-01-01T05:01:27.697373+04 43 passport 123456790 info.glogout 3687.69 211.212.213.214 33.33.44.55 123142415 - -\n" + \
    "1 1970-01-01T05:01:27.697373+04 43 passport 123456791 info.karma_full 6100 211.212.213.214 33.33.44.55 123142415 - -\n" + \
    "1 1970-01-01T05:01:27.697373+04 DE bb 123456789 - - oauthcheck ses_kill ssl=1;aid=1409658335000:ea6MJQ:84;ttl=5 95.108.242.91 - - - - -\n" + \
    "1 2014-09-04T15:34:27.676785+04 DE bb 21181453 - - oauthcheck successful clid=6b01dea51b6b456db5425564228f1abb 83.220.239.240 - - - - -\n" + \
    "1 2014-09-04T15:34:27.679551+04 DE bb 108941866 andkudrus - web ses_update aid=1406012378000:eF922Q:12;ttl=5;host=.yandex.ru; 217.118.95.107 - - - - -\n" + \
    "1 2014-09-04T15:34:27.690270+04 DE bb 46829208 - - oauthcheck successful clid=6b01dea51b6b456db5425564228f1abb 95.108.242.91 - - - - -\n" + \
    "1 2014-09-04T15:34:27.709845+04 DE bb 156487455 - - oauthcheck successful clid=82e7f4a4fbc044078a75c05e86bc9f82 141.101.241.104 - - - - -\n" + \
    "1 2014-09-04T15:34:27.729418+04 DE bb 211249453 - - oauthcheck successful clid=6b01dea51b6b456db5425564228f1abb 2a02:6b8:0:1424::89 - - - - -\n" + \
    "2 2016-12-07T16:41:24.496092+03 8E passport 1130000000267581 info.default_avatar 1450/1130000000267581-488529 127.0.0.1 - - - -\n"

GOOD_EVENTS_DATA_SHORT = \
    "1 1970-01-01T05:01:27.697373+04 43 passport 123456789 info.ena 0 211.212.213.214 33.33.44.55 123142415 - -\n"

GOOD_EVENTS_DATA_EMPTY_VALUE = \
    "1 1970-01-01T05:01:27.697373+04 43 passport 123456789 info.glogout - 211.212.213.214 33.33.44.55 123142415 - -\n"

GOOD_OAUTH_EVENTS_DATA = \
    "v=1\ttimestamp=1411519067.325360\tscopes=direct:api,metrika:write,metrika:read\ttarget=token\tclient_id=82e7f4a4fbc044078a75c05e86bc9f82\taction=invalidate\ttoken_id=e959143e2172497b83870bb2d321d7b1\tuid=200670442\n" + \
    "v=1\ttimestamp=1411566122.170788\taction=invalidate\ttarget=user\tuid=118366880\n" + \
    "v=1\ttimestamp=1411518666.641738\tnew_scopes=login:birthday,login:email,login:info\taction=change\told_scopes=login:birthday,login:email,login:info\ttarget=client\tclient_id=932c1723e17844f0a7bfb4119505b8de\told_callback=https://www.grandrio.com/en/social/login/ya\tnew_callback=https://www.grandrio.com/{en|ru}/social/login/ya\n" + \
    "v=1\ttimestamp=1411514215.374172\taction=delete\tscopes=metrika:read\ttarget=client\tclient_id=13da17ca4db24e0b82e30575119115d3\n" + \
    "v=1\ttimestamp=1411514215.374172\taction=delete\tscopes=metrika:read\ttarget=client\tclient_id=13da17ca4db24e0b82e30575119115d3\n" + \
    "v=1\ttimestamp=1411514215.374172\taction=delete\tscopes=metrika:read\ttarget=client\tclient_id=13da17ca4db24e0b82e30575119115d3\n"

GOOD_EVENTS_DATA_YATEAM_MIX = \
    "1 1970-01-01T05:01:27.697373+04 43 passport 123456789 info.glogout 1.1 211.212.213.214 33.33.44.55 123142415 - -\n" + \
    "1 1970-01-01T05:01:27.697373+04 43 passport 1130000000267581 info.glogout 2.2 211.212.213.214 33.33.44.55 123142415 - -\n" + \
    "1 1970-01-01T05:01:27.697373+04 43 passport 1120000000267581 info.glogout 3.3 211.212.213.214 33.33.44.55 123142415 - -\n"


class TestMailHandler(object):
    XIVA_URL = 'http://xiva'
    XIVA_EXTRA_URL = 'http://extra-xiva'
    XIVA_YATEAM_URL = 'http://yateam-xiva'
    XIVA_HUB_URL = 'http://xiva_hub'
    XIVA_STOKEN = 'stoken'
    XIVA_STOKEN_STREAM = 'stoken_stream'
    config = Configurator(
        name='logbroker-client',
        configs=[
            'base.yaml',
            'xiva/base.yaml',
            'xiva/secrets.yaml',
            'xiva/testing.yaml',
            'logging.yaml',
            'xiva/export.yaml',
        ]
    )
    mail_handler = MailHandler(
        config,
        XIVA_URL,
        XIVA_HUB_URL,
        XIVA_STOKEN,
        XIVA_STOKEN_STREAM,
        events_classes,
    )
    mail_handler_with_extra_xiva = MailHandler(
        config,
        XIVA_URL,
        XIVA_HUB_URL,
        XIVA_STOKEN,
        XIVA_STOKEN_STREAM,
        events_classes,
        extra_host=XIVA_EXTRA_URL,
    )

    mail_handler_with_yateam_xiva = MailHandler(
        config,
        XIVA_URL,
        XIVA_HUB_URL,
        XIVA_STOKEN,
        XIVA_STOKEN_STREAM,
        events_classes,
        yateam_host=XIVA_YATEAM_URL,
    )

    def setup_method(self, method):
        self.fake_xiva = FakeXiva()
        self.fake_xiva.start()

    def teardown_method(self, method):
        self.fake_xiva.stop()

    def check_xiva_params(self, uid, event, event_ts, index=0,
                          xiva_url=XIVA_URL, is_stream_send=False, **post_args):
        if is_stream_send:
            url = xiva_url + '/v2/stream_send?token=%s&event=%s' % (self.XIVA_STOKEN_STREAM, event)
        else:
            url = xiva_url + '/v1/send?stoken=%s&uid=%s&event=%s&event_ts=%s' % (
                self.XIVA_STOKEN, uid, event, event_ts,
            )

        self.fake_xiva.requests[index].assert_properties_equal(method='POST', url=url)
        if post_args:
            post_args['name'] = event
            post_args['timestamp'] = event_ts
            if is_stream_send:
                post_args = dict(payload=dict(post_args, uid=str(uid)))
            assert json.loads(self.fake_xiva.requests[index].post_args) == post_args

    def test_log_and_push_metrics(self):
        self.config.set_as_passport_settings()

        self.mail_handler = MailHandler(
            self.config,
            self.XIVA_URL,
            self.XIVA_HUB_URL,
            self.XIVA_STOKEN,
            self.XIVA_STOKEN_STREAM,
            events_classes,
            log_metrics=True,
            push_metrics_to_xunistater=True,
        )

        with LoggingMock() as log:
            with FakeXunistater() as fake_xunistater:
                fake_xunistater.set_response_value('', json.dumps(TEST_XUNISTATER_OK_RESPONSE))
                self.fake_xiva.set_xiva_response_value('', 200)
                self.mail_handler.process(HEADER_WITH_EVENT_FILE, GOOD_EVENTS_DATA)

        assert len(fake_xunistater.requests) == 1
        fake_xunistater.requests[0].assert_properties_equal(
            url='http://localhost:10296/xpush',
            method='POST',
            post_args=json.dumps(
                {
                    "xiva.entries.pass-dd-i84.sezam.yandex.net.var/log/yandex/passport-api/historydb/event.log_dmmm": {
                        "value": 4,
                    },
                    "xiva.entries.total.var/log/yandex/passport-api/historydb/event.log_dmmm": {
                        "value": 4,
                    },
                },
                sort_keys=True,
            ),
        )

        assert log.getLogger('logbroker_client.metrics').entries == [
            ({'file': '/var/log/yandex/passport-api/historydb/event.log',
              'handler_name': 'xiva',
              u'metric:xiva.entries.pass-dd-i84.sezam.yandex.net.var/log/yandex/passport-api/historydb/event.log': 4,
              u'metric:xiva.entries.total.var/log/yandex/passport-api/historydb/event.log': 4,
              'server': 'pass-dd-i84.sezam.yandex.net'},
             'INFO',
             None,
             None),
        ]

    def test_mail_handler_process_messages(self):
        self.fake_xiva.set_xiva_response_value('', 200)
        self.mail_handler.process(HEADER_WITH_EVENT_FILE, GOOD_EVENTS_DATA)
        # Походы в v1/send
        self.check_xiva_params(123456790, 'account.invalidate', 3687, index=2, comment='account.glogout')
        self.check_xiva_params(
            123456791,
            'account.changed',
            3687,
            index=4,
            comment='karma.changed',
            is_stream_send=True,
            karma='100',
            karma_status='6',
        )
        self.check_xiva_params(
            1130000000267581,
            'account.changed',
            1481118084,
            index=5,
            comment='account.default_avatar_changed',
        )
        # Походы в v2/stream_send
        self.check_xiva_params(123456790, 'account.invalidate', 3687, index=3,
                               comment='account.glogout', is_stream_send=True)
        # В stream_send не отправляем событие с аватаркой
        assert len(self.fake_xiva.requests) == 6

    def test_mail_handler_process_messages_with_extra_xiva_host(self):
        self.fake_xiva.set_xiva_response_value('', 200)
        self.mail_handler_with_extra_xiva.process(HEADER_WITH_EVENT_FILE, GOOD_EVENTS_DATA_SHORT)
        assert len(self.fake_xiva.requests) == 4
        call_checker = partial(
            self.check_xiva_params,
            123456789,
            'account.invalidate',
            3687,
            comment='account.disable',
        )
        call_checker(index=0)
        call_checker(index=1, is_stream_send=True)
        call_checker(index=2, xiva_url=self.XIVA_EXTRA_URL)
        call_checker(index=3, xiva_url=self.XIVA_EXTRA_URL, is_stream_send=True)

    def test_mail_handler_process_messages_with_yateam_xiva_host(self):
        self.fake_xiva.set_xiva_response_value('', 200)
        self.mail_handler_with_yateam_xiva.process(HEADER_WITH_EVENT_FILE, GOOD_EVENTS_DATA_YATEAM_MIX)
        assert len(self.fake_xiva.requests) == 6

        call_checker = partial(
            self.check_xiva_params,
            event='account.invalidate',
            comment='account.glogout',
        )
        call_checker(uid=123456789, event_ts=1, index=0)
        call_checker(uid=123456789, event_ts=1, index=1, is_stream_send=True)
        call_checker(uid=1130000000267581, event_ts=2, index=2)
        call_checker(uid=1130000000267581, event_ts=2, index=3, is_stream_send=True)
        # yateam
        call_checker(uid=1120000000267581, event_ts=3, index=4, xiva_url=self.XIVA_YATEAM_URL)
        call_checker(uid=1120000000267581, event_ts=3, index=5, is_stream_send=True, xiva_url=self.XIVA_YATEAM_URL)

    def test_mail_handler_process_message_with_empty_value_host(self):
        self.fake_xiva.set_xiva_response_value('', 200)
        self.mail_handler.process(HEADER_WITH_EVENT_FILE, GOOD_EVENTS_DATA_EMPTY_VALUE)
        assert len(self.fake_xiva.requests) == 2
        call_checker = partial(
            self.check_xiva_params,
            123456789,
            'account.invalidate',
            3687,
            comment='account.glogout',
        )
        call_checker(index=0)
        call_checker(index=1, is_stream_send=True)

    def test_mail_handler_process_messages_no_events(self):
        self.fake_xiva.set_xiva_response_value('', 200)
        self.mail_handler.process(HEADER_WITH_EVENT_FILE, NO_APPROPRIATE_EVENTS_DATA)
        assert len(self.fake_xiva.requests) == 0

    def test_mail_handler_process_response_client_error(self):
        self.fake_xiva.set_xiva_response_side_effect(XivaTemporaryError())
        with pytest.raises(MailHandlerException):
            self.mail_handler.process(HEADER_WITH_EVENT_FILE, GOOD_EVENTS_DATA)

    def test_mail_handler_process_pass_400_response_client_error(self):
        self.fake_xiva.set_xiva_response_side_effect(XivaPersistentError())
        self.mail_handler.process(HEADER_WITH_EVENT_FILE, GOOD_EVENTS_DATA)
        self.check_xiva_params(123456789, 'account.invalidate', 3687, index=0)
        self.check_xiva_params(123456790, 'account.invalidate', 3687, index=1)

    def test_mail_handler_process_request_client_error(self):
        self.fake_xiva.set_xiva_response_side_effect(XivaRequestError())

        with pytest.raises(MailHandlerException):
            self.mail_handler.process(HEADER_WITH_EVENT_FILE, GOOD_EVENTS_DATA)
