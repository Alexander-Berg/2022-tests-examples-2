# pylint: disable=protected-access
import typing

import pytest

from taxi.util import monrun

from crm_admin.monrun_checks.checkers import base

CRM_ADMIN_MONRUN = {
    'Limits': {
        'testing_limit_in_seconds': 100,
        'not_start_limit_in_seconds': 0,
    },
}


class TestBaseChecker(base.BaseChecker):
    async def _gen_report(self) -> typing.Dict[str, typing.Iterable]:
        pass


@pytest.mark.config(CRM_ADMIN_MONRUN=CRM_ADMIN_MONRUN)
async def test_seconds_limit_property(cron_context):
    async with cron_context.pg.master_pool.acquire() as conn:
        checker = TestBaseChecker('testing', cron_context, conn)

        settings = cron_context.config.CRM_ADMIN_MONRUN['Limits']
        assert checker.seconds_limit == settings['testing_limit_in_seconds']


async def test_make_message_from_report():
    report = {
        'Frozen campaigns': [1, 3, 4, 5],
        'Additional errors': ['something go wrong', 'error'],
        'Errors': [],
    }
    answer = await TestBaseChecker._make_message(report)
    expected = (
        'Frozen campaigns: 1, 3, 4, 5.\n'
        'Additional errors: something go wrong, error.'
    )
    assert answer == expected


async def test_success_gen_answer(cron_context):
    async with cron_context.pg.master_pool.acquire() as conn:
        checker = TestBaseChecker('testing', cron_context, conn)

        report = {'Empty': [], 'Empty #2': ()}

        answer = await checker._gen_answer(report)
        assert answer == (monrun.LEVEL_NORMAL, checker.SUCCESS_DESCRIPTION)


async def test_warning_gen_answer(cron_context):
    async with cron_context.pg.master_pool.acquire() as conn:
        checker = TestBaseChecker('testing', cron_context, conn)
        report = {'Errors': ['error']}

        answer = await checker._gen_answer(report)
        assert answer == (monrun.LEVEL_WARNING, 'Errors: error.')


@pytest.mark.config(CRM_ADMIN_MONRUN=CRM_ADMIN_MONRUN)
@pytest.mark.parametrize('entity', ['not_start', 'something'])
async def test_check_is_off(cron_context, mock, entity):
    TestBaseChecker._gen_report = mock(lambda *args, **kwargs: ...)

    async with cron_context.pg.master_pool.acquire() as conn:
        checker = TestBaseChecker(entity, cron_context, conn)
        answer = await checker.check()

        # pylint: disable=no-member
        assert not TestBaseChecker._gen_report.calls
        assert answer == (monrun.LEVEL_NORMAL, checker.SUCCESS_DESCRIPTION)
