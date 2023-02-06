import collections
import datetime


from hiring_tariffs.generated.cron import run_cron


async def _run():
    await run_cron.main(
        [
            'hiring_tariffs.crontasks.subscriptions_drafts_create_and_poll',
            '-t',
            '0',
        ],
    )


async def _check_subs(sub, first_run: bool = True):
    periods = sub['periods']
    updates = sub['updates']
    status = periods[0]['status']
    assert len(periods) == 1

    if first_run:
        assert status in ['draft', 'active', 'rejected']
        if status == 'active':
            assert len(updates) == 1
        else:
            assert len(updates) == 2
    else:
        if status == 'processing':
            assert len(updates) == 3
            today_str = datetime.datetime.now().date().isoformat()
            assert periods[0]['starts_at'] == today_str
        elif status == 'active':
            assert len(updates) == 1
        else:
            assert 2 <= len(updates) <= 3

    return status


async def test_drafts_create_and_apply(
        pgsql, load_json, mock_approvals, create_subs, find_subs,
):
    await create_subs('multiple')
    with pgsql['hiring_misc'].cursor() as cursor:
        cursor.execute(
            'WITH "ids" as ('
            '   SELECT "id"'
            '   FROM "hiring_tariffs"."subscriptions" '
            '   WHERE "subscriber_id" = ANY(ARRAY[\'CLID4\', \'CLID5\']) '
            '), "updates" AS ('
            '   UPDATE "hiring_tariffs"."subscriptions_periods" '
            '   SET "status" = \'initiated\''
            ') '
            'UPDATE "hiring_tariffs"."subscriptions_periods" '
            'SET "status" = \'active\' '
            'FROM (SELECT "id" FROM "ids") AS "ids"'
            'WHERE'
            '   "subscription_id" = "ids"."id"',
        )
        cursor.execute(
            'UPDATE "hiring_tariffs"."subscriptions_periods" '
            'SET "starts_at" = CURRENT_DATE + interval \'1\' day * 5',
        )
    await _run()
    real_subs = await find_subs()
    for sub in real_subs:
        await _check_subs(sub)

    await _run()
    expected = {'active': 1, 'rejected': 2, 'processing': 2}
    real_subs = await find_subs()
    statuses = collections.defaultdict(int)
    for sub in real_subs:
        status = await _check_subs(sub, first_run=False)
        statuses[status] += 1
    assert expected == statuses
