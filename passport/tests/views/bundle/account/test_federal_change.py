# -*- coding: utf-8 -*-
import json

from nose.tools import eq_
from passport.backend.api.test.mixins import EmailTestMixin
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_hosted_domains_response,
    blackbox_loginoccupation_response,
    blackbox_userinfo_response,
)
from passport.backend.core.eav_type_mapping import EXTENDED_ATTRIBUTES_EMAIL_NAME_TO_TYPE_MAPPING as EMAIL_NAME_MAPPING
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)
from passport.backend.utils.common import deep_merge


TEST_LOGIN = 'login'
TEST_ADDITIONAL_LOGIN = 'any_login'
TEST_LOGIN_NEW = 'login_new'
TEST_DOMAIN = 'okna.ru'
TEST_DOMAIN_EXTERNAL = 'external.ru'
TEST_DOMAIN_ID = 1
TEST_PDD_LOGIN = '%s@%s' % (TEST_LOGIN, TEST_DOMAIN)
TEST_ADDITIONAL_PDD_LOGIN = '%s@%s' % (TEST_ADDITIONAL_LOGIN, TEST_DOMAIN)
TEST_EMAIL_SAME_DOMAIN = '%s@%s' % (TEST_LOGIN_NEW, TEST_DOMAIN)
TEST_EMAIL_EXTERNAL = '%s@%s' % (TEST_LOGIN, TEST_DOMAIN_EXTERNAL)

TEST_NAME_ID = '%s/%s' % (TEST_DOMAIN_ID, TEST_LOGIN)
TEST_PDD_UID = 1130000000000001
TEST_USER_IP = '8.8.8.8'
TEST_HOST = 'passport-test.yandex.ru'
TEST_USER_AGENT = 'curl'

TEST_USER_COUNTRY = 'ru'
TEST_USER_FIRSTNAME = 'a'
TEST_USER_LASTNAME = 'b'
TEST_USER_DISPLAYNAME = 'Display Name'
TEST_USER_DISPLAYNAME_FORMATTED = 'p:' + TEST_USER_DISPLAYNAME


@with_settings_hosts()
class TestChangeFederalSubmit(BaseBundleTestViews, EmailTestMixin):
    default_url = '/1/bundle/account/federal/change/?consumer=dev'
    http_method = 'post'
    http_headers = dict(
        user_ip=TEST_USER_IP,
        user_agent=TEST_USER_AGENT,
        host=TEST_HOST,
    )
    http_query_args = dict(
        uid=TEST_PDD_UID,
        firstname=TEST_USER_FIRSTNAME + '_new',
        lastname=TEST_USER_LASTNAME + '_new',
        active=True,
        display_name=TEST_USER_DISPLAYNAME + '_new',
    )

    def setup_account(self, account_kwargs):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(**account_kwargs),
        )
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(
                domain=TEST_DOMAIN,
                domid=TEST_DOMAIN_ID,
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({TEST_EMAIL_SAME_DOMAIN: 'free'}),
        )

    def account_kwargs(self,
                       with_email=False,
                       aliases=None,
                       **kwargs):
        base_kwargs = dict(
            uid=TEST_PDD_UID,
            display_name=dict(name=TEST_USER_DISPLAYNAME),
            login=TEST_PDD_LOGIN,
            firstname=TEST_USER_FIRSTNAME,
            lastname=TEST_USER_LASTNAME,
            domain=TEST_DOMAIN,
            subscribed_to=[2, 102],
            aliases=aliases or {
                'pdd': TEST_PDD_LOGIN,
                'federal': TEST_NAME_ID,
            }
        )
        if with_email:
            base_kwargs['emails'] = [
                self.create_validated_external_email('any', TEST_DOMAIN_EXTERNAL),
            ]
            base_kwargs['email_attributes'] = [
                {
                    'id': 1,
                    'attributes': {
                        EMAIL_NAME_MAPPING['address']: '%s@%s' % ('any', TEST_DOMAIN_EXTERNAL),
                    },
                },
            ]
        return deep_merge(base_kwargs, kwargs)

    def check_response(self, rv, expected_values):
        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            expected_values,
        )

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'account': ['federal_change']}))
        self.setup_statbox_templates()

    def tearDown(self):
        self.env.stop()
        del self.env

    def check_events(self,
                     firstname=None,
                     lastname=None,
                     display_name=None,
                     is_disabled=False,
                     simple_email_add=None,
                     simple_email_remove=None,
                     pdd_alias_add=None,
                     pdd_alias_remove=None):
        expected = {
            'action': 'federal_change',
            'consumer': 'dev',
            'user_agent': TEST_USER_AGENT,
        }
        if firstname:
            expected['info.firstname'] = firstname
        if lastname:
            expected['info.lastname'] = lastname
        if display_name:
            expected['info.display_name'] = display_name
        if is_disabled:
            expected['info.disabled_status'] = '1'
        if simple_email_add:
            expected['email.1'] = 'created'
            expected['email.1.address'] = simple_email_add
            expected['email.1.created_at'] = TimeNow()
        if pdd_alias_add:
            expected['alias.pddalias.add'] = pdd_alias_add
        if pdd_alias_remove:
            expected['alias.pddalias.rm'] = pdd_alias_remove
        if simple_email_remove:
            expected['email.1'] = 'deleted'
            expected['email.1.address'] = simple_email_remove

        self.assert_events_are_logged(self.env.handle_mock, expected)

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'account_modification',
            _inherit_from=['account_modification'],
            _exclude=['mode'],
            ip=TEST_USER_IP,
            consumer='dev',
            user_agent=TEST_USER_AGENT,
            operation='updated',
            uid=str(TEST_PDD_UID),
        )

    def check_statbox_ok(self,
                         firstname=TEST_USER_FIRSTNAME,
                         lastname=TEST_USER_LASTNAME,
                         display_name=None,
                         is_disabled=False,
                         add_simple_email=None,
                         add_pddalias_login=None,
                         remove_simple_email=None,
                         remove_pddalias_login=None):
        entries = []
        if add_simple_email:
            entries.extend([
                self.env.statbox.entry(
                    'account_modification',
                    operation='added',
                    email_id='1',
                    is_suitable_for_restore='0',
                    entity='account.emails',
                    new=add_simple_email,
                    old='-',
                    created_at=DatetimeNow(convert_to_datetime=True),
                ),
            ])
        if remove_simple_email:
            entries.extend([
                self.env.statbox.entry(
                    'account_modification',
                    operation='deleted',
                    email_id='1',
                    is_suitable_for_restore='0',
                    entity='account.emails',
                    new='-',
                    old=remove_simple_email,
                ),
            ])
        if add_pddalias_login:
            entries.extend([
                self.env.statbox.entry(
                    'account_modification',
                    operation='added',
                    entity='pdd_alias_login',
                    type='8',
                    login=add_pddalias_login,
                ),
            ])
        if remove_pddalias_login:
            entries.extend([
                self.env.statbox.entry(
                    'account_modification',
                    operation='removed',
                    entity='pdd_alias_login',
                    type='8',
                    login=remove_pddalias_login,
                ),
            ])
        if is_disabled:
            entries.extend([
                self.env.statbox.entry(
                    'account_modification',
                    entity='account.disabled_status',
                    new='disabled' if is_disabled else 'enabled',
                ),
            ])

        if firstname:
            entries.extend([
                self.env.statbox.entry(
                    'account_modification',
                    entity='person.firstname',
                    new=firstname,
                    old=TEST_USER_FIRSTNAME,
                ),
            ])
        if firstname:
            entries.extend([
                self.env.statbox.entry(
                    'account_modification',
                    entity='person.lastname',
                    new=lastname,
                    old=TEST_USER_LASTNAME,
                ),
            ])
        if display_name:
            entries.extend([
                self.env.statbox.entry(
                    'account_modification',
                    entity='person.display_name',
                    new=display_name,
                    old=TEST_USER_DISPLAYNAME_FORMATTED,
                    operation='deleted' if display_name == '-' else 'updated',
                ),
            ])
        if firstname or lastname:
            entries.extend([
                self.env.statbox.entry(
                    'account_modification',
                    entity='person.fullname',
                    new='{} {}'.format(firstname, lastname),
                    old='{} {}'.format(TEST_USER_FIRSTNAME, TEST_USER_LASTNAME),
                ),
            ])
        self.env.statbox.assert_has_written(entries)

    def assert_ok_db(self,
                     firstname=None,
                     lastname=None,
                     display_name=None,
                     is_disabled=False,
                     db_central_count=0,
                     db_shard2_count=1,
                     pddalias_add=None
                     ):
        eq_(self.env.db.query_count('passportdbcentral'), db_central_count)
        eq_(self.env.db.query_count('passportdbshard2'), db_shard2_count)
        if pddalias_add:
            self.env.db.check('aliases', 'pddalias', '%s/%s' % (TEST_DOMAIN_ID, TEST_LOGIN_NEW), uid=TEST_PDD_UID, db='passportdbcentral')
        if firstname:
            self.env.db.check('attributes', 'person.firstname', firstname, uid=TEST_PDD_UID, db='passportdbshard2')
        else:
            self.env.db.check_missing('attributes', 'account.firstname', uid=TEST_PDD_UID, db='passportdbshard2')
        if lastname:
            self.env.db.check('attributes', 'person.lastname', lastname, uid=TEST_PDD_UID, db='passportdbshard2')
        else:
            self.env.db.check_missing('attributes', 'account.lastname', uid=TEST_PDD_UID, db='passportdbshard2')

        if display_name:
            self.env.db.check('attributes', 'account.display_name', display_name, uid=TEST_PDD_UID, db='passportdbshard2')
        else:
            self.env.db.check_missing('attributes', 'account.display_name', uid=TEST_PDD_UID, db='passportdbshard2')

        if is_disabled:
            self.env.db.check('attributes', 'account.is_disabled', '1', uid=TEST_PDD_UID, db='passportdbshard2')
        else:
            self.env.db.check_missing('attributes', 'account.is_disabled', uid=TEST_PDD_UID, db='passportdbshard2')

    def test_ok(self):
        self.setup_account(self.account_kwargs())
        rv = self.make_request()
        self.check_response(rv, {'status': 'ok'})
        self.assert_ok_db(
            display_name=TEST_USER_DISPLAYNAME_FORMATTED + '_new',
            is_disabled=False,
            firstname=self.http_query_args['firstname'],
            lastname=self.http_query_args['lastname'],
        )
        self.check_statbox_ok(
            display_name=TEST_USER_DISPLAYNAME_FORMATTED + '_new',
            is_disabled=False,
            firstname=self.http_query_args['firstname'],
            lastname=self.http_query_args['lastname'],
        )
        self.check_events(
            firstname=TEST_USER_FIRSTNAME + '_new',
            lastname=TEST_USER_LASTNAME + '_new',
            display_name=TEST_USER_DISPLAYNAME_FORMATTED + '_new',
        )

    def test_add_emails_ok(self):
        self.setup_account(self.account_kwargs())
        rv = self.make_request(query_args={'emails': ','.join([TEST_EMAIL_SAME_DOMAIN, TEST_PDD_LOGIN, TEST_EMAIL_EXTERNAL])})
        self.check_response(rv, {'status': 'ok'})
        self.assert_ok_db(
            display_name=TEST_USER_DISPLAYNAME_FORMATTED + '_new',
            is_disabled=False,
            firstname=self.http_query_args['firstname'],
            lastname=self.http_query_args['lastname'],
            db_central_count=2,
            db_shard2_count=3,
            pddalias_add=TEST_EMAIL_SAME_DOMAIN,
        )
        self.check_statbox_ok(
            add_simple_email='*****@' + TEST_DOMAIN_EXTERNAL,
            add_pddalias_login=TEST_LOGIN_NEW,
            display_name=TEST_USER_DISPLAYNAME_FORMATTED + '_new',
            is_disabled=False,
            firstname=self.http_query_args['firstname'],
            lastname=self.http_query_args['lastname'],
        )
        self.check_events(
            firstname=TEST_USER_FIRSTNAME + '_new',
            lastname=TEST_USER_LASTNAME + '_new',
            display_name=TEST_USER_DISPLAYNAME_FORMATTED + '_new',
            simple_email_add=TEST_EMAIL_EXTERNAL,
            pdd_alias_add=TEST_EMAIL_SAME_DOMAIN,
        )

    def test_add_and_remove_emails_ok(self):
        self.setup_account(
            self.account_kwargs(
                with_email=True,
                aliases={
                    'pdd': TEST_PDD_LOGIN,
                    'pddalias': [TEST_ADDITIONAL_PDD_LOGIN],
                    'federal': TEST_NAME_ID,
                }
            ),
        )
        rv = self.make_request(query_args={'emails': ','.join([TEST_EMAIL_SAME_DOMAIN, TEST_PDD_LOGIN, TEST_EMAIL_EXTERNAL])})
        self.check_response(rv, {'status': 'ok'})
        self.assert_ok_db(
            display_name=TEST_USER_DISPLAYNAME_FORMATTED + '_new',
            is_disabled=False,
            firstname=self.http_query_args['firstname'],
            lastname=self.http_query_args['lastname'],
            db_central_count=4,
            db_shard2_count=5,
        )
        self.check_statbox_ok(
            add_simple_email='*****@' + TEST_DOMAIN_EXTERNAL,
            add_pddalias_login=TEST_LOGIN_NEW,
            display_name=TEST_USER_DISPLAYNAME_FORMATTED + '_new',
            is_disabled=False,
            firstname=self.http_query_args['firstname'],
            lastname=self.http_query_args['lastname'],
            remove_simple_email='*****@' + TEST_DOMAIN_EXTERNAL,
            remove_pddalias_login=TEST_ADDITIONAL_LOGIN,
        )
        self.check_events(
            firstname=TEST_USER_FIRSTNAME + '_new',
            lastname=TEST_USER_LASTNAME + '_new',
            display_name=TEST_USER_DISPLAYNAME_FORMATTED + '_new',
            simple_email_add=TEST_EMAIL_EXTERNAL,
            pdd_alias_add=TEST_EMAIL_SAME_DOMAIN,
            pdd_alias_remove=TEST_ADDITIONAL_PDD_LOGIN,
        )

    def test_add_and_remove_emails_upper_case_ok(self):
        self.setup_account(
            self.account_kwargs(
                with_email=True,
                aliases={
                    'pdd': TEST_PDD_LOGIN.upper(),  # в верхнем регистре
                    'pddalias': [TEST_ADDITIONAL_PDD_LOGIN],
                    'federal': TEST_NAME_ID,
                }
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({TEST_EMAIL_SAME_DOMAIN.upper(): 'free'}),
        )
        rv = self.make_request(query_args={'emails': ','.join([
            TEST_EMAIL_SAME_DOMAIN.upper(),  # в верхнем регистре
            TEST_PDD_LOGIN,
            TEST_EMAIL_EXTERNAL.upper()])})  # в верхнем регистре
        self.check_response(rv, {'status': 'ok'})
        self.assert_ok_db(
            display_name=TEST_USER_DISPLAYNAME_FORMATTED + '_new',
            is_disabled=False,
            firstname=self.http_query_args['firstname'],
            lastname=self.http_query_args['lastname'],
            db_central_count=4,
            db_shard2_count=5,
        )
        self.check_statbox_ok(
            add_simple_email='*****@' + TEST_DOMAIN_EXTERNAL.upper(),
            add_pddalias_login=TEST_LOGIN_NEW,
            display_name=TEST_USER_DISPLAYNAME_FORMATTED + '_new',
            is_disabled=False,
            firstname=self.http_query_args['firstname'],
            lastname=self.http_query_args['lastname'],
            remove_simple_email='*****@' + TEST_DOMAIN_EXTERNAL,
            remove_pddalias_login=TEST_ADDITIONAL_LOGIN,
        )
        self.check_events(
            firstname=TEST_USER_FIRSTNAME + '_new',
            lastname=TEST_USER_LASTNAME + '_new',
            display_name=TEST_USER_DISPLAYNAME_FORMATTED + '_new',
            simple_email_add=TEST_EMAIL_EXTERNAL,
            pdd_alias_add=TEST_EMAIL_SAME_DOMAIN,
            pdd_alias_remove=TEST_ADDITIONAL_PDD_LOGIN,
        )

    def test_remove_all_from_account_ok(self):
        self.setup_account(
            self.account_kwargs(
                with_email=True,
                aliases={
                    'pdd': TEST_PDD_LOGIN,
                    'pddalias': [TEST_ADDITIONAL_PDD_LOGIN],
                    'federal': TEST_NAME_ID,
                }
            ),
        )
        rv = self.make_request(
            query_args=dict(
                firstname='',
                lastname='',
                display_name='',
                emails=''
            )
        )
        self.check_response(rv, {'status': 'ok'})
        self.assert_ok_db(
            db_central_count=2,
            db_shard2_count=3,
        )
        self.check_statbox_ok(
            display_name='-',
            firstname=None,
            lastname=None,
            remove_simple_email='*****@' + TEST_DOMAIN_EXTERNAL,
            remove_pddalias_login=TEST_ADDITIONAL_LOGIN,
        )
        self.check_events(
            display_name='-',
            pdd_alias_remove=TEST_ADDITIONAL_PDD_LOGIN,
            simple_email_remove='any@' + TEST_DOMAIN_EXTERNAL,
        )

    def test_add_occupied_emails_error(self):
        self.setup_account(self.account_kwargs())
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({TEST_EMAIL_SAME_DOMAIN: 'occupied'}),
        )
        rv = self.make_request(query_args={'emails': ','.join([TEST_EMAIL_SAME_DOMAIN, TEST_PDD_LOGIN, TEST_EMAIL_EXTERNAL])})
        self.check_response(
            rv,
            {
                'status': 'error',
                'errors': ['alias.notavailable'],
            },
        )

    def test_account_invalid_type_error(self):
        self.setup_account(self.account_kwargs(aliases={'pdd': TEST_PDD_LOGIN}))
        rv = self.make_request()
        self.check_response(
            rv,
            {
                'status': 'error',
                'errors': ['account.invalid_type'],
            },
        )

    def test_account_unexisted_user_error(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            json.dumps({'users': [{'id': '', 'uid': {}}]}),
        )
        rv = self.make_request()
        self.check_response(
            rv,
            {
                'status': 'error',
                'errors': ['account.not_found'],
            },
        )
