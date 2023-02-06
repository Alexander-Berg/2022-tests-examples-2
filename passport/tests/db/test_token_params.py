# -*- coding: utf-8 -*-
from datetime import (
    datetime,
    timedelta,
)

from django.test.utils import override_settings
from nose.tools import ok_
from passport.backend.oauth.core.db.token.params import should_issue_stateless
from passport.backend.oauth.core.test.framework import DBTestCase


TEST_UID_IN_EXPERIMENT = 10
TEST_UID_NOT_IN_EXPERIMENT = 11

TEST_DATETIME = datetime(2020, 1, 1)


class ShouldIssueStatelessTestCase(DBTestCase):
    def test_stateless__simple_rule_by_client_id(self):
        ok_(should_issue_stateless(uid=TEST_UID_NOT_IN_EXPERIMENT, client_id='client_id_2'))

    def test_stateless__simple_rule_by_app_id(self):
        ok_(should_issue_stateless(uid=TEST_UID_NOT_IN_EXPERIMENT, client_id='client_id_3', app_id='app_id_2'))

    def test_stateless__complicated_rule(self):
        ok_(should_issue_stateless(uid=TEST_UID_IN_EXPERIMENT, client_id='client_id_1', app_id='app_id_1', app_platform='Apple', app_version='1.2.3'))

    def test_normal__uid_mismatch(self):
        ok_(not should_issue_stateless(uid=TEST_UID_NOT_IN_EXPERIMENT, client_id='client_id_1', app_id='app_id_1', app_platform='Apple', app_version='1.2.3'))

    def test_normal__client_id_mismatch(self):
        ok_(not should_issue_stateless(uid=TEST_UID_IN_EXPERIMENT, client_id='client_id_3', app_id='app_id_1', app_platform='Apple', app_version='1.2.3'))

    def test_normal__app_id_mismatch(self):
        ok_(not should_issue_stateless(uid=TEST_UID_IN_EXPERIMENT, client_id='client_id_1', app_id='app_id_3', app_platform='Apple', app_version='1.2.3'))

    def test_normal__platform_mismatch(self):
        ok_(not should_issue_stateless(uid=TEST_UID_IN_EXPERIMENT, client_id='client_id_1', app_id='app_id_1', app_platform='Android', app_version='1.2.3'))

    def test_normal__version_mismatch(self):
        ok_(not should_issue_stateless(uid=TEST_UID_IN_EXPERIMENT, client_id='client_id_1', app_id='app_id_1', app_platform='Apple', app_version='1.2.2'))

    def test_normal__invalid_params(self):
        ok_(not should_issue_stateless(uid=TEST_UID_IN_EXPERIMENT, client_id='client_id_1', app_id='app_id_1', app_platform='foo', app_version='bar'))

    def test_normal__is_xtoken(self):
        ok_(not should_issue_stateless(uid=TEST_UID_NOT_IN_EXPERIMENT, client_id='client_id_2', is_xtoken=True))

    @override_settings(FORCE_STATELESS_FOR_AM_CLIENTS_CREATED_AFTER=TEST_DATETIME)
    def test_old_client(self):
        ok_(not should_issue_stateless(uid=TEST_UID_NOT_IN_EXPERIMENT, client_id='client_id_3', app_platform='Android', client_create_time=TEST_DATETIME - timedelta(hours=1)))

    @override_settings(FORCE_STATELESS_FOR_AM_CLIENTS_CREATED_AFTER=TEST_DATETIME)
    def test_new_client(self):
        ok_(should_issue_stateless(uid=TEST_UID_NOT_IN_EXPERIMENT, client_id='client_id_3', app_platform='Android', client_create_time=TEST_DATETIME + timedelta(hours=1)))
