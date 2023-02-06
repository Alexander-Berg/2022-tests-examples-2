# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from contextlib import contextmanager

from passport.backend.social.common.test.consts import (
    CONSUMER1,
    CONSUMER2,
    CONSUMER_IP1,
    GRANT1,
    GRANT2,
    TICKET_BODY1,
    TVM_CLIENT_ID1,
)
from passport.backend.social.common.web_service import Request
from passport.backend.social.proxy2.exception import GrantsMissingError
from passport.backend.social.proxy2.test import TestCase
from passport.backend.social.proxy2.utils import (
    get_grants_context,
    Grant,
)


class GrantsTestCase(TestCase):
    @contextmanager
    def _assert_access_denied(self, description):
        with self.assertRaises(GrantsMissingError) as assertion:
            yield
        self.assertEqual(assertion.exception.description, description)

    def _build_request(self, consumer_ip=CONSUMER_IP1, consumer=None, ticket_body=None):
        args = dict()
        if consumer:
            args['consumer'] = consumer
        return Request.create(args=args, consumer_ip=consumer_ip, ticket_body=ticket_body)


class TestGrantsNoGrantsByIp(GrantsTestCase):
    def setUp(self):
        super(TestGrantsNoGrantsByIp, self).setUp()
        self._fake_grants_config.add_consumer(
            CONSUMER1,
            networks=[CONSUMER_IP1],
            grants=[GRANT2],
        )

    def test(self):
        request = self._build_request(consumer_ip=CONSUMER_IP1)

        with self._assert_access_denied(
            'Missing grants [%s] from Consumer(ip = %s, matching_consumers = %s)' % (GRANT1, CONSUMER_IP1, CONSUMER1)
        ):
            Grant(GRANT1).check(request, get_grants_context(request))


class TestGrantsHasGrantsByIp(GrantsTestCase):
    def setUp(self):
        super(TestGrantsHasGrantsByIp, self).setUp()
        self._fake_grants_config.add_consumer(
            CONSUMER1,
            networks=[CONSUMER_IP1],
            grants=[GRANT1],
        )

    def test(self):
        request = self._build_request(consumer_ip=CONSUMER_IP1)
        Grant(GRANT1).check(request, get_grants_context(request))


class TestGrantsNoGrantsByConsumer(GrantsTestCase):
    def setUp(self):
        super(TestGrantsNoGrantsByConsumer, self).setUp()
        self._fake_grants_config.add_consumer(
            CONSUMER1,
            networks=[CONSUMER_IP1],
            grants=[GRANT2],
        )

    def test(self):
        request = self._build_request(consumer=CONSUMER1)

        with self._assert_access_denied(
            'Missing grants [%s] from Consumer(ip = %s, name = %s, matching_consumers = %s)' % (
                GRANT1,
                CONSUMER_IP1,
                CONSUMER1,
                CONSUMER1,
            ),
        ):
            Grant(GRANT1).check(request, get_grants_context(request))


class TestGrantsHasGrantsByConsumer(GrantsTestCase):
    def setUp(self):
        super(TestGrantsHasGrantsByConsumer, self).setUp()
        self._fake_grants_config.add_consumer(
            CONSUMER1,
            networks=[CONSUMER_IP1],
            grants=[GRANT1],
        )

    def test(self):
        request = self._build_request(consumer=CONSUMER1)
        Grant(GRANT1).check(request, get_grants_context(request))


class TestGrantsNoGrantsByTicket(GrantsTestCase):
    def setUp(self):
        super(TestGrantsNoGrantsByTicket, self).setUp()
        self._fake_grants_config.add_consumer(
            CONSUMER1,
            networks=[CONSUMER_IP1],
            grants=[GRANT2],
            tvm_client_id=TVM_CLIENT_ID1,
        )

    def test(self):
        request = self._build_request(ticket_body=TICKET_BODY1)

        with self._assert_access_denied(
            'Missing grants [%s] from Consumer(ip = %s, matching_consumers = %s, name_from_tvm = %s, tvm_client_id = %s)' % (
                GRANT1,
                CONSUMER_IP1,
                CONSUMER1,
                CONSUMER1,
                TVM_CLIENT_ID1,
            ),
        ):
            Grant(GRANT1).check(request, get_grants_context(request))


class TestGrantsHasGrantsByTicket(GrantsTestCase):
    def setUp(self):
        super(TestGrantsHasGrantsByTicket, self).setUp()
        self._fake_grants_config.add_consumer(
            CONSUMER1,
            networks=[CONSUMER_IP1],
            grants=[GRANT1],
            tvm_client_id=TVM_CLIENT_ID1,
        )

    def test(self):
        request = self._build_request(ticket_body=TICKET_BODY1, consumer=CONSUMER2)
        Grant(GRANT1).check(request, get_grants_context(request))
