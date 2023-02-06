# -*- coding: utf-8 -*-
from passport.backend.logbroker_client.core.events import events
from passport.backend.logbroker_client.core.events.filters import BasicFilter
from passport.backend.logbroker_client.core.handlers.utils import MessageChunk

from .base import get_headers_event_file


events_classes = [
    "passport.backend.logbroker_client.core.events.events.AccountGlogoutEvent",
    "passport.backend.logbroker_client.core.events.events.AccountDisableEvent",
    "passport.backend.logbroker_client.core.events.events.SessionKillEvent",
    "passport.backend.logbroker_client.core.events.events.TokenInvalidateEvent",
    "passport.backend.logbroker_client.core.events.events.TokenInvalidateAllEvent"

]
events_filter = BasicFilter([
    events.AccountDisableEvent,
    events.AccountGlogoutEvent,
    events.SessionKillEvent,
    events.TokenInvalidateEvent,
    events.TokenInvalidateAllEvent,
])


NO_APPROPRIATE_EVENTS_DATA = (
    "1 1970-01-01T05:01:27.697373+04 43 passport 123456789 info.ena 5 211.212.213.214 33.33.44.55 123142415 - -\n"
    "1 2014-09-04T15:34:27.676785+04 DE bb 21181453 - - oauthcheck successful clid=6b01dea51b6b456db5425564228f1abb 83.220.239.240 - - - - -\n"
    "1 2014-09-04T15:34:27.679551+04 DE bb 108941866 andkudrus - web ses_update aid=1406012378000:eF922Q:12;ttl=5;host=.yandex.ru; 217.118.95.107 - - - - -\n"
    "1 2014-09-04T15:34:27.690270+04 DE bb 46829208 - - oauthcheck successful clid=6b01dea51b6b456db5425564228f1abb 95.108.242.91 - - - - -\n"
    "1 2014-09-04T15:34:27.709845+04 DE bb 156487455 - - oauthcheck successful clid=82e7f4a4fbc044078a75c05e86bc9f82 141.101.241.104 - - - - -\n"
    "1 2014-09-04T15:34:27.729418+04 DE bb 211249453 - - oauthcheck successful clid=6b01dea51b6b456db5425564228f1abb 2a02:6b8:0:1424::89 - - - - -\n"
    "1 2014-09-04T15:34:27.739590+04 DE bb 3703290 - - oauthcheck successful clid=197f6527da4b48a4bde884cd03fca56f 84.52.73.190 - - - - -\n"
)

GOOD_EVENTS_DATA = (
    "1 1970-01-01T05:01:27.697373+04 43 passport 123456789 info.ena 0 211.212.213.214 33.33.44.55 123142415 - -\n"
    "1 1970-01-01T05:01:27.697373+04 43 passport 123456789 info.glogout 3687.69 211.212.213.214 33.33.44.55 123142415 - -\n"
    "1 1970-01-01T05:01:27.697373+04 DE bb 123456789 - - oauthcheck ses_kill ssl=1;aid=1409658335000:ea6MJQ:84;ttl=5 95.108.242.91 - - - - -\n"
    "1 2014-09-04T15:34:27.676785+04 DE bb 21181453 - - oauthcheck successful clid=6b01dea51b6b456db5425564228f1abb 83.220.239.240 - - - - -\n"
    "1 2014-09-04T15:34:27.679551+04 DE bb 108941866 andkudrus - web ses_update aid=1406012378000:eF922Q:12;ttl=5;host=.yandex.ru; 217.118.95.107 - - - - -\n"
    "1 2014-09-04T15:34:27.690270+04 DE bb 46829208 - - oauthcheck successful clid=6b01dea51b6b456db5425564228f1abb 95.108.242.91 - - - - -\n"
    "1 2014-09-04T15:34:27.709845+04 DE bb 156487455 - - oauthcheck successful clid=82e7f4a4fbc044078a75c05e86bc9f82 141.101.241.104 - - - - -\n"
    "1 2014-09-04T15:34:27.729418+04 DE bb 211249453 - - oauthcheck successful clid=6b01dea51b6b456db5425564228f1abb 2a02:6b8:0:1424::89 - - - - -\n"
)

GOOD_OAUTH_EVENTS_DATA = (
    "v=1\ttimestamp=1411519067.325360\tscopes=direct:api,metrika:write,metrika:read\ttarget=token\t"
    "client_id=82e7f4a4fbc044078a75c05e86bc9f82\taction=invalidate\ttoken_id=e959143e2172497b83870bb2d321d7b1\tuid=200670442\n"
    "v=1\ttimestamp=1411566122.170788\taction=invalidate\ttarget=user\tuid=118366880\n"
    "v=1\ttimestamp=1411518666.641738\tnew_scopes=login:birthday,login:email,login:info\taction=change\told_scopes=login:birthday,login:email,login:info"
    "\ttarget=client\tclient_id=932c1723e17844f0a7bfb4119505b8de\told_callback=https://www.grandrio.com/en/social/login/ya"
    "\tnew_callback=https://www.grandrio.com/{en|ru}/social/login/ya\n"
    "v=1\ttimestamp=1411514215.374172\taction=delete\tscopes=metrika:read\ttarget=client\tclient_id=13da17ca4db24e0b82e30575119115d3\n"
    "v=1\ttimestamp=1411514215.374172\taction=delete\tscopes=metrika:read\ttarget=client\tclient_id=13da17ca4db24e0b82e30575119115d3\n"
    "v=1\ttimestamp=1411514215.374172\taction=delete\tscopes=metrika:read\ttarget=client\tclient_id=13da17ca4db24e0b82e30575119115d3\n"
)


class TestEventsFilter(object):

    def test_filter_two_good_events_from_event_log(self):
        message = MessageChunk(get_headers_event_file('event'), GOOD_EVENTS_DATA)
        events = events_filter.filter(message)
        assert len(events) == 2

        assert events[0].uid == 123456789
        assert events[0].name == 'account.disable'
        assert events[0].timestamp == 3687

        assert events[1].uid == 123456789
        assert events[1].name == 'account.glogout'
        assert events[1].timestamp == 3687

    def test_filter_one_good_events_from_auth_log(self):
        message = MessageChunk(get_headers_event_file('auth'), GOOD_EVENTS_DATA)
        events = events_filter.filter(message)
        assert len(events) == 1

        assert events[0].uid == 123456789
        assert events[0].name == 'session.kill'
        assert events[0].timestamp == 3687
        assert events[0].to_dict()['authid'] == '1409658335000:ea6MJQ:84'

    def test_filter_two_good_events_from_oauth_log(self):
        message = MessageChunk(get_headers_event_file('oauth'), GOOD_OAUTH_EVENTS_DATA)
        events = events_filter.filter(message)
        assert len(events) == 2

        assert events[0].uid == 200670442
        assert events[0].name == 'token.invalidate'
        assert events[0].timestamp == 1411519067
        assert events[0].token_id == 'e959143e2172497b83870bb2d321d7b1'
        assert events[0].client_id == '82e7f4a4fbc044078a75c05e86bc9f82'

        assert events[1].uid == 118366880
        assert events[1].name == 'token.invalidate_all'
        assert events[1].timestamp == 1411566122

    def test_filter_no_good_events(self):
        message = MessageChunk(get_headers_event_file('event'), NO_APPROPRIATE_EVENTS_DATA)
        events = events_filter.filter(message)
        assert len(events) == 0

    def test_filter_no_file_in_headers(self):
        header = {
            'sourceid': 'base64:tTOfUD6sTFy9l4a_mIq8WQ',
            'seqno': '509549082',
            'topic': 'rt3.iva--historydb--raw',
            'server': 'pass-dd-i84.sezam.yandex.net',
            'partition': '7',
            'offset': '535729'
        }
        message = MessageChunk(header, NO_APPROPRIATE_EVENTS_DATA)
        events = events_filter.filter(message)
        assert len(events) == 0

    def test_filter_incorrect_file(self):
        header = {
            'sourceid': 'base64:tTOfUD6sTFy9l4a_mIq8WQ',
            'seqno': '509549082',
            'topic': 'rt3.iva--historydb--raw',
            'path': '/var/log/yandex/passport-api/historydb/unexisting.log',
            'server': 'pass-dd-i84.sezam.yandex.net',
            'partition': '7',
            'offset': '535729'
        }
        message = MessageChunk(header, NO_APPROPRIATE_EVENTS_DATA)
        events = events_filter.filter(message)
        assert len(events) == 0

    def test_filter_empty_data(self):
        data = ""

        message = MessageChunk(get_headers_event_file('event'), data)
        events = events_filter.filter(message)
        assert len(events) == 0
