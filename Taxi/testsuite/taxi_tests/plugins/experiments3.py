import shutil

import pytest

LAST_MODIFIED_AT = 'last_modified_at'
CONSUMER = 'consumer'
FILENAME = 'filename'


class Experiments3ProxyMock:
    def __init__(self):
        self.experiments = {}
        self.configs = []
        self.revision = 0

    def add_consumer_if_not_exists(self, consumer):
        if consumer not in self.experiments:
            self.experiments[consumer] = []

    def get_consumers(self):
        return self.experiments.keys()

    def add_experiment(
            self, match, name, consumers, clauses, default_value=None,
    ):
        self.revision += 1
        for consumer in consumers:
            self.add_consumer_if_not_exists(consumer)
            exp = {
                'name': name,
                'match': match,
                'clauses': clauses,
                LAST_MODIFIED_AT: self.revision,
            }
            if default_value is not None:
                exp['default_value'] = default_value
            self.experiments[consumer].append(exp)

    def add_driver_experiment(self, dbid, uuid, consumers, name, value=None):
        if value is None:
            value = {}
        consumers_json = []
        for consumer_name in consumers:
            consumers_json.append({'name': consumer_name})
        self.add_experiment(
            match={
                'consumers': consumers_json,
                'predicate': {'type': 'true'},
                'enabled': True,
                'driver_id': uuid,
                'park_db_id': dbid,
                'applications': [{'name': 'taximeter', 'version_range': {}}],
            },
            name=name,
            consumers=consumers,
            clauses=[],
            default_value=value,
        )

    def add_experiments_json(self, json):
        for json_entry in json['experiments']:
            self.add_experiment_json_entry(json_entry)

    def add_experiment_json_entry(self, json_entry):
        if LAST_MODIFIED_AT in json_entry:
            self.revision = max(self.revision, json_entry[LAST_MODIFIED_AT])
        for consumer in json_entry['match']['consumers']:
            consumer_name = consumer['name']
            self.add_consumer_if_not_exists(consumer_name)
            self.experiments[consumer_name].append(json_entry)

    def get_experiments(self, consumer, version):
        if consumer not in self.experiments:
            return []
        return [
            exp
            for exp in self.experiments[consumer]
            if exp[LAST_MODIFIED_AT] > version
        ]

    def get_config(self, version):
        return [exp for exp in self.configs if exp[LAST_MODIFIED_AT] > version]

    def parse_experiment3_marker(self, marker, load_json):
        if FILENAME in marker.kwargs:
            self.add_experiments_json(load_json(marker.kwargs[FILENAME]))
        else:
            self.add_experiment(**marker.kwargs)

    def clear_cache_files(self, path):
        if self.experiments:
            self.experiments.clear()
            shutil.rmtree(path, True)


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

    if request.node.get_marker('driver_experiments3'):
        for marker in request.node.get_marker('driver_experiments3'):
            experiments.add_driver_experiment(**marker.kwargs)

    yield experiments

    experiments.clear_cache_files(experiments3_cache_files_path)
