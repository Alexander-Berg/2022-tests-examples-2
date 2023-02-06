import datetime

import pytest
import regex

from taxi_billing_calculators.utils import migration

_NOW = datetime.datetime(2021, 10, 1, tzinfo=datetime.timezone.utc)


@pytest.mark.parametrize(
    'expected_mode, settings',
    [
        pytest.param(
            migration.Mode.ENABLED,
            {
                '__default__': {
                    'enabled': [{'since': '1999-06-18T07:15:00+00:00'}],
                },
            },
        ),
        pytest.param(migration.Mode.DISABLED, {'__default__': {}}),
        pytest.param(
            migration.Mode.DISABLED,
            {
                '__default__': {
                    'enabled': [{'since': '1999-06-18T07:15:00+00:00'}],
                },
                'kursk': {
                    'disabled': [{'since': '2021-09-29T00:00:00+00:00'}],
                },
            },
        ),
        pytest.param(
            migration.Mode.ENABLED,
            {
                '__default__': {
                    'enabled': [{'since': '1999-06-18T07:15:00+00:00'}],
                },
                'kursk': {
                    'disabled': [
                        {
                            'since': '2021-09-29T00:00:00+00:00',
                            'till': '2021-09-30T00:00:00+00:00',
                        },
                    ],
                },
            },
            id='enabled by default due to no match interval in zone config',
        ),
        pytest.param(
            migration.Mode.TEST,
            {
                '__default__': {
                    'enabled': [
                        {
                            'since': '2021-09-30T00:10:00+00:00',
                            'till': '2021-10-02T00:10:00+00:00',
                        },
                    ],
                    'test': [
                        {
                            'since': '2021-09-30T00:10:00+00:00',
                            'till': '2021-10-02T00:10:00+00:00',
                        },
                    ],
                },
            },
            id='`test` priority is higher than `enabled`',
        ),
        pytest.param(
            migration.Mode.DISABLED,
            {
                '__default__': {
                    'test': [
                        {
                            'since': '2021-09-30T00:10:00+00:00',
                            'till': '2021-10-02T00:10:00+00:00',
                        },
                    ],
                    'disabled': [
                        {
                            'since': '2021-09-30T00:10:00+00:00',
                            'till': '2021-10-02T00:10:00+00:00',
                        },
                    ],
                },
            },
            id='`disabled` priority is highest',
        ),
    ],
)
def test_match(expected_mode, settings):
    actual_mode = migration.match(settings, 'kursk', _NOW)
    assert actual_mode == expected_mode


@pytest.mark.parametrize(
    'mode, std_call, ng_call, std_result, '
    'ng_result, expected_result, log_exists',
    [
        (migration.Mode.DISABLED, True, False, 1, 2, 1, False),
        (migration.Mode.ENABLED, False, True, 1, 2, 2, False),
        (migration.Mode.TEST, True, True, 1, 2, 1, True),
        (migration.Mode.TEST, True, True, 1, 1, 1, False),
    ],
)
async def test_migration_executer(
        mode,
        std_call,
        ng_call,
        std_result,
        ng_result,
        expected_result,
        log_exists,
        caplog,
):
    async def ng_fn():
        ng_fn.called = True
        return ng_result

    ng_fn.called = False

    async def std_fn():
        std_fn.called = True
        return std_result

    std_fn.called = False

    result = await migration.execute(std_fn, ng_fn, mode)
    assert result == expected_result
    assert ng_call == ng_fn.called
    assert std_call == std_fn.called
    if log_exists:
        assert regex.findall('(ERROR|WARNING)', caplog.text) == ['WARNING']


async def test_migration_executer_call_logger():
    async def ng_fn():
        return -1

    async def std_fn():
        return 1

    def logger_fn(*args, **kwargs):
        logger_fn.called += 1

    logger_fn.called = 0

    result = await migration.execute(
        std_fn, ng_fn, migration.Mode.TEST, logger_func=logger_fn,
    )
    assert result == 1
    assert logger_fn.called == 1


async def test_migration_executer_call_eq():
    async def ng_fn():
        return -1

    async def std_fn():
        return 1

    def eq_fn(std_result, ng_result):
        eq_fn.called += 1
        return std_result == ng_result

    eq_fn.called = 0

    result = await migration.execute(
        std_fn, ng_fn, migration.Mode.TEST, eq_func=eq_fn,
    )
    assert result == 1
    assert eq_fn.called == 1
