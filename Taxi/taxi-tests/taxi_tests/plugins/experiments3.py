import copy
import itertools
import typing
import uuid

import pytest

from taxi_tests import utils
from taxi_tests.utils import log_requests


ROLLOUT_ERROR_MSG = (
    f'Waiting for experiment roll-out failed.'
    f'consumer: %s, last_modified_at: %s, params: %s'
)


class ExperimentsArg(typing.NamedTuple):
    name: str
    type: str
    value: typing.Any


class ClientApplication(typing.NamedTuple):
    application: str
    version: str


class Experiments3Client:
    def __init__(self, base_url, api_token) -> None:
        self.base_url = base_url
        self.api_token = api_token

    def get_values(
            self,
            consumer: str,
            experiments_args: typing.Iterable[ExperimentsArg],
            client_application: typing.Optional[ClientApplication] = None,
            user_agent: typing.Optional[str] = None,
            log_extra: typing.Optional[dict] = None,
    ) -> typing.Dict:
        if client_application:
            application_args = [
                ExperimentsArg(
                    'application',
                    'application',
                    client_application.application,
                ),
                ExperimentsArg(
                    'version',
                    'application_version',
                    client_application.version,
                ),
            ]
            args_iterator = itertools.chain(experiments_args, application_args)
        else:
            args_iterator = typing.cast(itertools.chain, experiments_args)

        data = {
            'consumer': consumer,
            'args': [
                {'name': kwarg.name, 'type': kwarg.type, 'value': kwarg.value}
                for kwarg in args_iterator
            ],
        }
        if user_agent is not None:
            data['user_agent'] = user_agent

        return self._request('v1/experiments', json=data, log_extra=log_extra)

    def _request(self, location, json, log_extra=None):
        url = '{}/{}'.format(self.base_url, location)
        headers = {'YaTaxi-Api-Key': self.api_token}
        if log_extra and '_link' in log_extra:
            headers['X-YaRequestId'] = log_extra['_link']
        else:
            request_id = uuid.uuid4().hex
            headers['X-YaRequestId'] = request_id
            log_extra = copy.deepcopy(log_extra) if log_extra else {}
            log_extra['_link'] = request_id

        response = log_requests.post(url, headers=headers, json=json)
        response.raise_for_status()
        return response.json()

    def waiting_roll_out(self, consumer, last_modified_at, **kwargs):
        params = {
            'experiments_args': [],
            'client_application': None,
            'user_agent': None,
            'log_extra': None,
        }
        params.update(kwargs)

        for _ in utils.wait_for(
                1000, ROLLOUT_ERROR_MSG % (consumer, last_modified_at, params),
        ):
            data = self.get_values(consumer=consumer, **params)
            if data['version'] >= last_modified_at:
                return data
        return None


@pytest.fixture
def experiments3_client():
    return Experiments3Client(
        base_url='http://exp3-matcher.taxi.yandex.net',
        api_token='taxi_exp3_server_api_token',
    )
