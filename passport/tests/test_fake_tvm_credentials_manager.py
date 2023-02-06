# -*- coding: utf-8 -*-

from nose.tools import eq_
from passport.backend.core.test.consts import (
    TEST_UID1,
    TEST_UID2,
    TEST_USER_TICKET1,
)
from passport.backend.core.test.test_utils import (
    PassportTestCase,
    with_settings_hosts,
)
from passport.backend.core.tvm import get_tvm_credentials_manager
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_invalid_user_ticket,
    fake_tvm_credentials_data,
    fake_user_ticket,
    FakeTvmCredentialsManager,
    FakeTvmTicketChecker,
    TEST_CLIENT_ID,
    TEST_CLIENT_SECRET,
    TEST_KEYS,
    TEST_TICKET_DATA,
)
import ticket_parser2
from ticket_parser2.exceptions import TicketParsingException


class FakeTvmCredentialsManagerTestCase(PassportTestCase):
    def setUp(self):
        super(FakeTvmCredentialsManagerTestCase, self).setUp()
        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.start()

    def tearDown(self):
        self.fake_tvm_credentials_manager.stop()
        del self.fake_tvm_credentials_manager
        super(FakeTvmCredentialsManagerTestCase, self).tearDown()

    def test_set_data(self):
        eq_(self.fake_tvm_credentials_manager._mock.call_count, 0)
        self.fake_tvm_credentials_manager.set_data(fake_tvm_credentials_data())
        eq_(get_tvm_credentials_manager().config, fake_tvm_credentials_data())
        eq_(self.fake_tvm_credentials_manager._mock.call_count, 1)


class FakeTvmCredentialsDataTestCase(PassportTestCase):
    def test_default(self):
        eq_(
            fake_tvm_credentials_data(),
            {
                'keys': TEST_KEYS,
                'client_id': TEST_CLIENT_ID,
                'client_secret': TEST_CLIENT_SECRET,
                'tickets': TEST_TICKET_DATA,
            },
        )

    def test_custom(self):
        eq_(
            fake_tvm_credentials_data(
                keys='k',
                client_id=1,
                client_secret='s',
                ticket_data={'2': {'ticket': 't', 'alias': 'a'}},
            ),
            {
                'keys': 'k',
                'client_id': 1,
                'client_secret': 's',
                'tickets': {'2': {'ticket': 't', 'alias': 'a'}},
            },
        )


@with_settings_hosts()
class TestFakeTvmTicketCheckerUserContext(PassportTestCase):
    def setUp(self):
        super(TestFakeTvmTicketCheckerUserContext, self).setUp()
        self.fake_ticket_checker = FakeTvmTicketChecker()
        fake_tvm_manager = FakeTvmCredentialsManager()
        self.__patches = [
            fake_tvm_manager,
            self.fake_ticket_checker,
        ]
        for patch in self.__patches:
            patch.start()

        fake_tvm_manager.set_data(fake_tvm_credentials_data())
        self.user_context = get_tvm_credentials_manager().get_user_context()

    def tearDown(self):
        del self.user_context
        for patch in reversed(self.__patches):
            patch.stop()
        del self.__patches
        super(TestFakeTvmTicketCheckerUserContext, self).tearDown()

    def test_expired_user_ticket(self):
        self.fake_ticket_checker.set_check_user_ticket_side_effect([fake_invalid_user_ticket('Expired', uids=[100500])])

        with self.assertRaises(TicketParsingException) as assertion:
            self.user_context.check(TEST_USER_TICKET1)
        self.assertEqual(assertion.exception.status, ticket_parser2.Status.Expired)

    def test_malformed_user_ticket(self):
        self.fake_ticket_checker.set_check_user_ticket_side_effect([fake_invalid_user_ticket('Malformed', uids=[100500])])

        with self.assertRaises(TicketParsingException) as assertion:
            self.user_context.check(TEST_USER_TICKET1)
        self.assertEqual(assertion.exception.status, ticket_parser2.Status.Malformed)

    def test_valid_user_ticket_default(self):
        self.fake_ticket_checker.set_check_user_ticket_side_effect([fake_user_ticket()])

        user_ticket = self.user_context.check(TEST_USER_TICKET1)

        self.assertEqual(user_ticket.default_uid, 1)
        self.assertEqual(user_ticket.uids, [1])
        self.assertEqual(user_ticket.scopes, list())

    def test_valid_user_ticket_custom(self):
        self.fake_ticket_checker.set_check_user_ticket_side_effect(
            [
                fake_user_ticket(
                    default_uid=TEST_UID1,
                    scopes=['foo', 'bar'],
                    uids=[TEST_UID2, TEST_UID1],
                ),
            ],
        )

        user_ticket = self.user_context.check(TEST_USER_TICKET1)

        self.assertEqual(user_ticket.default_uid, TEST_UID1)
        self.assertEqual(set(user_ticket.uids), {TEST_UID2, TEST_UID1})
        self.assertEqual(set(user_ticket.scopes), {'foo', 'bar'})
