# coding=utf-8
import logging

from flask import request
from passport.backend.core.utils.decorators import cached_property
from passport.backend.qa.test_user_service.tus_api.common.blackbox.blackbox import validate_oauth_token
from passport.backend.qa.test_user_service.tus_api.common.xunistater import request_time
from passport.backend.qa.test_user_service.tus_api.exceptions import AuthorizationHeaderError
from passport.backend.qa.test_user_service.tus_api.logger import YasmLogger
from passport.backend.qa.test_user_service.tus_api.settings import OAUTH_TUS_CLIENT_ID
from passport.backend.qa.test_user_service.tus_api.views.base import BaseView
from passport.backend.qa.test_user_service.tus_api.views.headers import HEADER_CONSUMER_AUTHORIZATION


log = logging.getLogger(__name__)

OAUTH_HEADER_PREFIX = 'oauth '


class TusBaseView(BaseView):

    @property
    def authorization(self):
        return self.headers.get(HEADER_CONSUMER_AUTHORIZATION.name)

    @cached_property
    def oauth_token(self):
        auth_header = self.authorization
        if not auth_header.lower().startswith(OAUTH_HEADER_PREFIX):
            raise AuthorizationHeaderError(  # TODO: посмотреть где-нибудь, что делать с кавычками в хедерах
                'Authorization header value should be formatted like \'OAuth TOKEN_VALUE\'. Link to create new token: '
                'https://oauth.yandex-team.ru/authorize?response_type=token&client_id={client_id}'.format(
                    client_id=OAUTH_TUS_CLIENT_ID)
            )
        return auth_header[len(OAUTH_HEADER_PREFIX):].strip()

    @cached_property
    def yasm_logger(self):
        return YasmLogger(
            client_ip=self.client_ip,
        )

    def __init__(self):
        super(TusBaseView, self).__init__()
        self.requester_info = None

    # Список необходимых хедеров. Хедера берутся из passport.backend.qa.test_user_service.tus_api.views.headers
    expected_headers = [HEADER_CONSUMER_AUTHORIZATION]

    @request_time()
    def dispatch_request(self):
        return super(TusBaseView, self).dispatch_request()

    def _log_http_status(self, response, error=None):
        endpoint = request.path.strip('/').replace('/', '_')

        if 200 <= response.status_code < 300:
            http_status = 'http.ok'
        elif 400 <= response.status_code < 500:
            http_status = 'http.client_error'
        elif 500 <= response.status_code < 600:
            http_status = 'http.server_error'
        else:
            http_status = 'http.specific_error'

        entries = dict(status=http_status, endpoint=endpoint, code=response.status_code)
        if error:
            tus_error_code = getattr(error, 'code', None)
            if tus_error_code is not None:
                entries['error_code'] = tus_error_code

        self.yasm_logger.log(status=http_status, endpoint='total', code=response.status_code)
        self.yasm_logger.log(**entries)

    def respond_success(self):
        response = super(TusBaseView, self).respond_success()
        self._log_http_status(response)
        return response

    def respond_error(self, e):
        response = super(TusBaseView, self).respond_error(e)
        self._log_http_status(response, error=e)
        return response

    def check_headers(self):
        super(TusBaseView, self).check_headers()

        self.requester_info = validate_oauth_token(oauth_token=self.oauth_token, user_ip=self.client_ip)
        if 'tus_consumer' in self.form_values:
            self.requester_info['tus_consumer'] = self.form_values['tus_consumer']

        log.debug(
            'Requester {login} with uid: {uid} has valid token'.format(
                login=self.requester_info['login'],
                uid=self.requester_info['uid']
            )
        )
