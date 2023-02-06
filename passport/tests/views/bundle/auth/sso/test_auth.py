# -*- coding: utf-8 -*-
from base64 import (
    b64decode,
    b64encode,
)
from datetime import datetime
import json
import zlib

import mock
from nose.tools import (
    eq_,
    ok_,
)
from nose_parameterized import parameterized
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.auth.base_test_data import (
    TEST_HOST,
    TEST_PDD_UID,
    TEST_USER_AGENT,
    TEST_USER_IP,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_hosted_domains_response,
    blackbox_loginoccupation_response,
    blackbox_userinfo_response,
)
from passport.backend.core.builders.federal_configs_api import FederalConfigsApiNotFoundError
from passport.backend.core.builders.federal_configs_api.faker import federal_config_ok
from passport.backend.core.conf import settings
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)
from passport.backend.utils.string import smart_text
from six.moves.urllib.parse import (
    parse_qs,
    urlparse,
)

from .base_test_data import (
    TEST_EMAIL,
    TEST_FEDERAL_ALIAS_VALUE,
    TEST_IDP_DOMAIN,
    TEST_IDP_DOMAIN_ID,
    TEST_IDP_SSO_NETLOC,
    TEST_LOGOUT_REQUEST,
    TEST_NAME_ID,
    TEST_PDD_ALIAS_VALUE,
    TEST_RELAYSTATE,
    TEST_SAML_RESPONSE,
    TEST_TRACK,
)


@with_settings_hosts()
class BaseTestSSO(BaseBundleTestViews):
    action = None
    consumer = 'dev'

    http_headers = dict(
        host=TEST_HOST,
        user_agent=TEST_USER_AGENT,
        user_ip=TEST_USER_IP,
    )

    mocked_grants = ['auth_by_sso.base']

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grant_list(self.mocked_grants)
        self.setup_statbox_templates()
        self.env.federal_configs_api.set_response_value('config_by_domain_id', federal_config_ok())
        self.env.federal_configs_api.set_response_value('config_by_entity_id', federal_config_ok())

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        self.http_query_args.update({'track_id': self.track_id})
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.user_entered_login = TEST_NAME_ID

        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            json.dumps({'users': [{'id': '', 'uid': {}}]}),
        )
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(
                domain=TEST_IDP_DOMAIN,
                domid=TEST_IDP_DOMAIN_ID,
                is_enabled=True,
            ),
        )

    def tearDown(self):
        del self.track_manager
        self.env.stop()
        del self.env

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'local_base',
            ip=TEST_USER_IP,
            consumer=self.consumer,
            user_agent=TEST_USER_AGENT,
        )
        self.env.statbox.bind_entry(
            'local_sso_base',
            _inherit_from=['local_base'],
            mode='auth_by_sso',
            action=self.action,
            saml_idp_domain=TEST_IDP_DOMAIN,
        )
        self.env.statbox.bind_entry(
            'success',
            _inherit_from=['local_sso_base'],
            status='success',
        )
        self.env.statbox.bind_entry(
            'error',
            _inherit_from=['local_sso_base'],
            status='error',
        )

    def assert_statbox_clear(self):
        self.check_statbox_log_entries(self.env.statbox_handle_mock, [])


class TestSSOSubmit(BaseTestSSO):
    http_method = 'get'
    default_url = '/1/bundle/auth/sso/submit/'
    action = 'create_sso_samlrequest'

    def assert_track_not_changed(self):
        track = self.track_manager.read(self.track_id)
        ok_(not track.uid)
        ok_(not track.oauth_code_challenge)
        ok_(not track.oauth_code_challenge_method)

    def test_ok(self):
        resp = self.make_request()
        self.assert_ok_response(resp, redirect_to=mock.ANY)
        self.assert_track_not_changed()
        track = self.track_manager.read(self.track_id)
        eq_(track.domain, TEST_IDP_DOMAIN)

        redirect_url = urlparse(resp.json['redirect_to'])
        eq_(redirect_url.netloc, TEST_IDP_SSO_NETLOC)
        query_string = parse_qs(redirect_url.query)
        saml_request = zlib.decompress(b64decode(query_string['SAMLRequest'][0]), -15).decode('utf-8')
        ok_('ID="track_{}"'.format(self.track_id) in saml_request)
        ok_('ForceAuthn="true"' in saml_request)
        ok_('AssertionConsumerServiceURL="{}"'.format(settings.SAMLRESPONSE_RECEIVER_URL_TEMPLATE % TEST_HOST) in saml_request)
        eq_(query_string['RelayState'][0], settings.SAMLRESPONSE_RECEIVER_URL_TEMPLATE % TEST_HOST)

        self.env.statbox.assert_has_written(
            self.env.statbox.entry(
                'success',
                track_id=self.track_id,
            ),
        )

    def test_ok_with_code_challenge(self):
        resp = self.make_request(query_args=dict(code_challenge='challenge', code_challenge_method='S256'))
        self.assert_ok_response(resp, redirect_to=mock.ANY)
        track = self.track_manager.read(self.track_id)
        eq_(track.oauth_code_challenge, 'challenge')
        eq_(track.oauth_code_challenge_method, 'S256')

        self.env.statbox.assert_has_written(
            self.env.statbox.entry(
                'success',
                track_id=self.track_id,
            ),
        )

    @parameterized.expand([
        (None,),
        ('vasily@any_domain_not_supported.tr',),
        ('vasya_pupkin',),
        ('@@@@@',),
        ('',),
    ])
    def test_any_invalid_domain_error(self, login):
        # этот ответ ЧЯ нужен только для 'vasily@any_domain_not_supported.tr', так как остальные случаи ломаются раньше
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(
                domain=TEST_IDP_DOMAIN,
                domid=TEST_IDP_DOMAIN_ID + 1,  # суть теста в том что приходит id который не поддерживает sso
                is_enabled=True,
            ),
        )
        self.env.federal_configs_api.set_response_side_effect('config_by_domain_id', FederalConfigsApiNotFoundError())

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.user_entered_login = login
        resp = self.make_request()
        self.assert_error_response(resp, ['domain.not_found'])
        self.assert_track_not_changed()
        self.assert_statbox_clear()


class TestSSOCommit(BaseTestSSO):
    http_method = 'post'
    default_url = '/1/bundle/auth/sso/commit/'
    action = 'processing_sso_samlresponse'

    http_query_args = dict(
        saml_response=TEST_SAML_RESPONSE,
        relay_state=TEST_RELAYSTATE,
    )

    def setUp(self):
        super(TestSSOCommit, self).setUp()
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.domain = TEST_IDP_DOMAIN
        # ответ считается валидным (каждый saml response имеет время действия, и как минимум по этому параметру он
        # не пройдет валидацию иначе)
        self.response_is_valid_mock = mock.Mock(return_value=True)
        self.response_is_valid_patch = mock.patch(
            'onelogin.saml2.response.OneLogin_Saml2_Response.is_valid',
            self.response_is_valid_mock,
        )
        # в saml response зашит другой трек, который сейчас не существует, но в проде (если пользователь прошел
        # полный цикл авторизации) он нормальный
        self.get_track_id_patch = mock.patch(
            'passport.backend.api.views.bundle.auth.sso.controllers.CommitToSSOLoginView.get_track_id',
            return_value=self.track_id,
        )
        self.patches = [
            self.response_is_valid_patch,
            self.get_track_id_patch,
        ]
        for patch in self.patches:
            patch.start()

    def tearDown(self):
        for patch in reversed(self.patches):
            patch.stop()
        super(TestSSOCommit, self).tearDown()

    def setup_statbox_templates(self):
        super(TestSSOCommit, self).setup_statbox_templates()
        self.env.statbox.bind_entry(
            'account_modification',
            _inherit_from=['account_modification', 'local_base'],
            _exclude=['mode'],
            old='-',
            operation='created',
            uid=str(TEST_PDD_UID),
        )

    def check_statbox_ok(self, with_account_created=False, ready_to_issue_cookies=True, **kwargs):
        entries = []
        if with_account_created:
            entries.extend([
                self.env.statbox.entry(
                    'account_modification',
                    operation='created',
                    entity='account.disabled_status',
                    new='enabled',
                ),
                self.env.statbox.entry(
                    'account_modification',
                    operation='created',
                    entity='account.mail_status',
                    new='active',
                ),
                self.env.statbox.entry(
                    'account_modification',
                    operation='added',
                    entity='aliases',
                    type='7',
                    value=TEST_EMAIL,
                    _exclude=['old'],
                ),
                self.env.statbox.entry(
                    'account_modification',
                    entity='aliases',
                    type='24',
                    operation='added',
                    value=TEST_FEDERAL_ALIAS_VALUE,
                    _exclude=['old'],
                ),
                self.env.statbox.entry(
                    'account_modification',
                    entity='person.firstname',
                    new=smart_text('Огульгерек'),
                ),
                self.env.statbox.entry(
                    'account_modification',
                    entity='person.lastname',
                    new=smart_text('Бердымухамедова'),
                ),
                self.env.statbox.entry(
                    'account_modification',
                    entity='person.language',
                    new='ru',
                ),
                self.env.statbox.entry(
                    'account_modification',
                    entity='person.country',
                    new='ru',
                ),
                self.env.statbox.entry(
                    'account_modification',
                    entity='person.fullname',
                    new=smart_text('Огульгерек Бердымухамедова'),
                ),
                self.env.statbox.entry(
                    'account_modification',
                    entity='domain_name',
                    new=TEST_IDP_DOMAIN,
                ),
                self.env.statbox.entry(
                    'account_modification',
                    entity='domain_id',
                    new=str(TEST_IDP_DOMAIN_ID),
                ),
                self.env.statbox.entry(
                    'account_modification',
                    action='account_register_federal',
                    entity='karma',
                    destination='frodo',
                    new='0',
                    suid='1',
                    registration_datetime=DatetimeNow(convert_to_datetime=True),
                    _exclude=['operation'],
                    login=TEST_NAME_ID,
                ),
                self.env.statbox.entry(
                    'account_modification',
                    sid='2',
                    suid='1',
                    entity='subscriptions',
                    operation='added',
                    _exclude=['old'],
                ),
            ])
        if ready_to_issue_cookies:
            entries.extend([
                self.env.statbox.entry(
                    'success',
                    name_id=TEST_NAME_ID,
                    track_id=kwargs.get('track_id'),
                    uid=str(TEST_PDD_UID),
                ),
            ])
        self.env.statbox.assert_has_written(entries)

    def assert_ok_db(self):
        eq_(self.env.db.query_count('passportdbcentral'), 4)
        eq_(self.env.db.query_count('passportdbshard2'), 1)

        self.env.db.check('aliases', 'federal', TEST_FEDERAL_ALIAS_VALUE, uid=TEST_PDD_UID, db='passportdbcentral')
        self.env.db.check('aliases', 'pdd', TEST_PDD_ALIAS_VALUE, uid=TEST_PDD_UID, db='passportdbcentral')
        self.env.db.check('attributes', 'subscription.mail.status', '1', uid=TEST_PDD_UID, db='passportdbshard2')
        self.env.db.check('attributes', 'account.registration_datetime', TimeNow(), uid=TEST_PDD_UID, db='passportdbshard2')
        self.env.db.check_missing('attributes', 'account.user_defined_login', uid=TEST_PDD_UID, db='passportdbshard2')
        self.env.db.check_missing('attributes', 'account.is_disabled', uid=TEST_PDD_UID, db='passportdbshard2')
        self.env.db.check_missing('attributes', 'karma.value', uid=TEST_PDD_UID, db='passportdbshard2')
        self.env.db.check('attributes', 'person.firstname', 'Огульгерек', uid=TEST_PDD_UID, db='passportdbshard2')
        self.env.db.check('attributes', 'person.lastname', 'Бердымухамедова', uid=TEST_PDD_UID, db='passportdbshard2')
        self.env.db.check_missing('attributes', 'person.gender', uid=TEST_PDD_UID, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'person.birthday', uid=TEST_PDD_UID, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'person.country', uid=TEST_PDD_UID, db='passportdbshard2')

    def test_register_ok(self):
        # ответ на поиск такой почты среди занятых
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({TEST_EMAIL: 'free'}),
        )
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            state='complete_federal',
            account=dict(
                uid=TEST_PDD_UID,
                login=TEST_NAME_ID,
                display_login='',
            ),
            track_id=self.track_id,
        )
        self.assert_ok_db()
        self.check_statbox_ok(
            with_account_created=True,
            ready_to_issue_cookies=False,
            track_id=self.track_id,
        )
        track = self.track_manager.read(self.track_id)
        eq_(track.uid, str(TEST_PDD_UID))
        eq_(track.allow_authorization, False)
        eq_(track.is_successful_registered, True)
        eq_(track.auth_method, settings.AUTH_METHOD_SAML_SSO)
        eq_(track.human_readable_login, TEST_NAME_ID)
        eq_(track.machine_readable_login, TEST_NAME_ID)
        ok_(track.submit_response_cache is not None)

    def test_account_exists_ok(self):
        # ответ на поиск по алиасу
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_PDD_UID,
                login=TEST_EMAIL,
                subscribed_to=[102],  # is_pdd_agreement_accepted
                aliases={
                    'pdd': TEST_EMAIL,
                    'federal': TEST_NAME_ID,
                },
            ),
        )
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            track_id=self.track_id,
        )
        self.check_statbox_ok(
            with_account_created=False,
            ready_to_issue_cookies=True,
            track_id=self.track_id,
        )
        track = self.track_manager.read(self.track_id)
        eq_(track.uid, str(TEST_PDD_UID))
        eq_(track.allow_authorization, True)
        eq_(track.is_successful_registered, None)
        eq_(track.auth_method, settings.AUTH_METHOD_SAML_SSO)

    def test_account_not_exists_jit_provisioning_disabled_error(self):
        self.env.federal_configs_api.set_response_value('config_by_domain_id', federal_config_ok(disable_jit_provisioning=True))

        resp = self.make_request()
        self.assert_error_response(resp, ['saml.registration_not_supported'])
        self.assert_statbox_clear()

    def test_sso_disabled_error(self):
        self.env.federal_configs_api.set_response_value('config_by_domain_id', federal_config_ok(enabled=False))

        resp = self.make_request()
        self.assert_error_response(resp, ['domain.not_found'])
        self.assert_statbox_clear()

    def test_account_exists_but_requires_completion_ok(self):
        # ответ на поиск по алиасу
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_PDD_UID,
                login=TEST_EMAIL,
                aliases={
                    'pdd': TEST_EMAIL,
                    'federal': TEST_NAME_ID,
                },
            ),
        )
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            state='complete_federal',
            account=dict(
                uid=TEST_PDD_UID,
                login=TEST_EMAIL,
                display_login=TEST_EMAIL,
            ),
            track_id=self.track_id,
        )
        self.check_statbox_ok(
            with_account_created=False,
            ready_to_issue_cookies=False,
            track_id=self.track_id,
        )
        track = self.track_manager.read(self.track_id)
        eq_(track.uid, str(TEST_PDD_UID))
        eq_(track.allow_authorization, False)
        eq_(track.is_successful_registered, None)
        eq_(track.auth_method, settings.AUTH_METHOD_SAML_SSO)

    def test_one_issuer_two_domains_ok(self):
        # IdP обслуживает в том числе домен any-other-domain.com
        other_domain = 'any-other-domain.com'

        # ответ на поиск такой почты среди занятых
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({'berd_email@' + other_domain: 'free'}),
        )
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(
                domain=other_domain,
                domid=TEST_IDP_DOMAIN_ID,
                is_enabled=True,
            ),
        )
        reprocessed_response = b64encode(b64decode(TEST_SAML_RESPONSE).replace(
            '<Attribute Name="User.EmailAddress"><AttributeValue>{}</AttributeValue></Attribute>'.format(TEST_EMAIL),
            '<Attribute Name="User.EmailAddress"><AttributeValue>berd_email@{}</AttributeValue></Attribute>'.format(other_domain),
            1))

        resp = self.make_request(
            query_args=dict(
                saml_response=reprocessed_response,
                relay_state=TEST_RELAYSTATE,
            ),
        )
        self.assert_ok_response(
            resp,
            state='complete_federal',
            account=dict(
                uid=TEST_PDD_UID,
                login=TEST_NAME_ID + '@' + other_domain,
                display_login='',
            ),
            track_id=self.track_id,
        )

    def test_invalid_signature_error(self):
        self.response_is_valid_patch.stop()
        with mock.patch(
            'onelogin.saml2.response.OneLogin_Saml2_Response.get_error',
            mock.Mock(return_value='Signature validation failed. SAML Response rejected'),
        ):
            resp = self.make_request()
        self.assert_error_response(resp, ['saml.invalid_signature'])

    def test_invalid_email_error(self):
        reprocessed_response = b64encode(b64decode(TEST_SAML_RESPONSE).replace(
            '<Attribute Name="User.EmailAddress"><AttributeValue>{}</AttributeValue></Attribute>'.format(TEST_EMAIL),
            '<Attribute Name="User.EmailAddress"><AttributeValue>{}</AttributeValue></Attribute>'.format(TEST_EMAIL[:2] + 'д' + TEST_EMAIL[2:]),  # вставили русскую букву
            1))

        resp = self.make_request(
            query_args=dict(
                saml_response=reprocessed_response,
                relay_state=TEST_RELAYSTATE,
            ),
        )
        self.assert_error_response(resp, ['email.invalid'])

    def test_email_unsupportable_domain_error(self):
        reprocessed_response = b64encode(b64decode(TEST_SAML_RESPONSE).replace(
            '<Attribute Name="User.EmailAddress"><AttributeValue>{}</AttributeValue></Attribute>'.format(TEST_EMAIL),
            '<Attribute Name="User.EmailAddress"><AttributeValue>{}</AttributeValue></Attribute>'.format('@'.join(map(lambda x: x[1:], TEST_EMAIL.split('@')))),
            1))

        resp = self.make_request(
            query_args=dict(
                saml_response=reprocessed_response,
                relay_state=TEST_RELAYSTATE,
            ),
        )
        self.assert_error_response(resp, ['email.unsupportable_domain'])

    def test_invalid_name_id_error(self):
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({TEST_EMAIL: 'free'}),
        )
        reprocessed_response = b64encode(b64decode(TEST_SAML_RESPONSE).replace(
            '<NameID Format="urn:oasis:names:tc:SAML:2.0:nameid-format:transient">{}</NameID>'.format(TEST_NAME_ID),
            '<NameID Format="urn:oasis:names:tc:SAML:2.0:nameid-format:transient">{}</NameID>'.format(TEST_NAME_ID[:2] + 'д' + TEST_NAME_ID[2:]),  # вставили русскую букву
            1))

        resp = self.make_request(
            query_args=dict(
                saml_response=reprocessed_response,
                relay_state=TEST_RELAYSTATE,
            ),
        )
        self.assert_error_response(resp, ['login.notavailable'])

    def test_no_mail_in_response_error(self):
        # Отвечаем что пользователь без почты, почта запрашивается первой из этого метода
        with mock.patch('passport.backend.api.views.bundle.auth.sso.controllers.CommitToSSOLoginView.get_attribute_from_response', return_value=None):
            resp = self.make_request()
        self.assert_error_response(resp, ['email.no_in_response'])
        self.assert_statbox_clear()

    def test_no_nameid_in_response_error(self):
        reprocessed_response = b64encode(b64decode(TEST_SAML_RESPONSE).replace('<NameID Format="urn:oasis:names:tc:SAML:2.0:nameid-format:transient">berd@sso-adfs-test-domain.com</NameID>', '', 1))
        resp = self.make_request(
            query_args=dict(
                saml_response=reprocessed_response,
                relay_state=TEST_RELAYSTATE,
            ),
        )
        self.assert_error_response(resp, ['samlresponse.invalid'])
        self.env.statbox.assert_has_written(
            self.env.statbox.entry(
                'error',
                error='38 NameID not found in the assertion of the Response',
                _exclude=['saml_idp_domain'],
            ),
        )

    def test_invalid_base64_error(self):
        resp = self.make_request(
            query_args={
                'saml_response': TEST_SAML_RESPONSE[:-66],
                'relay_state': TEST_RELAYSTATE,
            },
        )
        self.assert_error_response(resp, ['samlresponse.invalid'])
        self.assert_statbox_clear()

    def test_invalid_xml_response_error(self):
        resp = self.make_request(
            query_args={
                'saml_response': b64encode('Цой Жив!'),
                'relay_state': TEST_RELAYSTATE,
            },
        )
        self.assert_error_response(resp, ['samlresponse.invalid'])
        self.assert_statbox_clear()

    def test_invalid_response_error(self):
        self.response_is_valid_mock.return_value = False
        resp = self.make_request()
        self.assert_error_response(resp, ['samlresponse.invalid'])
        self.env.statbox.assert_has_written(
            self.env.statbox.entry(
                'error',
                error='Not authorized: [invalid_response]',
                track_id=self.track_id,
            ),
        )

    def test_invalid_track_format_error(self):
        # трек в ответе не содержит приставки 'track_'
        self.get_track_id_patch.stop()
        reprocessed_response = b64encode(b64decode(TEST_SAML_RESPONSE).replace('track_{}'.format(TEST_TRACK), TEST_TRACK, 1))

        resp = self.make_request(
            query_args=dict(
                saml_response=reprocessed_response,
                relay_state=TEST_RELAYSTATE,
            ),
        )
        self.assert_error_response(resp, ['samlresponse.invalid'])
        self.assert_statbox_clear()

    def test_adfs_returned_error(self):
        self.response_is_valid_patch.stop()

        reprocessed_response = b64encode(b64decode(TEST_SAML_RESPONSE).replace(
            '<samlp:StatusCode Value="urn:oasis:names:tc:SAML:2.0:status:Success" />',
            '<samlp:StatusCode Value="urn:oasis:names:tc:SAML:2.0:status:Requester" /><samlp:StatusMessage>ooooppppsss!</samlp:StatusMessage>',
            1))
        resp = self.make_request(
            query_args=dict(
                saml_response=reprocessed_response,
                relay_state=TEST_RELAYSTATE,
            ),
        )
        self.assert_error_response(resp, ['saml.request_your_admin'])
        self.env.statbox.assert_has_written(
            self.env.statbox.entry(
                'error',
                error='Not authorized: [invalid_response]',
                track_id=self.track_id,
            ),
        )


class TestSSOLogout(BaseTestSSO):
    http_method = 'post'
    default_url = '/1/bundle/auth/sso/logout/'
    action = 'logout_sso_idp_initiated'

    http_query_args = dict(
        saml_request=TEST_LOGOUT_REQUEST,
        relay_state=TEST_RELAYSTATE,
    )

    def setUp(self):
        super(TestSSOLogout, self).setUp()
        # ответ считается валидным (каждый saml request имеет время действия, и как минимум по этому параметру он
        # не пройдет валидацию иначе)
        self.response_is_valid_mock = mock.Mock(return_value=True)
        self.response_is_valid_patch = mock.patch(
            'onelogin.saml2.logout_request.OneLogin_Saml2_Logout_Request.is_valid',
            self.response_is_valid_mock,
        )
        self.patches = [
            self.response_is_valid_patch,
        ]
        for patch in self.patches:
            patch.start()

    def setup_statbox_templates(self):
        super(TestSSOLogout, self).setup_statbox_templates()
        self.env.statbox.bind_entry(
            'account_modification',
            _inherit_from=['account_modification', 'local_base'],
            _exclude=['mode'],
            operation='updated',
            uid=str(TEST_PDD_UID),
        )

    def test_logout_ok(self):
        # ответ на поиск по алиасу
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_PDD_UID,
                login=TEST_EMAIL,
                aliases={
                    'pdd': TEST_EMAIL,
                    'federal': TEST_NAME_ID,
                },
            ),
        )

        resp = self.make_request()
        self.assert_ok_response(resp, redirect_to=mock.ANY)

        redirect_url = urlparse(resp.json['redirect_to'])
        eq_(redirect_url.netloc, TEST_IDP_SSO_NETLOC)
        query_string = parse_qs(redirect_url.query)
        saml_response = zlib.decompress(b64decode(query_string['SAMLResponse'][0]), -15).decode('utf-8')
        ok_('<samlp:StatusCode Value="urn:oasis:names:tc:SAML:2.0:status:Success" />' in saml_response)

        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'account_modification',
                entity='account.global_logout_datetime',
                new=DatetimeNow(convert_to_datetime=True),
                old=datetime.fromtimestamp(1).strftime('%Y-%m-%d %H:%M:%S'),
            ),
            self.env.statbox.entry(
                'success',
                uid=str(TEST_PDD_UID),
                _exclude=['saml_idp_domain'],
            ),
        ])

    def test_logout_user_not_exist_error(self):
        resp = self.make_request()
        self.assert_error_response(resp, ['account.not_found'])
        self.env.statbox.assert_has_written(
            self.env.statbox.entry(
                'error',
                error='Logout request failed: user {} not found on domain ids [{}]'.format(TEST_NAME_ID, TEST_IDP_DOMAIN_ID),
                _exclude=['saml_idp_domain'],
            ),
        )

    def test_logout_domain_not_exist_error(self):
        self.env.federal_configs_api.set_response_side_effect('config_by_entity_id', FederalConfigsApiNotFoundError())

        resp = self.make_request()
        self.assert_error_response(resp, ['domain.not_found'])
        self.assert_statbox_clear()

    def test_logout_request_error(self):
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(count=0),
        )

        resp = self.make_request(
            query_args={
                'saml_request': TEST_LOGOUT_REQUEST[:-22],
                'relay_state': TEST_RELAYSTATE,
            },
        )
        self.assert_error_response(resp, ['samlrequest.invalid'])
        self.assert_statbox_clear()

    def test_logout_request_is_not_valid_error(self):
        self.response_is_valid_mock.return_value = False

        resp = self.make_request()
        self.assert_error_response(resp, ['samlrequest.invalid'])
        self.env.statbox.assert_has_written(
            self.env.statbox.entry(
                'error',
                error='Logout request failed: [invalid_logout_request]',
                _exclude=['saml_idp_domain'],
            ),
        )
