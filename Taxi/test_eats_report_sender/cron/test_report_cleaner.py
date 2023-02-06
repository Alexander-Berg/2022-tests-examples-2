# pylint: disable=redefined-outer-name
import datetime

import pytest

from eats_report_sender.generated.cron import run_cron


def check_report_exists(pgsql, report_uuid):
    with pgsql['eats_report_sender'].cursor() as cursor:
        cursor.execute(
            'SELECT EXISTS (SELECT 1 from reports WHERE uuid = \'%s\')'
            % report_uuid,
        )
        return cursor.fetchone()[0]


async def test_remove_old_reports(pgsql, create_report_by_sql, cron_context):

    success_ttl = (
        cron_context.config.EATS_REPORT_SENDER_REPORT_CLEANER_SETTINGS[
            'success_ttl'
        ]
    )
    fail_ttl = cron_context.config.EATS_REPORT_SENDER_REPORT_CLEANER_SETTINGS[
        'fail_ttl'
    ]

    time_ago_for_success = datetime.datetime.now() - datetime.timedelta(
        hours=success_ttl + 1,
    )
    time_ago_for_fail = datetime.datetime.now() - datetime.timedelta(
        hours=fail_ttl + 1,
    )

    deleted_success_uuid = create_report_by_sql(
        uuid='old_success_uuid__1',
        status='success',
        updated_at=time_ago_for_success,
        created_at=time_ago_for_success,
    )
    deleted_fail_uuid = create_report_by_sql(
        uuid='old_fail_uuid__1',
        status='success',
        updated_at=time_ago_for_fail,
        created_at=time_ago_for_fail,
    )

    not_deleted_success_uuid = create_report_by_sql(
        uuid='new_success_uuid__1', status='success',
    )
    not_deleted_fail_uuid = create_report_by_sql(
        uuid='new_fail_uuid__1', status='fail',
    )

    await run_cron.main(
        ['eats_report_sender.crontasks.report_cleaner', '-t', '0'],
    )

    assert check_report_exists(pgsql, not_deleted_success_uuid)
    assert check_report_exists(pgsql, not_deleted_fail_uuid)
    assert not check_report_exists(pgsql, deleted_success_uuid)
    assert not check_report_exists(pgsql, deleted_fail_uuid)


@pytest.mark.config(
    EATS_REPORT_SENDER_REPORT_CLEANER_SETTINGS={'enabled': False},
)
async def test_crontask_disable(patch):
    @patch('eats_report_sender.crontasks.report_cleaner._do_stuff')
    async def crontask_logic_mock(*args, **kwargs):
        pass

    await run_cron.main(
        ['eats_report_sender.crontasks.report_cleaner', '-t', '0'],
    )

    assert crontask_logic_mock.calls == []
