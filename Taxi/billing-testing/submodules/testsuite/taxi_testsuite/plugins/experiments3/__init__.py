import functools
import pathlib
import shutil
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union
import warnings

import jsonschema
import mypy_extensions
import pytest
import yaml

LAST_MODIFIED_AT = 'last_modified_at'
FILENAME = 'filename'
SKIP_CHECK_SCHEMA_FIELD = 'skip_check_schema'
STRICT_CHECK_SCHEMA = False

DEFAULT_FILENAME = 'experiments3_defaults.json'
SENTINEL = object()

DEFAULT_PREDICATE = {'type': 'true'}
DEFAULT_VERSION_RANGE = {'from': '0.0.0', 'to': '99.99.99'}
REQUIRED_CLAUSE_KEYS = {'predicate', 'value'}


class JsonValidatorStore:
    yaml_path = None
    _validators: Dict[str, jsonschema.Draft4Validator] = {}

    def __init__(
            self,
            schemes_basepath: Optional[Union[str, pathlib.Path]] = None,
            reference_filenames: Optional[list] = None,
    ) -> None:
        self.schemes_basepath: Optional[pathlib.Path]
        if schemes_basepath is not None:
            self.schemes_basepath = pathlib.Path(schemes_basepath)
        else:
            self.schemes_basepath = None
        self.reference_filenames = reference_filenames or []

    @functools.lru_cache(maxsize=None)
    def _get_yaml(self, filename: pathlib.Path) -> dict:
        if self.schemes_basepath:
            filename = self.schemes_basepath.joinpath(filename)
        with open(filename, encoding='utf-8') as _f:
            result = yaml.safe_load(_f)
            if not isinstance(result, dict):
                raise TypeError('Schema must be an instance of dict')
        return result

    def _load_json_validator(self, ref: str) -> jsonschema.Draft4Validator:
        filename, path = ref.split('#/')
        schema = self._get_yaml(pathlib.Path(filename))
        resolver = self._create_resolver(schema)
        fields = path.split('/')
        fragment = schema
        for field in fields:
            fragment = fragment[field]
        jsonschema.Draft4Validator.check_schema(schema)
        return jsonschema.Draft4Validator(
            fragment,
            resolver=resolver,
            format_checker=jsonschema.FormatChecker(),
            types={'array': (list, tuple)},
        )

    def _create_resolver(self, schema):
        store = {
            '/' + filename: self._get_yaml(filename)
            for filename in self.reference_filenames
        }
        return jsonschema.RefResolver('', schema, store=store)

    def __getitem__(self, ref: str) -> jsonschema.Draft4Validator:
        validator = self._validators.get(ref)
        if validator is None:
            validator = self._load_json_validator(ref)
            self._validators[ref] = validator
        return validator


DEFAULT_SCHEMA_SEARCH_PATH = pathlib.Path(__file__).parent.joinpath('schemas')

CONFIG_VALIDATOR_PATH = 'definitions.yaml#/definitions/Config'
EXPERIMENT_VALIDATOR_PATH = 'definitions.yaml#/definitions/Experiment'


def _get_pathmessage_by_exception(
        exc: Union[jsonschema.SchemaError, jsonschema.ValidationError],
) -> str:
    path_message = ''
    if exc.relative_path != [0]:
        path = '->'.join(str(item) for item in exc.relative_path)
        path_message = '' if not path else f', see `{path}`'
    return path_message


class Clause(mypy_extensions.TypedDict):
    title: str
    value: Any
    predicate: Dict
    alias: Optional[str]
    is_signal: Optional[bool]
    is_paired_signal: Optional[bool]


DEFAULT_MATCH = {'enabled': True, 'predicate': DEFAULT_PREDICATE}


class BadTestArgs(Exception):
    pass


class BadTestStatic(Exception):
    pass


class MatchTriesRecorder:
    class MatchTry:
        def __init__(self, data):
            match = data['match']
            self.clause_id: int = match.get('clause_id')
            self.clause_alias: str = match.get('clause_alias')

            kwargs_list = data['kwargs']
            self.kwargs: Dict = {
                kwarg['name']: kwarg['value'] for kwarg in kwargs_list
            }

        def ensure_matched_with_default(self):
            assert self.clause_id == -1

        def ensure_matched_with_clause(self, clause):
            if isinstance(clause, str):
                assert self.clause_alias == clause
            elif isinstance(clause, int):
                assert self.clause_id == clause
            else:
                assert False

        def ensure_no_match(self):
            assert self.clause_id is None

    def __init__(self, testpoint, exp_name: str):
        self._exp_name = exp_name

        @testpoint(f'exp3::match_{exp_name}')
        def handler(data):
            pass

        self._handler = handler

    async def get_match_tries(self, ensure_ntries: int):
        match_tries = []
        for _ in range(ensure_ntries):
            data = (await self._handler.wait_call())['data']
            match_tries.append(self.MatchTry(data))
        assert not self._handler.has_calls
        return match_tries


class Experiments3ProxyMock:
    def __init__(
            self,
            validators: JsonValidatorStore,
            testpoint,
            strict_schema_checks: bool = False,
    ):
        self.experiments: Dict = {}
        self.configs: Dict = {}
        self.revision = 0
        self.strict_schema_checks = strict_schema_checks
        self._validators = validators
        self._testpoint = testpoint

    def get_consumers(self):
        return list(self.experiments.keys()) + list(self.configs.keys())

    def add_experiment3_from_marker(self, marker, load_json):
        if not marker.kwargs:
            self.add_experiments_json(
                load_json(DEFAULT_FILENAME), file_name=DEFAULT_FILENAME,
            )
        elif FILENAME in marker.kwargs:
            self.add_experiments_json(
                load_json(marker.kwargs[FILENAME]),
                file_name=marker.kwargs[FILENAME],
                skip_check_schema=marker.kwargs.get(SKIP_CHECK_SCHEMA_FIELD)
                or False,
            )
        else:
            self._add_experiment(**marker.kwargs)

    def get_experiments(self, consumer, version):
        return self._get_experiments(consumer, version, is_config=False)

    def get_configs(self, consumer, version):
        return self._get_experiments(consumer, version, is_config=True)

    def add_experiment(self, **kwargs):
        self._add_experiment(is_config=False, **kwargs)

    def add_config(self, **kwargs):
        self._add_experiment(is_config=True, **kwargs)

    def clear_cache_files(self, path):
        if self.experiments:
            self.experiments.clear()
            shutil.rmtree(path, True)

        if self.configs:
            self.configs.clear()
            shutil.rmtree(path, True)

    def add_experiments_json(
            self, json, file_name=None, skip_check_schema=False,
    ):
        if 'experiments' not in json and 'configs' not in json:
            raise BadTestArgs('add field `experiments` or `configs` to json')

        if 'experiments' in json:
            for json_entry in json['experiments']:
                self._add_experiment_json_entry(
                    json_entry,
                    is_config=False,
                    file_name=file_name,
                    skip_check_schema=skip_check_schema,
                )
        if 'configs' in json:
            for json_entry in json['configs']:
                self._add_experiment_json_entry(
                    json_entry,
                    is_config=True,
                    file_name=file_name,
                    skip_check_schema=skip_check_schema,
                )

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
            match: Optional[Dict],
            consumers: Optional[List[str]],
            applications: Optional[List[str]] = None,
            is_config: bool = False,
    ) -> Dict:
        if match is not None:
            full_match = match.copy()
        else:
            full_match = DEFAULT_MATCH.copy()
        assert 'consumers' in full_match or consumers, (
            'Testsuite error: non empty consumers field must be specified',
        )

        if 'consumers' not in full_match:
            full_match['consumers'] = [
                {'name': name} for name in consumers or []
            ]
        elif consumers is not None:
            assert {
                consumer['name'] for consumer in full_match['consumers']
            } == set(consumers), (
                'Testsuite error: consumer list must be equal '
                'to list consumer names in match->consumers'
            )

        if not is_config and applications is not None:
            full_match['applications'] = [
                {'name': app, 'version_range': DEFAULT_VERSION_RANGE}
                for app in applications
            ]
        return full_match

    def _check_and_fill_clauses(self, clauses: Optional[List[Clause]] = None):
        if clauses is None:
            return []

        for index, clause in enumerate(clauses):
            for field in REQUIRED_CLAUSE_KEYS:
                assert (
                    field in clause
                ), f'Testsuite error: {field} is required field in clause'
            if 'title' not in clause:
                clause['title'] = f'title_{index+1}'
        return clauses

    def _add_experiment(
            self,
            match: Optional[Dict] = None,
            name: Optional[str] = None,
            consumers: Optional[List[str]] = None,
            clauses: Optional[List[Clause]] = None,
            default_value: Any = SENTINEL,
            applications: Optional[List[str]] = None,
            enable_debug: bool = False,
            trait_tags: List[str] = None,
            skip_check_schema: bool = False,
            is_config: bool = False,
            merge_values_by: Optional[Dict] = None,
    ):
        self.revision += 1
        _clauses = self._check_and_fill_clauses(clauses)
        _match = self._fill_match(
            match=match,
            applications=applications,
            consumers=consumers,
            is_config=is_config,
        )
        exp = {
            'name': name,
            'match': _match,
            'clauses': _clauses,
            'enable_debug': enable_debug,
            'trait_tags': trait_tags or [],
            LAST_MODIFIED_AT: self.revision,
        }
        if default_value == SENTINEL:
            default_value = {} if is_config else None
        if default_value is not None:
            exp['default_value'] = default_value
        if merge_values_by is not None:
            exp['merge_values_by'] = merge_values_by

        self._check_by_schema(
            json_entry=exp,
            is_config=is_config,
            skip_check_schema=skip_check_schema,
            place='experiments3 mark',
        )

        match_consumers = (
            consumer['name'] for consumer in _match['consumers']
        )
        for consumer in match_consumers:
            self._add_consumer_if_not_exists(consumer, is_config)
            self._select_container(is_config)[consumer].append(exp.copy())

    def _add_experiment_json_entry(
            self,
            json_entry,
            is_config,
            skip_check_schema=False,
            file_name=None,
    ):
        self._check_by_schema(
            json_entry=json_entry,
            is_config=is_config,
            skip_check_schema=skip_check_schema,
            place=f'file {file_name}',
        )

        if LAST_MODIFIED_AT in json_entry:
            self.revision = max(self.revision, json_entry[LAST_MODIFIED_AT])
        else:
            self.revision += 1
            json_entry[LAST_MODIFIED_AT] = self.revision
        for consumer in json_entry['match']['consumers']:
            consumer_name = consumer['name']
            self._add_consumer_if_not_exists(consumer_name, is_config)
            self._select_container(is_config)[consumer_name].append(json_entry)

    def _check_by_schema(
            self,
            json_entry: Dict,
            is_config: bool,
            skip_check_schema: bool,
            place: str,
    ):
        last_part_error_message = f', see {place}'
        if json_entry.get('default_value') is None and not json_entry.get(
                'clauses',
        ):
            raise BadTestArgs(
                f'Testsuite error: specify default_value argument or '
                f'at least one clause in clauses argument'
                f'{last_part_error_message}',
            )

        if skip_check_schema:
            warnings.warn(
                f'Testsuite warning: your experiment`s schemas '
                f'may be incorrect, '
                f'see {place} for check '
                f'and remove skip_check_schema argument '
                f'from experiments3 mark',
                SyntaxWarning,
            )
            return

        validator = (
            self._validators[CONFIG_VALIDATOR_PATH]
            if is_config
            else self._validators[EXPERIMENT_VALIDATOR_PATH]
        )
        error_message: Optional[str] = None
        try:
            validator.validate(json_entry)
        except jsonschema.ValidationError as exc:
            path_message = _get_pathmessage_by_exception(exc)
            error_message = (
                f'Testsuite error: {exc.message}, path={path_message}'
                f'{last_part_error_message}'
            )
        except jsonschema.RefResolutionError as exc:
            error_message = (
                f'Testsuite error: Bad reference in schema: {exc.__context__}'
                f'{last_part_error_message}'
            )
        except jsonschema.exceptions.UnknownType as exc:
            error_message = (
                f'Testsuite error: Don`t use bad "{exc.type}" '
                f'type{last_part_error_message}'
            )

        if error_message is not None:
            if self.strict_schema_checks:
                raise BadTestStatic(error_message)
            else:
                warnings.warn(error_message, SyntaxWarning)

    def _select_container(self, is_config):
        if is_config:
            return self.configs
        return self.experiments

    def _add_consumer_if_not_exists(self, consumer, is_config):
        container = self._select_container(is_config)
        if consumer not in container:
            container[consumer] = []

    def record_match_tries(self, exp_name):
        return MatchTriesRecorder(testpoint=self._testpoint, exp_name=exp_name)


def pytest_configure(config):
    config.addinivalue_line(
        'markers', 'experiments3: per-test experiments3.0 configuration',
    )


def pytest_addoption(parser):
    group = parser.getgroup('experiments3')
    group.addoption(
        '--strict-schema-checks',
        help='Enable strict checks experiment body by schema',
    )


@pytest.fixture(scope='session')
def experiments3_cache_files_path(worker_id):
    worker_suffix = '_' + worker_id if worker_id != 'master' else ''
    return '/var/tmp/cache/yandex/exp3' + worker_suffix


@pytest.fixture(scope='session')
def experiments3_schemas_path() -> pathlib.Path:
    return DEFAULT_SCHEMA_SEARCH_PATH


@pytest.fixture(scope='session')
def experiments3_validator_store(
        experiments3_schemas_path,
) -> JsonValidatorStore:
    return JsonValidatorStore(
        experiments3_schemas_path, reference_filenames=[],
    )


@pytest.fixture
def experiments3(
        request,
        pytestconfig,
        load_json,
        experiments3_validator_store,
        experiments3_cache_files_path,
        testpoint,
):
    strict_schema_checks = STRICT_CHECK_SCHEMA
    if pytestconfig.option.strict_schema_checks:
        strict_schema_checks = pytestconfig.option.strict_schema_checks

    experiments = Experiments3ProxyMock(
        experiments3_validator_store, testpoint, strict_schema_checks,
    )
    for marker in request.node.iter_markers('experiments3'):
        experiments.add_experiment3_from_marker(marker, load_json)

    yield experiments

    experiments.clear_cache_files(experiments3_cache_files_path)
