import pytest


@pytest.fixture(name='ucommunications')
def mock_ucommunications(mockserver):
    class Context:
        def __init__(self):
            self.title = None
            self.text = None
            self.push_intent = None
            self.sms_intent = None
            self.locale = None
            self.user_id = None
            self.recipients = None
            self.idempotency_token = None
            self.sender = None
            self.check_request_flag = False
            self.error_code = None
            self.receipt_url = None
            self.receipt_type = None
            self.phone_id = None
            self.application = None
            self.deeplink = None
            self.notification = None

        def set_error_code(self, code):
            self.error_code = code

        def check_request(
                self,
                *,
                title=None,
                text=None,
                push_intent=None,
                sms_intent=None,
                locale=None,
                user_id=None,
                recipients=None,
                idempotency_token=None,
                sender=None,
                phone_id=None,
                application=None,
                deeplink=None,
                notification=None,
        ):
            self.title = title
            self.text = text
            self.push_intent = push_intent
            self.sms_intent = sms_intent
            self.locale = locale
            self.user_id = user_id
            self.idempotency_token = idempotency_token
            self.sender = sender
            self.phone_id = phone_id
            self.application = application
            self.recipients = recipients
            self.deeplink = deeplink
            self.notification = notification

            self.check_request_flag = True

        def times_notification_push_called(self):
            return mock_notification_push.times_called

        def times_bulk_push_called(self):
            return mock_bulk_push.times_called

        def times_unauthorized_push_called(self):
            return mock_unauthorized_push.times_called

        def times_sms_send_called(self):
            return mock_sms_send.times_called

        def times_user_sms_send_called(self):
            return mock_user_sms_send.times_called

        def times_sms_push_called(self):
            return (
                self.times_notification_push_called()
                + self.times_sms_send_called()
            )

        def times_user_diagnostics_called(self):
            return mock_user_diagnostics.times_called

        def flush(self):
            mock_notification_push.flush()

    context = Context()

    @mockserver.json_handler('/ucommunications/user/notification/push')
    def mock_notification_push(request):
        if context.check_request_flag:
            some_push_info_is_set = (
                context.text is not None
                or context.title is not None
                or context.push_intent is not None
                or context.locale is not None
                or context.user_id is not None
            )
            if some_push_info_is_set:
                _check_push_request(request, context)

            if context.idempotency_token is not None:
                assert (
                    request.headers['X-Idempotency-Token']
                    == context.idempotency_token
                )

        if context.error_code:
            return mockserver.make_response(
                json={'message': '', 'code': str(context.error_code)},
                status=context.error_code,
            )

        return {}

    @mockserver.json_handler('/ucommunications/user/notification/bulk-push')
    def mock_bulk_push(request):
        if context.check_request_flag:
            assert (
                request.headers['X-Idempotency-Token']
                == context.idempotency_token
            )
            _check_bulk_push(request, context)

        if context.error_code:
            return mockserver.make_response(
                json={'message': '', 'code': str(context.error_code)},
                status=context.error_code,
            )

        return {}

    @mockserver.json_handler(
        '/ucommunications/user/unauthorized/notification/push',
    )
    def mock_unauthorized_push(request):
        if context.check_request_flag:
            assert (
                request.headers['X-Idempotency-Token']
                == context.idempotency_token
            )
            _check_unauthorized_push(request, context)

        if context.error_code:
            return mockserver.make_response(
                json={'message': '', 'code': str(context.error_code)},
                status=context.error_code,
            )

        return {}

    @mockserver.json_handler('/ucommunications/general/sms/send')
    def mock_sms_send(request):
        return _sms_send_common(request, context, mockserver)

    @mockserver.json_handler('/ucommunications/user/sms/send')
    def mock_user_sms_send(request):
        return _sms_send_common(request, context, mockserver)

    @mockserver.json_handler('/ucommunications/user/notification/diagnostics')
    def mock_user_diagnostics(request):
        if context.error_code:
            return mockserver.make_response(
                json={'message': '', 'code': str(context.error_code)},
                status=context.error_code,
            )
        body = request.json
        assert body['user_id'] == context.user_id

        return {
            'is_notifications_available': 'yes',
            'features': {
                'is_notifications_enabled_by_system': {
                    'value': 'yes',
                    'updated_at': '2020-01-01T02:03:00+00:00',
                },
                'is_subscribed': {
                    'value': True,
                    'updated_at': '2020-01-01T02:03:00+00:00',
                },
            },
        }

    return context


def _check_push_request(request, context):
    to_cmp = _fill_request_common_fields(context)
    to_cmp['user'] = context.user_id
    if context.locale is not None:
        to_cmp['locale'] = context.locale
    assert request.json == to_cmp


def _check_bulk_push(request, context):
    to_cmp = _fill_request_common_fields(context)
    to_cmp['recipients'] = context.recipients
    assert request.json == to_cmp


def _check_unauthorized_push(request, context):
    to_cmp = _fill_request_common_fields(context)
    to_cmp['user'] = context.user_id
    if context.locale is not None:
        to_cmp['locale'] = context.locale
    to_cmp['application'] = context.application
    assert request.json == to_cmp


def _fill_request_common_fields(context):
    if context.deeplink is not None:
        insert_deeplink = {'deeplink': context.deeplink}
    else:
        insert_deeplink = {}
    to_cmp = {
        'data': {
            'payload': {
                'body': context.text,
                'title': context.title,
                **insert_deeplink,
            },
            'repack': {
                'apns': {
                    'aps': {
                        'alert': {
                            'body': context.text,
                            'title': context.title,
                        },
                        'content-available': 1,
                    },
                },
                'fcm': {
                    'notification': {
                        'body': context.text,
                        'title': context.title,
                    },
                },
                'hms': {
                    'notification': {
                        'body': context.text,
                        'title': context.title,
                    },
                },
            },
        },
        'intent': context.push_intent,
    }
    return to_cmp


def _sms_send_common(request, context, mockserver):
    if context.check_request_flag:
        if context.idempotency_token is not None:
            assert (
                request.headers['X-Idempotency-Token']
                == context.idempotency_token
            )
        body = request.json

        assert 'user_id' in body or 'phone_id' in body
        assert 'user_id' not in body or 'phone_id' not in body

        if context.sms_intent is not None:
            assert body['intent'] == context.sms_intent
        if context.locale is not None:
            assert body['locale'] == context.locale
        if context.text is not None:
            assert body['text'] == context.text
        if context.phone_id is not None and 'phone_id' in body:
            assert body['phone_id'] == context.phone_id
        if context.user_id is not None and 'user_id' in body:
            assert body['user_id'] == context.user_id
        if context.sender is not None:
            assert body['sender'] == context.sender
        if context.notification is not None:
            assert body['notification'] == context.notification

    if context.error_code:
        return mockserver.make_response(
            json={'message': '', 'code': str(context.error_code)},
            status=context.error_code,
        )

    return {'message': 'ok', 'code': '200'}
