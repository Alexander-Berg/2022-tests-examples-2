# -*- coding: utf-8 -*-
from datetime import datetime

from nose.tools import eq_
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.views.bundle.account.aliases import (
    ALIAS_BANK_PHONENUMBER_GRANT,
    ALIASES_ALTDOMAIN_GRANT,
    ALIASES_BASE_GRANT,
    ALIASES_PDDALIAS_GRANT,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_hosted_domains_response,
    blackbox_loginoccupation_response,
    blackbox_phone_bindings_response,
    blackbox_userinfo_response,
)
from passport.backend.core.eav_type_mapping import ALIAS_NAME_TO_TYPE as ANT
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.core.types.account.account import PDD_UID_BOUNDARY
from passport.backend.core.types.phone_number.phone_number import PhoneNumber


TEST_LOGIN = 'login'
TEST_UID = 1
TEST_PDD_UID = PDD_UID_BOUNDARY + 1

TEST_ALTDOMAIN_ALIAS_LOGIN = 'foo'
TEST_ALTDOMAIN_ALIAS_DOMAIN = 'auto.ru'
TEST_ALTDOMAIN_ALIAS_DOMAIN_ID = '1120001'
TEST_ALTDOMAIN_ALIAS = '%s@%s' % (
    TEST_ALTDOMAIN_ALIAS_LOGIN,
    TEST_ALTDOMAIN_ALIAS_DOMAIN,
)
TEST_ALTDOMAIN_ALIAS_SERIALIZED = '%s/%s' % (
    TEST_ALTDOMAIN_ALIAS_DOMAIN_ID,
    TEST_ALTDOMAIN_ALIAS_LOGIN,
)
TEST_OTHER_ALTDOMAIN_ALIAS = 'bar@auto.ru'

TEST_PDD_LOGIN = 'login@okna.ru'
TEST_ADDITIONAL_LOGIN = 'login1'
TEST_DOMAIN = 'okna.ru'
TEST_DOMAIN_ID = 1
TEST_PDD_ALIAS_SERIALIZED = '%s/%s' % (TEST_DOMAIN_ID, 'login')
TEST_ADDITIONAL_PDD_LOGIN = '%s@%s' % (TEST_ADDITIONAL_LOGIN, TEST_DOMAIN)
TEST_ADDITIONAL_PDD_ALIAS_SERIALIZED = '%s/%s' % (TEST_DOMAIN_ID, TEST_ADDITIONAL_LOGIN)

TEST_BANK_PHONE_NUMBER = '79112234455'
TEST_BANK_PHONE_NUMBER_OTHER = '799988776655'
TEST_BANK_PHONE = PhoneNumber.parse(TEST_BANK_PHONE_NUMBER)
TEST_PHONE_ID = 1


@with_settings_hosts(
    BLACKBOX_URL='localhost',
    ALT_DOMAINS={
        TEST_ALTDOMAIN_ALIAS_DOMAIN: TEST_ALTDOMAIN_ALIAS_DOMAIN_ID,
    },
)
class BaseTestAccountAliasView(BaseBundleTestViews):

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({
                TEST_ALTDOMAIN_ALIAS: 'free',
            }),
        )
        self.setup_grants()
        self.setup_statbox_templates()

        self.aliases_table = 'aliases'

    def tearDown(self):
        self.env.stop()
        del self.env

    def default_userinfo_response(self, uid=TEST_UID, aliases=None):
        return blackbox_userinfo_response(
            uid=uid,
            login=TEST_LOGIN,
            subscribed_to=None,
            dbfields={},
            attributes={},
            aliases=aliases,
        )

    def setup_grants(self, *args):
        prefix, suffix = ALIASES_BASE_GRANT.split('.')
        grants = {prefix: [suffix]}
        for grant in args:
            prefix, suffix = grant.split('.')
            grants.setdefault(prefix, []).append(suffix)
        self.env.grants.set_grants_return_value(mock_grants(grants=grants))

    def setup_statbox_templates(self):
        self.env.statbox.bind_base(
            event='account_modification',
            uid=str(TEST_UID),
            ip='127.0.0.1',
            user_agent='-',
            consumer='dev',
            entity='aliases',
            type=str(ANT['altdomain']),
            domain_id=TEST_ALTDOMAIN_ALIAS_DOMAIN_ID,
        )
        self.env.statbox.bind_entry(
            'aliases_added',
            operation='added',
        )
        self.env.statbox.bind_entry(
            'aliases_removed',
            operation='removed',
        )
        self.env.statbox.bind_entry(
            'pddalias_added',
            _exclude=['domain_id'],
            operation='added',
            entity='pdd_alias_login',
            type=str(ANT['pddalias']),
            uid=str(TEST_PDD_UID),
        )
        self.env.statbox.bind_entry(
            'pddalias_removed',
            _inherit_from='pddalias_added',
            _exclude=['domain_id'],
            operation='removed',
        )
        self.env.statbox.bind_entry(
            'bank_phonenumber_alias_added',
            _exclude=['domain_id'],
            operation='added',
            type=str(ANT['bank_phonenumber']),
            value=TEST_BANK_PHONE.digital,
        )
        self.env.statbox.bind_entry(
            'bank_phonenumber_alias_removed',
            _exclude=['domain_id'],
            operation='removed',
            type=str(ANT['bank_phonenumber']),
        )
        self.env.statbox.bind_entry(
            'phone_bound',
            _exclude=['domain_id', 'type', 'entity', 'event', 'user_agent', 'consumer'],
            action='phone_bound',
            mode='account_bank_phonenumber_alias_bind_phone',
        )
        self.env.statbox.bind_entry(
            'phone_operation_created',
            _exclude=['domain_id', 'type', 'entity', 'event'],
            action='phone_operation_created',
            operation_id='1',
            operation_type='simple_bind',
            phone_id='1',
        )
        self.env.statbox.bind_entry(
            'phone_confirmed',
            _exclude=['domain_id', 'type', 'entity', 'event', 'user_agent', 'consumer'],
            action='phone_confirmed',
            mode='account_bank_phonenumber_alias_bind_phone',
            code_checks_count='0',
            operation_id='1',
            phone_id='1',
        )
        self.env.statbox.bind_entry(
            'simple_phone_bound',
            _exclude=['domain_id', 'type', 'entity', 'event', 'user_agent', 'consumer'],
            action='simple_phone_bound',
            mode='account_bank_phonenumber_alias_bind_phone',
            operation_id='1',
            phone_id='1',
            ip='127.0.0.1',
        )

    def set_and_serialize_userinfo(self, blackbox_response):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_response,
        )
        self.env.db.serialize(blackbox_response)

    def check_db_ok(self, centraldb_query_count=0, sharddb_query_count=0,
                    alias=None, field=None, uid=TEST_UID, **kwargs):
        eq_(
            self.env.db.query_count('passportdbcentral'),
            centraldb_query_count,
        )
        eq_(
            self.env.db.query_count('passportdbshard1'),
            sharddb_query_count,
        )

        field = field or 'altdomain'

        if alias:
            self.env.db.check(
                self.aliases_table,
                field,
                alias,
                uid=uid,
                db='passportdbcentral',
                **kwargs
            )
        else:
            self.env.db.check_missing(
                self.aliases_table,
                field,
                uid=uid,
                db='passportdbcentral',
                **kwargs
            )


class TestAccountAliasAltDomainCreateView(BaseTestAccountAliasView):

    default_url = '/1/account/%d/alias/altdomain/?consumer=dev' % TEST_UID
    http_method = 'post'
    http_query_args = dict(
        alias=TEST_ALTDOMAIN_ALIAS,
    )

    def check_events_ok(self):
        self.assert_events_are_logged(
            self.env.handle_mock,
            {
                'action': 'alias',
                'consumer': 'dev',
                'alias.altdomain.add': TEST_ALTDOMAIN_ALIAS_SERIALIZED,
            },
        )

    def test_unknown_uid_fails(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(uid=None),
        )
        resp = self.make_request()
        self.assert_error_response(resp, ['account.not_found'])

    def test_grant_missing_fails(self):
        userinfo_response = self.default_userinfo_response()
        self.set_and_serialize_userinfo(userinfo_response)
        self.setup_grants(ALIASES_BASE_GRANT)
        resp = self.make_request()
        self.assert_error_response(resp, ['access.denied'], status_code=403)

    def test_create_altdomain_alias_ok(self):
        userinfo_response = self.default_userinfo_response()
        self.set_and_serialize_userinfo(userinfo_response)
        self.setup_grants(ALIASES_BASE_GRANT, ALIASES_ALTDOMAIN_GRANT)
        resp = self.make_request()
        self.assert_ok_response(resp)
        self.check_db_ok(centraldb_query_count=1, alias=TEST_ALTDOMAIN_ALIAS_SERIALIZED)
        self.check_events_ok()
        self.env.statbox.assert_has_written(
            [
                self.env.statbox.entry('aliases_added'),
            ],
        )

    def test_altdomain_alias_exists(self):
        userinfo_response = self.default_userinfo_response(
            aliases={
                'portal': TEST_LOGIN,
                'altdomain': TEST_OTHER_ALTDOMAIN_ALIAS,
            },
        )
        self.set_and_serialize_userinfo(userinfo_response)
        self.setup_grants(ALIASES_BASE_GRANT, ALIASES_ALTDOMAIN_GRANT)
        resp = self.make_request()
        self.assert_error_response(resp, ['alias.exists'])


class TestAccountAliasAltDomainDeleteView(BaseTestAccountAliasView):

    default_url = '/1/account/%d/alias/altdomain/' % TEST_UID
    http_method = 'delete'
    http_query_args = dict(consumer='dev')

    def check_events_ok(self):
        self.assert_events_are_logged(
            self.env.handle_mock,
            {
                'action': 'alias',
                'consumer': 'dev',
                'alias.altdomain.rm': TEST_ALTDOMAIN_ALIAS_SERIALIZED,
            },
        )

    def test_unknown_uid_fails(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(uid=None),
        )
        resp = self.make_request()
        self.assert_error_response(resp, ['account.not_found'])

    def test_grant_missing_fails(self):
        userinfo_response = self.default_userinfo_response()
        self.set_and_serialize_userinfo(userinfo_response)
        self.setup_grants(ALIASES_BASE_GRANT)
        resp = self.make_request()
        self.assert_error_response(resp, ['access.denied'], status_code=403)

    def test_delete_altdomain_alias_ok(self):
        userinfo_response = self.default_userinfo_response(
            aliases={
                'portal': TEST_LOGIN,
                'altdomain': TEST_ALTDOMAIN_ALIAS,
            },
        )
        self.set_and_serialize_userinfo(userinfo_response)
        self.setup_grants(ALIASES_BASE_GRANT, ALIASES_ALTDOMAIN_GRANT)
        resp = self.make_request()
        self.assert_ok_response(resp)
        self.check_db_ok(centraldb_query_count=2, alias=None)
        self.check_events_ok()
        self.env.statbox.assert_has_written(
            [
                self.env.statbox.entry('aliases_removed'),
            ],
        )


class TestAccountAliasPddDomainCreateView(BaseTestAccountAliasView):

    default_url = '/1/account/%d/alias/pdddomain/?consumer=dev' % TEST_UID
    http_method = 'post'
    http_query_args = dict(
        alias=TEST_PDD_LOGIN,
    )

    def setUp(self):
        super(TestAccountAliasPddDomainCreateView, self).setUp()
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({
                TEST_PDD_LOGIN: 'free',
            }),
        )
        self.default_hosted_domains_setup()

    def default_hosted_domains_setup(self, test_domain=TEST_DOMAIN):
        hosted_domains_response = blackbox_hosted_domains_response(
            count=1,
            domid=TEST_DOMAIN_ID,
            domain=test_domain,
            is_enabled=True,
        )
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            hosted_domains_response,
        )

    def default_userinfo_response(self, uid=TEST_PDD_UID, aliases=None, domain=TEST_DOMAIN,
                                  login=TEST_PDD_LOGIN, subscribed_to=None):
        aliases = aliases or dict(portal=TEST_LOGIN)
        return blackbox_userinfo_response(
            uid=uid,
            login=login,
            subscribed_to=subscribed_to or [],
            dbfields={},
            attributes={},
            aliases=aliases,
        )

    def check_events_ok(self, **kwargs):
        event = {
            'action': 'alias',
            'consumer': 'dev',
            'alias.pdd.add': TEST_PDD_ALIAS_SERIALIZED,
            'info.domain_name': TEST_DOMAIN,
            'info.domain_id': str(TEST_DOMAIN_ID),
        }
        event.update(kwargs)
        self.assert_events_are_logged(
            self.env.handle_mock,
            event
        )

    def setup_statbox_templates(self):
        super(TestAccountAliasPddDomainCreateView, self).setup_statbox_templates()
        self.env.statbox.bind_entry(
            'domain_name_created',
            entity='domain_name',
            operation='created',
            old='-',
            new=TEST_DOMAIN,
            _exclude=['type', 'domain_id']
        )
        self.env.statbox.bind_entry(
            'domain_id_created',
            entity='domain_id',
            operation='created',
            old='-',
            new=str(TEST_DOMAIN_ID),
            _exclude=['type', 'domain_id']
        )

    def test_unknown_uid_fails(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(uid=None),
        )
        resp = self.make_request()
        self.assert_error_response(resp, ['account.not_found'])

    def test_grant_missing_fails(self):
        userinfo_response = self.default_userinfo_response()
        self.set_and_serialize_userinfo(userinfo_response)
        self.setup_grants(ALIASES_BASE_GRANT)
        resp = self.make_request()
        self.assert_error_response(resp, ['access.denied'], status_code=403)

    def test_create_pdddomain_alias_without_122_subscription(self):
        userinfo_response = self.default_userinfo_response()
        self.set_and_serialize_userinfo(userinfo_response)
        self.setup_grants(ALIASES_BASE_GRANT, ALIASES_PDDALIAS_GRANT)
        resp = self.make_request()
        self.assert_error_response(resp, ['account.not_subscribed'])

    def test_create_pdddomain_alias_ok(self):
        userinfo_response = self.default_userinfo_response(
            subscribed_to=[122],
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            userinfo_response,
        )
        self.setup_grants(ALIASES_BASE_GRANT, ALIASES_PDDALIAS_GRANT)
        resp = self.make_request()
        self.assert_ok_response(resp)

        self.check_db_ok(
            centraldb_query_count=1,
            field='value',
            alias=TEST_PDD_ALIAS_SERIALIZED,
            uid=TEST_PDD_UID,
            type=str(ANT['pdd']),
        )
        self.check_events_ok()
        self.env.statbox.assert_has_written(
            [
                self.env.statbox.entry(
                    'aliases_added',
                    uid=str(TEST_PDD_UID),
                    type=str(ANT['pdd']),
                    value=TEST_PDD_LOGIN,
                    _exclude=['domain_id'],
                ),
                self.env.statbox.entry(
                    'domain_name_created',
                    uid=str(TEST_PDD_UID),
                ),
                self.env.statbox.entry(
                    'domain_id_created',
                    uid=str(TEST_PDD_UID),
                ),
            ],
        )

    def test_create_cyrillic_pdddomain_alias_ok(self):
        cyrillic_domain = u'русский-домен.рф'
        cyrillic_domain_pynicode = cyrillic_domain.encode('idna')
        test_login = 'login@' + cyrillic_domain

        userinfo_response = self.default_userinfo_response(
            subscribed_to=[122],
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            userinfo_response,
        )
        self.default_hosted_domains_setup(test_domain=cyrillic_domain)
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({
                test_login: 'free',
            }),
        )
        self.setup_grants(ALIASES_BASE_GRANT, ALIASES_PDDALIAS_GRANT)

        resp = self.make_request(query_args=dict(
            alias=test_login,
        ))
        self.assert_ok_response(resp)

        self.check_db_ok(
            centraldb_query_count=1,
            field='value',
            alias=TEST_PDD_ALIAS_SERIALIZED,
            uid=TEST_PDD_UID,
            type=str(ANT['pdd']),
        )
        self.check_events_ok(**{'info.domain_name': cyrillic_domain_pynicode})
        self.env.statbox.assert_has_written(
            [
                self.env.statbox.entry(
                    'aliases_added',
                    uid=str(TEST_PDD_UID),
                    type=str(ANT['pdd']),
                    value=test_login,
                    _exclude=['domain_id'],
                ),
                self.env.statbox.entry(
                    'domain_name_created',
                    uid=str(TEST_PDD_UID),
                    new=cyrillic_domain_pynicode,
                ),
                self.env.statbox.entry(
                    'domain_id_created',
                    uid=str(TEST_PDD_UID),
                ),
            ],
        )

    def test_pdddomain_alias_exists(self):
        userinfo_response = self.default_userinfo_response(
            subscribed_to=[122],
            aliases={
                'portal': TEST_LOGIN,
                'pdd': TEST_PDD_LOGIN,
            },
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            userinfo_response,
        )
        self.setup_grants(ALIASES_BASE_GRANT, ALIASES_PDDALIAS_GRANT)
        resp = self.make_request()
        self.assert_error_response(resp, ['alias.exists'])

    def test_pdddomain_alias_not_available(self):
        userinfo_response = self.default_userinfo_response(
            subscribed_to=[122],
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            userinfo_response,
        )
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({
                TEST_PDD_LOGIN: 'occupied',
            }),
        )
        self.setup_grants(ALIASES_BASE_GRANT, ALIASES_PDDALIAS_GRANT)
        resp = self.make_request()
        self.assert_error_response(resp, ['alias.notavailable'])


class TestAccountAliasPddDomainDeleteView(BaseTestAccountAliasView):

    default_url = '/1/account/%d/alias/pdddomain/' % TEST_UID
    http_method = 'delete'
    http_query_args = dict(consumer='dev')

    def check_events_ok(self):
        self.assert_events_are_logged(
            self.env.handle_mock,
            {
                'action': 'alias',
                'consumer': 'dev',
                'alias.pdd.rm': TEST_PDD_ALIAS_SERIALIZED,
            },
        )

    def default_userinfo_response(self, uid=TEST_PDD_UID, aliases=None, domain=TEST_DOMAIN,
                                  login=TEST_PDD_LOGIN, subscribed_to=None):
        aliases = aliases or dict(portal=TEST_LOGIN)
        return blackbox_userinfo_response(
            uid=uid,
            login=login,
            subscribed_to=subscribed_to or [],
            dbfields={},
            attributes={},
            aliases=aliases,
        )

    def test_unknown_uid_fails(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(uid=None),
        )
        resp = self.make_request()
        self.assert_error_response(resp, ['account.not_found'])

    def test_grant_missing_fails(self):
        userinfo_response = self.default_userinfo_response()
        self.set_and_serialize_userinfo(userinfo_response)
        self.setup_grants(ALIASES_BASE_GRANT)
        resp = self.make_request()
        self.assert_error_response(resp, ['access.denied'], status_code=403)

    def test_delete_pdddomain_alias_ok(self):
        userinfo_response = self.default_userinfo_response(
            aliases={
                'portal': TEST_LOGIN,
                'pdd': TEST_PDD_LOGIN,
            },
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            userinfo_response,
        )
        self.setup_grants(ALIASES_BASE_GRANT, ALIASES_PDDALIAS_GRANT)
        resp = self.make_request()
        self.assert_ok_response(resp)
        self.check_db_ok(centraldb_query_count=2, alias=None)
        self.env.statbox.assert_has_written(
            [
                self.env.statbox.entry(
                    'aliases_removed',
                    uid=str(TEST_PDD_UID),
                    type=str(ANT['pdd']),
                    _exclude=['domain_id'],
                ),
            ],
        )

    def test_delete_not_existed_pdddomain(self):
        userinfo_response = self.default_userinfo_response()
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            userinfo_response,
        )
        self.setup_grants(ALIASES_BASE_GRANT, ALIASES_PDDALIAS_GRANT)
        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['alias.not_found'],
        )


class BasePddTestAccountAliasView(BaseTestAccountAliasView):
    def check_events_ok(self, alias_op='alias.pddalias.add',
                        alias=TEST_ADDITIONAL_PDD_ALIAS_SERIALIZED):
        self.assert_events_are_logged(
            self.env.handle_mock,
            {
                'action': 'alias',
                'consumer': 'dev',
                alias_op: alias,
            },
        )

    def default_userinfo_response(self, uid=TEST_PDD_UID, aliases=None, domain=TEST_DOMAIN,
                                  login=TEST_PDD_LOGIN):
        aliases = aliases or dict(pdd=TEST_PDD_LOGIN)
        return blackbox_userinfo_response(
            uid=uid,
            login=login,
            subscribed_to=None,
            dbfields={},
            attributes={},
            aliases=aliases,
            domid=TEST_DOMAIN_ID,
            domain=domain,
        )


@with_settings_hosts(
    MAX_PDD_ALIASES_COUNT=10,
)
class TestAccountPddAliasLoginCreateView(BasePddTestAccountAliasView):

    default_url = '/1/account/%d/alias/pddalias/%s/?consumer=dev' % (TEST_PDD_UID, TEST_ADDITIONAL_LOGIN)
    http_method = 'post'

    def setUp(self):
        super(TestAccountPddAliasLoginCreateView, self).setUp()
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({
                TEST_ADDITIONAL_PDD_LOGIN: 'free',
            }),
        )

    def test_error_unknown_uid_fails(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(uid=None),
        )
        self.setup_grants(
            ALIASES_BASE_GRANT,
            ALIASES_PDDALIAS_GRANT,
        )
        resp = self.make_request()
        self.assert_error_response(resp, ['account.not_found'])

    def test_error_grant_missing_fails(self):
        userinfo_response = self.default_userinfo_response(uid=TEST_PDD_UID)
        self.set_and_serialize_userinfo(userinfo_response)
        self.setup_grants(ALIASES_BASE_GRANT)
        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['access.denied'],
            status_code=403,
        )

    def test_error_create_pddalias_that_exists(self):
        userinfo_response = self.default_userinfo_response()
        self.set_and_serialize_userinfo(userinfo_response)
        self.setup_grants(
            ALIASES_BASE_GRANT,
            ALIASES_PDDALIAS_GRANT,
        )
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({
                TEST_ADDITIONAL_PDD_LOGIN: 'occupied',
            }),
        )

        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['alias.exists'],
        )

    def test_create_pddalias_login_ok(self):
        userinfo_response = self.default_userinfo_response()
        self.set_and_serialize_userinfo(userinfo_response)
        self.setup_grants(
            ALIASES_BASE_GRANT,
            ALIASES_PDDALIAS_GRANT,
        )
        resp = self.make_request()
        self.assert_ok_response(resp)

        self.check_db_ok(
            centraldb_query_count=1,
            field='value',
            alias=TEST_ADDITIONAL_PDD_ALIAS_SERIALIZED,
            uid=TEST_PDD_UID,
        )
        self.check_events_ok(
            alias=TEST_ADDITIONAL_PDD_LOGIN,
            alias_op='alias.pddalias.add',
        )
        self.env.statbox.assert_has_written(
            [
                self.env.statbox.entry(
                    'pddalias_added',
                    login=TEST_ADDITIONAL_LOGIN,
                ),
            ],
        )

    def test_error_create_pddalias_login(self):
        userinfo_response = blackbox_userinfo_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            subscribed_to=None,
            dbfields={},
            attributes={},
        )
        self.set_and_serialize_userinfo(userinfo_response)
        self.setup_grants(
            ALIASES_BASE_GRANT,
            ALIASES_PDDALIAS_GRANT,
        )
        resp = self.make_request()
        self.assert_error_response(resp, ['account.invalid_type'])

    def test_maximum_alises_exceeded_error(self):
        userinfo_response = self.default_userinfo_response(
            aliases={
                'pdd': TEST_PDD_LOGIN,
                'pddalias': [('pdd_alias_%s' % i) for i in range(10)],
            },
        )
        self.set_and_serialize_userinfo(userinfo_response)
        self.setup_grants(
            ALIASES_BASE_GRANT,
            ALIASES_PDDALIAS_GRANT,
        )
        resp = self.make_request()
        self.assert_error_response(resp, ['max_numbers_of_aliases.exceeded'])


class TestAccountPddAliasLoginDeleteView(BasePddTestAccountAliasView):

    default_url = '/1/account/%d/alias/pddalias/%s/' % (TEST_PDD_UID, TEST_ADDITIONAL_LOGIN)
    http_method = 'delete'
    http_query_args = dict(consumer='dev')

    def test_error_delete_pddalias_not_alias(self):
        userinfo_response = self.default_userinfo_response()
        self.set_and_serialize_userinfo(userinfo_response)
        self.setup_grants(
            ALIASES_BASE_GRANT,
            ALIASES_PDDALIAS_GRANT,
        )
        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['alias.not_found'],
        )

    def test_error_delete_main_pdd_alias(self):
        userinfo_response = self.default_userinfo_response(
            aliases={
                'pdd': TEST_PDD_LOGIN,
                'pddalias': [
                    TEST_ADDITIONAL_PDD_LOGIN,
                ],
            },
        )
        self.set_and_serialize_userinfo(userinfo_response)
        self.setup_grants(
            ALIASES_BASE_GRANT,
            ALIASES_PDDALIAS_GRANT,
        )
        resp = self.make_request(url='/1/account/%d/alias/pddalias/%s/' % (TEST_PDD_UID, TEST_PDD_LOGIN.split('@')[0]))
        self.assert_error_response(
            resp,
            ['alias.not_found'],
        )

    def test_delete_pddalias_login_ok(self):
        userinfo_response = self.default_userinfo_response(
            aliases={
                'pdd': TEST_PDD_LOGIN,
                'pddalias': [
                    TEST_ADDITIONAL_PDD_LOGIN,
                ],
            },
        )
        self.set_and_serialize_userinfo(userinfo_response)
        self.setup_grants(
            ALIASES_BASE_GRANT,
            ALIASES_PDDALIAS_GRANT,
        )
        resp = self.make_request()
        self.assert_ok_response(resp)

        self.check_db_ok(
            centraldb_query_count=2,
            field='value',
            alias=None,
            uid=TEST_PDD_UID,
            type=str(ANT['pddalias']),
        )
        self.check_events_ok(
            alias=TEST_ADDITIONAL_PDD_LOGIN,
            alias_op='alias.pddalias.rm',
        )
        self.env.statbox.assert_has_written(
            [
                self.env.statbox.entry(
                    'pddalias_removed',
                    login=TEST_ADDITIONAL_LOGIN,
                ),
            ],
        )

    def test_cyrillic_domain(self):
        self.setup_grants(
            ALIASES_BASE_GRANT,
            ALIASES_PDDALIAS_GRANT,
        )

        userinfo_response = self.default_userinfo_response(
            uid=TEST_PDD_UID,
            login=u'билли@виндовс.рф',
            aliases={
                'pdd': u'билли@виндовс.рф',
                'pddalias': [
                    TEST_ADDITIONAL_PDD_LOGIN,
                ],
            },
            domain=u'виндовс.рф',
        )
        self.set_and_serialize_userinfo(userinfo_response)

        rv = self.make_request()

        self.assert_ok_response(rv)

        self.env.db.check(
            'removed_aliases',
            'value',
            '%s/%s' % (u'виндовс.рф'.encode('idna'), TEST_ADDITIONAL_LOGIN),
            uid=TEST_PDD_UID,
            type=ANT['pddalias'],
            db='passportdbcentral',
        )


class BaseTestAccountBankPhoneNumberAliasView(BaseTestAccountAliasView):
    def check_events_ok(self, alias_op='add', alias=TEST_BANK_PHONE.digital, bound_phone_number=None):
        alias_op = 'alias.bank_phonenumber.%s' % alias_op
        events = []
        if bound_phone_number:
            events = [
                {'name': 'phone.1.action', 'value': 'created'},
                {'name': 'phone.1.created', 'value': TimeNow()},
                {'name': 'phone.1.number', 'value': bound_phone_number.e164},
                {'name': 'phone.1.operation.1.action', 'value': 'created'},
                {'name': 'phone.1.operation.1.finished', 'value': TimeNow(offset=60)},
                {'name': 'phone.1.operation.1.security_identity', 'value': bound_phone_number.digital},
                {'name': 'phone.1.operation.1.started', 'value': TimeNow()},
                {'name': 'phone.1.operation.1.type', 'value': 'bind'},
                {'name': 'action', 'value': 'acquire_phone'},
                {'name': 'consumer', 'value': 'dev'},
                {'name': 'phone.1.action', 'value': 'changed'},
                {'name': 'phone.1.bound', 'value': TimeNow()},
                {'name': 'phone.1.confirmed', 'value': TimeNow()},
                {'name': 'phone.1.number', 'value': bound_phone_number.e164},
                {'name': 'phone.1.operation.1.action', 'value': 'deleted'},
                {'name': 'phone.1.operation.1.security_identity', 'value': bound_phone_number.digital},
                {'name': 'phone.1.operation.1.type', 'value': 'bind'},
                {'name': 'action', 'value': 'create_and_bind_phone'},
                {'name': 'consumer', 'value': 'dev'},
            ]

        events.extend([
            {'name': alias_op, 'value': alias},
            {'name': 'action', 'value': 'alias'},
            {'name': 'consumer', 'value': 'dev'},
        ])

        self.assert_events_are_logged_with_order(
            self.env.handle_mock,
            events,
        )

    def default_userinfo_response(self, uid=TEST_UID, aliases=None, login=TEST_LOGIN, phones=None):
        aliases = aliases or dict(portal=TEST_LOGIN)
        return blackbox_userinfo_response(
            uid=uid,
            login=login,
            subscribed_to=None,
            dbfields={},
            attributes={},
            aliases=aliases,
            phones=phones,
        )


class TestAccountBankPhoneNumberAliasCreateView(BaseTestAccountBankPhoneNumberAliasView):

    default_url = '/1/account/%d/alias/bank_phonenumber/?consumer=dev' % TEST_UID
    http_method = 'post'
    http_query_args = dict(
        phone_number=TEST_BANK_PHONE_NUMBER,
    )

    def test_unknown_uid_fails(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(uid=None),
        )
        resp = self.make_request()
        self.assert_error_response(resp, ['account.not_found'])

    def test_create_bank_phonenumber_alias_with_phone_number_ok(self):
        userinfo_response = self.default_userinfo_response()
        self.env.blackbox.set_blackbox_response_side_effect(
            'userinfo',
            [
                userinfo_response,
                self.default_userinfo_response(uid=None),
            ],
        )
        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response([]),
        )
        self.env.db.serialize(userinfo_response)
        self.setup_grants(ALIASES_BASE_GRANT, ALIAS_BANK_PHONENUMBER_GRANT)

        resp = self.make_request()

        self.assert_ok_response(resp)
        self.check_db_ok(
            centraldb_query_count=2,
            sharddb_query_count=7,
            field='bank_phonenumber',
            alias=TEST_BANK_PHONE.digital,
        )
        self.check_events_ok(bound_phone_number=TEST_BANK_PHONE)
        self.env.statbox.assert_has_written(
            [
                self.env.statbox.entry(
                    'phone_operation_created',
                    number=TEST_BANK_PHONE.masked_format_for_statbox,
                ),
                self.env.statbox.entry('phone_bound'),
                self.env.statbox.entry(
                    'phone_confirmed',
                    number=TEST_BANK_PHONE.masked_format_for_statbox,
                ),
                self.env.statbox.entry(
                    'simple_phone_bound',
                    number=TEST_BANK_PHONE.masked_format_for_statbox,
                ),
                self.env.statbox.entry('bank_phonenumber_alias_added'),
            ],
        )

    def test_create_bank_phonenumber_alias_with_phone_id_ok(self):
        self.http_query_args = dict(
            phone_id=TEST_PHONE_ID,
        )

        userinfo_response = self.default_userinfo_response(
            phones=[{
                'id': TEST_PHONE_ID,
                'number': TEST_BANK_PHONE.e164,
                'created': datetime.now(),
                'confirmed': datetime.now(),
                'bound': datetime.now(),
            }]
        )
        self.env.blackbox.set_blackbox_response_side_effect(
            'userinfo',
            [
                userinfo_response,
                self.default_userinfo_response(uid=None),
            ],
        )
        self.env.db.serialize(userinfo_response)

        self.setup_grants(ALIASES_BASE_GRANT, ALIAS_BANK_PHONENUMBER_GRANT)
        resp = self.make_request()
        self.assert_ok_response(resp)
        self.check_db_ok(
            centraldb_query_count=1,
            field='bank_phonenumber',
            alias=TEST_BANK_PHONE.digital,
        )
        self.check_events_ok()
        self.env.statbox.assert_has_written(
            [
                self.env.statbox.entry('bank_phonenumber_alias_added'),
            ],
        )

    def test_create_bank_phonenumber_alias_with_already_existing_phone_number_ok(self):
        userinfo_response = self.default_userinfo_response(
            phones=[{
                'id': 1,
                'number': TEST_BANK_PHONE.e164,
                'created': datetime.now(),
                'confirmed': datetime.now(),
                'bound': datetime.now(),
            }]
        )
        self.env.blackbox.set_blackbox_response_side_effect(
            'userinfo',
            [
                userinfo_response,
                self.default_userinfo_response(uid=None),
            ],
        )
        self.env.db.serialize(userinfo_response)

        self.setup_grants(ALIASES_BASE_GRANT, ALIAS_BANK_PHONENUMBER_GRANT)
        resp = self.make_request()
        self.assert_ok_response(resp)
        self.check_db_ok(
            centraldb_query_count=1,
            field='bank_phonenumber',
            alias=TEST_BANK_PHONE.digital,
        )
        self.check_events_ok()
        self.env.statbox.assert_has_written(
            [
                self.env.statbox.entry('bank_phonenumber_alias_added'),
            ],
        )

    def test_bank_phonenumber_alias_exists(self):
        userinfo_response = self.default_userinfo_response(
            aliases={
                'portal': TEST_LOGIN,
                'bank_phonenumber': TEST_BANK_PHONE_NUMBER_OTHER,
            },
        )
        self.env.blackbox.set_blackbox_response_side_effect(
            'userinfo',
            [
                userinfo_response,
                self.default_userinfo_response(),
            ],
        )
        self.env.db.serialize(userinfo_response)

        self.setup_grants(ALIASES_BASE_GRANT, ALIAS_BANK_PHONENUMBER_GRANT)
        resp = self.make_request()
        self.assert_error_response(resp, ['alias.exists'])

    def test_bank_phonenumber_not_unique_fails(self):
        # ЧЯ ответит не пустым значением и в проверке на уникальность, поэтому не unique
        userinfo_response = self.default_userinfo_response()
        self.set_and_serialize_userinfo(userinfo_response)
        self.setup_grants(ALIASES_BASE_GRANT, ALIAS_BANK_PHONENUMBER_GRANT)

        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['alias.notavailable'],
        )

    def test_create_bank_phonenumber_alias_with_not_bound_phone_id_fails(self):
        self.http_query_args = dict(
            phone_id=TEST_PHONE_ID,
        )

        userinfo_response = self.default_userinfo_response(
            phones=[{
                'id': 12,
                'number': TEST_BANK_PHONE.e164,
                'created': datetime.now(),
                'confirmed': datetime.now(),
                'bound': datetime.now(),
            }]
        )
        self.env.blackbox.set_blackbox_response_side_effect(
            'userinfo',
            [
                userinfo_response,
                self.default_userinfo_response(uid=None),
            ],
        )

        self.setup_grants(ALIASES_BASE_GRANT, ALIAS_BANK_PHONENUMBER_GRANT)

        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['phone_id.not_bound'],
        )

    def test_create_bank_phonenumber_alias_for_federal_account_fails(self):
        """Проверка ошибки при попытке добавить банковский телефон с федерал аккаунта."""
        userinfo_response = self.default_userinfo_response(
            aliases={
                'pdd': TEST_PDD_LOGIN,
                'federal': '1/login',
            },
            phones=[{
                'id': TEST_PHONE_ID,
                'number': TEST_BANK_PHONE.e164,
                'created': datetime.now(),
                'confirmed': datetime.now(),
                'bound': datetime.now(),
            }]
        )
        self.env.blackbox.set_blackbox_response_side_effect(
            'userinfo',
            [
                userinfo_response,
                self.default_userinfo_response(uid=None),
            ],
        )

        self.setup_grants(ALIASES_BASE_GRANT, ALIAS_BANK_PHONENUMBER_GRANT)
        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['account.invalid_type'],
        )

    def test_create_bank_phonenumber_alias_for_pdd_account_fails(self):
        """Проверка ошибки при попытке добавить банковский телефон с ПДД аккаунта."""
        userinfo_response = self.default_userinfo_response(
            aliases={
                'pdd': TEST_PDD_LOGIN,
            },
            phones=[{
                'id': TEST_PHONE_ID,
                'number': TEST_BANK_PHONE.e164,
                'created': datetime.now(),
                'confirmed': datetime.now(),
                'bound': datetime.now(),
            }]
        )
        self.env.blackbox.set_blackbox_response_side_effect(
            'userinfo',
            [
                userinfo_response,
                self.default_userinfo_response(uid=None),
            ],
        )

        self.setup_grants(ALIASES_BASE_GRANT, ALIAS_BANK_PHONENUMBER_GRANT)
        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['account.invalid_type'],
        )


class TestAccountBankPhoneNumberAliasDeleteView(BaseTestAccountBankPhoneNumberAliasView):

    default_url = '/1/account/%d/alias/bank_phonenumber/?consumer=dev' % TEST_UID
    http_method = 'delete'

    def test_unknown_uid_fails(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(uid=None),
        )
        resp = self.make_request()
        self.assert_error_response(resp, ['account.not_found'])

    def test_delete_bank_phonenumber_alias_ok(self):
        userinfo_response = self.default_userinfo_response(
            aliases={
                'portal': TEST_LOGIN,
                'bank_phonenumber': TEST_BANK_PHONE_NUMBER_OTHER,
            },
            phones=[{
                'id': 1,
                'number': TEST_BANK_PHONE.e164,
                'created': datetime.now(),
                'confirmed': datetime.now(),
                'bound': datetime.now(),
            }]
        )
        self.set_and_serialize_userinfo(userinfo_response)
        self.setup_grants(ALIASES_BASE_GRANT, ALIAS_BANK_PHONENUMBER_GRANT)
        resp = self.make_request()
        self.assert_ok_response(resp)
        self.check_db_ok(centraldb_query_count=2, field='bank_phonenumber')
        self.check_events_ok(alias_op='rm', alias='-')
        self.env.statbox.assert_has_written(
            [
                self.env.statbox.entry('bank_phonenumber_alias_removed'),
            ],
        )
