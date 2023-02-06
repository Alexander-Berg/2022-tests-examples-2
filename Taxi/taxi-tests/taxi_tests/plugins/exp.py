import datetime
import typing
import uuid

import pytest

from taxi_tests.utils import log_requests


CURRENT_YEAR = datetime.datetime.now().year

EXP_URL = 'http://exp.taxi.yandex.net'

DEFAULT_PREDICATE = {'type': 'true'}
DEFAULT_SCHEMA = (
    """
description: 'default schema'
additionalProperty: true
    """
)
DEFAULT_ACTION_TIME = {
    'from': '2000-01-01T00:00:00+0300',
    'to': f'{CURRENT_YEAR + 2}-12-31T23:59:59+0300',
}
DEFAULT_CLAUSES = [{
    'title': 'default',
    'predicate': DEFAULT_PREDICATE,
    'value': {},
}]
DEFAULT_CONSUMERS = [
    {'name': 'launch'},
    {'name': 'client_protocol/launch'},
]

DEFAULT = object()

HASH_CHUNK = 500


def _generate_experiment(
        name,
        consumers=DEFAULT,
        applications=None,
        match_predicate=DEFAULT,
        clauses=DEFAULT,
        schema=DEFAULT,
        action_time=DEFAULT,
        enabled=True,
        description=None,
        default_value=None,
):
    if consumers is DEFAULT:
        consumers = DEFAULT_CONSUMERS
    if match_predicate is DEFAULT:
        match_predicate = DEFAULT_PREDICATE
    if clauses is DEFAULT:
        clauses = DEFAULT_CLAUSES
    if schema is DEFAULT:
        schema = DEFAULT_SCHEMA
    if action_time is DEFAULT:
        action_time = DEFAULT_ACTION_TIME

    experiment = {
        'description': description or f'Description for {name}',
        'match': {
            'enabled': enabled,
            'schema': schema,
            'predicate': match_predicate,
            'action_time': action_time,
            'consumers': consumers,
        },
        'clauses': clauses,
        'default_value': default_value,
    }

    if applications is not None:
        experiment['match']['applications'] = applications

    return experiment


def _calculate_lines(content: typing.Union[str, bytes]) -> int:
    body = content
    if isinstance(body, bytes):
        body = body.decode('utf-8')
    return body.count('\n')


class ExpManager:

    def __init__(self):
        self._experiment_names = set()

    def del_experiment(self, name, last_modified_at):
        response = log_requests.delete(
            EXP_URL + '/v1/experiments/',
            headers={'YaTaxi-Api-Key': 'taxi_exp_api_token'},
            params={'name': name, 'last_modified_at': last_modified_at},
        )
        response.raise_for_status()

        self._experiment_names.remove(name)

    def add_experiment(self, name=None, **kwargs):
        name = name or uuid.uuid4().hex

        experiment = _generate_experiment(name, **kwargs)

        response = log_requests.post(
            EXP_URL + '/v1/experiments/',
            headers={'YaTaxi-Api-Key': 'taxi_exp_api_token'},
            params={'name': name},
            json=experiment,
        )
        response.raise_for_status()
        self._experiment_names.add(name)

        return name

    def clean_experiments(self):
        for experiment_name in list(self._experiment_names):
            last_modified_at = self.get_last_modified_at(experiment_name)
            self.del_experiment(experiment_name, last_modified_at)

    @staticmethod
    def add_consumer(name):
        response = log_requests.post(
            EXP_URL + '/v1/experiments/filters/consumers/',
            headers={'YaTaxi-Api-Key': 'taxi_exp_api_token'},
            params={'name': name},
        )
        return response

    @staticmethod
    def add_tag(name, body, body_type='string'):
        count_lines = _calculate_lines(body)
        content = body.encode() if isinstance(body, str) else body
        response = log_requests.post(
            EXP_URL + '/v1/files/',
            headers={
                'YaTaxi-Api-Key': 'taxi_exp_api_token',
                'X-File-Tag': name,
                'X-Is-Trusted': 'true',
                'X-Arg-Lines': str(count_lines),
            },
            data=content,
        )

        response.raise_for_status()

    @staticmethod
    def get_experiment(name):
        response = log_requests.get(
            EXP_URL + '/v1/experiments/',
            headers={'YaTaxi-Api-Key': 'taxi_exp_api_token'},
            params={'name': name},
        )
        response.raise_for_status()
        return response.json()

    def get_last_modified_at(self, name):
        response = self.get_experiment(name)
        return response['last_modified_at']

    @staticmethod
    def update_experiment(name, version, **kwargs):
        experiment = _generate_experiment(name, **kwargs)

        response = log_requests.put(
            EXP_URL + '/v1/experiments/',
            headers={'YaTaxi-Api-Key': 'taxi_exp_api_token'},
            params={'name': name, 'last_modified_at': version},
            json=experiment,
        )
        response.raise_for_status()

    @staticmethod
    def add_or_update_file(
            content,
            file_name=None, file_type='string', experiment=None,
    ):
        file_name = file_name or uuid.uuid4().hex
        params = {'experiment': experiment} if experiment else {}
        response = log_requests.post(
            EXP_URL + '/v1/files/',
            headers={
                'YaTaxi-Api-Key': 'taxi_exp_api_token',
                'X-File-Name': file_name,
                'X-Arg-Type': file_type,
            },
            params=params,
            data=content,
        )
        response.raise_for_status()

        file_id = response.json()['id']
        return file_id


@pytest.fixture
def exp(request):
    exp_manager = ExpManager()
    yield exp_manager
    exp_manager.clean_experiments()
