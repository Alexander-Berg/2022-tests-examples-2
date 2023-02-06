import datetime

import pytest
import pytz

from workforce_management.common.models.additional_shifts import rank
from workforce_management.storage.postgresql import db

FIRST_PARAMETERS = {
    'addshifts_count': {
        'start_timedelta_minutes_before': 43200,
        'use_start_timedelta_minutes_before': False,
    },
}

SECOND_PARAMETERS = {
    'addshifts_count': {
        'start_timedelta_minutes_before': 43200,
        'use_start_timedelta_minutes_before': True,
    },
}


@pytest.mark.pgsql(
    'workforce_management',
    files=[
        'simple_operators.sql',
        'simple_addshifts_jobs.sql',
        'simple_addshifts_candidates.sql',
    ],
)
@pytest.mark.parametrize(
    'input_uids, parameters, datetime_from, limit, expected_result',
    [
        pytest.param(
            [1, 2, 3],
            FIRST_PARAMETERS,
            datetime.datetime(2020, 7, 2, 00, tzinfo=pytz.UTC),
            3,
            [2, 1, 3],
            id='old_candidates',
        ),
        pytest.param(
            [1, 2, 3, 4],
            FIRST_PARAMETERS,
            datetime.datetime(2020, 7, 2, 00, tzinfo=pytz.UTC),
            4,
            [4, 2, 1, 3],
            id='uid4_new',
        ),
        pytest.param(
            [1, 2, 3, 4],
            FIRST_PARAMETERS,
            datetime.datetime(2020, 1, 2, 00, tzinfo=pytz.UTC),
            4,
            [4, 2, 1, 3],
            id='all_new_candidates',
        ),
        pytest.param(
            [1, 2, 3, 4],
            FIRST_PARAMETERS,
            datetime.datetime(2020, 6, 2, 00, tzinfo=pytz.UTC),
            4,
            [4, 2, 1, 3],
            id='mixed_shifts_intersections',
        ),
        pytest.param(
            [1, 2, 3],
            SECOND_PARAMETERS,
            datetime.datetime(2020, 10, 15, 00, tzinfo=pytz.UTC),
            3,
            [2, 3, 1],
            id='with_addshift_last_month',
        ),
        pytest.param(
            [1, 2, 3],
            SECOND_PARAMETERS,
            datetime.datetime(2020, 10, 15, 00, tzinfo=pytz.UTC),
            2.8,
            [2, 3, 1],
            id='with_float_limit',
        ),
    ],
)
async def test_ranked_candidates(
        stq3_context,
        stq_runner,
        stq,
        input_uids,
        parameters,
        datetime_from,
        limit,
        expected_result,
):
    operators_db = db.OperatorsRepo(context=stq3_context)
    async with operators_db.slave.acquire() as conn, conn.transaction():
        ranked_candidates = await rank.rank_candidates(
            operators_db=operators_db,
            conn=conn,
            parameters=parameters,
            candidates_uoids=input_uids,
            job_datetime_from=datetime_from,
            limit=limit,
        )

    assert [
        candidate['id'] for candidate in ranked_candidates
    ] == expected_result
