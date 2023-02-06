# -*- coding: utf-8 -*-

from mock import Mock
from nose.tools import eq_
from passport.backend.social.api.common import get_full_sids_list

from .common import (
    error_in_json,
    TestApiAppCase,
    TestApiViewsCase,
)


class TestCommonMethods(TestApiViewsCase):
    def test_get_full_sids_list(self):
        def _single_test(original_sids, resulting_sids):
            orig = [Mock(sid=s, value=v) for s, v in original_sids]
            res = [r['sid'] for r in get_full_sids_list(orig)]
            eq_(set(res), set(resulting_sids), [res, resulting_sids])

        _single_test([], [2, 102])
        _single_test([(2, 1)], [2, 102])
        _single_test([(1, 1)], [1, 2, 102])
        _single_test([(2, 0)], [102])


class TestGrants(TestApiAppCase):
    def test_no_required_grant(self):
        self.app_client = self.app.test_client()
        self.app_client.set_context({'consumer': 'local'})

        r = self.app_client.get('/api/profile/1', remote_addr='77.88.0.1')
        error_in_json(r, 403, name='access-denied')
