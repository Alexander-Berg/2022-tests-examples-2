import pytest


@pytest.fixture(name='eats_notifications')
def mock_eats_notifications(mockserver):
    class Context:
        def __init__(self):
            self.project = None
            self.application = None
            self.notification_key = None
            self.options_values = None
            self.user_id = None
            self.locale = None

            self.check_request_flag = False

        def check_request(
                self,
                *,
                project=None,
                application=None,
                notification_key=None,
                options_values=None,
                user_id=None,
                locale=None,
        ):
            self.project = project
            self.application = application
            self.notification_key = notification_key
            self.options_values = options_values
            self.user_id = user_id
            self.locale = locale

            self.check_request_flag = True

        def times_notification_called(self):
            return mock_notification.times_called

    context = Context()

    @mockserver.json_handler('/eats-notifications/v1/notification')
    def mock_notification(request):
        if context.check_request_flag:
            body = request.json
            if context.project is not None:
                assert body['project'] == context.project
            if context.application is not None:
                assert body['application'] == context.application
            if context.notification_key is not None:
                assert body['notification_key'] == context.notification_key
            if context.options_values is not None:
                assert body['options_values'] == context.options_values
            if context.user_id is not None:
                assert body['user_id'] == context.user_id
            if context.locale is not None:
                assert body['locale'] == context.locale

        return {'token': 'test_token'}

    return context
