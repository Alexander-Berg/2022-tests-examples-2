import cached_property
import requests

from cargo_newflow import utils
from cargo_newflow import library


class HttpError(Exception):
    pass


class HttpNotFoundError(HttpError):
    pass


class HttpConflictError(HttpError):
    pass


HTTP_CODES = {404: HttpNotFoundError, 409: HttpConflictError}


class BaseClient:
    _base_url = 'http://example.org/'
    _tvm_id = None

    def __init__(self, *, net_address=None):
        self._net_address = net_address

    def _json_request(self, method, path, **kwargs):
        response = requests.request(method, self._base_url + path, **kwargs)
        if response.status_code not in (200, 201):

            link = response.headers.get('x-yarequestid')
            exception = HTTP_CODES.get(response.status_code, HttpError)
            raise exception(
                f'{path}: code={response.status_code}\n\n'
                f'Tariff-editor: {library.get_admin_link(link)}\n'
                f'headers: {response.headers}\n'
                f'content:\n{response.content}',
            )
        return response.json()

    def _perform_get(self, path, **kwargs):
        kwargs['headers'] = self._get_headers(kwargs.get('headers'))
        return self._json_request('GET', path, **kwargs)

    def _perform_post(self, path, **kwargs):
        kwargs['headers'] = self._get_headers(kwargs.get('headers'))
        return self._json_request('POST', path, **kwargs)

    def _perform_put(self, path, **kwargs):
        kwargs['headers'] = self._get_headers(kwargs.get('headers'))
        return self._json_request('PUT', path, **kwargs)

    def _get_headers(self, headers):
        if not self._tvm_id:
            result = {}
        else:
            result = {
                'X-Remote-IP': self._net_address,
                'X-Real-IP': self._net_address,
                'X-Ya-Service-Ticket': self._tvm_ticket,
            }

        if headers:
            result.update(headers)
        return result

    @cached_property.cached_property
    def _tvm_ticket(self):
        return utils.get_tvm_ticket(self._tvm_id)
