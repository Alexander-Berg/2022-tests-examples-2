# pylint: disable=protected-access
import datetime
import pathlib
import re
import typing

import attr
from dateutil import parser as date_parser
import freezegun
import pytest
import yaml

from taxi.pg import pool
from taxi.util import itertools_ext

from archiving import consts
from archiving import cron_run
from archiving import loaders
from archiving import settings
from archiving.metrics import solomon
from archiving.sources.postgres import archiver as postgres_archiver
from test_archiving import conftest

_POSTGRES_TESTS_DIR = 'pg-tests'
_TESTCASES_DIR = 'testcases'

_INIT_DB_FILE = 'init_db.sql'
_METAINFO_FILE = 'metainfo.yaml'

_TESTCASE_REGEX = r'test-([0-9]+)\.(before|after)\.sql'

_DROP_TABLE_QUERY = 'DROP TABLE IF EXISTS {table}'
_CLEAN_TABLE_QUERY = 'TRUNCATE {table} CASCADE'

_QUERY_MISSING_ERR_MSG = (
    'Either query filling db or expected db '
    'state query is missing rule {rule_name}, '
    'testcase {idx}, path: {testcases_dir_path}'
)


def _timestr_to_datetime(value):
    if value is None:
        return value
    return date_parser.parse(value)


class _PGTestsInfo(typing.NamedTuple):
    init_db_path: pathlib.Path
    fill_db_query: str
    expected_db_query: str
    freeze_now: str
    tables_involved: typing.Optional[list] = None
    replication_min_ts: typing.Optional[datetime.datetime] = None


@attr.dataclass
class _TestsMetaInfo:
    freeze_now: str = attr.ib()
    tables_involved: typing.Optional[typing.List[str]] = attr.ib(default=None)
    replication_min_ts: typing.Optional[datetime.datetime] = attr.ib(
        default=None, converter=_timestr_to_datetime,  # type: ignore
    )

    @freeze_now.validator
    def check(self, attribute, value):
        date_parser.parse(value)

    @tables_involved.validator
    def check_tables(self, attribute, value):
        if value is None:
            return
        if not isinstance(value, list):
            raise TypeError(f'Field tables_involved should be of list type')
        if not all(isinstance(x, str) for x in value):
            raise TypeError(f'Fields in tables_involved should be strings')


def _get_tests_struct(rule_tests_dir, rule_name) -> typing.List[_PGTestsInfo]:
    init_db_path = pathlib.Path(
        rule_tests_dir.parent, 'schemas', _INIT_DB_FILE,
    )
    testcases_dir_path = pathlib.Path(rule_tests_dir, _TESTCASES_DIR)
    metainfo_path = pathlib.Path(rule_tests_dir, _METAINFO_FILE)
    _validate_test_files(
        init_db_path, metainfo_path, rule_name, testcases_dir_path,
    )
    metainfo_dict = (
        yaml.load(metainfo_path.read_text(), Loader=yaml.CSafeLoader) or {}
    )
    try:
        tests_metainfo: _TestsMetaInfo = _TestsMetaInfo(**metainfo_dict)
    except (AttributeError, ValueError, TypeError) as exc:
        raise ValueError(f'Wrong tests metainfo, rule {rule_name}: {str(exc)}')
    testcases_paths = sorted(
        x for x in testcases_dir_path.iterdir() if x.is_file()
    )
    if not testcases_paths:
        raise ValueError(f'Empty testcases dir, rule {rule_name}')
    tests_struct_list = []
    for idx, testcase_pair in enumerate(
            itertools_ext.chunks(testcases_paths, 2),
    ):
        if len(testcase_pair) != 2:
            raise ValueError(
                _QUERY_MISSING_ERR_MSG.format(
                    rule_name=rule_name,
                    idx=idx,
                    testcases_dir_path=str(testcases_dir_path),
                ),
            )
        expected_db_query, fill_db_query = _get_db_queries(
            idx, rule_name, testcase_pair, testcases_dir_path,
        )
        if tests_metainfo.replication_min_ts is not None:
            replication_min_ts = tests_metainfo.replication_min_ts
        else:
            replication_min_ts = date_parser.parse(tests_metainfo.freeze_now)
        tests_struct_list.append(
            _PGTestsInfo(
                init_db_path=init_db_path,
                fill_db_query=fill_db_query,
                expected_db_query=expected_db_query,
                freeze_now=tests_metainfo.freeze_now,
                replication_min_ts=replication_min_ts,
                tables_involved=tests_metainfo.tables_involved,
            ),
        )
    return tests_struct_list


def _validate_test_files(
        init_db_path, metainfo_path, rule_name, testcases_dir_path,
):
    if not init_db_path.is_file():
        raise ValueError(
            f'Init db file {str(init_db_path)} is missing, '
            f'rule {rule_name}',
        )
    if not metainfo_path.is_file():
        raise ValueError(
            f'Metainfo file {str(init_db_path)} is missing, '
            f'rule {rule_name}',
        )
    if not testcases_dir_path.is_dir():
        raise ValueError(
            f'Testcases dir {str(testcases_dir_path)} is missing, '
            f'rule {rule_name}',
        )


def _get_db_queries(idx, rule_name, testcase_pair, testcases_dir_path):
    fill_db_query = None
    expected_db_query = None
    file_path: pathlib.Path
    for file_path in testcase_pair:
        file_name = file_path.name
        match_obj = re.match(_TESTCASE_REGEX, str(file_name))
        if match_obj is None:
            raise ValueError(
                f'{str(file_path)} name {file_name} does not correspond '
                f'to regex {_TESTCASE_REGEX}',
            )
        testcase_idx, state_identifier = match_obj.groups()
        if int(testcase_idx) != idx:
            raise ValueError(
                _QUERY_MISSING_ERR_MSG.format(
                    rule_name=rule_name,
                    idx=idx,
                    testcases_dir_path=str(testcases_dir_path),
                ),
            )
        if state_identifier == 'before':
            fill_db_query = file_path.read_text()
        else:
            expected_db_query = file_path.read_text()
    if any(x is None for x in [fill_db_query, expected_db_query]):
        raise ValueError(
            _QUERY_MISSING_ERR_MSG.format(
                rule_name=rule_name,
                idx=idx,
                testcases_dir_path=str(testcases_dir_path),
            ),
        )
    if not fill_db_query:
        raise ValueError(
            f'Testcase can not be empty, rule name: {rule_name}, '
            f'index: {idx}, testcases_dir_path: {str(testcases_dir_path)})',
        )
    return expected_db_query, fill_db_query


def _parametrize_pg_db_tests(rules_dir):
    parametrize_values = []
    parametrize_keys = []
    rules_preparing_info: typing.Sequence[loaders.RulePreparingInfo] = (
        loaders.get_rules_static_info(
            rules_dir=rules_dir, source_type=consts.POSTGRES_SOURCE_TYPE,
        )
    )
    for rule_preparing_info in rules_preparing_info:
        rule_name = rule_preparing_info.name
        rule_tests_dir = pathlib.Path(
            rules_dir,
            rule_preparing_info.group_name,
            _POSTGRES_TESTS_DIR,
            rule_name,
        )
        if not rule_tests_dir.exists():
            continue
        tests_struct_list: typing.List[_PGTestsInfo] = _get_tests_struct(
            rule_tests_dir, rule_name,
        )
        for idx, tests_struct in enumerate(tests_struct_list):
            parametrize_values.append((rule_preparing_info.name, tests_struct))
            parametrize_keys.append('_'.join([rule_name, str(idx)]))

    return pytest.mark.parametrize(
        'rule_name, tests_struct', parametrize_values, ids=parametrize_keys,
    )


@pytest.fixture(scope='session')
def _pg_init_db_calls():
    return set()


@_parametrize_pg_db_tests(rules_dir=conftest._TEST_RULES_DIR)
async def test_test_rules_db(
        cron_context,
        patch_test_env,
        _pg_init_db_calls,
        pg_secdist_patch,
        replication_state_min_ts,
        requests_handlers,
        rule_name,
        tests_struct: _PGTestsInfo,
):
    with freezegun.freeze_time(tests_struct.freeze_now):
        await _test_pg_rules_with_db(
            cron_context,
            _pg_init_db_calls,
            rule_name,
            tests_struct,
            replication_state_min_ts,
        )


@_parametrize_pg_db_tests(rules_dir=settings.RULES_DIR)
@pytest.mark.norerun
async def test_production_rules_db(
        cron_context,
        _pg_init_db_calls,
        pg_secdist_patch,
        requests_handlers,
        replication_state_min_ts,
        rule_name,
        tests_struct: _PGTestsInfo,
):
    with freezegun.freeze_time(tests_struct.freeze_now):
        await _test_pg_rules_with_db(
            cron_context,
            _pg_init_db_calls,
            rule_name,
            tests_struct,
            replication_state_min_ts,
        )


async def _test_pg_rules_with_db(
        cron_context,
        _pg_init_db_calls,
        rule_name,
        tests_struct,
        replication_state_min_ts,
):
    archiving_rule = await loaders.load_rule(
        cron_context.clients.archiving_admin, rule_name, cron_context.config,
    )
    replication_state_min_ts.apply_simple(
        [archiving_rule.replication_metainfo.rule_name]
        + (archiving_rule.replication_metainfo.dependent_rule_names or []),
        field=archiving_rule.ttl_info.field,
        replication_min_ts=tests_struct.replication_min_ts,
    )

    archivers = await cron_run.prepare_archivers(
        cron_context, rule_name, task_id='test',
    )
    archiver = next(iter(archivers.values()))
    archiver: postgres_archiver.PostgresArchiver  # type: ignore
    source: pool.Pool = await archiver.get_source(slave=False)
    tables_to_check = [archiver._table]
    tables_involved = tests_struct.tables_involved
    if tables_involved is not None:
        for table in tables_involved:
            if table not in tables_to_check:
                tables_to_check.append(table)
    init_db_path_str = str(tests_struct.init_db_path)
    if init_db_path_str not in _pg_init_db_calls:
        _pg_init_db_calls.add(init_db_path_str)
        init_db_query = tests_struct.init_db_path.read_text()
        await source.execute(init_db_query)
    for table in tables_to_check:
        await source.execute(_CLEAN_TABLE_QUERY.format(table=table))
    await source.execute(tests_struct.fill_db_query)
    await archiver.remove_documents(monitor=solomon.get_monitor(rule_name))
    state_after_archiving_by_tables = {}
    primary_key_by_tables = {}
    for table_to_check in tables_to_check:
        pk_query, pk_query_args = cron_context.sqlt(
            'get_pk_names.sqlt', {'table_name': table_to_check},
        )
        primary_key_list = await source.fetch(pk_query, *pk_query_args)
        assert primary_key_list, (
            f'Primary key is required for tests, table: {table_to_check} '
            f'rule: {rule_name}',
        )
        primary_key_by_tables[table_to_check] = [
            x['primary_key'] for x in primary_key_list
        ]
        state_after_archiving_by_tables[table_to_check] = (
            await conftest.load_pg_source_docs(
                archiver,
                table_name=table_to_check,
                get_all_columns=True,
                primary_key=primary_key_by_tables[table_to_check],
                get_ordered=True,
            )
        )
    for table_to_check in tables_to_check:
        await source.execute(_CLEAN_TABLE_QUERY.format(table=table_to_check))
    if tests_struct.expected_db_query:  # if anything is left in db
        await source.execute(tests_struct.expected_db_query)
    for (
            table_to_check,
            state_after_archiving,
    ) in state_after_archiving_by_tables.items():
        assert state_after_archiving == await conftest.load_pg_source_docs(
            archiver,
            table_name=table_to_check,
            get_all_columns=True,
            primary_key=primary_key_by_tables[table_to_check],
            get_ordered=True,
        ), (
            f'Rows left in database after archiving do '
            f'not match expected in the testcase, rule: {rule_name}, '
            f'table: {table_to_check}'
        )
    await archiver.close()
