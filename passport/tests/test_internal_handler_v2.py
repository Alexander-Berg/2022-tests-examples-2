# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from json import loads as load_from_json_string

from mock import (
    Mock,
    patch,
)
from nose.tools import (
    istest,
    nottest,
)
from passport.backend.core.builders.blackbox import exceptions as blackbox_exceptions
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
)
from passport.backend.core.tvm.tvm_credentials_manager import TvmCredentialsManager
from passport.backend.social.common import exception as common_exceptions
from passport.backend.social.common.grants import GrantsConfig
from passport.backend.social.common.test.consts import (
    CONSUMER1,
    CONSUMER2,
    CONSUMER_IP1,
    GRANT1,
    GRANT2,
    REQUEST_ID1,
    TICKET_BODY1,
    TVM_CLIENT_ID1,
)
from passport.backend.social.common.test.grants import FakeGrantsConfig
from passport.backend.social.common.test.test_case import TestCase
from passport.backend.social.common.test.types import FakeResponse
from passport.backend.social.common.web_service import (
    InternalHandlerV2,
    Request,
)


class InternalHandlerV2TestCase(TestCase):
    def _build_handler(self):
        handler_class = self._build_handler_class()
        handler = handler_class(self._build_request())
        handler._response_class = FakeResponse.werkzeug_build
        return handler

    def _build_handler_class(self):
        class _Handler(InternalHandlerV2):
            def _process_request(self):
                return
        return _Handler

    def _build_request(self):
        return Request.create(
            id=REQUEST_ID1,
            args={'consumer': CONSUMER1},
            form=dict(),
            consumer_ip=CONSUMER_IP1,
        )

    def _assert_ok_response(self, rv):
        self.assertEqual(rv.status_code, 200)
        rv = load_from_json_string(rv.data)
        self.assertEqual(rv, {'status': 'ok'})

    def _assert_error_response(self, rv, errors):
        self.assertEqual(rv.status_code, 200)
        rv = load_from_json_string(rv.data)
        self.assertEqual(
            rv,
            {
                'status': 'error',
                'errors': errors,
                'request_id': REQUEST_ID1,
            },
        )

    def setUp(self):
        super(InternalHandlerV2TestCase, self).setUp()
        self._fake_grants_config = FakeGrantsConfig()
        self._fake_grants_config.add_consumer(CONSUMER1, networks=[CONSUMER_IP1])

        self._fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self._fake_tvm_credentials_manager.set_data(fake_tvm_credentials_data())

        self._fake_get_grants_config = Mock(name='fake_get_grants_config')
        self._patch_for_get_grants_config = patch.object(
            InternalHandlerV2,
            '_get_grants_config',
            self._fake_get_grants_config,
        )

        self.__patches = [
            self._fake_grants_config,
            self._fake_tvm_credentials_manager,
            self._patch_for_get_grants_config,
        ]
        for _patch in self.__patches:
            _patch.start()

        tvm_credentials_manager = TvmCredentialsManager(
            keyring_config_name='keyring',
            cache_time=1,
        )
        grants_config = GrantsConfig(
            'abc',
            tvm_credentials_manager=tvm_credentials_manager,
        )

        self._fake_get_grants_config.return_value = grants_config
        self._handler = self._build_handler()

    def tearDown(self):
        for _patch in reversed(self.__patches):
            _patch.stop()
        super(InternalHandlerV2TestCase, self).tearDown()


@nottest
class ExceptionInternalHandlerV2TestCase(InternalHandlerV2TestCase):
    exception = None
    error_code = None
    description = None

    def _build_handler_class(self):
        class _Handler(InternalHandlerV2):
            def _process_request(handler):
                raise self.exception
        return _Handler

    def test(self):
        rv = self._handler.get()

        self.assertEqual(rv.status_code, 200)

        rv = load_from_json_string(rv.data)
        expected = {
            'status': 'error',
            'errors': [self.error_code],
            'request_id': REQUEST_ID1,
        }
        if self.description:
            expected.update({
                'description': self.description,
            })
        self.assertEqual(rv, expected)


@istest
class TestInternalHandlerV2UnhandledException(ExceptionInternalHandlerV2TestCase):
    exception = Exception()
    error_code = 'exception.unhandled'


@istest
class TestInternalHandlerV2BlackboxInvalidResponseError(ExceptionInternalHandlerV2TestCase):
    exception = blackbox_exceptions.BlackboxInvalidResponseError()
    error_code = 'internal_error'
    description = 'Blackbox failed'


@istest
class TestInternalHandlerV2BlackboxTemporaryError(ExceptionInternalHandlerV2TestCase):
    exception = blackbox_exceptions.BlackboxTemporaryError()
    error_code = 'internal_error'
    description = 'Blackbox failed'


@istest
class TestInternalHandlerV2BlackboxUnknownError(ExceptionInternalHandlerV2TestCase):
    exception = blackbox_exceptions.BlackboxUnknownError()
    error_code = 'internal_error'
    description = 'Blackbox failed'


@istest
class TestInternalHandlerV2SocialDatabaseError(ExceptionInternalHandlerV2TestCase):
    exception = common_exceptions.DatabaseError()
    error_code = 'internal_error'
    description = 'Database failed'


class GrantsInternalHandlerV2TestCase(InternalHandlerV2TestCase):
    REQUIRED_GRANTS = None

    def _build_handler_class(self):
        class _Handler(InternalHandlerV2):
            required_grants = self.REQUIRED_GRANTS

            def _process_request(self):
                return
        return _Handler

    def _assert_access_denied_response(self, rv, description):
        self.assertEqual(rv.status_code, 200)
        rv = load_from_json_string(rv.data)
        self.assertEqual(
            rv,
            {
                'status': 'error',
                'errors': ['access.denied'],
                'request_id': REQUEST_ID1,
                'description': description,
            },
        )


class NoGrantsByConsumerGrantsInternalHandlerV2TestCase(GrantsInternalHandlerV2TestCase):
    REQUIRED_GRANTS = [GRANT1]

    def setUp(self):
        super(NoGrantsByConsumerGrantsInternalHandlerV2TestCase, self).setUp()
        self._fake_grants_config.add_consumer(
            CONSUMER1,
            networks=[CONSUMER_IP1],
            grants=[GRANT2],
        )

    def test(self):
        rv = self._handler.get()

        self._assert_access_denied_response(
            rv,
            'Missing grants [%s] from Consumer(ip = %s, name = %s, matching_consumers = %s)' % (
                GRANT1,
                CONSUMER_IP1,
                CONSUMER1,
                CONSUMER1,
            ),
        )


class HasGrantsByConsumerGrantsInternalHandlerV2TestCase(GrantsInternalHandlerV2TestCase):
    REQUIRED_GRANTS = [GRANT1]

    def setUp(self):
        super(HasGrantsByConsumerGrantsInternalHandlerV2TestCase, self).setUp()
        self._fake_grants_config.add_consumer(
            CONSUMER1,
            networks=[CONSUMER_IP1],
            grants=[GRANT1],
        )

    def test(self):
        rv = self._handler.get()
        self._assert_ok_response(rv)


class NoGrantsByTicketGrantsInternalHandlerV2TestCase(GrantsInternalHandlerV2TestCase):
    REQUIRED_GRANTS = [GRANT1]

    def _build_request(self):
        return Request.create(
            id=REQUEST_ID1,
            args={'consumer': CONSUMER2},
            form=dict(),
            consumer_ip=CONSUMER_IP1,
            ticket_body=TICKET_BODY1,
        )

    def setUp(self):
        super(NoGrantsByTicketGrantsInternalHandlerV2TestCase, self).setUp()
        self._fake_grants_config.add_consumer(
            CONSUMER1,
            networks=[CONSUMER_IP1],
            grants=[GRANT2],
            tvm_client_id=TVM_CLIENT_ID1,
        )
        self._fake_grants_config.add_consumer(
            CONSUMER2,
            networks=[CONSUMER_IP1],
            grants=[GRANT1],
        )

    def test(self):
        rv = self._handler.get()

        self._assert_access_denied_response(
            rv,
            'Missing grants [%s] from Consumer(ip = %s, name = %s, matching_consumers = %s, name_from_tvm = %s, tvm_client_id = %s)' % (
                GRANT1,
                CONSUMER_IP1,
                CONSUMER2,
                CONSUMER1,
                CONSUMER1,
                TVM_CLIENT_ID1,
            ),
        )


class HasGrantsByTicketGrantsInternalHandlerV2TestCase(GrantsInternalHandlerV2TestCase):
    REQUIRED_GRANTS = [GRANT1]

    def _build_request(self):
        return Request.create(
            id=REQUEST_ID1,
            args={'consumer': CONSUMER1},
            form=dict(),
            consumer_ip=CONSUMER_IP1,
            ticket_body=TICKET_BODY1,
        )

    def setUp(self):
        super(HasGrantsByTicketGrantsInternalHandlerV2TestCase, self).setUp()
        self._fake_grants_config.add_consumer(
            CONSUMER1,
            networks=[CONSUMER_IP1],
            grants=[GRANT1],
            tvm_client_id=TVM_CLIENT_ID1,
        )

    def test(self):
        rv = self._handler.get()
        self._assert_ok_response(rv)


class NoConsumerInternalHandlerV2TestCase(InternalHandlerV2TestCase):
    def _build_request(self):
        return Request.create(
            id=REQUEST_ID1,
            args=dict(),
            form=dict(),
            consumer_ip=CONSUMER_IP1,
        )

    def test(self):
        rv = self._handler.get()
        self._assert_error_response(rv, ['consumer.empty'])
