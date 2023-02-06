# -*- coding: utf-8 -*-

import mock
from passport.backend.social.api.test import ApiV2TestCase
from passport.backend.social.api.views.v2.base import (
    HandlerV2,
    HandlerV2WithCustomViewFunction,
)
from passport.backend.social.common.exception import DatabaseError
from passport.backend.social.common.test.consts import (
    CONSUMER1,
    CONSUMER_IP1,
    REQUEST_ID1,
)
from passport.backend.social.common.web_service import Request


class _HandlerV2TestCase(ApiV2TestCase):
    def setUp(self):
        super(_HandlerV2TestCase, self).setUp()
        self._request_context = self._app.test_request_context(headers={'X-Real-Ip': CONSUMER_IP1})
        self._request_context.push()

    def tearDown(self):
        self._request_context.pop()
        super(_HandlerV2TestCase, self).tearDown()

    def _build_handler(self):
        handler_class = self._build_handler_class()
        handler = handler_class(self._build_request())
        return handler

    def _build_handler_class(self):
        raise NotImplementedError()  # pragma: no cover

    def _build_request(self):
        return Request.create(
            id=REQUEST_ID1,
            args={'consumer': CONSUMER1},
            form=dict(),
            consumer_ip=CONSUMER_IP1,
        )


class TestHandlerV2OkResponse(_HandlerV2TestCase):
    def _build_handler_class(self):
        class _Handler(HandlerV2):
            def _process_request(self):
                return 'ok'
        return _Handler

    def test(self):
        handler = self._build_handler()
        rv = handler.process_request()
        self.assertEqual(rv, 'ok')


class TestHandlerV2DatabaseError(_HandlerV2TestCase):
    def _build_handler_class(self):
        class _Handler(HandlerV2):
            def _process_request(self):
                raise DatabaseError()
        return _Handler

    def test(self):
        handler = self._build_handler()
        rv = handler.process_request()

        self._assert_error_response(
            rv,
            'internal-exception',
            description='Database failed',
            status_code=500,
        )


class TestHandlerV2WithCustomViewFunction(_HandlerV2TestCase):
    def test_save_original_func_name(self):
        foo = lambda: 0
        foo.__name__ = 'foo'
        self.assertEqual(
            HandlerV2WithCustomViewFunction.adapt_view(foo).__name__,
            'foo',
        )

        foo.__name__ = 'bar'
        self.assertEqual(
            HandlerV2WithCustomViewFunction.adapt_view(foo).__name__,
            'bar',
        )

    def test_call_view_func(self):
        view_func = mock.Mock(name='view_func')
        view_func.side_effect = ['foo', 'bar']
        view_func.__name__ = 'view_func'
        handler = HandlerV2WithCustomViewFunction.adapt_view(view_func)

        responses = [
            handler(),
            handler(foo='bar'),
        ]

        self.assertEqual(responses, ['foo', 'bar'])
        self.assertEqual(
            view_func.call_args_list,
            [
                mock.call(),
                mock.call(foo='bar'),
            ],
        )
