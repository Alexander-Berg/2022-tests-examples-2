# -*- coding: utf-8 -*-
from collections import OrderedDict

import mock
from passport.backend.core.builders.abc.faker import (
    abc_cursor_paginated_response,
    FakeABC,
)
from passport.backend.core.builders.antifraud.faker.fake_antifraud import (
    antifraud_score_response,
    FakeAntifraudAPI,
)
from passport.backend.core.builders.avatars_mds_api.faker import FakeAvatarsMdsApi
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_create_oauth_token_response,
    blackbox_login_response,
    blackbox_oauth_response,
    blackbox_sessionid_multi_append_user,
    blackbox_sessionid_multi_response,
    blackbox_userinfo_response,
    FakeBlackbox,
)
from passport.backend.core.builders.captcha.faker import (
    captcha_response_check,
    captcha_response_generate,
    FakeCaptcha,
)
from passport.backend.core.builders.kolmogor.faker import FakeKolmogor
from passport.backend.core.builders.money_api.faker import (
    FakeMoneyPaymentAuthApi,
    money_payment_api_auth_context_response,
)
from passport.backend.core.builders.passport.faker import (
    FakePassport,
    passport_ok_response,
)
from passport.backend.core.builders.tvm.faker import FakeTVM
from passport.backend.core.logging_utils.faker.fake_tskv_logger import (
    AntifraudLoggerFaker,
    CredentialsLoggerFaker,
)
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    fake_user_ticket,
    FakeTvmCredentialsManager,
    FakeTvmTicketChecker,
)
from passport.backend.core.ydb.faker.ydb import FakeYdb
from passport.backend.oauth.core.test.base_test_data import (
    TEST_ACL_CONFIG,
    TEST_ANOTHER_UID,
    TEST_DEVICE_NAMES_MAPPING_CONFIG,
    TEST_GRANTS_CONFIG,
    TEST_LOGIN,
    TEST_LOGIN_ID,
    TEST_LOGIN_TO_UID_MAPPING_CONFIG,
    TEST_SCOPE_LOCALIZATIONS_CONFIG,
    TEST_SCOPE_SHORT_LOCALIZATIONS_CONFIG,
    TEST_SCOPES_CONFIG,
    TEST_SERVICE_LOCALIZATIONS_CONFIG,
    TEST_TOKEN_PARAMS_CONFIG,
    TEST_TVM_TICKET,
    TEST_UID,
)
from passport.backend.oauth.core.test.fake_configs import (
    FakeAclGrants,
    FakeClientLists,
    FakeDeviceNamesMapping,
    FakeLoginToUidMapping,
    FakeScopeGrants,
    FakeScopes,
    FakeScopeShortTranslations,
    FakeScopeTranslations,
    FakeServiceTranslations,
    FakeTokenParams,
)
from passport.backend.oauth.core.test.fake_db import FakeDB


TEST_NORMALIZED_LOGIN = TEST_LOGIN.replace('.', '-')


class PatchesMixin(object):
    patches = OrderedDict()

    def patch_environment(self):
        self.fake_captcha = FakeCaptcha()
        self.fake_captcha.set_response_value(
            'generate',
            captcha_response_generate(link='url', key='key'),
        )
        self.fake_captcha.set_response_value(
            'check',
            captcha_response_check(successful=True),
        )

        self.fake_blackbox = FakeBlackbox()
        default_blackbox_kwargs = {
            'uid': TEST_UID,
            'aliases': {
                'portal': TEST_LOGIN,
            },
            'attributes': {
                'account.normalized_login': TEST_NORMALIZED_LOGIN,
            },
        }
        self.fake_blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(**default_blackbox_kwargs),
        )
        self.fake_blackbox.set_response_value(
            'login',
            blackbox_login_response(version=1, **default_blackbox_kwargs),
        )
        self.fake_blackbox.set_response_value(
            'sessionid',
            blackbox_sessionid_multi_append_user(
                blackbox_sessionid_multi_response(login_id=TEST_LOGIN_ID, **default_blackbox_kwargs),
                **(dict(default_blackbox_kwargs, uid=TEST_ANOTHER_UID))
            ),
        )
        self.fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(
                scope='test:xtoken',
                oauth_token_info={'device_id': 'iFridge'},
                login_id=TEST_LOGIN_ID,
                **default_blackbox_kwargs
            ),
        )
        self.fake_blackbox.set_response_value(
            'create_oauth_token',
            blackbox_create_oauth_token_response(
                access_token='state.less.default',
            ),
        )

        self.fake_avatars_mds_api = FakeAvatarsMdsApi()

        self.fake_passport = FakePassport()
        self.fake_passport.set_response_value(
            'send_challenge_email',
            passport_ok_response(email_sent=True),
        )

        self.fake_tvm = FakeTVM()
        self.fake_tvm.set_response_value('verify_ssh', '{"status": "OK"}')

        self.fake_kolmogor = FakeKolmogor()
        self.fake_kolmogor.set_response_value('get', '0,0')
        self.fake_kolmogor.set_response_value('inc', 'OK')

        self.fake_abc = FakeABC()
        self.fake_abc.set_response_value('get_service_members', abc_cursor_paginated_response([]))

        self.fake_money_api = FakeMoneyPaymentAuthApi()
        self.fake_money_api.set_response_value('create_auth_context', money_payment_api_auth_context_response())
        self.fake_money_api.set_response_value('check_auth_context', money_payment_api_auth_context_response())

        self.fake_antifraud_api = FakeAntifraudAPI()
        self.fake_antifraud_api.set_response_value('score', antifraud_score_response())

        self._apply_patches({
            'blackbox': self.fake_blackbox,
            'captcha': self.fake_captcha,
            'avatars_mds_api': self.fake_avatars_mds_api,
            'passport': self.fake_passport,
            'tvm': self.fake_tvm,
            'kolmogor': self.fake_kolmogor,
            'abc': self.fake_abc,
            'money': self.fake_money_api,
            'antifraud_api': self.fake_antifraud_api,
        })

    def patch_db(self):
        self.fake_db = FakeDB()
        self._apply_patches({
            'fake_db': self.fake_db,
        })

    def patch_ydb(self):
        self.fake_ydb = FakeYdb()
        self._apply_patches({
            'fake_ydb': self.fake_ydb,
        })

    def patch_login_to_uid_mapping(self):
        self.fake_login_to_uid_mapping = FakeLoginToUidMapping()
        self.fake_login_to_uid_mapping.set_data(TEST_LOGIN_TO_UID_MAPPING_CONFIG)
        self._apply_patches({
            'login_to_uid_mapping': self.fake_login_to_uid_mapping,
        })

    def patch_scopes(self):
        self.fake_scopes = FakeScopes()
        self.fake_scopes.set_data(TEST_SCOPES_CONFIG)
        self.fake_scope_translations = FakeScopeTranslations()
        self.fake_scope_translations.set_data(TEST_SCOPE_LOCALIZATIONS_CONFIG)
        self.fake_scope_short_translations = FakeScopeShortTranslations()
        self.fake_scope_short_translations.set_data(TEST_SCOPE_SHORT_LOCALIZATIONS_CONFIG)
        self.fake_service_translations = FakeServiceTranslations()
        self.fake_service_translations.set_data(TEST_SERVICE_LOCALIZATIONS_CONFIG)

        self._apply_patches({
            'scopes': self.fake_scopes,
            'scope_translations': self.fake_scope_translations,
            'scope_short_translations': self.fake_scope_short_translations,
            'service_translations': self.fake_service_translations,
        })

    def patch_grants(self):
        self.fake_grants = FakeScopeGrants()
        self.fake_grants.set_data(TEST_GRANTS_CONFIG)
        self.fake_acl = FakeAclGrants()
        self.fake_acl.set_data(TEST_ACL_CONFIG)
        self._apply_patches({
            'grants': self.fake_grants,
            'acl': self.fake_acl,
        })

    def patch_device_names_mapping(self):
        self.fake_device_names_mapping = FakeDeviceNamesMapping()
        self.fake_device_names_mapping.set_data(TEST_DEVICE_NAMES_MAPPING_CONFIG)
        self._apply_patches({
            'device_names_mapping': self.fake_device_names_mapping,
        })

    def patch_token_params(self):
        self.fake_token_params = FakeTokenParams()
        self.fake_token_params.set_data(TEST_TOKEN_PARAMS_CONFIG)
        self._apply_patches({
            'token_params': self.fake_token_params,
        })

    def patch_client_lists(self):
        self.fake_client_lists = FakeClientLists()
        self.fake_client_lists.set_data({'whitelist_for_scope': {}})
        self._apply_patches({
            'client_lists': self.fake_client_lists,
        })

    def patch_antifraud_logger(self):
        self.antifraud_logger_faker = AntifraudLoggerFaker()
        self._apply_patches({
            'antifraud_log': self.antifraud_logger_faker,
        })

    def patch_credentials_logger(self):
        self.credentials_logger_faker = CredentialsLoggerFaker()
        self._apply_patches({
            'credentials': self.credentials_logger_faker,
        })

    def patch_statbox(self):
        self.statbox_handle_mock = mock.Mock()
        self.statbox_logger = mock.Mock()
        self.statbox_logger.debug = self.statbox_handle_mock
        self._apply_patches({
            'statbox': mock.patch('passport.backend.oauth.core.logs.statbox.statbox_log', self.statbox_logger),
        })

    def patch_historydb(self):
        self.event_log_handle_mock = mock.Mock()
        self.event_logger = mock.Mock()
        self.event_logger.debug = self.event_log_handle_mock
        self._apply_patches({
            'historydb.event': mock.patch('passport.backend.oauth.core.logs.historydb.event_log', self.event_logger),
        })

    def patch_graphite(self):
        self.graphite_handle_mock = mock.Mock()
        self.graphite_logger = mock.Mock()
        self.graphite_logger.debug = self.graphite_handle_mock
        self._apply_patches({
            'graphite': mock.patch('passport.backend.oauth.core.logs.graphite.graphite_log', self.graphite_logger),
        })

    def patch_tvm_credentials_manager(self):
        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.set_data(
            fake_tvm_credentials_data(
                ticket_data={
                    '1': {'alias': 'blackbox', 'ticket': TEST_TVM_TICKET},
                    '2': {'alias': 'passport', 'ticket': TEST_TVM_TICKET},
                    '3': {'alias': 'kolmogor', 'ticket': TEST_TVM_TICKET},
                    '4': {'alias': 'blackbox_resolve', 'ticket': TEST_TVM_TICKET},
                    '5': {'alias': 'tvm_api', 'ticket': TEST_TVM_TICKET},
                    '6': {'alias': 'ydb', 'ticket': TEST_TVM_TICKET},
                    '7': {'alias': 'antifraud_api', 'ticket': TEST_TVM_TICKET},
                    '8': {'alias': 'abc', 'ticket': TEST_TVM_TICKET},
                },
            ),
        )
        self.fake_tvm_ticket_checker = FakeTvmTicketChecker()
        self.fake_tvm_ticket_checker.set_check_user_ticket_side_effect([
            fake_user_ticket(default_uid=TEST_UID, scopes=['test:xtoken']),
        ])
        self._apply_patches({
            'tvm_credentials_manager': self.fake_tvm_credentials_manager,
            'tvm_ticket_checker': self.fake_tvm_ticket_checker,
        })

    def _apply_patches(self, patches):
        for name, patch in patches.items():
            patch.start()
            self.patches[name] = patch

    def stop_patches(self):
        for name in reversed(list(self.patches.keys())):
            self.stop_patch(name)

    def stop_patch(self, name):
        self.patches[name].stop()
        del self.patches[name]
