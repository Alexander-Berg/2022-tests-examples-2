# -*- coding: utf-8 -*-
from datetime import (
    datetime,
    timedelta,
)

import mock
from nose.tools import (
    assert_almost_equal,
    assert_false,
    assert_raises,
    eq_,
    ok_,
    raises,
)
from passport.backend.oauth.core.db.client import Client
from passport.backend.oauth.core.db.eav import (
    CREATE,
    DBIntegrityError,
    UPDATE,
)
from passport.backend.oauth.core.db.eav.dbmanager import get_dbm
from passport.backend.oauth.core.db.errors import (
    ExpiredRequestError,
    PaymentAuthNotPassedError,
    VerificationCodeCollisionError,
    WrongRequestUserError,
)
from passport.backend.oauth.core.db.request import (
    accept_request,
    CodeChallengeMethod,
    CodeStrength,
    CodeType,
    create_request,
    does_code_look_valid,
    get_request,
    Request,
)
from passport.backend.oauth.core.db.scope import Scope
from passport.backend.oauth.core.test.framework.testcases import DBTestCase
from passport.backend.oauth.core.test.utils import set_side_effect_errors


TEST_UID = 1
TEST_CODE_VERIFIER = 'foo'
TEST_CODE_CHALLENGE = 'LCa0a2j_xo_5m0U8HTBBNBNCLXBkg7-g-YpeiGJm564'

TIME_DELTA = timedelta(seconds=5)


class RequestTestCase(DBTestCase):
    def setUp(self):
        super(RequestTestCase, self).setUp()
        with CREATE(Client.create(
            uid=TEST_UID,
            scopes=[Scope.by_keyword('test:foo'), Scope.by_keyword('test:bar')],
            default_title='Test client',
        )) as client:
            self.test_client = client

        with CREATE(Request.create(
            uid=TEST_UID,
            client=self.test_client,
        )) as request:
            self.test_request = request

        self._apply_patches({
            'urandom': mock.patch('os.urandom', mock.Mock(return_value=b'\x00' * 16)),
        })

        self.fake_db.reset_mocks()

    def test_common(self):
        assert_false(self.test_request.is_accepted)
        eq_(self.test_request.code, '')
        eq_(self.test_request.get_client().display_id, self.test_client.display_id)
        eq_(self.test_request.code_strength, CodeStrength.Basic)
        assert_almost_equal(
            self.test_request.created,
            datetime.now(),
            delta=TIME_DELTA,
        )

    def test_is_invalidated_by_user_logout(self):
        assert_false(
            self.test_request.is_invalidated_by_user_logout(datetime.now() - timedelta(seconds=10)),
        )
        ok_(
            self.test_request.is_invalidated_by_user_logout(datetime.now() + timedelta(seconds=10)),
        )

    def test_create_ok(self):
        request = create_request(client=self.test_client)
        assert_false(request.is_accepted)
        eq_(request.code, '')

    def test_create_accepted_with_code_ok(self):
        request = create_request(client=self.test_client, is_accepted=True, uid=TEST_UID, make_code=True)
        ok_(request.is_accepted)
        ok_(request.code.isdigit())
        eq_(len(request.code), 7)

    @raises(ValueError)
    def test_create_accepted_withount_code_or_uid_error(self):
        create_request(client=self.test_client, is_accepted=True)

    def test_accept_ok(self):
        request = get_request(self.test_request.display_id, TEST_UID)
        request = accept_request(request)
        ok_(request.is_accepted)
        eq_(request.scopes, self.test_client.scopes)
        eq_(request.code, request._client_bound_code)
        ok_(not request._unique_code)
        ok_(request.code.isdigit())
        eq_(len(request.code), 7)
        ok_(does_code_look_valid(request.code))
        assert_almost_equal(
            request.expires,
            datetime.now() + timedelta(seconds=600),
            delta=TIME_DELTA,
        )

        eq_(self.fake_db.query_count('oauthdbcentral'), 1)  # получение реквеста
        eq_(self.fake_db.transaction_count('oauthdbcentral'), 1)  # апдейт реквеста
        eq_(self.fake_db.query_count('oauthdbshard1'), 0)
        eq_(self.fake_db.transaction_count('oauthdbshard1'), 0)

        request_from_db = Request.by_id(self.test_request.id)
        eq_(request, request_from_db)

    def test_accept_below_medium_code_ok(self):
        request = get_request(self.test_request.display_id, TEST_UID)
        request.code_strength = CodeStrength.BelowMedium
        request = accept_request(request, ttl=3600)
        ok_(request.is_accepted)
        ok_(request.code.isdigit())
        eq_(len(request.code), 8)
        ok_(does_code_look_valid(request.code))
        assert_almost_equal(
            request.expires,
            datetime.now() + timedelta(seconds=3600),
            delta=TIME_DELTA,
        )

    def test_accept_below_medium_with_crc_code_ok(self):
        request = get_request(self.test_request.display_id, TEST_UID)
        request.code_strength = CodeStrength.BelowMediumWithCRC
        request = accept_request(request, ttl=3600)
        ok_(request.is_accepted)
        ok_(request.code.isdigit())
        eq_(len(request.code), 10)
        ok_(does_code_look_valid(request.code))
        assert_almost_equal(
            request.expires,
            datetime.now() + timedelta(seconds=3600),
            delta=timedelta(seconds=3),
        )

    def test_accept_medium_code_ok(self):
        request = get_request(self.test_request.display_id, TEST_UID)
        request.code_strength = CodeStrength.Medium
        request = accept_request(request, ttl=3600)
        ok_(request.is_accepted)
        eq_(request.code, 'a' * 8)
        ok_(does_code_look_valid(request.code))
        assert_almost_equal(
            request.expires,
            datetime.now() + timedelta(seconds=3600),
            delta=TIME_DELTA,
        )

    def test_accept_medium_with_crc_code_ok(self):
        request = get_request(self.test_request.display_id, TEST_UID)
        request.code_strength = CodeStrength.MediumWithCRC
        request = accept_request(request, ttl=3600)
        ok_(request.is_accepted)
        eq_(request.code, 'a' * 8 + 'Y')
        ok_(does_code_look_valid(request.code))
        assert_almost_equal(
            request.expires,
            datetime.now() + timedelta(seconds=3600),
            delta=timedelta(seconds=3),
        )

    def test_accept_long_code_ok(self):
        request = get_request(self.test_request.display_id, TEST_UID)
        request.code_strength = CodeStrength.Long
        request = accept_request(request, ttl=86400)
        ok_(request.is_accepted)
        eq_(request.code, 'a' * 16)
        ok_(does_code_look_valid(request.code))
        assert_almost_equal(
            request.expires,
            datetime.now() + timedelta(seconds=86400),
            delta=TIME_DELTA,
        )

    def test_accept_unique_code_ok(self):
        self.test_request.code_strength = CodeStrength.Medium
        self.test_request.code_type = CodeType.Unique
        request = accept_request(self.test_request)
        ok_(request.is_accepted)
        eq_(request.code, request._unique_code)
        ok_(not request._client_bound_code)
        eq_(request.code, 'a' * 8)
        ok_(does_code_look_valid(request.code))

    def test_accept_unique_but_not_strong_error(self):
        self.test_request.code_strength = CodeStrength.Basic
        self.test_request.code_type = CodeType.Unique
        with assert_raises(AssertionError):
            accept_request(self.test_request)

    def test_accept_with_scope_limitation_ok(self):
        request = get_request(self.test_request.display_id, TEST_UID)
        request = accept_request(request, scopes=[Scope.by_keyword('test:foo')])
        ok_(request.is_accepted)
        eq_(request.scopes, {Scope.by_keyword('test:foo')})

    def test_accept_with_scope_expansion_error(self):
        request = get_request(self.test_request.display_id, TEST_UID)
        with assert_raises(ValueError):
            accept_request(request, scopes=[Scope.by_keyword('test:ttl')])

    def test_accept_with_db_error_ok(self):
        set_side_effect_errors(get_dbm('oauthdbcentral').transaction, [DBIntegrityError])
        request = accept_request(self.test_request)
        ok_(request.is_accepted)
        eq_(len(request.code), 7)

        request_from_db = Request.by_id(request.id)
        eq_(request, request_from_db)

    def test_accept_without_uid_error(self):
        self.test_request.uid = None
        with assert_raises(ValueError):
            accept_request(self.test_request)

    @raises(ExpiredRequestError)
    def test_get_bad_id(self):
        get_request(42, TEST_UID)

    @raises(ExpiredRequestError)
    def test_get_invalid_id(self):
        get_request('id реквеста', TEST_UID)

    @raises(WrongRequestUserError)
    def test_get_bad_uid(self):
        get_request(self.test_request.display_id, 3)

    @raises(ExpiredRequestError)
    def test_get_accepted(self):
        accept_request(self.test_request)
        get_request(self.test_request.display_id, TEST_UID)

    @raises(ExpiredRequestError)
    def test_get_expired(self):
        with UPDATE(self.test_request):
            self.test_request.expires = datetime.now() - timedelta(10)

        get_request(self.test_request.display_id, TEST_UID)

    def test_get_request_by_client_bound_code(self):
        request = accept_request(self.test_request)
        eq_(
            Request.by_verification_code(self.test_client.id, request.code),
            request,
        )
        ok_(Request.by_verification_code(client_id=None, code=request.code) is None)

    def test_get_request_by_unique_code(self):
        with UPDATE(self.test_request):
            self.test_request.code_strength = CodeStrength.Medium
            self.test_request.code_type = CodeType.Unique
        request = accept_request(self.test_request)
        eq_(
            Request.by_verification_code(client_id=None, code=request.code),
            request,
        )
        ok_(Request.by_verification_code(self.test_client.id, request.code) is None)

    def test_get_unaccepted_request_by_code_error(self):
        for code in ['', None]:
            ok_(Request.by_verification_code(self.test_client.id, code) is None)

    def test_get_request_by_cyrillic_code_error(self):
        for client_id in [self.test_client.id, None]:
            ok_(Request.by_verification_code(client_id, 'код') is None)

    @raises(VerificationCodeCollisionError)
    def test_accept_request_db_failed(self):
        get_dbm('oauthdbcentral').transaction.side_effect = DBIntegrityError
        accept_request(self.test_request)

    @raises(PaymentAuthNotPassedError)
    def test_payment_auth_not_passed_error(self):
        self.test_request.set_scopes([Scope.by_keyword('money:all')])
        accept_request(self.test_request)

    def test_payment_auth_passed_ok(self):
        self.test_request.set_scopes([Scope.by_keyword('money:all')])
        self.test_request.payment_auth_context_id = 'context_id'
        request = accept_request(self.test_request, payment_auth_scope_addendum='addendum')
        ok_(request.is_accepted)
        eq_(request.payment_auth_scope_addendum, 'addendum')

    def test_check_code_verifier_plain_ok(self):
        self.test_request.code_challenge_method = CodeChallengeMethod.Plain
        self.test_request.code_challenge = TEST_CODE_VERIFIER
        ok_(self.test_request.check_code_verifier(TEST_CODE_VERIFIER))

    def test_check_code_verifier_sha256_ok(self):
        self.test_request.code_challenge_method = CodeChallengeMethod.S256
        self.test_request.code_challenge = TEST_CODE_CHALLENGE
        ok_(self.test_request.check_code_verifier(TEST_CODE_VERIFIER))

    def test_check_code_verifier_not_required_ok(self):
        for empty_value in ('', None):
            ok_(self.test_request.check_code_verifier(empty_value))

    def test_check_code_verifier_not_matched(self):
        self.test_request.code_challenge_method = CodeChallengeMethod.Plain
        self.test_request.code_challenge = TEST_CODE_VERIFIER
        ok_(not self.test_request.check_code_verifier(TEST_CODE_VERIFIER + '1'))

    def test_check_code_verifier_not_required_but_passed(self):
        ok_(not self.test_request.check_code_verifier(TEST_CODE_VERIFIER))

    def test_does_looks_valid(self):
        for invalid_value in (
            '',
            '1',
            'a' * 8 + 'aa',  # неверный crc
        ):
            ok_(not does_code_look_valid(invalid_value))
