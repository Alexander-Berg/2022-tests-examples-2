import shlex
import mock
import pytest

from datetime import datetime

from click.testing import CliRunner

from dmp_suite.ctl.storage import DictStorage
from connection.ctl import WrapCtl
from dmp_suite.yt import (
    NotLayeredYtLayout,
    NotLayeredYtTable,
    DayPartitionScale,
    String
)
from dmp_suite.greenplum import (
    ExternalGPLayout,
    ExternalGPTable,
)
from dmp_suite.clickhouse import (
    CHTable,
    CHLayout
)
from dmp_suite.ctl import (
    CTL_LAST_LOAD_DATE,
    CTL_LAST_LOAD_DATE_MICROSECONDS,
    CTL_LAST_DDS_LOAD_DATE_MICROSECONDS,
    CTL_LAST_LOAD_ID,
    CTL_LAST_SYNC_DATE,
    CTL_DISABLED_UNTIL_DTTM,
    Parameter as CtlParameter,
    types as ctl_types,
)
from dmp_suite.task.base import PyTask


@pytest.fixture(autouse=True)
def ctl_mock():
    ctl = WrapCtl(DictStorage())
    patch_ = mock.patch('connection.ctl.get_ctl', return_value=ctl)
    with patch_:
        yield ctl


@pytest.fixture(autouse=True)
def ch_prefix_mock():
    with mock.patch(
        'dmp_suite.clickhouse.table.settings',
        return_value='',
    ):
        yield


class TestYtTable(NotLayeredYtTable):
    __layout__ = NotLayeredYtLayout('test', 'test_entity')


class TestYtTableWScale(NotLayeredYtTable):
    __layout__ = NotLayeredYtLayout('test', 'test_entity_scale')
    __partition_scale__ = DayPartitionScale('d')
    d = String()


class TestGPTable(ExternalGPTable):
    __layout__ = ExternalGPLayout('test_schema', 'test_entity')


class TestCHTable(CHTable):
    __layout__ = CHLayout('test_entity', db='test_db')


CTL_LAST_LOAD_DATE_TEST_CASES = [
    (
        'CTL_LAST_LOAD_DATE',
        CTL_LAST_LOAD_DATE,
        '2020-01-17 12:33:11',
        datetime(2020, 1, 17, 12, 33, 11),
    ),
]
CTL_LAST_LOAD_ID_TEST_CASES = [
    (
        'CTL_LAST_LOAD_ID',
        CTL_LAST_LOAD_ID,
        '42',
        42,
    )
]
CTL_LAST_LOAD_DATE_MICROSECONDS_TEST_CASES = [
    (
        'CTL_LAST_LOAD_DATE_MICROSECONDS',
        CTL_LAST_LOAD_DATE_MICROSECONDS,
        '2020-01-17 12:33:11.123456',
        datetime(2020, 1, 17, 12, 33, 11, 123456),
    ),
]
CTL_LAST_DDS_LOAD_DATE_MICROSECONDS_TEST_CASES = [
    (
        'CTL_LAST_DDS_LOAD_DATE_MICROSECONDS',
        CTL_LAST_DDS_LOAD_DATE_MICROSECONDS,
        '2020-01-17 12:33:11.123456',
        datetime(2020, 1, 17, 12, 33, 11, 123456),
    ),
]
CTL_LAST_SYNC_DATE_TEST_CASES = [
    (
        'CTL_LAST_SYNC_DATE',
        CTL_LAST_SYNC_DATE,
        '2020-01-18',
        datetime(2020, 1, 18),
    ),
]


@pytest.mark.parametrize(
    'domain, entity_click, entity_control',
    [
        (
            'yt',
            'test_dmp_suite.cli.ctl.set_test.TestYtTable',
            '//dummy/test/test_entity',
        ),
        (
            'yt',
            'test_dmp_suite.cli.ctl.set_test.TestYtTableWScale',
            '//dummy/test/test_entity_scale',
        ),
        (
            'source',
            'yttable#//home/taxi-dwh/ods/oktell/monitoring#octell.com',
            'yttable#//home/taxi-dwh/ods/oktell/monitoring#octell.com',
        ),
        (
            'gp',
            'test_dmp_suite.cli.ctl.set_test.TestGPTable',
            'test_schema.test_entity'
        ),
        (
            'ch',
            'test_dmp_suite.cli.ctl.set_test.TestCHTable',
            'test_db.test_entity'
        )
    ],
)
@pytest.mark.parametrize(
    'parameter_click, parameter_control, value_click, value_control',
    [
        *CTL_LAST_LOAD_DATE_TEST_CASES,
        *CTL_LAST_LOAD_DATE_MICROSECONDS_TEST_CASES,
        *CTL_LAST_DDS_LOAD_DATE_MICROSECONDS_TEST_CASES,
        *CTL_LAST_LOAD_ID_TEST_CASES,
        *CTL_LAST_SYNC_DATE_TEST_CASES,
    ]
)
def test_set_works_correctly(
        ctl_mock,
        domain,
        entity_click,
        entity_control,
        parameter_click,
        parameter_control,
        value_click,
        value_control,
):
    from dmp_suite.cli.main import cli

    runner = CliRunner()

    params = [
        entity_click,
        parameter_click,
        value_click,
    ]

    result = runner.invoke(cli, ['ctl', 'set', domain] + params)

    assert result.exit_code == 0, result

    domain_provider = getattr(ctl_mock, domain)
    actual = domain_provider.get_param(entity_control, parameter_control)
    assert actual == value_control, 'incorrect ctl returned'


def _run_with_raise(
        ctl,
        domain: str,
        entity_click,
        entity_control,
        parameter_click,
        parameter_control,
        value_click,
        value_control,
        err_msg,
):
    from dmp_suite.cli.main import cli

    runner = CliRunner()

    params = [
        entity_click,
        parameter_click,
        value_click,
    ]

    command = ['ctl', 'set', domain] + params
    result = runner.invoke(cli, command)
    joined_command = ' '.join(command)
    message = (
        f'Unhandled exception or success when calling "{joined_command}": {result}\n'
        f'OUTPUT:\n{result.stdout}\n\n'
    )
    assert result.exit_code == 2, message
    assert err_msg in str(result.output)
    domain_provider = getattr(ctl, domain, None)
    if domain_provider is not None:
        assert domain_provider.get_param(
            entity_control, parameter_control) is None


@pytest.mark.parametrize(
    'domain, entity_click, entity_control, err_msg',
    [
        pytest.param(
            'yt',
            'test_dmp_suite/cli/ctl/set_test/TestYtTable',
            '//dummy/test/test_entity',

            'Path to table should',
            id='incorrect_table_path'
        ),
        pytest.param(
            'gp',
            'test_dmp_suite.cli.ctl.set_test.TestYtTableWScale',
            '//dummy/test/test_entity_scale',

            'Wrong table',
            id='entity_does_not_match_domain'
        ),
        pytest.param(
            'incorrect domain',
            'test_dmp_suite.cli.ctl.set_test.TestYtTableWScale',
            '//dummy/test/test_entity_scale',
            'Usage: cli ctl',
            id='non_existent_domain'
        ),
    ],
)
@pytest.mark.parametrize(
    'parameter_click, parameter_control, value_click, value_control',
    [
        *CTL_LAST_LOAD_ID_TEST_CASES,
    ]
)
def test_set_with_incorrect_entity_raises(
        ctl_mock,
        domain,
        entity_click,
        entity_control,
        parameter_click,
        parameter_control,
        value_click,
        value_control,
        err_msg,
):
    _run_with_raise(
        ctl_mock,
        domain,
        entity_click,
        entity_control,
        parameter_click,
        parameter_control,
        value_click,
        value_control,
        err_msg,
    )


@pytest.mark.parametrize(
    'domain, entity_click, entity_control',
    [
        (
            'yt',
            'test_dmp_suite.cli.ctl.set_test.TestYtTable',
            '//dummy/test/test_entity',
        ),
    ],
)
@pytest.mark.parametrize(
    'parameter_click, parameter_control, value_click, value_control, err_msg',
    [
        (
            'CTL_LAST_LOAD_ID',
            CTL_LAST_LOAD_ID,
            'not an integer',
            12,
            'Wrong `value`',
        ),
        (
            'NON_EXISTENT_PARAM',
            CtlParameter('non_existent_param', ctl_types.Integer),
            '12',
            12,
            'Wrong `parameter`',
        )
    ]
)
def test_set_with_incorrect_params_yraises(
        ctl_mock,
        domain,
        entity_click,
        entity_control,
        parameter_click,
        parameter_control,
        value_click,
        value_control,
        err_msg,
):
    _run_with_raise(
        ctl_mock,
        domain,
        entity_click,
        entity_control,
        parameter_click,
        parameter_control,
        value_click,
        value_control,
        err_msg,
    )


def test_disable_task(ctl_mock):
    from dmp_suite.cli.main import cli

    runner = CliRunner()
    task = PyTask('test_task', lambda x: None)

    params = [
        'ctl',
        'set',
        'task',
        'test_task',
        'CTL_DISABLED_UNTIL_DTTM',
        '2020-01-01 19:44:44',
    ]

    with mock.patch('dmp_suite.cli.ctl.utils.arguments.resolve_task_instance',
                    return_value=task):
        result = runner.invoke(cli, params)

    assert result.exit_code == 0, result

    actual = ctl_mock.task.get_param(task, CTL_DISABLED_UNTIL_DTTM)
    assert actual == datetime(2020, 1, 1, 19, 44, 44)


def shlex_join(xs):
    return ' '.join(map(shlex.quote, xs))


@pytest.mark.parametrize(
    'commands',
    [
        # single command
        [
            (
                'yt',
                'test_dmp_suite.cli.ctl.set_test.TestYtTable',
                '//dummy/test/test_entity',
                'CTL_LAST_LOAD_DATE',
                CTL_LAST_LOAD_DATE,
                '2020-01-17 12:33:11',
                datetime(2020, 1, 17, 12, 33, 11),
            )
        ],
        # multiple same commands
        [
            (
                'yt',
                'test_dmp_suite.cli.ctl.set_test.TestYtTable',
                '//dummy/test/test_entity',
                'CTL_LAST_SYNC_DATE',
                CTL_LAST_SYNC_DATE,
                '2020-01-18',
                datetime(2020, 1, 18),
            ),
            (
                'yt',
                'test_dmp_suite.cli.ctl.set_test.TestYtTableWScale',
                '//dummy/test/test_entity_scale',
                'CTL_LAST_SYNC_DATE',
                CTL_LAST_SYNC_DATE,
                '2020-01-18',
                datetime(2020, 1, 18),
            ),
            (
                'source',
                'yttable#//home/taxi-dwh/ods/oktell/monitoring#octell.com',
                'yttable#//home/taxi-dwh/ods/oktell/monitoring#octell.com',
                'CTL_LAST_SYNC_DATE',
                CTL_LAST_SYNC_DATE,
                '2020-01-18',
                datetime(2020, 1, 18),
            ),
            (
                'gp',
                'test_dmp_suite.cli.ctl.set_test.TestGPTable',
                'test_schema.test_entity',
                'CTL_LAST_SYNC_DATE',
                CTL_LAST_SYNC_DATE,
                '2020-01-18',
                datetime(2020, 1, 18),
            ),
            (
                'ch',
                'test_dmp_suite.cli.ctl.set_test.TestCHTable',
                'test_db.test_entity',
                'CTL_LAST_SYNC_DATE',
                CTL_LAST_SYNC_DATE,
                '2020-01-18',
                datetime(2020, 1, 18),
            ),
        ],
        # multiple different commands
        [
            (
                'yt',
                'test_dmp_suite.cli.ctl.set_test.TestYtTable',
                '//dummy/test/test_entity',
                'CTL_LAST_LOAD_ID',
                CTL_LAST_LOAD_ID,
                '42',
                42,
            ),
            (
                'yt',
                'test_dmp_suite.cli.ctl.set_test.TestYtTable',
                '//dummy/test/test_entity',
                'CTL_LAST_LOAD_DATE_MICROSECONDS',
                CTL_LAST_LOAD_DATE_MICROSECONDS,
                '2020-01-17 12:33:11.123456',
                datetime(2020, 1, 17, 12, 33, 11, 123456),
            ),
            (
                'yt',
                'test_dmp_suite.cli.ctl.set_test.TestYtTable',
                '//dummy/test/test_entity',
                'CTL_LAST_DDS_LOAD_DATE_MICROSECONDS',
                CTL_LAST_DDS_LOAD_DATE_MICROSECONDS,
                '2020-01-17 12:33:11.123456',
                datetime(2020, 1, 17, 12, 33, 11, 123456),

            ),
        ],
    ]
)
def test_set_multiple_works_correctly(ctl_mock, commands):

    args = []
    targets = []
    for domain, entity, entity_ctl, param, param_ctl, value, value_ctl in commands:
        args.extend(['--', domain, entity, param, value])
        targets.append((domain, entity_ctl, param_ctl, value_ctl))

    from dmp_suite.cli.main import cli
    runner = CliRunner()
    result = runner.invoke(cli, ['ctl', 'set', *args])
    assert result.exit_code == 0, result

    for domain, entity, param, value in targets:
        domain_provider = getattr(ctl_mock, domain)
        actual = domain_provider.get_param(entity, param)
        assert actual == value, f'incorrect ctl returned for ' \
                                f'domain={domain}, entity={entity}, param={param}:' \
                                f'expected {value} got {actual}'


def test_set_multiple_fails_correctly(ctl_mock):

    task = PyTask('test_task', lambda x: None)

    expected_value = datetime(2020, 1, 1, 7, 7, 7)
    ctl_mock.task.set_param(task, CTL_DISABLED_UNTIL_DTTM, expected_value)

    params = [
        'ctl',
        'set',
        '--',
        'task',
        'test_task',
        'CTL_DISABLED_UNTIL_DTTM',
        '2020-01-01 13:13:13',
        '--',
        'task',
        'test_task',
        'CTL_DISABLED_UNTIL_DTTM',
        '2020-01-01 71:17:17',
        '--',
        'task',
        'test_task',
        'CTL_DISABLED_UNTIL_DTTM',
        '2020-01-01 23:23:23',
    ]

    with mock.patch('dmp_suite.cli.ctl.utils.arguments.resolve_task_instance',
                    return_value=task):
        from dmp_suite.cli.main import cli
        runner = CliRunner()
        result = runner.invoke(cli, params)

    assert result.exit_code == 2, result

    actual = ctl_mock.task.get_param(task, CTL_DISABLED_UNTIL_DTTM)
    assert actual == expected_value
