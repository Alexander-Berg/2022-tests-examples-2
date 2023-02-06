# -*- coding: utf-8 -*-
import json

from passport.backend.core.builders.xunistater.faker.fake_xunistater import (
    FakeXunistater,
    TEST_XUNISTATER_OK_RESPONSE,
)
from passport.backend.library.configurator import Configurator
from passport.backend.logbroker_client.oauth.exceptions import (
    OAuthPersistentError,
    OAuthTemporaryError,
)
from passport.backend.logbroker_client.oauth.fake import FakeOAuth
from passport.backend.logbroker_client.oauth.handler import (
    OAuthHandler,
    OAuthHandlerException,
)
from passport.backend.utils.logging_mock import LoggingMock
import pytest


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

GOOD_EVENTS_DATA = \
    "1 1970-01-01T05:01:27.697373+04 43 passport 123456789 info.ena 5 211.212.213.214 33.33.44.55 123142415 - -\n" + \
    "1 2014-09-04T15:34:27.676785+04 DE bb 21181453 - - oauthcheck successful clid=6b01dea51b6b456db5425564228f1abb;rf=1;tokid=123456; 83.220.239.240 - - - - -\n" + \
    "1 2014-09-04T15:34:27.679551+04 DE bb 108941866 andkudrus - web ses_update aid=1406012378000:eF922Q:12;ttl=5;host=.yandex.ru; 217.118.95.107 - - - - -\n" + \
    "1 2014-09-04T15:34:27.690270+04 DE bb 46829208 - - oauthcheck successful clid=6b01dea51b6b456db5425564228f1abb 95.108.242.91 - - - - -\n" + \
    "1 2014-09-04T15:34:27.709845+04 DE bb 156487455 - - oauthcheck successful clid=82e7f4a4fbc044078a75c05e86bc9f82 141.101.241.104 - - - - -\n" + \
    "1 2014-09-04T15:34:27.729418+04 DE bb 211249453 - - oauthcheck successful clid=6b01dea51b6b456db5425564228f1abb 2a02:6b8:0:1424::89 - - - - -\n" + \
    "1 2014-09-04T15:34:27.739590+04 DE bb 3703290 - - oauthcheck successful clid=197f6527da4b48a4bde884cd03fca56f 84.52.73.190 - - - - -\n"

NO_APPROPRIATE_EVENTS_DATA = \
    "1 1970-01-01T05:01:27.697373+04 43 passport 123456789 info.ena 0 211.212.213.214 33.33.44.55 123142415 - -\n" + \
    "1 1970-01-01T05:01:27.697373+04 43 passport 123456790 info.glogout 3687.69 211.212.213.214 33.33.44.55 123142415 - -\n" + \
    "1 1970-01-01T05:01:27.697373+04 DE bb 123456789 - - oauthcheck ses_kill ssl=1;aid=1409658335000:ea6MJQ:84;ttl=5 95.108.242.91 - - - - -\n" + \
    "1 2014-09-04T15:34:27.676785+04 DE bb 21181453 - - oauthcheck successful clid=6b01dea51b6b456db5425564228f1abb 83.220.239.240 - - - - -\n" + \
    "1 2014-09-04T15:34:27.679551+04 DE bb 108941866 andkudrus - web ses_update aid=1406012378000:eF922Q:12;ttl=5;host=.yandex.ru; 217.118.95.107 - - - - -\n" + \
    "1 2014-09-04T15:34:27.690270+04 DE bb 46829208 - - oauthcheck successful clid=6b01dea51b6b456db5425564228f1abb 95.108.242.91 - - - - -\n" + \
    "1 2014-09-04T15:34:27.709845+04 DE bb 156487455 - - oauthcheck successful clid=82e7f4a4fbc044078a75c05e86bc9f82 141.101.241.104 - - - - -\n" + \
    "1 2014-09-04T15:34:27.729418+04 DE bb 211249453 - - oauthcheck successful clid=6b01dea51b6b456db5425564228f1abb 2a02:6b8:0:1424::89 - - - - -\n"

GOOD_OAUTH_EVENTS_DATA = \
    "v=1\ttimestamp=1411519067.325360\tscopes=direct:api,metrika:write,metrika:read\ttarget=token\tclient_id=82e7f4a4fbc044078a75c05e86bc9f82\taction=invalidate\ttoken_id=e959143e2172497b83870bb2d321d7b1\tuid=200670442\n" + \
    "v=1\ttimestamp=1411566122.170788\taction=invalidate\ttarget=user\tuid=118366880\n" + \
    "v=1\ttimestamp=1411518666.641738\tnew_scopes=login:birthday,login:email,login:info\taction=change\told_scopes=login:birthday,login:email,login:info\ttarget=client\tclient_id=932c1723e17844f0a7bfb4119505b8de\told_callback=https://www.grandrio.com/en/social/login/ya\tnew_callback=https://www.grandrio.com/{en|ru}/social/login/ya\n" + \
    "v=1\ttimestamp=1411514215.374172\taction=delete\tscopes=metrika:read\ttarget=client\tclient_id=13da17ca4db24e0b82e30575119115d3\n" + \
    "v=1\ttimestamp=1411514215.374172\taction=delete\tscopes=metrika:read\ttarget=client\tclient_id=13da17ca4db24e0b82e30575119115d3\n" + \
    "v=1\ttimestamp=1411514215.374172\taction=delete\tscopes=metrika:read\ttarget=client\tclient_id=13da17ca4db24e0b82e30575119115d3\n"


class TestOAuthHandler(object):
    OAUTH_URL = 'http://oauth'
    OAUTH_CONSUMER = 'passport-lbc'

    oauth_handler = OAuthHandler(
        Configurator(
            name='logbroker-client',
            configs=[
                'base.yaml',
                'oauth/base.yaml',
                'oauth/testing.yaml',
                'logging.yaml',
                'export.yaml',
            ]
        ),
        OAUTH_URL,
    )

    def setup_method(self, method):
        self.fake_oauth = FakeOAuth()
        self.fake_oauth.start()

    def teardown_method(self, method):
        self.fake_oauth.stop()

    def check_oauth_params(self, token_id, index=0):
        self.fake_oauth.requests[index].assert_properties_equal(
            method='POST',
            url=self.OAUTH_URL + '/api/1/token/refresh?consumer=%s' % self.OAUTH_CONSUMER,
            post_args={'token_id': token_id},
        )

    def test_log_and_push_metrics(self):
        config = Configurator(
            name='logbroker-client',
            configs=[
                'base.yaml',
                'oauth/base.yaml',
                'oauth/testing.yaml',
                'logging.yaml',
                'export.yaml',
            ]
        )
        config.set_as_passport_settings()

        handler = OAuthHandler(
            config,
            self.OAUTH_URL,
            log_metrics=True,
            push_metrics_to_xunistater=True,
        )

        self.fake_oauth.set_oauth_response_value(
            json.dumps({'status': 'ok'}),
            200,
        )

        with LoggingMock() as log:
            with FakeXunistater() as fake_xunistater:
                fake_xunistater.set_response_value('', json.dumps(TEST_XUNISTATER_OK_RESPONSE))
                handler.process(HEADER_WITH_AUTH_FILE, GOOD_EVENTS_DATA)

        assert len(fake_xunistater.requests) == 1
        fake_xunistater.requests[0].assert_properties_equal(
            url='http://localhost:10293/xpush',
            method='POST',
            post_args=json.dumps(
                {
                    "oauth.entries.pass-dd-i84.sezam.yandex.net.var/log/yandex/passport-api/historydb/auth.log_dmmm": {
                        "value": 1,
                    },
                    "oauth.entries.total.var/log/yandex/passport-api/historydb/auth.log_dmmm": {
                        "value": 1,
                    },
                },
                sort_keys=True,
            ),
        )

        assert log.getLogger('logbroker_client.metrics').entries == [
            ({'file': '/var/log/yandex/passport-api/historydb/auth.log',
              'handler_name': 'oauth',
              u'metric:oauth.entries.pass-dd-i84.sezam.yandex.net.var/log/yandex/passport-api/historydb/auth.log': 1,
              u'metric:oauth.entries.total.var/log/yandex/passport-api/historydb/auth.log': 1,
              'server': 'pass-dd-i84.sezam.yandex.net'},
             'INFO',
             None,
             None),
        ]

    def test_oauth_handler_process_messages(self):
        self.fake_oauth.set_oauth_response_value(
            json.dumps({'status': 'ok'}),
            200,
        )
        self.oauth_handler.process(HEADER_WITH_AUTH_FILE, GOOD_EVENTS_DATA)
        # не проверяем все ивенты, хватит только одного
        self.check_oauth_params('123456')

    def test_oauth_handler_process_messages_no_events(self):
        self.fake_oauth.set_oauth_response_value('', 200)
        self.oauth_handler.process(HEADER_WITH_EVENT_FILE, NO_APPROPRIATE_EVENTS_DATA)
        assert len(self.fake_oauth.requests) == 0

    def test_oauth_handler_process_response_temporary_client_error(self):
        self.fake_oauth.set_oauth_response_side_effect(OAuthTemporaryError())
        with pytest.raises(OAuthHandlerException):
            self.oauth_handler.process(HEADER_WITH_AUTH_FILE, GOOD_EVENTS_DATA)

    def test_mail_handler_process_reponse_persistent__client_error(self):
        self.fake_oauth.set_oauth_response_side_effect(OAuthPersistentError)
        with pytest.raises(OAuthHandlerException):
            self.oauth_handler.process(HEADER_WITH_AUTH_FILE, GOOD_EVENTS_DATA)
