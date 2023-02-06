import datetime

import pytest

from hiring_tariffs.generated.cron import run_cron


async def _run():
    await run_cron.main(
        ['hiring_tariffs.crontasks.subscriptions_control_periods', '-t', '0'],
    )


@pytest.fixture
def _update_subs(pgsql):
    async def _wrapper(real_subs):
        result = {}
        for index, case in enumerate(
                [(31, True), (0, True), (-31, True), (-31, False)],
        ):
            sub_id = real_subs[index]['id']
            result[sub_id] = case
            ends_at = (
                datetime.datetime.now() + datetime.timedelta(days=case[0])
            ).strftime('%Y-%m-%d')
            starts_at = (
                datetime.datetime.now() - datetime.timedelta(days=31)
            ).strftime('%Y-%m-%d')
            with pgsql['hiring_misc'].cursor() as cursor:
                cursor.execute(
                    'UPDATE '
                    '   "hiring_tariffs"."subscriptions" '
                    'SET '
                    '   "autoprolong" = {autoprolong} '
                    'WHERE '
                    '   "id" = \'{sub_id}\''
                    '; '
                    'UPDATE '
                    '   "hiring_tariffs"."subscriptions_periods" '
                    'SET '
                    '   "status" = \'active\', '
                    '   "starts_at" = \'{starts_at}\', '
                    '   "ends_at" = \'{ends_at}\', '
                    '   "is_active" = TRUE '
                    'WHERE '
                    '   "subscription_id" = \'{sub_id}\''
                    ';'.format(
                        autoprolong=case[1],
                        sub_id=sub_id,
                        starts_at=starts_at,
                        ends_at=ends_at,
                    ),
                )
        return result

    return _wrapper


async def _check_subs(sub, expected):
    assert expected
    case = expected.get(sub['id'])
    if not case:
        return
    updates = sub['updates']
    statuses = {item['status']: item for item in sub['periods']}
    if case[0] >= 0:
        assert len(statuses) == 1
        assert len(updates) == 1
    elif case[1] is True:
        assert len(statuses) == 2
        assert len(updates) == 3
        assert sorted(statuses) == ['completed', 'processing']
        ends_at = datetime.datetime.strptime(
            statuses['processing']['ends_at'], '%Y-%m-%d',
        )
        assert ends_at > datetime.datetime.now()
    else:
        assert len(statuses) == 1
        assert len(updates) == 2
        assert sorted(statuses) == ['completed']


async def test_control_periods(
        pgsql, load_json, mock_approvals, create_subs, find_subs, _update_subs,
):
    await create_subs('multiple')

    real_subs = await find_subs()
    expected = await _update_subs(real_subs)

    await _run()

    real_subs = await find_subs()
    for sub in real_subs:
        await _check_subs(sub, expected)
