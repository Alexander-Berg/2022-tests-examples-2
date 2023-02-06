# -*- coding: utf-8 -*-

from nose.tools import (
    eq_,
    istest,
    nottest,
)
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.views.bundle.constants import (
    BIND_PHONE_OAUTH_SCOPE,
    X_TOKEN_OAUTH_SCOPE,
)
from passport.backend.api.views.bundle.mixins.phone import (
    format_for_android_sms_retriever,
    hash_android_package,
)
from passport.backend.api.views.bundle.phone.controllers_v2 import BIND_OR_CONFIRM_BOUND_STATE
from passport.backend.api.views.bundle.phone.helpers import format_code_by_3
from passport.backend.core.builders.blackbox.constants import (
    BLACKBOX_OAUTH_INVALID_STATUS,
    BLACKBOX_SESSIONID_INVALID_STATUS,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_oauth_response,
    blackbox_phone_bindings_response,
    blackbox_sessionid_multi_response,
    blackbox_userinfo_response,
)
from passport.backend.core.models.phones.faker import (
    assert_simple_phone_being_securified,
    assert_simple_phone_bound,
    build_phone_bound,
    build_secure_phone_being_bound,
    build_securify_operation,
)
from passport.backend.core.test.consts import *
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import (
    settings_context,
    with_settings_hosts,
)
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)
from passport.backend.utils.common import (
    deep_merge,
    merge_dicts,
)

from .base import (
    BaseConfirmCommitterTestCase,
    BaseConfirmSubmitterTestCase,
    CommonSubmitterCommitterTestMixin,
    ConfirmCommitterLocalPhonenumberTestMixin,
    ConfirmCommitterSentCodeTestMixin,
    ConfirmCommitterTestMixin,
    ConfirmSubmitterAccountTestMixin,
    ConfirmSubmitterAlreadyConfirmedPhoneWithNewPhoneTestMixin,
    ConfirmSubmitterLocalPhonenumberMixin,
    ConfirmSubmitterSendSmsTestMixin,
    TEST_HOST,
    TEST_PHONE_ID1,
    TEST_PHONE_NUMBER,
    TEST_SMS_RETRIEVER_TEXT,
    TEST_TAXI_APPLICATION,
    TEST_TOKEN,
    TEST_UID,
    TEST_UID2,
    TEST_USER_IP,
)


TEST_TIME1 = datetime(2015, 1, 2, 5, 1, 5)
TEST_WHITELISTED_CLIENT_ID = 'whitelisted_clid'


class TestBuilder(object):
    __test__ = False

    def __init__(self, env):
        self.env = env

    def setup_account_from_uid(self, userinfo=None, serialize_to_db=True):
        if userinfo is None:
            userinfo = self.build_userinfo()
        userinfo_response = blackbox_userinfo_response(**userinfo)
        self.env.blackbox.set_response_value('userinfo', userinfo_response)
        if serialize_to_db:
            self.env.db.serialize(userinfo_response)

    def setup_account_from_token(self):
        userinfo_args = self.build_userinfo()
        oauth_args = merge_dicts(userinfo_args, dict(scope=X_TOKEN_OAUTH_SCOPE))
        self.env.blackbox.set_response_value('oauth', blackbox_oauth_response(**oauth_args))

    def setup_account_from_session(self):
        userinfo_args = self.build_userinfo()
        sessionid_args = userinfo_args
        self.env.blackbox.set_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                login_id='login-id',
                **sessionid_args
            ),
        )

    def build_userinfo(self,
                       phone_bound=False,
                       secure_phone_being_bound=False,
                       bound_phone_being_securified=False):
        phones = dict()
        if phone_bound:
            phones = build_phone_bound(
                TEST_PHONE_ID1,
                TEST_PHONE_NUMBER.e164,
                phone_created=TEST_TIME1,
                phone_bound=TEST_TIME1,
                phone_confirmed=TEST_TIME1,
            )
        elif secure_phone_being_bound:
            phones = build_secure_phone_being_bound(
                TEST_PHONE_ID1,
                TEST_PHONE_NUMBER.e164,
                operation_id=1,
                phone_created=TEST_TIME1,
            )
        elif bound_phone_being_securified:
            phones = deep_merge(
                build_phone_bound(
                    TEST_PHONE_ID1,
                    TEST_PHONE_NUMBER.e164,
                    phone_created=TEST_TIME1,
                    phone_bound=TEST_TIME1,
                    phone_confirmed=TEST_TIME1,
                ),
                build_securify_operation(
                    operation_id=1,
                    phone_id=TEST_PHONE_ID1,
                ),
            )
        return deep_merge(
            dict(uid=TEST_UID),
            phones,
        )

    def build_phonish_userinfo(self, phone_number=TEST_PHONE_NUMBER):
        return deep_merge(
            dict(
                uid=TEST_UID,
                login=TEST_PHONISH_LOGIN1,
                aliases={'phonish': TEST_PHONISH_LOGIN1},
            ),
            build_phone_bound(
                TEST_PHONE_ID1,
                phone_number.e164,
                phone_created=TEST_TIME1,
                phone_bound=TEST_TIME1,
                phone_confirmed=TEST_TIME1,
            ),
        )

    def setup_oauth_token_is_invalid(self):
        self.env.blackbox.set_response_value('oauth', blackbox_oauth_response(status=BLACKBOX_OAUTH_INVALID_STATUS))

    def setup_oauth_token_no_scope(self, client_id='test_clid'):
        self.env.blackbox.set_response_value('oauth', blackbox_oauth_response(scope='ololo', client_id=client_id))

    def setup_sessionid_is_invalid(self):
        sessionid_args = dict(status=BLACKBOX_SESSIONID_INVALID_STATUS)
        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_multi_response(**sessionid_args))

    def setup_account_no_phone(self):
        userinfo = self.build_userinfo()
        self.setup_account_from_uid(userinfo)

    def setup_account_phone_bound(self):
        userinfo = self.build_userinfo(phone_bound=True)
        self.setup_account_from_uid(userinfo)

    def setup_account_secure_phone_being_bound(self):
        userinfo = self.build_userinfo(secure_phone_being_bound=True)
        self.setup_account_from_uid(userinfo)

    def setup_account_bound_phone_being_securified(self):
        userinfo = self.build_userinfo(bound_phone_being_securified=True)
        self.setup_account_from_uid(userinfo)

    def setup_phonish_account(self, **kwargs):
        userinfo = self.build_phonish_userinfo(**kwargs)
        self.setup_account_from_uid(userinfo)

    def build_oauth_token_headers(self):
        return {
            'Ya-Consumer-Authorization': 'Oauth ' + TEST_TOKEN,
            'Ya-Consumer-Client-Ip': TEST_USER_IP,
        }

    def build_sessionid_headers(self):
        return {
            'Ya-Client-Host': TEST_HOST,
            'Ya-Client-Cookie': 'Session_id=Session_id',
            'Ya-Consumer-Client-Ip': TEST_USER_IP,
        }


class CommitTestBuilder(TestBuilder):
    def setup_account_from_uid(self, *args, **kwargs):
        super(CommitTestBuilder, self).setup_account_from_uid(*args, **kwargs)
        self.setup_phone_bindings()

    def setup_phone_bindings(self):
        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response([]),
        )


@nottest
class CommonBindOrConfirmBoundSubmitTestcase(BaseConfirmSubmitterTestCase,
                                             CommonSubmitterCommitterTestMixin,
                                             ConfirmSubmitterAccountTestMixin,
                                             ConfirmSubmitterSendSmsTestMixin,
                                             ConfirmSubmitterLocalPhonenumberMixin,
                                             ConfirmSubmitterAlreadyConfirmedPhoneWithNewPhoneTestMixin):
    url = '/2/bundle/phone/bind_simple_or_confirm_bound/submit/?consumer=dev'
    specific_grants = {'base'}
    track_state = BIND_OR_CONFIRM_BOUND_STATE

    def setUp(self):
        super(CommonBindOrConfirmBoundSubmitTestcase, self).setUp()
        self.builder = TestBuilder(env=self.env)
        self.setup_default_headers()
        self.setup_default_account()

    def tearDown(self):
        del self.builder
        super(CommonBindOrConfirmBoundSubmitTestcase, self).tearDown()

    def setup_default_headers(self):
        self.base_headers = mock_headers(user_agent='curl')

    def setup_default_account(self):
        self.builder.setup_account_from_uid(serialize_to_db=False)

    def query_params(self, exclude=None, **kwargs):
        base_params = {
            'uid': TEST_UID,
            'number': TEST_PHONE_NUMBER.e164,
            'display_language': 'ru',
            'track_id': self.track_id,
        }
        for key in exclude or []:
            del base_params[key]
        return merge_dicts(base_params, kwargs)

    def build_ok_response(self):
        return self.base_send_code_response

    def build_error_response(self):
        return merge_dicts(
            self.base_submitter_response,
            dict(status='error'),
        )

    def test_uid(self):
        self.builder.setup_account_from_uid()

        rv = self.make_request(data=self.query_params(uid=TEST_UID))

        self.assert_ok_response(rv, **self.build_ok_response())

    def test_uid__without_uid_grant(self):
        self.env.grants.set_grants_return_value(mock_grants(grants={'phone_bundle': ['base']}))
        self.builder.setup_account_from_uid()

        rv = self.make_request(data=self.query_params(uid=TEST_UID))

        self.assert_error_response(rv, ['access.denied'], status_code=403)

    def test_oauth_token(self):
        self.builder.setup_account_from_token()

        rv = self.make_request(
            data=self.query_params(exclude=['uid']),
            headers=self.builder.build_oauth_token_headers(),
        )

        self.assert_ok_response(rv, **self.build_ok_response())

    def test_oauth_token_invalid(self):
        self.builder.setup_oauth_token_is_invalid()

        rv = self.make_request(
            data=self.query_params(exclude=['uid']),
            headers=self.builder.build_oauth_token_headers(),
        )

        self.assert_error_response(rv, ['oauth_token.invalid'], **self.build_error_response())

    def test_oauth_token_no_scope(self):
        self.builder.setup_oauth_token_no_scope()

        rv = self.make_request(
            data=self.query_params(exclude=['uid']),
            headers=self.builder.build_oauth_token_headers(),
        )

        self.assert_error_response(rv, ['oauth_token.invalid'], **self.build_error_response())

    def test_oauth_token_no_scope_but_whitelisted_client(self):
        self.builder.setup_oauth_token_no_scope(client_id=TEST_WHITELISTED_CLIENT_ID)

        rv = self.make_request(
            data=self.query_params(exclude=['uid']),
            headers=self.builder.build_oauth_token_headers(),
        )

        self.assert_ok_response(rv, **self.build_ok_response())

    def test_oauth_token_bind_phone_scope(self):
        self.env.blackbox.set_response_value('oauth', blackbox_oauth_response(scope=BIND_PHONE_OAUTH_SCOPE))

        rv = self.make_request(
            data=self.query_params(exclude=['uid']),
            headers=self.builder.build_oauth_token_headers(),
        )

        self.assert_ok_response(rv, **self.build_ok_response())

    def test_sessionid_code_format(self):
        self.builder.setup_account_from_session()

        rv = self.make_request(
            data=self.query_params(
                code_format='by_3',
                exclude=['uid'],
            ),
            headers=self.builder.build_sessionid_headers(),
        )

        self.assert_ok_response(rv, **self.build_ok_response())

        self.confirmation_code = format_code_by_3(self.confirmation_code)

        requests = self.env.yasms.requests
        eq_(len(requests), 1)
        requests[0].assert_query_contains({
            'phone': TEST_PHONE_NUMBER.e164,
            'text': self.sms_text,
            'identity': 'bind_or_confirm_bound',
        })
        requests[0].assert_post_data_contains({
            'text_template_params': self.sms_text_template_params,
        })

    def test_sessionid(self):
        self.builder.setup_account_from_session()

        with settings_context(PHONE_CONFIRM_CHECK_ANTIFRAUD_SCORE=True):
            rv = self.make_request(
                data=self.query_params(exclude=['uid']),
                headers=self.builder.build_sessionid_headers(),
            )

        self.assert_ok_response(rv, **self.build_ok_response())
        self.assert_antifraud_score_called(login_id='login-id')

    def test_sessionid_invalid(self):
        self.builder.setup_sessionid_is_invalid()

        rv = self.make_request(
            data=self.query_params(exclude=['uid']),
            headers=self.builder.build_sessionid_headers(),
        )

        self.assert_error_response(rv, ['sessionid.invalid'], **self.build_error_response())

    def test_uid_not_in_session(self):
        with self.track_transaction() as track:
            track.uid = str(TEST_UID2)
        self.builder.setup_account_from_session()

        rv = self.make_request(
            data=self.query_params(exclude=['uid']),
            headers=self.builder.build_sessionid_headers(),
        )

        self.assert_error_response(rv, ['track.invalid_state'], **self.build_error_response())

    def test_ok_track(self):
        rv = self.make_request()

        self.assert_ok_response(rv, **self.build_ok_response())

        track = self.track_manager.read(self.track_id)
        self.check_ok_track(track)

    def test_ok_statbox(self):
        rv = self.make_request()

        self.assert_ok_response(rv, **self.build_ok_response())
        self.assert_statbox_ok()

    def test_ok_events(self):
        rv = self.make_request()

        self.assert_ok_response(rv, **self.build_ok_response())
        self.env.event_logger.assert_events_are_logged([])

    def test_phonish__bound_number(self):
        self.builder.setup_phonish_account()

        rv = self.make_request()

        self.assert_ok_response(rv, **self.build_ok_response())

    def test_phonish__not_bound_number(self):
        self.builder.setup_phonish_account(phone_number=TEST_PHONE_NUMBER2)

        rv = self.make_request()

        self.assert_error_response(rv, ['account.invalid_type'], **self.build_error_response())


@istest
@with_settings_hosts(
    SMS_VALIDATION_MAX_SMS_COUNT=3,
    SMS_VALIDATION_RESEND_TIMEOUT=0,
    APP_ID_TO_SMS_ROUTE={TEST_TAXI_APPLICATION: 'taxi'},
    CLIENT_IDS_ALLOWED_TO_BIND_PHONE=[TEST_WHITELISTED_CLIENT_ID],
)
class TestBindOrConfirmBoundSubmit(CommonBindOrConfirmBoundSubmitTestcase):
    pass


@istest
@with_settings_hosts(
    SMS_VALIDATION_MAX_SMS_COUNT=3,
    SMS_VALIDATION_RESEND_TIMEOUT=0,
    APP_ID_TO_SMS_ROUTE={TEST_TAXI_APPLICATION: 'taxi'},
    CLIENT_IDS_ALLOWED_TO_BIND_PHONE=[TEST_WHITELISTED_CLIENT_ID],
    ANDROID_PACKAGE_PREFIXES_WHITELIST={'com.yandex'},
    ANDROID_PACKAGE_PUBLIC_KEY_DEFAULT='public-key',
    ANDROID_PACKAGE_PREFIX_TO_KEY={},
)
class TestBindOrConfirmBoundSubmitForSmsRetriever(CommonBindOrConfirmBoundSubmitTestcase):
    def setUp(self):
        super(TestBindOrConfirmBoundSubmitForSmsRetriever, self).setUp()

        self.package_name = 'com.yandex.passport.testapp1'

        self.setup_statbox_templates(
            sms_retriever_kwargs=dict(
                gps_package_name=self.package_name,
                sms_retriever='1',
            ),
        )

        eq_(hash_android_package(self.package_name, 'public-key'), 'gNNu9q4gcSd')

    @property
    def sms_text(self):
        return format_for_android_sms_retriever(
            TEST_SMS_RETRIEVER_TEXT,
            'gNNu9q4gcSd',
        )

    def query_params(self, **kwargs):
        return super(TestBindOrConfirmBoundSubmitForSmsRetriever, self).query_params(
            gps_package_name=self.package_name,
            **kwargs
        )

@istest
@with_settings_hosts(
    SMS_VALIDATION_MAX_SMS_COUNT=3,
    SMS_VALIDATION_RESEND_TIMEOUT=0,
    APP_ID_TO_SMS_ROUTE={TEST_TAXI_APPLICATION: 'taxi'},
    CLIENT_IDS_ALLOWED_TO_BIND_PHONE=[TEST_WHITELISTED_CLIENT_ID],
    ANDROID_PACKAGE_PREFIXES_WHITELIST={'com.yandex'},
    ANDROID_PACKAGE_PUBLIC_KEY_DEFAULT='public-key',
    ANDROID_PACKAGE_PREFIX_TO_KEY={
        'com.yandex.passport': 'public-key-2',
    },
)
class TestBindOrConfirmBoundSubmitForSmsRetrieverAndCustomPublicKey(CommonBindOrConfirmBoundSubmitTestcase):
    def setUp(self):
        super(TestBindOrConfirmBoundSubmitForSmsRetrieverAndCustomPublicKey, self).setUp()

        self.package_name = 'com.yandex.passport.testapp1'

        self.setup_statbox_templates(
            sms_retriever_kwargs=dict(
                gps_package_name=self.package_name,
                sms_retriever='1',
            ),
        )

        eq_(hash_android_package(self.package_name, 'public-key-2'), 'ui9RGtUFW1z')

    @property
    def sms_text(self):
        return format_for_android_sms_retriever(
            TEST_SMS_RETRIEVER_TEXT,
            'ui9RGtUFW1z',
        )

    def query_params(self, **kwargs):
        return super(TestBindOrConfirmBoundSubmitForSmsRetrieverAndCustomPublicKey, self).query_params(
            gps_package_name=self.package_name,
            **kwargs
        )


@with_settings_hosts(
    CLIENT_IDS_ALLOWED_TO_BIND_PHONE=[TEST_WHITELISTED_CLIENT_ID],
)
class TestBindOrConfirmBoundCommit(BaseConfirmCommitterTestCase,
                                   CommonSubmitterCommitterTestMixin,
                                   ConfirmCommitterTestMixin,
                                   ConfirmCommitterSentCodeTestMixin,
                                   ConfirmCommitterLocalPhonenumberTestMixin):
    url = '/2/bundle/phone/bind_simple_or_confirm_bound/commit/?consumer=dev'
    specific_grants = {'base'}
    track_state = BIND_OR_CONFIRM_BOUND_STATE

    def setUp(self):
        super(TestBindOrConfirmBoundCommit, self).setUp()
        self.builder = CommitTestBuilder(env=self.env)
        self.setup_default_headers()
        self.setup_default_account()

    def tearDown(self):
        del self.builder
        super(TestBindOrConfirmBoundCommit, self).tearDown()

    def setup_default_headers(self):
        self.base_headers = mock_headers(user_agent='curl')

    def setup_default_account(self):
        self.builder.setup_account_from_uid(serialize_to_db=False)

    def query_params(self, exclude=None, **kwargs):
        base_params = {
            'uid': TEST_UID,
            'code': self.confirmation_code,
            'track_id': self.track_id,
        }
        for key in exclude or []:
            del base_params[key]
        return merge_dicts(base_params, kwargs)

    def build_ok_response(self):
        return self.base_response

    def build_error_response(self):
        return merge_dicts(
            self.base_response,
            dict(status='error'),
        )

    def build_events(self, uid, name_value_list):
        return [{'uid': str(uid), 'name': n, 'value': v} for n, v in name_value_list]

    def assert_new_simple_phone_bound(self):
        assert_simple_phone_bound.check_db(
            db_faker=self.env.db,
            uid=TEST_UID,
            phone_attributes=dict(
                id=1,
                number=TEST_PHONE_NUMBER.e164,
                created=DatetimeNow(),
                bound=DatetimeNow(),
                confirmed=DatetimeNow(),
            ),
        )

        self.env.pharma_logger.assert_has_written([
            self.env.pharma_logger.entry(
                'base',
                action='confirmed',
                uid=str(TEST_UID),
                user_agent=TEST_USER_AGENT1,
                user_ip=TEST_USER_IP,
                phonenumber=TEST_PHONE_NUMBER.digital,
            )
        ])

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('enter_code'),
            self.env.statbox.entry('local_simple_bind_operation_created'),
            self.env.statbox.entry('local_account_modification', action='confirm_and_bind'),
            self.env.statbox.entry('local_phone_confirmed'),
            self.env.statbox.entry('local_simple_phone_bound'),
            self.env.statbox.entry('success'),
        ])

        self.env.event_logger.assert_events_are_logged(
            self.build_events(
                uid=TEST_UID,
                name_value_list=[
                    ('phone.1.action', 'created'),
                    ('phone.1.created', TimeNow()),
                    ('phone.1.number', TEST_PHONE_NUMBER.e164),
                    ('phone.1.operation.1.action', 'created'),
                    ('phone.1.operation.1.finished', TimeNow(offset=60)),
                    ('phone.1.operation.1.security_identity', TEST_PHONE_NUMBER.digital),
                    ('phone.1.operation.1.started', TimeNow()),
                    ('phone.1.operation.1.type', 'bind'),
                    ('action', 'acquire_phone'),
                    ('consumer', 'dev'),
                    ('user_agent', 'curl'),

                    ('info.karma_prefix', '6'),
                    ('info.karma_full', '6000'),
                    ('phone.1.action', 'changed'),
                    ('phone.1.bound', TimeNow()),
                    ('phone.1.confirmed', TimeNow()),
                    ('phone.1.number', TEST_PHONE_NUMBER.e164),
                    ('phone.1.operation.1.action', 'deleted'),
                    ('phone.1.operation.1.security_identity', TEST_PHONE_NUMBER.digital),
                    ('phone.1.operation.1.type', 'bind'),
                    ('action', 'confirm_and_bind'),
                    ('consumer', 'dev'),
                    ('user_agent', 'curl'),
                ],
            ),
            in_order=True,
        )

    def assert_old_simple_phone_reconfirmed(self):
        assert_simple_phone_bound.check_db(
            db_faker=self.env.db,
            uid=TEST_UID,
            phone_attributes=dict(
                id=TEST_PHONE_ID1,
                number=TEST_PHONE_NUMBER.e164,
                created=TEST_TIME1,
                bound=TEST_TIME1,
                confirmed=DatetimeNow(),
            ),
        )

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('enter_code'),
            self.env.statbox.entry('update_phone'),
            self.env.statbox.entry('success'),
        ])

        self.env.event_logger.assert_events_are_logged(
            self.build_events(
                uid=TEST_UID,
                name_value_list=[
                    ('phone.1.action', 'changed'),
                    ('phone.1.confirmed', TimeNow()),
                    ('phone.1.number', TEST_PHONE_NUMBER.e164),
                    ('action', 'confirm_bound'),
                    ('consumer', 'dev'),
                    ('user_agent', 'curl'),
                ],
            ),
            in_order=True,
        )

        self.env.pharma_logger.assert_has_written([
            self.env.pharma_logger.entry(
                'base',
                action='confirmed',
                uid=str(TEST_UID),
                user_agent=TEST_USER_AGENT1,
                user_ip=TEST_USER_IP,
                phonenumber=TEST_PHONE_NUMBER.digital,
            )
        ])

    def test_uid(self):
        self.builder.setup_account_from_uid()
        self.setup_track_for_commit()

        rv = self.make_request(data=self.query_params(uid=TEST_UID))

        self.assert_ok_response(rv, **self.build_ok_response())

    def test_uid_formatted_code_in_query(self):
        self.builder.setup_account_from_uid()
        self.setup_track_for_commit()

        rv = self.make_request(
            data=self.query_params(
                uid=TEST_UID,
                code=format_code_by_3(self.confirmation_code),
            ),
        )
        self.assert_ok_response(rv, **self.build_ok_response())

    def test_uid_formatted_code_in_track(self):
        self.builder.setup_account_from_uid()
        self.setup_track_for_commit(
            phone_confirmation_code=format_code_by_3(self.confirmation_code),
        )

        rv = self.make_request(data=self.query_params(uid=TEST_UID))
        self.assert_ok_response(rv, **self.build_ok_response())

    def test_uid__without_uid_grant(self):
        self.env.grants.set_grants_return_value(mock_grants(grants={'phone_bundle': ['base']}))
        self.builder.setup_account_from_uid()
        self.setup_track_for_commit()

        rv = self.make_request(data=self.query_params(uid=TEST_UID))

        self.assert_error_response(rv, ['access.denied'], status_code=403)

    def test_uid_not_match_track(self):
        self.setup_track_for_commit(uid=TEST_UID2)

        rv = self.make_request(data=self.query_params(uid=TEST_UID))

        self.assert_error_response(rv, ['account.uid_mismatch'], **self.build_error_response())

    def test_oauth_token(self):
        self.builder.setup_account_from_token()
        self.setup_track_for_commit()

        rv = self.make_request(
            data=self.query_params(exclude=['uid']),
            headers=self.builder.build_oauth_token_headers(),
        )

        self.assert_ok_response(rv, **self.build_ok_response())

    def test_oauth_token_invalid(self):
        self.builder.setup_oauth_token_is_invalid()
        self.setup_track_for_commit()

        rv = self.make_request(
            data=self.query_params(exclude=['uid']),
            headers=self.builder.build_oauth_token_headers(),
        )

        self.assert_error_response(rv, ['oauth_token.invalid'], **self.build_error_response())

    def test_oauth_token_no_scope(self):
        self.builder.setup_oauth_token_no_scope()
        self.setup_track_for_commit()

        rv = self.make_request(
            data=self.query_params(exclude=['uid']),
            headers=self.builder.build_oauth_token_headers(),
        )

        self.assert_error_response(rv, ['oauth_token.invalid'], **self.build_error_response())

    def test_oauth_token_no_scope_but_whitelisted_client(self):
        self.builder.setup_oauth_token_no_scope(client_id=TEST_WHITELISTED_CLIENT_ID)
        self.setup_track_for_commit()

        rv = self.make_request(
            data=self.query_params(exclude=['uid']),
            headers=self.builder.build_oauth_token_headers(),
        )

        self.assert_ok_response(rv, **self.build_ok_response())

    def test_oauth_token_bind_phone_scope(self):
        self.env.blackbox.set_response_value('oauth', blackbox_oauth_response(scope=BIND_PHONE_OAUTH_SCOPE))
        self.setup_track_for_commit()

        rv = self.make_request(
            data=self.query_params(exclude=['uid']),
            headers=self.builder.build_oauth_token_headers(),
        )

        self.assert_ok_response(rv, **self.build_ok_response())

    def test_sessionid(self):
        self.builder.setup_account_from_session()
        self.setup_track_for_commit()

        rv = self.make_request(
            data=self.query_params(exclude=['uid']),
            headers=self.builder.build_sessionid_headers(),
        )

        self.assert_ok_response(rv, **self.build_ok_response())

    def test_sessionid_invalid(self):
        self.builder.setup_sessionid_is_invalid()
        self.setup_track_for_commit()

        rv = self.make_request(
            data=self.query_params(exclude=['uid']),
            headers=self.builder.build_sessionid_headers(),
        )

        self.assert_error_response(rv, ['sessionid.invalid'], **self.build_error_response())

    def test_uid_not_in_session(self):
        self.builder.setup_account_from_session()
        self.setup_track_for_commit(uid=TEST_UID2)

        rv = self.make_request(
            data=self.query_params(exclude=['uid']),
            headers=self.builder.build_sessionid_headers(),
        )

        self.assert_error_response(rv, ['track.invalid_state'], **self.build_error_response())

    def test_no_phone(self):
        self.builder.setup_account_no_phone()
        self.setup_track_for_commit()

        rv = self.make_request()

        self.assert_ok_response(rv, **self.build_ok_response())
        self.assert_new_simple_phone_bound()

    def test_bound_phone(self):
        self.builder.setup_account_phone_bound()
        self.setup_track_for_commit()

        rv = self.make_request()

        self.assert_ok_response(rv, **self.build_ok_response())
        self.assert_old_simple_phone_reconfirmed()

    def test_secure_phone_being_bound(self):
        self.builder.setup_account_secure_phone_being_bound()
        self.setup_track_for_commit()

        rv = self.make_request()

        self.assert_ok_response(rv, **self.build_ok_response())

        assert_simple_phone_bound.check_db(
            db_faker=self.env.db,
            uid=TEST_UID,
            phone_attributes=dict(
                id=1,
                number=TEST_PHONE_NUMBER.e164,
                created=DatetimeNow(),
                bound=DatetimeNow(),
                confirmed=DatetimeNow(),
            ),
        )

    def test_bound_phone_being_securified(self):
        self.builder.setup_account_bound_phone_being_securified()
        self.setup_track_for_commit()

        rv = self.make_request()

        self.assert_ok_response(rv, **self.build_ok_response())

        assert_simple_phone_being_securified.check_db(
            db_faker=self.env.db,
            uid=TEST_UID,
            phone_attributes=dict(
                id=1,
                number=TEST_PHONE_NUMBER.e164,
                confirmed=DatetimeNow(),
            ),
        )

    def test_phonish__bound_number(self):
        self.builder.setup_phonish_account()
        self.setup_track_for_commit()

        rv = self.make_request()

        self.assert_ok_response(rv, **self.build_ok_response())

        assert_simple_phone_bound.check_db(
            db_faker=self.env.db,
            uid=TEST_UID,
            phone_attributes=dict(
                id=1,
                number=TEST_PHONE_NUMBER.e164,
                created=TEST_TIME1,
                bound=TEST_TIME1,
                confirmed=DatetimeNow(),
            ),
        )

    def test_phonish__not_bound_number(self):
        self.builder.setup_phonish_account(phone_number=TEST_PHONE_NUMBER2)
        self.setup_track_for_commit()

        rv = self.make_request()

        self.assert_error_response(rv, ['account.invalid_type'], **self.build_error_response())
