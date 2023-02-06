# -*- coding: utf-8 -*-
from nose_parameterized import parameterized
from passport.backend.adm_api.test.utils import with_settings_hosts
from passport.backend.adm_api.test.views import BaseViewTestCase
from passport.backend.adm_api.tests.views.base_test_data import *
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_loginoccupation_response,
    blackbox_sessionid_response,
    blackbox_userinfo_response,
    get_parsed_blackbox_response,
)
from passport.backend.core.eav_type_mapping import ALIAS_NAME_TO_TYPE as ANT
from passport.backend.core.models.account import Account
from passport.backend.core.types.login.login import normalize_login


TEST_PUBLIC_ID = 'Elon.Musk'
TEST_PUBLIC_ID2 = 'Musk.Elon'


@with_settings_hosts()
class SetPublicIdViewTestCase(BaseViewTestCase):
    path = '/1/account/public_id/set/'
    query_params = {
        'uid': TEST_UID,
        'public_id': TEST_PUBLIC_ID,
    }

    def setUp(self):
        super(SetPublicIdViewTestCase, self).setUp()

        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response(login='admin'))
        self.env.blackbox.set_response_value('userinfo', blackbox_userinfo_response(uid=TEST_UID))
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({normalize_login(TEST_PUBLIC_ID): 'free'}),
        )

        self.account = Account().parse(
            get_parsed_blackbox_response(
                'userinfo',
                blackbox_userinfo_response(uid=TEST_UID),
            ),
        )
        self.env.db._serialize_to_eav(self.account)

    def check_db_entries(self, public_id=TEST_PUBLIC_ID):
        if public_id:
            self.env.db.check_db_attr(
                TEST_UID,
                'account.user_defined_public_id',
                TEST_PUBLIC_ID,
            )
            self.env.db.check(
                'aliases',
                'value',
                normalize_login(TEST_PUBLIC_ID),
                uid=TEST_UID,
                db='passportdbcentral',
                type=ANT['public_id'],
            )
        else:
            self.env.db.check_db_attr_missing(
                TEST_UID,
                'account.user_defined_public_id',
            )
            self.env.db.check_missing(
                'aliases',
                'value',
                uid=TEST_UID,
                db='passportdbcentral',
                type=ANT['public_id'],
            )

        if self.account.public_id_alias.alias:
            self.env.db.check(
                'aliases',
                'value',
                self.account.public_id_alias.alias,
                uid=TEST_UID,
                db='passportdbcentral',
                type=ANT['old_public_id'],
            )

    def check_historydb_entries(self, comment=None):
        expected_entries = {
            'action': 'set_public_id',
            'admin': 'admin',
            'user_agent': 'curl',
        }
        if comment:
            expected_entries['comment'] = comment
        expected_entries['account.user_defined_public_id'] = TEST_PUBLIC_ID
        if self.account.public_id_alias.alias:
            expected_entries['alias.public_id.upd'] = normalize_login(TEST_PUBLIC_ID)
            expected_entries['alias.old_public_id.add'] = self.account.public_id_alias.alias
        else:
            expected_entries['alias.public_id.add'] = normalize_login(TEST_PUBLIC_ID)
        self.assert_events_are_logged(
            self.env.event_handle_mock,
            expected_entries,
        )

    def test_ok(self):
        resp = self.make_request(
            method='POST',
            path=self.path,
            data=self.query_params,
            headers=self.get_headers(),
        )
        self.check_response_ok(resp)
        self.check_db_entries()
        self.check_historydb_entries()
        self.env.blackbox.requests[1].assert_post_data_contains(dict(aliases='all_with_hidden'))

    def test_ok_with_comment(self):
        resp = self.make_request(
            method='POST',
            path=self.path,
            data=dict(self.query_params, comment='some comment'),
            headers=self.get_headers(),
        )
        self.check_response_ok(resp)
        self.check_db_entries()
        self.check_historydb_entries(comment='some comment')

    def test_public_id_occupied(self):
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response(
                {normalize_login(TEST_PUBLIC_ID): 'occupied'},
            ),
        )
        resp = self.make_request(
            method='POST',
            path=self.path,
            data=self.query_params,
            headers=self.get_headers(),
        )
        self.check_response_error(resp, ['public_id.not_available'])
        self.check_db_entries(public_id=None)

    def test_public_id_occupied_by_self(self):
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response(
                {normalize_login(TEST_PUBLIC_ID): 'occupied'},
                {normalize_login(TEST_PUBLIC_ID): str(TEST_UID)},
            ),
        )
        resp = self.make_request(
            method='POST',
            path=self.path,
            data=self.query_params,
            headers=self.get_headers(),
        )
        self.check_response_ok(resp)
        self.check_db_entries()
        self.check_historydb_entries()

    def test_ok_change_public_id(self):
        snapshot = self.account.snapshot()
        acc_data=dict(
            uid=TEST_UID,
            aliases=dict(
                public_id=normalize_login(TEST_PUBLIC_ID2),
                portal=self.account.login,
                old_public_id=['some.alias.2', 'some.alias.3'],
            ),
            attributes={
                'account.user_defined_public_id': 'Some-Alias',
            },

        )
        self.env.blackbox.set_response_value('userinfo', blackbox_userinfo_response(**acc_data))
        self.account = Account().parse(
            get_parsed_blackbox_response(
                'userinfo',
                blackbox_userinfo_response(**acc_data),
            ),
        )
        self.env.db._serialize_to_eav(self.account, snapshot)

        resp = self.make_request(
            method='POST',
            path=self.path,
            data=self.query_params,
            headers=self.get_headers(),
        )
        self.check_response_ok(resp)
        self.check_db_entries()
        self.check_historydb_entries()

    def test_no_public_id(self):
        resp = self.make_request(
            method='POST',
            path=self.path,
            data={'uid': TEST_UID},
            headers=self.get_headers(),
        )
        self.check_response_error(resp, ['public_id.empty'])

    def test_no_uid(self):
        resp = self.make_request(
            method='POST',
            path=self.path,
            data={'public_id': TEST_PUBLIC_ID},
            headers=self.get_headers(),
        )
        self.check_response_error(resp, ['uid.empty'])

    @parameterized.expand([
        ('p' * 31, 'public_id.long'),
        ('1public-id', 'public_id.startswithdigit'),
        ('.public-id', 'public_id.startswithdot'),
        ('-public-id', 'public_id.startswithhyphen'),
        ('public-id.', 'public_id.endwithdot'),
        ('public-id-', 'public_id.endswithhyphen'),
        ('public..id', 'public_id.doubleddot'),
        ('public--id', 'public_id.doubledhyphen'),
        ('public_id', 'public_id.prohibitedsymbols'),
        ('public.-id', 'public_id.dothyphen'),
        ('public-.id', 'public_id.hyphendot'),
    ])
    def test_discretized_public_id_errors(self, public_id, error):
        resp = self.make_request(
            method='POST',
            path=self.path,
            data=dict(self.query_params, public_id=public_id),
            headers=self.get_headers(),
        )
        self.check_response_error(resp, [error])


@with_settings_hosts()
class RemovePublicIdViewTestCase(BaseViewTestCase):
    path = '/1/account/public_id/remove/'
    query_params = {
        'uid': TEST_UID,
        'public_id': TEST_PUBLIC_ID,
    }

    def setUp(self):
        super(RemovePublicIdViewTestCase, self).setUp()

        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response(login='admin'))

        acc_data = dict(
            uid=TEST_UID,
            aliases=dict(
                public_id=normalize_login(TEST_PUBLIC_ID),
                portal='login',
                old_public_id=[normalize_login(TEST_PUBLIC_ID2), 'some.alias', 'some.alias.2'],
            ),
            attributes={
                'account.user_defined_public_id': TEST_PUBLIC_ID,
            },

        )
        self.env.blackbox.set_response_value('userinfo', blackbox_userinfo_response(**acc_data))
        self.account = Account().parse(
            get_parsed_blackbox_response(
                'userinfo',
                blackbox_userinfo_response(**acc_data),
            ),
        )
        self.env.db._serialize_to_eav(self.account)

    def check_db_entries(self, removed_public_id):
        if removed_public_id == self.account.user_defined_public_id:
            self.env.db.check_db_attr_missing(
                TEST_UID,
                'account.user_defined_public_id',
            )
            self.env.db.check_missing(
                'aliases',
                'value',
                uid=TEST_UID,
                db='passportdbcentral',
                type=ANT['public_id'],
            )
        for alias in self.account.public_id_alias.old_public_ids:
            if alias == normalize_login(removed_public_id):
                self.env.db.check_missing(
                    'aliases',
                    'value',
                    uid=TEST_UID,
                    db='passportdbcentral',
                    type=ANT['old_public_id'],
                    surrogate_type='{}-{}'.format(ANT['old_public_id'], alias).encode('utf-8'),
                )
            else:
                self.env.db.check(
                    'aliases',
                    'value',
                    alias,
                    uid=TEST_UID,
                    db='passportdbcentral',
                    type=ANT['old_public_id'],
                    surrogate_type='{}-{}'.format(ANT['old_public_id'], alias).encode('utf-8'),
                )

    def check_historydb_entries(self, removed_public_id, comment=None):
        expected_entries = {
            'action': 'remove_public_id',
            'admin': 'admin',
            'user_agent': 'curl',
        }
        if comment:
            expected_entries['comment'] = comment
        if removed_public_id == self.account.user_defined_public_id:
            expected_entries['account.user_defined_public_id'] = '-'
            expected_entries['alias.public_id.rm'] = normalize_login(removed_public_id)
        if normalize_login(removed_public_id) in self.account.public_id_alias.old_public_ids:
            expected_entries['alias.old_public_id.rm'] = normalize_login(removed_public_id)
        self.assert_events_are_logged(
            self.env.event_handle_mock,
            expected_entries,
        )

    def test_ok_public_id(self):
        resp = self.make_request(
            method='POST',
            path=self.path,
            data=self.query_params,
            headers=self.get_headers(),
        )
        self.check_response_ok(resp)
        self.check_db_entries(removed_public_id=TEST_PUBLIC_ID)
        self.check_historydb_entries(removed_public_id=TEST_PUBLIC_ID)
        self.env.blackbox.requests[1].assert_post_data_contains(dict(aliases='all_with_hidden'))

    def test_ok_public_id_with_comment(self):
        resp = self.make_request(
            method='POST',
            path=self.path,
            data=dict(self.query_params, comment='some comment'),
            headers=self.get_headers(),
        )
        self.check_response_ok(resp)
        self.check_db_entries(removed_public_id=TEST_PUBLIC_ID)
        self.check_historydb_entries(removed_public_id=TEST_PUBLIC_ID, comment='some comment')

    def test_ok_old_public_id(self):
        resp = self.make_request(
            method='POST',
            path=self.path,
            data={
                'uid': TEST_UID,
                'public_id': TEST_PUBLIC_ID2,
            },
            headers=self.get_headers(),
        )
        self.check_response_ok(resp)
        self.check_db_entries(removed_public_id=TEST_PUBLIC_ID2)
        self.check_historydb_entries(removed_public_id=TEST_PUBLIC_ID2)

    def test_unknown_public_id(self):
        resp = self.make_request(
            method='POST',
            path=self.path,
            data={
                'uid': TEST_UID,
                'public_id': 'Some.Unknown.Public.Id',
            },
            headers=self.get_headers(),
        )
        self.check_response_error(resp, ['public_id.not_found'])
        self.check_db_entries(removed_public_id=None)

    def test_no_public_id(self):
        resp = self.make_request(
            method='POST',
            path=self.path,
            data={'uid': TEST_UID},
            headers=self.get_headers(),
        )
        self.check_response_error(resp, ['public_id.empty'])

    def test_no_uid(self):
        resp = self.make_request(
            method='POST',
            path=self.path,
            data={'public_id': TEST_PUBLIC_ID},
            headers=self.get_headers(),
        )
        self.check_response_error(resp, ['uid.empty'])


@with_settings_hosts()
class RemoveAllPublicIdViewTestCase(BaseViewTestCase):
    path = '/1/account/public_id/remove_all/'
    query_params = {
        'uid': TEST_UID,
    }

    def setUp(self):
        super(RemoveAllPublicIdViewTestCase, self).setUp()
        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response(login='admin'))

    def setup_account(self, with_public_ids=True):
        acc_data = dict(
            uid=TEST_UID,
        )
        if with_public_ids:
            acc_data = dict(
                aliases=dict(
                    public_id=normalize_login(TEST_PUBLIC_ID),
                    portal='login',
                    old_public_id=[normalize_login(TEST_PUBLIC_ID2), 'some-alias', 'some-alias-2'],
                ),
                attributes={
                    'account.user_defined_public_id': TEST_PUBLIC_ID,
                },
                **acc_data
            )
        self.env.blackbox.set_response_value('userinfo', blackbox_userinfo_response(**acc_data))
        self.account = Account().parse(
            get_parsed_blackbox_response(
                'userinfo',
                blackbox_userinfo_response(**acc_data),
            ),
        )
        self.env.db._serialize_to_eav(self.account)

    def check_db_entries(self):
        self.env.db.check_db_attr_missing(
            TEST_UID,
            'account.user_defined_public_id',
        )
        self.env.db.check_missing(
            'aliases',
            'value',
            uid=TEST_UID,
            db='passportdbcentral',
            type=ANT['public_id'],
        )
        for alias in self.account.public_id_alias.old_public_ids:
            self.env.db.check_missing(
                'aliases',
                'value',
                uid=TEST_UID,
                db='passportdbcentral',
                type=ANT['old_public_id'],
                surrogate_type='{}-{}'.format(ANT['old_public_id'], alias).encode('utf-8'),
            )

    def check_historydb_entries(self, comment=None):
        expected_entries = {
            'action': 'remove_all_public_id',
            'admin': 'admin',
            'user_agent': 'curl',
        }
        if comment:
            expected_entries['comment'] = comment
        expected_entries['account.user_defined_public_id'] = '-'
        expected_entries['alias.public_id.rm'] = self.account.public_id_alias.alias
        expected_entries['alias.old_public_id.rm'] = ','.join(sorted(self.account.public_id_alias.old_public_ids))
        self.assert_events_are_logged(
            self.env.event_handle_mock,
            expected_entries,
        )

    def test_ok(self):
        self.setup_account()
        resp = self.make_request(
            method='POST',
            path=self.path,
            data=self.query_params,
            headers=self.get_headers(),
        )
        self.check_response_ok(resp)
        self.check_db_entries()
        self.check_historydb_entries()
        self.env.blackbox.requests[1].assert_post_data_contains(dict(aliases='all_with_hidden'))

    def test_ok_with_comment(self):
        self.setup_account()
        resp = self.make_request(
            method='POST',
            path=self.path,
            data=dict(self.query_params, comment='some comment'),
            headers=self.get_headers(),
        )
        self.check_response_ok(resp)
        self.check_db_entries()
        self.check_historydb_entries(comment='some comment')

    def test_no_uid(self):
        resp = self.make_request(
            method='POST',
            path=self.path,
            data=None,
            headers=self.get_headers(),
        )
        self.check_response_error(resp, ['uid.empty'])

    def test_no_public_ids_to_remove_ok(self):
        self.setup_account(False)
        resp = self.make_request(
            method='POST',
            path=self.path,
            data=self.query_params,
            headers=self.get_headers(),
        )
        self.check_response_ok(resp)
        self.check_db_entries()
        self.assert_events_are_empty(self.env.event_handle_mock)
