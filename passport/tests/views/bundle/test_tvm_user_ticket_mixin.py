# -*- coding: utf-8 -*-

from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.views.bundle.base import BaseBundleView
from passport.backend.api.views.bundle.mixins.common import BundleTvmUserTicketMixin
from passport.backend.core.test.consts import (
    TEST_CONSUMER1,
    TEST_CONSUMER_IP1,
    TEST_UID1,
    TEST_UID2,
    TEST_USER_TICKET1,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_invalid_user_ticket,
    fake_user_ticket,
)


SCOPE1 = 'scope1'
SCOPE2 = 'scope2'
SCOPE3 = 'scope3'
SCOPE4 = 'scope4'


class BaseTestCase(BaseBundleTestViews):
    def setUp(self):
        super(BaseTestCase, self).setUp()
        self.env = ViewsTestEnvironment()
        self.__patches = [
            self.env,
        ]
        for patch in self.__patches:
            patch.start()
        self.env.grants.set_grants_return_value(
            {
                TEST_CONSUMER1: dict(
                    networks=[TEST_CONSUMER_IP1],
                ),
            },
        )

    def tearDown(self):
        for patch in reversed(self.__patches):
            patch.stop()
        del self.__patches
        del self.env
        super(BaseTestCase, self).tearDown()

    def setup_check_user_ticket_handle(self):
        class Handle(BaseBundleView, BundleTvmUserTicketMixin):
            required_user_ticket_scopes = [SCOPE3, SCOPE4]

            def process_request(this):
                ticket = this.check_user_ticket()
                this.response_values.update(
                    default_uid=ticket.default_uid,
                    scopes=ticket.scopes,
                    uids=ticket.uids,
                )

        self.env.client.application.add_url_rule('/', view_func=Handle().as_view())

    def setup_get_default_uid_from_user_ticket_handle(self):
        class Handle(BaseBundleView, BundleTvmUserTicketMixin):
            required_user_ticket_scopes = []

            def process_request(this):
                ticket = this.check_user_ticket()
                uid = this.get_uid_or_default_from_user_ticket(ticket)
                this.response_values.update(uid=uid)

        self.env.client.application.add_url_rule('/', view_func=Handle().as_view())

    def setup_get_uid_from_user_ticket_handle(self, uid):
        class Handle(BaseBundleView, BundleTvmUserTicketMixin):
            required_user_ticket_scopes = []

            def process_request(this):
                ticket = this.check_user_ticket()
                _uid = this.get_uid_or_default_from_user_ticket(ticket, uid)
                this.response_values.update(uid=_uid)

        self.env.client.application.add_url_rule('/', view_func=Handle().as_view())


@with_settings_hosts()
class TestBundleTvmUserTicketMixin(BaseTestCase):
    default_url = '/'
    http_headers = {
        'consumer_ip': TEST_CONSUMER_IP1,
        'user_ticket': TEST_USER_TICKET1,
    }
    consumer = TEST_CONSUMER1

    def test_expired_user_ticket(self):
        self.setup_check_user_ticket_handle()
        self.env.tvm_ticket_checker.set_check_user_ticket_side_effect([fake_invalid_user_ticket(uids=[100500])])

        rv = self.make_request()

        self.assert_error_response(
            rv,
            ['tvm_user_ticket.invalid'],
            ignore_error_message=False,
            error_message='errors: [tvm_user_ticket.invalid]; args: Expired ticket',
        )

    def test_malformed_user_ticket(self):
        self.setup_check_user_ticket_handle()
        self.env.tvm_ticket_checker.set_check_user_ticket_side_effect([fake_invalid_user_ticket('Malformed', uids=[100500])])

        rv = self.make_request()

        self.assert_error_response(
            rv,
            ['tvm_user_ticket.invalid'],
            ignore_error_message=False,
            error_message='errors: [tvm_user_ticket.invalid]; args: Malformed ticket',
        )

    def test_missing_scope(self):
        self.setup_check_user_ticket_handle()
        self.env.tvm_ticket_checker.set_check_user_ticket_side_effect([fake_user_ticket(scopes=[SCOPE1, SCOPE2])])

        rv = self.make_request()

        self.assert_error_response(
            rv,
            ['tvm_user_ticket.missing_scopes'],
            ignore_error_message=False,
            error_message='Ticket missing one of scopes %s, %s (ticket scopes are %s, %s)' % (SCOPE3, SCOPE4, SCOPE1, SCOPE2),
        )

    def test_valid_user_ticket(self):
        self.setup_check_user_ticket_handle()
        self.env.tvm_ticket_checker.set_check_user_ticket_side_effect(
            [
                fake_user_ticket(
                    default_uid=TEST_UID1,
                    scopes=[SCOPE1, SCOPE2, SCOPE3, SCOPE4],
                    uids=[TEST_UID1, TEST_UID2],
                ),
            ],
        )

        rv = self.make_request()

        self.assert_ok_response(
            rv,
            default_uid=TEST_UID1,
            scopes=[SCOPE1, SCOPE2, SCOPE3, SCOPE4],
            uids=[TEST_UID1, TEST_UID2],
        )

    def test_get_default_no_default_in_user_ticket(self):
        self.setup_get_default_uid_from_user_ticket_handle()
        self.env.tvm_ticket_checker.set_check_user_ticket_side_effect(
            [
                fake_user_ticket(default_uid=0, uids=[TEST_UID1]),
            ],
        )

        rv = self.make_request()

        self.assert_error_response(
            rv,
            ['tvm_user_ticket.no_uid'],
            ignore_error_message=False,
            error_message='Specified or default uid not in ticket (ticket uids are %s)' % TEST_UID1,
        )

    def test_get_default(self):
        self.setup_get_default_uid_from_user_ticket_handle()
        self.env.tvm_ticket_checker.set_check_user_ticket_side_effect(
            [
                fake_user_ticket(default_uid=TEST_UID1, uids=[TEST_UID1]),
            ],
        )

        rv = self.make_request()

        self.assert_ok_response(rv, uid=TEST_UID1)

    def test_get_uid_no_uid_in_user_ticket(self):
        self.setup_get_uid_from_user_ticket_handle(TEST_UID2)
        self.env.tvm_ticket_checker.set_check_user_ticket_side_effect(
            [
                fake_user_ticket(default_uid=0, uids=[TEST_UID1]),
            ],
        )

        rv = self.make_request()

        self.assert_error_response(
            rv,
            ['tvm_user_ticket.no_uid'],
            ignore_error_message=False,
            error_message='Specified or default uid not in ticket (ticket uids are %s)' % TEST_UID1,
        )

    def test_get_uid(self):
        self.setup_get_uid_from_user_ticket_handle(TEST_UID1)
        self.env.tvm_ticket_checker.set_check_user_ticket_side_effect(
            [
                fake_user_ticket(default_uid=TEST_UID1, uids=[TEST_UID1]),
            ],
        )

        rv = self.make_request()

        self.assert_ok_response(rv, uid=TEST_UID1)


@with_settings_hosts()
class TestBundleTvmUserTicketMixinNoUserTicket(BaseTestCase):
    default_url = '/'
    http_headers = {
        'consumer_ip': TEST_CONSUMER_IP1,
    }
    consumer = TEST_CONSUMER1

    def setUp(self):
        super(TestBundleTvmUserTicketMixinNoUserTicket, self).setUp()
        self.env.tvm_ticket_checker.stop()

    def tearDown(self):
        self.env.tvm_ticket_checker.start()
        super(TestBundleTvmUserTicketMixinNoUserTicket, self).tearDown()

    def test(self):
        self.setup_check_user_ticket_handle()

        rv = self.make_request()

        self.assert_error_response(
            rv,
            ['tvm_user_ticket.invalid'],
            ignore_error_message=False,
            error_message='errors: [tvm_user_ticket.invalid]; args: No ticket',
        )
