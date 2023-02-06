# -*- coding: utf-8 -*-

import json

from passport.backend.library.test.time_mock import TimeMock
from passport.backend.vault.api.test.base_test_class import BaseTestClass


class TestGlobalStatsView(BaseTestClass):
    def test_ok(self):
        with TimeMock(incrementing=True):
            r = self.client.get_golovan_global_stats()
            self.assertResponseOk(r)
            self.assertListEqual(
                json.loads(r.text),
                [
                    [u'count_secrets_axxx', 4],
                    [u'count_active_secrets_axxx', 4],
                    [u'count_hidden_secrets_axxx', 0],
                    [u'count_versions_axxx', 14],
                    [u'count_active_versions_axxx', 14],
                    [u'count_hidden_versions_axxx', 0],
                    [u'count_tokens_axxx', 0],
                    [u'count_revoked_tokens_axxx', 0],
                    [u'today_count_secrets_axxx', 4],
                    [u'today_secrets_creators_axxx', 2],
                    [u'today_count_versions_axxx', 14],
                    [u'today_versions_creators_axxx', 2],
                    [u'today_count_tokens_axxx', 0],
                    [u'today_tokens_creators_axxx', 0],
                ],
            )
