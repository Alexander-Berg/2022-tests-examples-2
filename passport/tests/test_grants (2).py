# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from json import (
    dumps as dump_to_json_string,
    loads as load_from_json_string,
)

from flask.app import Flask
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
)
from passport.backend.social.api.app import (
    prepare_interprocess_environment,
    prepare_intraprocess_environment,
)
from passport.backend.social.api.test import ApiV3TestCase
from passport.backend.social.api.views.v2.grants import build_grants_checking_decorator
from passport.backend.social.common.test.consts import (
    CONSUMER1,
    CONSUMER2,
    CONSUMER_IP1,
    GRANT1,
    GRANT2,
    TICKET_BODY1,
    TVM_CLIENT_ID1,
)


class GrantsTestCase(ApiV3TestCase):
    REQUEST_HTTP_METHOD = 'GET'
    REQUEST_URL = '/'
    REQUEST_HEADERS = {'X-Real-Ip': CONSUMER_IP1}
    REQUIRED_GRANTS = None

    def _build_app(self):
        def _view():
            return dump_to_json_string({'status': 'ok'})

        decorate = build_grants_checking_decorator(self.REQUIRED_GRANTS)
        _view = decorate(_view)

        app = Flask(__name__)
        app.add_url_rule('/', methods=['GET'], view_func=_view)
        return app

    def _assert_access_denied_response(self, rv, description):
        self.assertEqual(rv.status_code, 403)
        rv = load_from_json_string(rv.data)
        self.assertEqual(
            rv,
            {
                'error': {
                    'name': 'access-denied',
                    'description': description,
                    'request_id': None,
                },
            },
        )

    def setUp(self):
        super(GrantsTestCase, self).setUp()
        self._fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self._fake_tvm_credentials_manager.start()
        self._fake_tvm_credentials_manager.set_data(fake_tvm_credentials_data())

        prepare_interprocess_environment()
        prepare_intraprocess_environment()

    def tearDown(self):
        self._fake_tvm_credentials_manager.stop()
        super(GrantsTestCase, self).tearDown()


class TestGrantsNoGrantsByIp(GrantsTestCase):
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


class TestGrantsHasGrantsByIp(GrantsTestCase):
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


class TestGrantsNoGrantsByConsumer(GrantsTestCase):
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


class TestGrantsHasGrantsByConsumer(GrantsTestCase):
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


class TestGrantsNoGrantsByTicket(GrantsTestCase):
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


class TestGrantsHasGrantsByTicket(GrantsTestCase):
    REQUIRED_GRANTS = [GRANT1]
    REQUEST_HEADERS = {
        'X-Real-Ip': CONSUMER_IP1,
        'X-Ya-Service-Ticket': TICKET_BODY1,
    }
    REQUEST_QUERY = {'consumer': CONSUMER2}

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
