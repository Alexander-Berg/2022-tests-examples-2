import copy

import pytest

from achievements_py3.generated.cron import run_cron
from achievements_py3.generated.web import web_context as context_module


def find_uploads(schedule_id: str, pgsql):
    cursor = pgsql['achievements_pg'].cursor()
    cursor.execute(
        f"""
        SELECT
            status, reward_code, upload_type, yql, author, created
        FROM achievements_pg.uploads
        WHERE
            schedule_id='{schedule_id}'
        ORDER BY created
        ;
        """,
    )
    return [
        {
            'status': row[0],
            'reward_code': row[1],
            'upload_type': row[2],
            'yql': row[3],
            'author': row[4],
            'created': row[5],
        }
        for row in cursor
    ]


@pytest.mark.parametrize(
    'schedule_id',
    [
        'sched_inactive',
        'sched_no_period',
        'sched_bad_period',
        'sched_no_yql',
        'sched_bad_levels',
    ],
)
async def test_schedule_upload_failed(
        web_context: context_module.Context, schedule_id, pgsql,
):
    # crontask
    await run_cron.main(
        ['achievements_py3.crontasks.schedule_upload', '-t', '0'],
    )

    uploads_found = find_uploads(schedule_id, pgsql)
    assert uploads_found == []


@pytest.mark.parametrize(
    'schedule_id, reward_code, upload_type, yql, author',
    [
        (
            'sched_set_covid_hero',
            'covid_hero',
            'set_unlocked',
            'SELECT 1;',
            'ivan',
        ),
        (
            'sched_leveled_ok',
            'driver_years',
            'set_unlocked',
            'SELECT 1,1;',
            'ivan',
        ),
    ],
)
async def test_schedule_upload_ok(
        web_context: context_module.Context,
        schedule_id,
        reward_code,
        upload_type,
        yql,
        author,
        pgsql,
):
    # crontask
    await run_cron.main(
        ['achievements_py3.crontasks.schedule_upload', '-t', '0'],
    )

    uploads_found = find_uploads(schedule_id, pgsql)
    assert len(uploads_found) == 1
    new_upload = uploads_found[0]
    new_upload_copy = copy.deepcopy(new_upload)
    new_upload_copy.pop('created')

    assert new_upload_copy == {
        'status': 'new',
        'reward_code': reward_code,
        'upload_type': upload_type,
        'yql': yql,
        'author': author,
    }

    # run task again and check that new upload will not be created so soon

    await run_cron.main(
        ['achievements_py3.crontasks.schedule_upload', '-t', '0'],
    )

    new_uploads_found = find_uploads(schedule_id, pgsql)
    assert new_uploads_found == uploads_found


@pytest.mark.now('2019-02-01T01:00:02+03:00')
@pytest.mark.pgsql(
    'achievements_pg', files=['pg_achievements_pg_schedule_idempotency.sql'],
)
@pytest.mark.parametrize(
    'schedule_id, upload_created',
    [
        ('sched_star', False),
        ('sched_express', False),
        ('sched_top_fives', True),
    ],
)
async def test_schedule_upload_idempotency(
        web_context: context_module.Context,
        schedule_id,
        upload_created,
        pgsql,
):
    # # crontask
    await run_cron.main(
        ['achievements_py3.crontasks.schedule_upload', '-t', '0'],
    )

    uploads_found = find_uploads(schedule_id, pgsql)
    if upload_created:
        assert len(uploads_found) == 2
        old_upload = uploads_found[0]
        new_upload = uploads_found[1]
        assert new_upload['created'] > old_upload['created']
    else:
        assert len(uploads_found) == 1
