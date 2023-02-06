import shutil
import typing

import mypy_extensions
import pytest

LAST_MODIFIED_AT = 'last_modified_at'
CONSUMER = 'consumer'
FILENAME = 'filename'

DEFAULT_FILENAME = 'experiments3_defaults.json'
SENTINEL = object()

DEFAULT_PREDICATE = {'type': 'true'}
DEFAULT_ACTION_TIME = {
    'from': '2020-01-01T00:00:00+0300',
    'to': '2120-12-31T23:59:59+0300',
}
DEFAULT_VERSION_RANGE = {'from': '0.0.0', 'to': '99.99.99'}
REQUIRED_CLAUSE_KEYS = {'predicate', 'value'}


class Clause(mypy_extensions.TypedDict):
    title: str
    value: typing.Any
    predicate: typing.Dict
    alias: typing.Optional[str]
    is_signal: typing.Optional[bool]
    is_paired_signal: typing.Optional[bool]


class Match(mypy_extensions.TypedDict):
    enabled: bool
    predicate: typing.Dict
    applications: typing.List[typing.Dict]
    action_time: typing.Dict


DEFAULT_MATCH = Match(
    enabled=True,
    predicate=DEFAULT_PREDICATE,
    applications=[],
    action_time=DEFAULT_ACTION_TIME,
)


class Experiments3ProxyMock:
    def __init__(self):
        self.experiments = {}
        self.configs = {}
        self.revision = 0

    def get_consumers(self):
        return self.experiments.keys()

    def add_experiment3_from_marker(self, marker, load_json):
        if not marker.kwargs:
            self.add_experiments_json(load_json(DEFAULT_FILENAME))
        elif FILENAME in marker.kwargs:
            self.add_experiments_json(load_json(marker.kwargs[FILENAME]))
        else:
            self._add_experiment(**marker.kwargs)

    def get_experiments(self, consumer, version):
        return self._get_experiments(consumer, version, is_config=False)

    def get_configs(self, consumer, version):
        return self._get_experiments(consumer, version, is_config=True)

    def add_experiment(
            self,
            match: typing.Optional[typing.Dict] = None,
            name: typing.Optional[str] = None,
            consumers: typing.Optional[typing.List[str]] = None,
            clauses: typing.Optional[typing.List[Clause]] = None,
            applications: typing.Optional[typing.List[str]] = None,
            default_value: typing.Any = SENTINEL,
            enable_debug: bool = False,
    ):
        self._add_experiment(
            name=name,
            consumers=consumers,
            match=match,
            clauses=clauses,
            default_value=default_value,
            applications=applications,
            enable_debug=enable_debug,
            is_config=False,
        )

    def add_config(
            self,
            match: typing.Optional[typing.Dict] = None,
            name: typing.Optional[str] = None,
            consumers: typing.Optional[typing.List[str]] = None,
            clauses: typing.Optional[typing.List[Clause]] = None,
            default_value: typing.Any = SENTINEL,
            enable_debug: bool = False,
    ):
        self._add_experiment(
            name=name,
            consumers=consumers,
            match=match,
            clauses=clauses,
            default_value=default_value,
            enable_debug=enable_debug,
            is_config=True,
        )

    def clear_cache_files(self, path):
        if self.experiments:
            self.experiments.clear()
            shutil.rmtree(path, True)

        if self.configs:
            self.configs.clear()
            shutil.rmtree(path, True)

    def add_experiments_json(self, json):
        if 'experiments' in json:
            for json_entry in json['experiments']:
                self._add_experiment_json_entry(json_entry, False)
        if 'configs' in json:
            for json_entry in json['configs']:
                self._add_experiment_json_entry(json_entry, True)

    def _get_experiments(self, consumer, version, is_config):
        container = self._select_container(is_config)
        if consumer not in container:
            return []
        return [
            exp
            for exp in container[consumer]
            if exp[LAST_MODIFIED_AT] > version
        ]

    def _fill_match(
            self,
            applications: typing.Optional[typing.List[str]] = None,
            is_config: bool = False,
    ) -> Match:
        match = DEFAULT_MATCH
        if not is_config and applications is not None:
            match_applications = [
                {'name': app, 'version_range': DEFAULT_VERSION_RANGE}
                for app in applications
            ]
        else:
            match_applications = []
        match['applications'] = match_applications
        return match

    def _add_experiment(
            self,
            match: typing.Optional[typing.Dict] = None,
            name: typing.Optional[str] = None,
            consumers: typing.Optional[typing.List[str]] = None,
            clauses: typing.Optional[typing.List[Clause]] = None,
            default_value: typing.Any = SENTINEL,
            applications: typing.Optional[typing.List[str]] = None,
            enable_debug: bool = False,
            is_config: bool = False,
    ):
        assert name, 'Testsuite error: name is required field'
        assert (
            consumers
        ), 'Testsuite error: non empty consumers field must be specified'
        if default_value is SENTINEL and not clauses:
            assert False, (
                'Testsuite error: specify default_value argument or '
                'at least one clause in clauses argument'
            )

        if clauses is None:
            clauses = []
        else:
            for clause in clauses:
                for field in REQUIRED_CLAUSE_KEYS:
                    assert (
                        field in clause
                    ), f'Testsuite error: {field} is required field in clause'

        if default_value == SENTINEL:
            default_value = None

        _match = match or self._fill_match(
            applications=applications, is_config=is_config,
        )

        self.revision += 1
        for consumer in consumers:
            self._add_consumer_if_not_exists(consumer, is_config)
            exp = {
                'name': name,
                'match': _match,
                'clauses': clauses,
                'enable_debug': enable_debug,
                LAST_MODIFIED_AT: self.revision,
            }
            if default_value is not None:
                exp['default_value'] = default_value
            self._select_container(is_config)[consumer].append(exp)

    def _add_experiment_json_entry(self, json_entry, is_config):
        if LAST_MODIFIED_AT in json_entry:
            self.revision = max(self.revision, json_entry[LAST_MODIFIED_AT])
        for consumer in json_entry['match']['consumers']:
            consumer_name = consumer['name']
            self._add_consumer_if_not_exists(consumer_name, is_config)
            self._select_container(is_config)[consumer_name].append(json_entry)

    def _select_container(self, is_config):
        if is_config:
            return self.configs
        return self.experiments

    def _add_consumer_if_not_exists(self, consumer, is_config):
        container = self._select_container(is_config)
        if consumer not in container:
            container[consumer] = []


def pytest_configure(config):
    config.addinivalue_line(
        'markers', 'experiments3: per-test experiments3.0 configuration',
    )


@pytest.fixture(scope='session')
def experiments3_cache_files_path(worker_id):
    worker_suffix = '_' + worker_id if worker_id != 'master' else ''
    return '/var/tmp/cache/yandex/exp3' + worker_suffix


@pytest.fixture
def experiments3(request, load_json, experiments3_cache_files_path):
    experiments = Experiments3ProxyMock()
    for marker in request.node.iter_markers('experiments3'):
        experiments.add_experiment3_from_marker(marker, load_json)

    yield experiments

    experiments.clear_cache_files(experiments3_cache_files_path)
