# -*- coding: utf-8 -*-
import json
import re

from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_userinfo_response,
    FakeBlackbox,
)
from passport.backend.core.builders.datasync_api.exceptions import DatasyncApiPermanentError
from passport.backend.core.builders.datasync_api.faker.fake_disk_api import (
    FakeDiskApi,
    plus_subscribe_created_response,
    plus_subscribe_removed_response,
)
from passport.backend.core.builders.edadeal.faker import FakeEdadealApi
from passport.backend.core.builders.xunistater.faker.fake_xunistater import (
    FakeXunistater,
    TEST_XUNISTATER_OK_RESPONSE,
)
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_CLIENT_ID,
    TEST_CLIENT_ID_2,
    TEST_TICKET,
)
from passport.backend.library.configurator import Configurator
from passport.backend.logbroker_client.account_events.exceptions import NotifyRequestError
from passport.backend.logbroker_client.account_events.handler import (
    EventsHandler,
    ServiceHandlerException,
)
from passport.backend.logbroker_client.account_events.test.fake import FakeNotify
from passport.backend.utils.logging_mock import LoggingMock
import pytest
from six.moves.urllib.parse import urlparse

from .utils import get_headers_event_file


NO_APPROPRIATE_EVENTS_DATA = \
    "1 1970-01-01T05:01:27.697373+04 43 passport 123456789 info.ena 5 211.212.213.214 33.33.44.55 123142415 - -\n" + \
    "1 2014-09-04T15:34:27.676785+04 DE bb 21181453 - - oauthcheck successful clid=6b01dea51b6b456db5425564228f1abb 83.220.239.240 - - - - -\n" + \
    "1 2014-09-04T15:34:27.679551+04 DE bb 108941866 andkudrus - web ses_update aid=1406012378000:eF922Q:12;ttl=5;host=.yandex.ru; 217.118.95.107 - - - - -\n" + \
    "1 2014-09-04T15:34:27.690270+04 DE bb 46829208 - - oauthcheck successful clid=6b01dea51b6b456db5425564228f1abb 95.108.242.91 - - - - -\n" + \
    "1 2014-09-04T15:34:27.709845+04 DE bb 156487455 - - oauthcheck successful clid=82e7f4a4fbc044078a75c05e86bc9f82 141.101.241.104 - - - - -\n" + \
    "1 2014-09-04T15:34:27.729418+04 DE bb 211249453 - - oauthcheck successful clid=6b01dea51b6b456db5425564228f1abb 2a02:6b8:0:1424::89 - - - - -\n" + \
    "1 2014-09-04T15:34:27.739590+04 DE bb 3703290 - - oauthcheck successful clid=197f6527da4b48a4bde884cd03fca56f 84.52.73.190 - - - - -\n"

GOOD_EVENTS_DATA = \
    "1 1970-01-01T05:01:27.697373+04 83 passport 139883646 sid.rm 5|leonid-kolomiets 37.140.161.69 - - - -\n" + \
    "1 1970-01-01T05:01:27.697373+04 83 passport 139883646 sid.rm 44|leonid-kolomiets 37.140.161.69 - - - -\n" + \
    "1 1970-01-01T05:01:27.697373+04 83 passport 139883646 sid.rm 59|leonid-kolomiets 37.140.161.69 - - - -\n" + \
    "1 1970-01-01T05:01:27.697373+04 43 passport 123456789 info.ena 0 211.212.213.214 33.33.44.55 123142415 - -\n" + \
    "1 1970-01-01T05:01:27.697373+04 9 passport 123456789 info.totp enabled 127.67.127.221 - - - -\n" + \
    "1 1970-01-01T05:01:27.697373+04 43 passport 123456789 info.glogout 3687.69 211.212.213.214 33.33.44.55 123142415 - -\n" + \
    "1 1970-01-01T05:01:27.697373+04 9 passport 123456789 info.totp disabled 127.67.127.221 - - - -\n" + \
    "1 1970-01-01T05:01:27.697373+04 9 passport 123456789 plus.enabled 0 127.67.127.221 - - - -\n" + \
    "1 1970-01-01T05:01:27.697373+04 DE bb 123456789 - - oauthcheck ses_kill ssl=1;aid=1409658335000:ea6MJQ:84;ttl=5 95.108.242.91 - - - - -\n" + \
    "1 2014-09-04T15:34:27.676785+04 DE bb 21181453 - - oauthcheck successful clid=6b01dea51b6b456db5425564228f1abb 83.220.239.240 - - - - -\n" + \
    "1 2014-09-04T15:34:27.679551+04 DE bb 108941866 andkudrus - web ses_update aid=1406012378000:eF922Q:12;ttl=5;host=.yandex.ru; 217.118.95.107 - - - - -\n" + \
    "1 2014-09-04T15:34:27.690270+04 DE bb 46829208 - - oauthcheck successful clid=6b01dea51b6b456db5425564228f1abb 95.108.242.91 - - - - -\n" + \
    "1 2014-09-04T15:34:27.709845+04 DE bb 156487455 - - oauthcheck successful clid=82e7f4a4fbc044078a75c05e86bc9f82 141.101.241.104 - - - - -\n" + \
    "1 2014-09-04T15:34:27.729418+04 DE bb 211249453 - - oauthcheck successful clid=6b01dea51b6b456db5425564228f1abb 2a02:6b8:0:1424::89 - - - - -\n" + \
    "2 2019-09-26T16:41:24.496092+03 8E passport 123456789 info.default_avatar 1450/1130000000267581-488529 127.0.0.1 - - - -\n" + \
    "2 2018-05-25T18:46:29.552568+03 9 passport 4012435800 info.disabled_status 2 37.9.104.22 - - - -"

PLUS_SUBSCRIBE_EVENTS_DATA = "1 1970-01-01T05:01:27.697373+04 9 passport 123456789 plus.enabled 1 127.67.127.221 - - - -\n"
PLUS_UNSUBSCRIBE_EVENTS_DATA = "1 1970-01-01T05:01:27.697373+04 9 passport 123456789 plus.enabled 0 127.67.127.221 - - - -\n"

GOOD_OAUTH_EVENTS_DATA = \
    "v=1\ttimestamp=1411519067.325360\tscopes=direct:api,metrika:write,metrika:read\ttarget=token\tclient_id=82e7f4a4fbc044078a75c05e86bc9f82\taction=invalidate\ttoken_id=e959143e2172497b83870bb2d321d7b1\tuid=200670442\n" + \
    "v=1\ttimestamp=1411566122.170788\taction=invalidate\ttarget=user\tuid=118366880\n" + \
    "v=1\ttimestamp=1411518666.641738\tnew_scopes=login:birthday,login:email,login:info\taction=change\told_scopes=login:birthday,login:email,login:info\ttarget=client\tclient_id=932c1723e17844f0a7bfb4119505b8de\told_callback=https://www.grandrio.com/en/social/login/ya\tnew_callback=https://www.grandrio.com/{en|ru}/social/login/ya\n" + \
    "v=1\ttimestamp=1411514215.374172\taction=delete\tscopes=metrika:read\ttarget=client\tclient_id=13da17ca4db24e0b82e30575119115d3\n" + \
    "v=1\ttimestamp=1411514215.374172\taction=delete\tscopes=metrika:read\ttarget=client\tclient_id=13da17ca4db24e0b82e30575119115d3\n" + \
    "v=1\ttimestamp=1411514215.374172\taction=delete\tscopes=metrika:read\ttarget=client\tclient_id=13da17ca4db24e0b82e30575119115d3\n"


TEST_UID = 123456789


class LBCFakeDiskApi(FakeDiskApi):
    @staticmethod
    def parse_method_from_request(http_method, url, data, headers=None):
        parsed = urlparse(url)
        url_path = parsed.path
        if url_path == '/v1/disk':
            return 'disk_info'
        elif url_path == '/v1/disk/billing/subscriptions':
            return 'billing_subscriptions'
        elif re.match(r'/v1/disk/partners/.+?/services/remove_by_product', url_path):
            return 'plus_unsubscribe'
        elif re.match(r'/v1/disk/partners/.+?/services', url_path):
            return 'plus_subscribe'


class TestEventsHandler(object):
    services = {
        'disk': {
            'notifier': 'passport.backend.logbroker_client.account_events.notify.DiskNotifyClient',
            'sid': 59,
            'url': 'http://disk',
            'events': [
                'passport.backend.logbroker_client.account_events.events.AccountUnsubscribeDiskEvent',
                'passport.backend.logbroker_client.core.events.events.AccountDisableEvent',
                'passport.backend.logbroker_client.core.events.events.AccountEnableEvent',
                'passport.backend.logbroker_client.account_events.events.AccountOtpEnabledEvent',
                'passport.backend.logbroker_client.account_events.events.AccountOtpDisabledEvent',
            ]
        },
        "disk_2": {
            "notifier": "passport.backend.logbroker_client.account_events.notify.DiskNotifyClient",
            "sid": 59,
            "url": "http://disk_2",
            "events": [
                "passport.backend.logbroker_client.account_events.events.AccountDisableEvent",
                "passport.backend.logbroker_client.account_events.events.AccountEnableEvent",
                "passport.backend.logbroker_client.account_events.events.AccountRemovalDisableEvent"
            ]
        },
        'plus_notifiers': {
            'notifier': 'passport.backend.logbroker_client.account_events.notify.PlusNotifyClient',
            'url': 'http://plus_notifiers',
            'events': [
                'passport.backend.logbroker_client.account_events.events.AccountPlusEvent',
            ]
        },
    }
    SIDS = [5, 59]

    def setup_method(self, method):
        self.fake_notify = FakeNotify()
        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.set_data(
            fake_tvm_credentials_data(
                ticket_data={
                    str(TEST_CLIENT_ID): {
                        'alias': 'passport',
                        'ticket': TEST_TICKET,
                    },
                    str(TEST_CLIENT_ID_2): {
                        'alias': 'datasync_api',
                        'ticket': TEST_TICKET,
                    },
                }
            )
        )
        self.fake_blackbox = FakeBlackbox()
        self.fake_disk_api = LBCFakeDiskApi()
        self.fake_edadeal_api = FakeEdadealApi()

        self.patches = [
            self.fake_tvm_credentials_manager,
            self.fake_notify,
            self.fake_blackbox,
            self.fake_disk_api,
            self.fake_edadeal_api,
        ]
        for patch in self.patches:
            patch.start()

        self.config = Configurator(
            name='logbroker-client',
            configs=[
                'base.yaml',
                'account-events/base.yaml',
                'account-events/secrets.yaml',
                'account-events/testing.yaml',
                'logging.yaml',
                'account-events/export.yaml',
            ]
        )

        self.handler = EventsHandler(
            self.config, False,
            'TestEventsHandler',
            'TestEventsHandler',
            'TestEventsHandler',
            'test-token',
            self.services,
        )

    def teardown_method(self, method):
        for patch in reversed(self.patches):
            patch.stop()

    def check_notify_params(self, service, uid, event, event_ts, index=0):
        data = {
            'v': 1,
            'uid': uid,
            'event': event,
            'timestamp': event_ts,
        }
        self.fake_notify.requests[index].assert_properties_equal(
            method='POST',
            url='http://%s' % service,
            post_args=json.dumps(data),
        )

    def check_disk_notify_params(self, service, uid, event, event_ts, index=0):
        data = {
            'v': 1,
            'uid': uid,
            'event': event,
            'timestamp': event_ts,
        }
        self.fake_disk_api.requests[index].assert_properties_equal(
            method='POST',
            url='http://%s' % service,
            post_args=json.dumps(data),
        )

    def check_disk_unsubscribe_request(self, index=0):
        self.fake_disk_api.requests[index].assert_properties_equal(
            method='DELETE',
            url='/v1/disk/partners/yandex_plus/services/remove_by_product?product_id=yandex_plus_10gb',
        )

    def check_disk_subscribe_request(self, index=0):
        self.fake_disk_api.requests[index].assert_properties_equal(
            method='POST',
            url='/v1/disk/partners/yandex_plus/services?product_id=yandex_plus_10gb',
        )

    def check_edadeal_request(self, is_active=True):
        assert len(self.fake_edadeal_api.requests) == 1
        print(self.fake_edadeal_api.requests[0])
        self.fake_edadeal_api.requests[0].assert_properties_equal(
            method='POST',
            url='/auth/v1/plus',
            json_data={'yuid': TEST_UID, 'is_active': is_active},
            headers={
                'Authorization': 'Bearer %s' % 'test-token',
                'Content-Type': 'application/json',
            },
        )

    def test_log_and_push_metrics(self):
        self.config = Configurator(
            name='logbroker-client',
            configs=[
                'base.yaml',
                'account-events/base.yaml',
                'account-events/secrets.yaml',
                'account-events/testing.yaml',
                'logging.yaml',
                'account-events/export.yaml',
            ],
        )
        self.config.set_as_passport_settings()

        self.handler = EventsHandler(
            self.config,
            False,
            'TestEventsHandler',
            'TestEventsHandler',
            'TestEventsHandler',
            'test-token',
            self.services,
            log_metrics=True,
            push_metrics_to_xunistater=True,
        )

        self.fake_blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                subscribed_to=self.SIDS,
                attributes={'160': '0'},
            ),
        )
        self.fake_notify.set_notify_response_value('{"status": "ok"}', 200)
        self.fake_disk_api.set_response_value_without_method('{"status": "ok"}', 200)
        self.fake_disk_api.set_response_value(
            'plus_unsubscribe',
            plus_subscribe_removed_response(),
            status=204,
        )
        self.fake_edadeal_api.set_response_value('update_plus_status', '')
        with LoggingMock() as log:
            with FakeXunistater() as fake_xunistater:
                fake_xunistater.set_response_value('', json.dumps(TEST_XUNISTATER_OK_RESPONSE))
                self.handler.process(get_headers_event_file('event'), GOOD_EVENTS_DATA)

        assert len(fake_xunistater.requests) == 1
        fake_xunistater.requests[0].assert_properties_equal(
            url='http://localhost:10291/xpush',
            method='POST',
            post_args=json.dumps(
                {
                    'account_events.entries._.var/log/yandex/passport-api/historydb/event.log_dmmm': {
                        'value': 6,
                    },
                    'account_events.entries.total.var/log/yandex/passport-api/historydb/event.log_dmmm': {
                        'value': 6,
                    },
                },
                sort_keys=True,
            ),
        )

        assert log.getLogger('logbroker_client.metrics').entries == [
            ({'file': '/var/log/yandex/passport-api/historydb/event.log',
              'handler_name': 'account_events',
              u'metric:account_events.entries._.var/log/yandex/passport-api/historydb/event.log': 6,
              u'metric:account_events.entries.total.var/log/yandex/passport-api/historydb/event.log': 6,
              'server': '_'},
             'INFO',
             None,
             None),
        ]

    def test_handler_process_messages(self):
        self.handler = EventsHandler(
            Configurator(
                name='logbroker-client',
                configs=[
                    'base.yaml',
                    'account-events/base.yaml',
                    'account-events/secrets.yaml',
                    'account-events/testing.yaml',
                    'logging.yaml',
                    'account-events/export.yaml',
                ]
            ),
            False,
            'TestEventsHandler',
            'TestEventsHandler',
            'TestEventsHandler',
            'test-token',
            self.services,
        )
        self.fake_blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                subscribed_to=self.SIDS,
                attributes={'160': '0'},
            ),
        )
        self.fake_notify.set_notify_response_value('{"status": "ok"}', 200)
        self.fake_disk_api.set_response_value_without_method('{"status": "ok"}', 200)
        self.fake_disk_api.set_response_value(
            'plus_unsubscribe',
            plus_subscribe_removed_response(),
            status=204,
        )
        self.fake_edadeal_api.set_response_value('update_plus_status', '')
        with LoggingMock():
            self.handler.process(get_headers_event_file('event'), GOOD_EVENTS_DATA)

        assert len(self.fake_disk_api.requests) == 6
        self.check_disk_unsubscribe_request(index=5)
        self.check_edadeal_request(is_active=False)

        # не проверяем все ивенты, хватит только одного
        self.check_disk_notify_params('disk', 123456789, 'account.changed', 3687, index=2)
        self.check_disk_notify_params('disk', 123456789, 'account.otp_enabled', 3687, index=3)
        self.check_disk_notify_params('disk', 123456789, 'account.otp_disabled', 3687, index=4)

    def test_handler_process_messages_filter_services(self):
        self.fake_blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                subscribed_to=[5],
            ),
        )
        self.fake_notify.set_notify_response_value('{"status": "ok"}', 200)
        self.fake_disk_api.set_response_value_without_method('{"status": "ok"}', 200)
        self.fake_disk_api.set_response_value(
            'plus_unsubscribe',
            plus_subscribe_removed_response(),
            status=204,
        )
        self.fake_edadeal_api.set_response_value('update_plus_status', '')
        self.handler.process(get_headers_event_file('event'), GOOD_EVENTS_DATA)

        assert len(self.fake_disk_api.requests) == 2
        self.check_disk_unsubscribe_request(index=1)
        self.check_edadeal_request(is_active=False)
        self.check_disk_notify_params('disk', 139883646, 'account.changed', 3687, index=0)

    def test_handler_process_messages_no_events(self):
        self.fake_notify.set_notify_response_value('{"status": "ok"}', 200)
        self.fake_blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                subscribed_to=self.SIDS,
            ),
        )
        self.handler.process(get_headers_event_file('event'), NO_APPROPRIATE_EVENTS_DATA)
        assert len(self.fake_notify.requests) == 0
        assert len(self.fake_disk_api.requests) == 0
        assert len(self.fake_edadeal_api.requests) == 0

    def test_plus_subscribe_events(self):
        self.fake_blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                subscribed_to=self.SIDS,
                attributes={'160': '1'},
            ),
        )
        self.fake_disk_api.set_response_value(
            'plus_subscribe',
            plus_subscribe_created_response(),
            status=201,
        )
        self.fake_edadeal_api.set_response_value('update_plus_status', '')
        self.handler.process(get_headers_event_file('event'), PLUS_SUBSCRIBE_EVENTS_DATA)
        assert len(self.fake_notify.requests) == 0
        self.check_disk_subscribe_request()
        self.check_edadeal_request()

    def test_plus_unsubscribe_events(self):
        self.fake_blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                subscribed_to=self.SIDS,
                attributes={'160': '0'},
            ),
        )
        self.fake_disk_api.set_response_value(
            'plus_unsubscribe',
            plus_subscribe_removed_response(),
            status=204,
        )
        self.fake_edadeal_api.set_response_value('update_plus_status', '')
        self.handler.process(get_headers_event_file('event'), PLUS_SUBSCRIBE_EVENTS_DATA)
        assert len(self.fake_notify.requests) == 0
        self.check_disk_unsubscribe_request()
        self.check_edadeal_request(is_active=False)

    def test_plus_subscribe_events_with_empty_blackbox(self):
        self.fake_blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                subscribed_to=self.SIDS,
            ),
        )
        self.fake_disk_api.set_response_value(
            'plus_unsubscribe',
            plus_subscribe_removed_response(),
            status=204,
        )
        self.fake_edadeal_api.set_response_value('update_plus_status', '')
        self.handler.process(get_headers_event_file('event'), PLUS_SUBSCRIBE_EVENTS_DATA)
        assert len(self.fake_notify.requests) == 0
        self.check_disk_unsubscribe_request()
        self.check_edadeal_request(is_active=False)

    def test_handler_process_deleted_account_ok(self):
        self.fake_blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=None),
        )
        self.fake_notify.set_notify_response_value('{"status": "ok"}', 200)
        self.fake_disk_api.set_response_value(
            'plus_unsubscribe',
            plus_subscribe_removed_response(),
            status=204,
        )
        self.fake_disk_api.set_response_value_without_method('{"status": "ok"}', 200)
        self.fake_edadeal_api.set_response_value('update_plus_status', '')
        self.handler.process(get_headers_event_file('event'), GOOD_EVENTS_DATA)

        assert len(self.fake_disk_api.requests) == 2
        self.check_disk_unsubscribe_request(index=1)
        self.check_edadeal_request(is_active=False)
        self.check_disk_notify_params('disk', 139883646, 'account.changed', 3687, index=0)

    def test_handler_process_invalid_response_client_error(self):
        self.fake_blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                subscribed_to=self.SIDS,
            ),
        )
        self.fake_notify.set_notify_response_value('invalid', 200)
        self.fake_disk_api.set_response_value(
            'plus_subscribe',
            plus_subscribe_created_response(),
            status=201,
        )
        self.fake_edadeal_api.set_response_value('update_plus_status', '')
        with pytest.raises(ServiceHandlerException):
            self.handler.process(get_headers_event_file('event'), GOOD_EVENTS_DATA)
        assert len(self.fake_edadeal_api.requests) == 0

    def test_handler_process_pass_400_response_client_error(self):
        self.fake_blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                subscribed_to=self.SIDS,
            ),
        )
        self.fake_notify.set_notify_response_value('{"status": "ok"}', 400)
        with pytest.raises(ServiceHandlerException):
            self.handler.process(get_headers_event_file('event'), GOOD_EVENTS_DATA)

    def test_handler_process_pass_500_response_client_error(self):
        self.fake_blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                subscribed_to=self.SIDS,
            ),
        )
        self.fake_notify.set_notify_response_value('{"status": "ok"}', 500)
        with pytest.raises(ServiceHandlerException):
            self.handler.process(get_headers_event_file('event'), GOOD_EVENTS_DATA)

    def test_handler_process_request_client_error(self):
        self.fake_blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                subscribed_to=self.SIDS,
            ),
        )
        self.fake_notify.set_notify_response_side_effect(NotifyRequestError())

        with pytest.raises(ServiceHandlerException):
            self.handler.process(get_headers_event_file('event'), GOOD_EVENTS_DATA)

    def test_disk_plus_client_error(self):
        self.fake_blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                subscribed_to=self.SIDS,
            ),
        )
        self.fake_disk_api.set_response_side_effect('plus_unsubscribe', DatasyncApiPermanentError())
        self.fake_edadeal_api.set_response_value('update_plus_status', '')
        with pytest.raises(ServiceHandlerException):
            self.handler.process(get_headers_event_file('event'), GOOD_EVENTS_DATA)
        assert len(self.fake_edadeal_api.requests) == 0
