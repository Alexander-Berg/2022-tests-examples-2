# -*- coding: utf-8 -*-
from nose.tools import eq_
from passport.backend.core.builders.blackbox.blackbox import Blackbox
from passport.backend.core.test.test_utils import (
    check_all_url_params_match,
    with_settings,
)
from passport.backend.utils.common import merge_dicts
from six.moves.urllib.parse import urlparse

from .test_blackbox import (
    BaseBlackboxRequestTestCase,
    BaseBlackboxTestCase,
)


TEST_BLACKBOX_RESPONSE = '''
{
    "hosts": [{
        "sid" : "2", "host_number" : "0", "host_id" : "7", "prio" : "170",
        "mx" : "ya.ya", "db_id" : "mdb667", "host_name" : "", "host_ip" : ""
    }]
}
'''


@with_settings(BLACKBOX_URL='http://localhost/')
class BlackboxGetHostsRequestTestCase(BaseBlackboxRequestTestCase):

    def test_get_hosts(self):
        self.set_blackbox_response_value(TEST_BLACKBOX_RESPONSE)

        response = self.blackbox.get_hosts()

        eq_(len(response), 1)  # Список верной длины

        host = response[0]
        eq_(host['sid'], '2')
        eq_(host['host_number'], '0')
        eq_(host['host_id'], '7')
        eq_(host['prio'], '170')
        eq_(host['mx'], 'ya.ya')
        eq_(host['db_id'], 'mdb667')
        eq_(host['host_name'], '')
        eq_(host['host_ip'], '')


@with_settings(BLACKBOX_URL='http://test.local/')
class BlackboxGetHostsUrlRequestTestCase(BaseBlackboxTestCase):

    base_params = {
        'method': 'get_hosts',
        'format': 'json',
    }

    def test_get_hosts_url(self):
        request_info = Blackbox().build_get_hosts_request(is_pdd=True, sid=2)

        url = urlparse(request_info.url)
        eq_(url.netloc, 'test.local')

        check_all_url_params_match(
            request_info.url,
            merge_dicts(
                self.base_params,
                {
                    'sid': '2',
                    'is_pdd': 'True',
                },
            ),
        )
