import shutil

import pytest

LAST_MODIFIED_AT = 'last_modified_at'
CONSUMER = 'consumer'
FILENAME = 'filename'


class Experiments3ProxyMock:
    def __init__(self):
        self.experiments = {}
        self.configs = {}
        self.revision = 0

    def get_consumers(self):
        return self.experiments.keys()

    def parse_experiment3_marker(self, marker, load_json):
        if FILENAME in marker.kwargs:
            self.add_experiments_json(load_json(marker.kwargs[FILENAME]))
        else:
            self._add_experiment(**marker.kwargs)

    def get_experiments(self, consumer, version):
        return self._get_experiments(consumer, version, is_config=False)

    def get_configs(self, consumer, version):
        return self._get_experiments(consumer, version, is_config=True)

    def add_experiment(
            self, match, name, consumers, clauses, default_value=None,
    ):
        self._add_experiment(
            match, name, consumers, clauses, default_value, is_config=False,
        )

    def add_config(self, match, name, consumers, clauses, default_value=None):
        self._add_experiment(
            match, name, consumers, clauses, default_value, is_config=True,
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

    def _add_experiment(
            self,
            match,
            name,
            consumers,
            clauses,
            default_value=None,
            is_config=False,
    ):
        self.revision += 1
        for consumer in consumers:
            self._add_consumer_if_not_exists(consumer, is_config)
            exp = {
                'name': name,
                'match': match,
                'clauses': clauses,
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


@pytest.fixture(scope='session')
def experiments3_cache_files_path(worker_id):
    worker_suffix = '_' + worker_id if worker_id != 'master' else ''
    return '/var/tmp/cache/yandex/exp3' + worker_suffix


@pytest.fixture
def experiments3(request, load_json, experiments3_cache_files_path):
    experiments = Experiments3ProxyMock()
    if request.node.get_marker('experiments3'):
        for marker in request.node.get_marker('experiments3'):
            experiments.parse_experiment3_marker(marker, load_json)

    yield experiments

    experiments.clear_cache_files(experiments3_cache_files_path)
