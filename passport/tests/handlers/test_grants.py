# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from json import loads as load_from_json_string

from passport.backend.social.broker.handlers.base import Handler
from passport.backend.social.broker.test import (
    FakeRoutes,
    InternalBrokerHandlerV1TestCase,
)
from passport.backend.social.common.test.consts import (
    CONSUMER1,
    CONSUMER_IP1,
    GRANT1,
    GRANT2,
    REQUEST_ID1,
    TICKET_BODY1,
    TVM_CLIENT_ID1,
)


class _GrantsTestCase(InternalBrokerHandlerV1TestCase):
    REQUEST_HTTP_METHOD = 'GET'
    REQUEST_URL = '/'
    REQUEST_HEADERS = {'X-Real-Ip': CONSUMER_IP1}

    def _build_handler_class(self):
        raise NotImplementedError()  # pragma: no cover

    def setUp(self):
        super(_GrantsTestCase, self).setUp()

        self._fake_routes = FakeRoutes(self._app).start()
        handler_class = self._build_handler_class()
        self._fake_routes.add('GET', '/', handler_class)

    def tearDown(self):
        self._fake_routes.stop()
        super(_GrantsTestCase, self).tearDown()


class _CheckGrantsTestCase(_GrantsTestCase):
    REQUIRED_GRANTS = None

    def _build_handler_class(self):
        class _Handler(Handler):
            def get(this):
                for grant in self.REQUIRED_GRANTS:
                    this.check_grant(grant)
                this.response.data = this.compose_json_response(dict())
                return this.response
        return _Handler

    def _assert_access_denied_response(self, rv, description):
        self.assertEqual(rv.status_code, 400)
        rv = load_from_json_string(rv.data)
        self.assertEqual(
            rv,
            {
                'error': {
                    'code': 'GrantsMissingError',
                    'message': description,
                },
                'request_id': REQUEST_ID1,
            },
        )


class TestGrantsNoGrantsByIp(_CheckGrantsTestCase):
    REQUIRED_GRANTS = [GRANT1]

    def setUp(self):
        super(TestGrantsNoGrantsByIp, self).setUp()
        self._fake_grants_config.add_consumer(
            CONSUMER1,
            networks=[CONSUMER_IP1],
            grants=[GRANT2],
        )

    def test(self):
        rv = self._make_request()
        self._assert_access_denied_response(
            rv,
            'Missing grants [%s] from Consumer(ip = %s, matching_consumers = %s)' % (GRANT1, CONSUMER_IP1, CONSUMER1),
        )


class TestGrantsHasGrantsByIp(_CheckGrantsTestCase):
    REQUIRED_GRANTS = [GRANT1]

    def setUp(self):
        super(TestGrantsHasGrantsByIp, self).setUp()
        self._fake_grants_config.add_consumer(
            CONSUMER1,
            networks=[CONSUMER_IP1],
            grants=[GRANT1],
        )

    def test(self):
        rv = self._make_request()
        self._assert_ok_response(rv)


class TestGrantsNoGrantsByConsumer(_CheckGrantsTestCase):
    REQUIRED_GRANTS = [GRANT1]
    REQUEST_QUERY = {'consumer': CONSUMER1}

    def setUp(self):
        super(TestGrantsNoGrantsByConsumer, self).setUp()
        self._fake_grants_config.add_consumer(
            CONSUMER1,
            networks=[CONSUMER_IP1],
            grants=[GRANT2],
        )

    def test(self):
        rv = self._make_request()
        self._assert_access_denied_response(
            rv,
            'Missing grants [%s] from Consumer(ip = %s, name = %s, matching_consumers = %s)' % (
                GRANT1,
                CONSUMER_IP1,
                CONSUMER1,
                CONSUMER1,
            ),
        )


class TestGrantsHasGrantsByConsumer(_CheckGrantsTestCase):
    REQUIRED_GRANTS = [GRANT1]
    REQUEST_QUERY = {'consumer': CONSUMER1}

    def setUp(self):
        super(TestGrantsHasGrantsByConsumer, self).setUp()
        self._fake_grants_config.add_consumer(
            CONSUMER1,
            networks=[CONSUMER_IP1],
            grants=[GRANT1],
        )

    def test(self):
        rv = self._make_request()
        self._assert_ok_response(rv)


class TestGrantsNoGrantsByTicket(_CheckGrantsTestCase):
    REQUIRED_GRANTS = [GRANT1]
    REQUEST_HEADERS = {
        'X-Real-Ip': CONSUMER_IP1,
        'X-Ya-Service-Ticket': TICKET_BODY1,
    }

    def setUp(self):
        super(TestGrantsNoGrantsByTicket, self).setUp()
        self._fake_grants_config.add_consumer(
            CONSUMER1,
            networks=[CONSUMER_IP1],
            grants=[GRANT2],
            tvm_client_id=TVM_CLIENT_ID1,
        )

    def test(self):
        rv = self._make_request()
        self._assert_access_denied_response(
            rv,
            'Missing grants [%s] from Consumer(ip = %s, matching_consumers = %s, name_from_tvm = %s, tvm_client_id = %s)' % (
                GRANT1,
                CONSUMER_IP1,
                CONSUMER1,
                CONSUMER1,
                TVM_CLIENT_ID1,
            ),
        )


class TestGrantsHasGrantsByTicket(_CheckGrantsTestCase):
    REQUIRED_GRANTS = [GRANT1]
    REQUEST_HEADERS = {
        'X-Real-Ip': CONSUMER_IP1,
        'X-Ya-Service-Ticket': TICKET_BODY1,
    }

    def setUp(self):
        super(TestGrantsHasGrantsByTicket, self).setUp()
        self._fake_grants_config.add_consumer(
            CONSUMER1,
            networks=[CONSUMER_IP1],
            grants=[GRANT1],
            tvm_client_id=TVM_CLIENT_ID1,
        )

    def test(self):
        rv = self._make_request()
        self._assert_ok_response(rv)


class _HasGrantsTestCase(_GrantsTestCase):
    REQUIRED_GRANT = None

    def _build_handler_class(self):
        class _Handler(Handler):
            def get(this):
                response = {'access_granted': this.consumer_has_grant(self.REQUIRED_GRANT)}
                this.response.data = this.compose_json_response(response)
                return this.response
        return _Handler

    def _assert_access_denied_response(self, rv):
        self.assertEqual(rv.status_code, 200)
        rv = load_from_json_string(rv.data)
        self.assertEqual(rv, {'access_granted': False})

    def _assert_access_granted_response(self, rv):
        self.assertEqual(rv.status_code, 200)
        rv = load_from_json_string(rv.data)
        self.assertEqual(rv, {'access_granted': True})


class TestHasGrantsNoGrantsByIp(_HasGrantsTestCase):
    REQUIRED_GRANT = GRANT1

    def setUp(self):
        super(TestHasGrantsNoGrantsByIp, self).setUp()
        self._fake_grants_config.add_consumer(
            CONSUMER1,
            networks=[CONSUMER_IP1],
            grants=[GRANT2],
        )

    def test(self):
        rv = self._make_request()
        self._assert_access_denied_response(rv)


class TestHasGrantsHasGrantsByIp(_HasGrantsTestCase):
    REQUIRED_GRANT = GRANT1

    def setUp(self):
        super(TestHasGrantsHasGrantsByIp, self).setUp()
        self._fake_grants_config.add_consumer(
            CONSUMER1,
            networks=[CONSUMER_IP1],
            grants=[GRANT1],
        )

    def test(self):
        rv = self._make_request()
        self._assert_access_granted_response(rv)
