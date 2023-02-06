# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest

from billing_payment_admin_plugins import *  # noqa: F403 F401

DEFAULT = '__default__'


class ApiTrackerContext:
    def __init__(self):
        self.response = {DEFAULT: {}}
        self.headers = {DEFAULT: {}}
        self.status = {DEFAULT: 201}

    def set_response(self, response, headers=None, handler=DEFAULT):
        self.response[handler] = response
        self.status[handler] = 201
        self.headers[handler] = headers

    def set_error(self, status=500, headers=None, handler=DEFAULT):
        self.response[handler] = dict(statusCode=status, errorMessages=[])
        self.status[handler] = status
        self.headers[handler] = headers


@pytest.fixture(name='api_tracker', autouse=True)
def api_tracker_request(mockserver):
    context = ApiTrackerContext()

    @mockserver.json_handler('/taxi-api-tracker/v2/issues')
    def _issues(request):
        handler = 'v2/issues'
        return mockserver.make_response(
            json=context.response.get(handler, context.response[DEFAULT]),
            status=context.status.get(handler, context.status[DEFAULT]),
            headers=context.headers.get(handler, context.headers[DEFAULT]),
        )

    @mockserver.json_handler('/taxi-api-tracker/v2/attachments')
    def _attachments(request):
        handler = 'v2/attachments'
        response = context.response.get(handler, context.response[DEFAULT])
        status = context.status.get(handler, context.status[DEFAULT])
        headers = context.headers.get(handler, context.headers[DEFAULT])
        if status == 201:
            response.update(dict(name=request.query['filename']))
        return mockserver.make_response(
            json=response, status=status, headers=headers,
        )

    @mockserver.json_handler('/taxi-api-tracker/v2/issues/', prefix=True)
    def _comments(request):
        handler = 'v2/issues/{issue}/comments'
        return mockserver.make_response(
            json=context.response.get(handler, context.response[DEFAULT]),
            status=context.status.get(handler, context.status[DEFAULT]),
            headers=context.headers.get(handler, context.headers[DEFAULT]),
        )

    return context
