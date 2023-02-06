# -*- coding: utf-8 -*-
import logging

from flask import request
from flask.views import View
from formencode import (
    Invalid,
    Schema,
)
from passport.backend.core.logging_utils.helpers import mask_sensitive_fields
from passport.backend.qa.test_user_service.tus_api.exceptions import (
    HeadersMissedError,
    InvalidRequestError,
)
from passport.backend.qa.test_user_service.tus_api.request_id import RequestIdManager
from passport.backend.qa.test_user_service.tus_api.settings import SENSITIVE_FIELDS_TO_MASK
from passport.backend.qa.test_user_service.tus_api.utils import (
    error_handler,
    ok_response,
    random_alphanumeric,
)
from passport.backend.qa.test_user_service.tus_api.views.headers import (
    HEADER_FORWARDED_FOR,
    HEADER_X_REQ_ID,
)


log = logging.getLogger(__name__)


class Schema(Schema):
    allow_extra_fields = True
    filter_extra_fields = True


def _create_request_id():
    request_id_len = 8
    return random_alphanumeric(request_id_len)


def _set_request_id(request_id):
    RequestIdManager.clear_request_id()
    RequestIdManager.push_request_id(request_id)


class BaseView(View):
    form = Schema

    @property
    def client_ip(self):
        return request.headers.get(HEADER_FORWARDED_FOR.name)

    @property
    def all_values(self):
        values = request.args.to_dict()
        values.update(request.form.to_dict())
        values.update(self.path_values)
        return values

    @property
    def headers(self):
        return request.headers

    @property
    def request_id(self):
        req_id = _create_request_id()
        received_req_id = self.headers.get(HEADER_X_REQ_ID.name)
        log.debug('Received request_id in header: {req_id}'.format(req_id=received_req_id))
        return req_id

    # Список необходимых хедеров
    expected_headers = []

    balancer_headers = [HEADER_X_REQ_ID, HEADER_FORWARDED_FOR]

    def __init__(self):
        self.validators = []
        self.response_values = {}
        self.form_values = {}
        _set_request_id(self.request_id)

    def dispatch_request(self, **kwargs):
        self.path_values = kwargs
        try:
            log.info('Called \'%s\' with args {%s}' % (
                self.__class__,
                ', '.join(['\'%s\': \'%s\'' % (k, v)
                           for k, v in mask_sensitive_fields(self.all_values, SENSITIVE_FIELDS_TO_MASK).items()]))
                     )
            self.process_form(self.form(), self.all_values)
            self.check_no_repeated_params()
            self.check_headers()
            self.process_request()
        except Exception as e:
            return self.respond_error(e)

        return self.respond_success()

    def respond_success(self):
        return ok_response(**self.response_values)

    def respond_error(self, e):
        log.debug('RESPOND_ERROR %s %s'
                  % (str(e), str(mask_sensitive_fields(self.response_values, SENSITIVE_FIELDS_TO_MASK))))
        return error_handler(e, **self.response_values)

    def process_request(self):
        """
        Этот метод надо переопределять в потомках
        """
        raise NotImplementedError()  # pragma: no cover

    @classmethod
    def as_view(cls, name=None, *args, **kwargs):
        name = name or cls.__name__
        return super(BaseView, cls).as_view(name, *args, **kwargs)

    def process_form(self, form, values):
        try:
            result = form.to_python(values)
            self.form_values = {key: value for key, value in result.items() if value is not None}
        except Invalid as e:
            _, self.form_values, _, error_list, error_dict = e.args
            assert error_list is None
            if error_dict:
                for error_field in error_dict:
                    if error_field in self.form_values:
                        del self.form_values[error_field]
            print(error_dict)
            raise InvalidRequestError(str(e))

    def check_no_repeated_params(self):
        for key in self.all_values:
            key_in_path_count = 1 if key in self.path_values else 0
            if len(request.args.getlist(key)) + len(request.form.getlist(key)) + key_in_path_count > 1:
                raise InvalidRequestError('Repeated parameter: %s' % key)

    def check_headers(self):
        names = [
            header.name for header in self.expected_headers
            if (header.name not in self.headers
                or (not self.headers.get(header.name) and not header.allow_empty_value))
        ]

        if names:
            raise HeadersMissedError('Missed headers: {headers_names}'.format(headers_names='; '.join(names)))
