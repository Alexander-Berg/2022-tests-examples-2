# -*- coding: utf-8 -*-

from passport.backend.logbroker_client.core.events import events
from passport.backend.logbroker_client.core.events.filters import BasicFilter
from passport.backend.logbroker_client.core.handlers.utils import MessageChunk

from .base import get_headers_event_file


class TestEvents(object):

    def test_account_disabled_event(self):
        log_data = "1 1970-01-01T05:01:27.697373+04 43 passport 123456789 info.ena 0 211.212.213.214 33.33.44.55 123142415 - -\n"
        message = MessageChunk(get_headers_event_file('event'), log_data)
        events_filter = BasicFilter([events.AccountDisableEvent])
        events_res = events_filter.filter(message)

        assert events_res[0].uid == 123456789
        assert events_res[0].name == 'account.disable'
        assert events_res[0].timestamp == 3687

    def test_account_enabled_event(self):
        log_data = "1 1970-01-01T05:01:27.697373+04 43 passport 123456789 info.ena 1 211.212.213.214 33.33.44.55 123142415 - -\n"
        message = MessageChunk(get_headers_event_file('event'), log_data)
        events_filter = BasicFilter([events.AccountEnableEvent])
        events_res = events_filter.filter(message)

        assert events_res[0].uid == 123456789
        assert events_res[0].name == 'account.enable'
        assert events_res[0].timestamp == 3687

    def test_account_glogout_event(self):
        log_data = "1 1970-01-01T05:01:27.697373+04 43 passport 123456789 info.glogout 3687.69 211.212.213.214 33.33.44.55 123142415 - -\n"
        message = MessageChunk(get_headers_event_file('event'), log_data)
        events_filter = BasicFilter([events.AccountGlogoutEvent])
        events_res = events_filter.filter(message)

        assert events_res[0].uid == 123456789
        assert events_res[0].name == 'account.glogout'
        assert events_res[0].timestamp == 3687

    def test_account_unsubscribe_event(self):
        log_data = "1 1970-01-01T05:01:27.697373+04 83 passport 139883646 sid.rm 5|leonid-kolomiets 37.140.161.69 - - - -\n"
        message = MessageChunk(get_headers_event_file('event'), log_data)
        events_filter = BasicFilter([events.AccountUnsubscribeEvent])
        events_res = events_filter.filter(message)

        assert events_res[0].uid == 139883646
        assert events_res[0].name == 'sid.rm'
        assert events_res[0].timestamp == 3687
        assert events_res[0].sid == 5

    def test_session_kill_event(self):
        log_data = "1 1970-01-01T05:01:27.697373+04 DE bb 123456789 - - oauthcheck ses_kill ssl=1;aid=1409658335000:ea6MJQ:84;ttl=5 95.108.242.91 - - - - -\n"
        message = MessageChunk(get_headers_event_file('auth'), log_data)
        events_filter = BasicFilter([events.SessionKillEvent])
        events_res = events_filter.filter(message)

        assert events_res[0].uid == 123456789
        assert events_res[0].name == 'session.kill'
        assert events_res[0].timestamp == 3687
        assert events_res[0].authid == '1409658335000:ea6MJQ:84'

    def test_token_invalidate_event(self):
        log_data = (
            "v=1\ttimestamp=3687\tscopes=direct:api,metrika:write,metrika:read\ttarget=token\t"
            "client_id=82e7f4a4fbc044078a75c05e86bc9f82\taction=invalidate\t"
            "token_id=e959143e2172497b83870bb2d321d7b1\tuid=123456789\n"
        )
        message = MessageChunk(get_headers_event_file('oauth'), log_data)
        events_filter = BasicFilter([events.TokenInvalidateEvent])
        events_res = events_filter.filter(message)

        assert events_res[0].uid == 123456789
        assert events_res[0].name == 'token.invalidate'
        assert events_res[0].timestamp == 3687
        assert events_res[0].token_id == 'e959143e2172497b83870bb2d321d7b1'
        assert events_res[0].client_id == '82e7f4a4fbc044078a75c05e86bc9f82'

    def test_token_invalidate_all_event(self):
        log_data = "v=1\ttimestamp=3687\taction=invalidate\ttarget=user\tuid=123456789\n"
        message = MessageChunk(get_headers_event_file('oauth'), log_data)
        events_filter = BasicFilter([events.TokenInvalidateAllEvent])
        events_res = events_filter.filter(message)

        assert events_res[0].uid == 123456789
        assert events_res[0].name == 'token.invalidate_all'
        assert events_res[0].timestamp == 3687

    def test_auth_challenge_event(self):
        log_data = (
            '1 1970-01-01T05:01:27.697373+04 updated 82879256 531a61de-9a85-11e5-bd44-002590ed3092 '
            'CAEQoJeGswUaBkFTNjY5NyCVASiXpAEwAzjXAUCcl4azBUoQUxph3pqFEeW9RAAlkO0wkg== `{"ip": "178.124.31.4", '
            '"yandexuid": "768858301449233308", "user_agent_info": {"OSFamily": "Windows", "BrowserEngine": "Gecko", '
            '"isBrowser": true, "BrowserVersion": "31.0", "OSName": "Windows 8.1", "BrowserName": "Firefox", '
            '"BrowserEngineVersion": "31.0", "x64": true, "OSVersion": "6.3"}}`'
        )
        message = MessageChunk(get_headers_event_file('auth_challenge'), log_data)
        events_filter = BasicFilter([events.AuthChallengeEvent])
        events_res = events_filter.filter(message)

        assert len(events_res) == 1
        assert type(events_res[0]) == events.AuthChallengeEvent
        assert events_res[0].uid == 82879256
        assert events_res[0].timestamp == 3687
        assert events_res[0].env_id == '531a61de-9a85-11e5-bd44-002590ed3092'
        assert events_res[0].env == {
            'ip': '178.124.31.4',
            'yandexuid': '768858301449233308',
            'user_agent_info': {
                'OSFamily': 'Windows',
                'BrowserEngine': 'Gecko',
                'isBrowser': True,
                'BrowserVersion': '31.0',
                'OSName': 'Windows 8.1',
                'BrowserName': 'Firefox',
                'BrowserEngineVersion': '31.0',
                'x64': True,
                'OSVersion': '6.3',
            },
        }
        assert events_res[0].comment is None

    def test_auth_challenge_event_with_comment(self):
        log_data = (
            '2 1970-01-01T05:01:27.697373+04 updated 82879256 531a61de-9a85-11e5-bd44-002590ed3092 '
            'CAEQoJeGswUaBkFTNjY5NyCVASiXpAEwAzjXAUCcl4azBUoQUxph3pqFEeW9RAAlkO0wkg== `{"ip": "178.124.31.4", '
            '"yandexuid": "768858301449233308", "user_agent_info": {"OSFamily": "Windows", "BrowserEngine": "Gecko", '
            '"isBrowser": true, "BrowserVersion": "31.0", "OSName": "Windows 8.1", "BrowserName": "Firefox", '
            '"BrowserEngineVersion": "31.0", "x64": true, "OSVersion": "6.3"}}` abc=def'
        )
        message = MessageChunk(get_headers_event_file('auth_challenge'), log_data)
        events_filter = BasicFilter([events.AuthChallengeEvent])
        events_res = events_filter.filter(message)

        assert len(events_res) == 1
        assert type(events_res[0]) == events.AuthChallengeEvent
        assert events_res[0].uid == 82879256
        assert events_res[0].timestamp == 3687
        assert events_res[0].env_id == '531a61de-9a85-11e5-bd44-002590ed3092'
        assert events_res[0].env == {
            'ip': '178.124.31.4',
            'yandexuid': '768858301449233308',
            'user_agent_info': {
                'OSFamily': 'Windows',
                'BrowserEngine': 'Gecko',
                'isBrowser': True,
                'BrowserVersion': '31.0',
                'OSName': 'Windows 8.1',
                'BrowserName': 'Firefox',
                'BrowserEngineVersion': '31.0',
                'x64': True,
                'OSVersion': '6.3',
            },
        }
        assert events_res[0].comment == 'abc=def'

    def test_account_default_avatar_changed_event(self):
        log_data = "2 2016-12-07T16:41:24.496092+03 8E passport 1130000000267581 info.default_avatar 1450/1130000000267581-488529 127.0.0.1 - - - -\n"
        message = MessageChunk(get_headers_event_file('event'), log_data)
        events_filter = BasicFilter([events.AccountDefaultAvatarEvent])
        events_res = events_filter.filter(message)

        assert events_res[0].uid == 1130000000267581
        assert events_res[0].name == 'account.default_avatar_changed'
        assert events_res[0].timestamp == 1481118084

    def test_account_default_avatar_changed_event__avatar_deleted(self):
        log_data = "2 2016-12-07T16:41:24.496092+03 8E passport 1130000000267581 info.default_avatar - 127.0.0.1 - - - -\n"
        message = MessageChunk(get_headers_event_file('event'), log_data)
        events_filter = BasicFilter([events.AccountDefaultAvatarEvent])
        events_res = events_filter.filter(message)

        assert events_res[0].uid == 1130000000267581
        assert events_res[0].name == 'account.default_avatar_changed'
        assert events_res[0].timestamp == 1481118084
