# -*- coding: utf-8 -*-
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)
from passport.backend.oauth.core.test.framework.testcases.base import BaseTestCase
from passport.backend.oauth.core.test.framework.testcases.mixins import PatchesMixin
from passport.backend.oauth.core.test.utils import (
    check_tskv_log_entries,
    check_tskv_log_entry,
)


class DBTestCase(BaseTestCase, PatchesMixin):
    def setUp(self):
        super(DBTestCase, self).setUp()
        self.patch_db()
        self.patch_login_to_uid_mapping()
        self.patch_scopes()
        self.patch_grants()
        self.patch_device_names_mapping()
        self.patch_token_params()
        self.patch_client_lists()
        self.patch_statbox()
        self.patch_antifraud_logger()
        self.patch_credentials_logger()
        self.patch_historydb()
        self.patch_graphite()
        self.patch_tvm_credentials_manager()

    def tearDown(self):
        self.stop_patches()

    @property
    def base_statbox_entry(self):
        return {
            'tskv_format': 'oauth-log',
            'timestamp': DatetimeNow(convert_to_datetime=True),
            'timezone': '+0300',
            'unixtime': TimeNow(),
        }

    def check_statbox_entries(self, entries):
        combined_entries = [
            dict(self.base_statbox_entry, **entry)
            for entry in entries
        ]
        check_tskv_log_entries(
            self.statbox_handle_mock,
            combined_entries,
        )

    def check_statbox_entry(self, entry, entry_index=-1):
        check_tskv_log_entry(
            self.statbox_handle_mock,
            dict(self.base_statbox_entry, **entry),
            entry_index,
        )

    def check_antifraud_entry(self, entry, offset=-1):
        self.antifraud_logger_faker.assert_equals(
            [
                self.antifraud_logger_faker.entry('base', **entry),
            ],
            offset=offset,
        )

    def check_credentials_entry(self, entry, offset=-1):
        self.credentials_logger_faker.assert_equals(
            [
                self.credentials_logger_faker.entry('base', **entry),
            ],
            offset=offset,
        )
