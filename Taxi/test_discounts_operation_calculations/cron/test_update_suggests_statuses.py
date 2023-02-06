# pylint: disable=redefined-outer-name,unused-variable
import datetime

from aiohttp import web
import pytest

from discounts_operation_calculations.generated.cron import run_cron
from discounts_operation_calculations.internals import statuses

EXPECTED_STATUSES = [
    (
        1,
        123,
        statuses.Statuses.waiting_to_start,
        None,
        datetime.datetime(2020, 8, 18, 12, 49, 22, 373412),
    ),
    (
        2,
        15,
        statuses.Statuses.rejected,
        None,
        datetime.datetime(2020, 8, 17, 12, 49, 22, 373412),
    ),
    (3, None, statuses.Statuses.not_published, None, None),
    (
        4,
        42,
        statuses.Statuses.rejected,
        None,
        datetime.datetime(2020, 8, 13, 12, 49, 22, 373412),
    ),
    (
        5,
        99,
        statuses.Statuses.finished,
        None,
        datetime.datetime(2020, 8, 13, 12, 49, 22, 373412),
    ),
    (6, 101, statuses.Statuses.finished, None, None),
    # with_push == false cases
    (
        7,
        107,
        statuses.Statuses.succeeded,
        datetime.datetime(2020, 8, 13, 12, 49, 22, 373412),
        datetime.datetime(2020, 8, 15, 12, 49, 22, 373412),
    ),
    (
        8,
        108,
        statuses.Statuses.succeeded,
        datetime.datetime(2020, 8, 13, 12, 49, 22, 373412),
        datetime.datetime(2020, 8, 15, 12, 49, 22, 373412),
    ),
    # with_push == true cases
    (
        9,
        109,
        statuses.Statuses.waiting_to_stop,
        datetime.datetime(2020, 8, 13, 12, 49, 22, 373412),
        datetime.datetime(2020, 8, 14, 12, 49, 22, 373412),
    ),
    (
        10,
        110,
        statuses.Statuses.succeeded,
        datetime.datetime(2020, 8, 13, 12, 49, 22, 373412),
        datetime.datetime(2020, 8, 15, 10, 49, 22, 373412),
    ),
    (
        11,
        111,
        statuses.Statuses.waiting_to_start,
        datetime.datetime(2020, 8, 14, 10, 49, 22, 373412),
        datetime.datetime(2020, 8, 16, 12, 49, 22, 373412),
    ),
    # update new discount started and old stopped
    (
        12,
        212,
        statuses.Statuses.finished,
        datetime.datetime(2020, 8, 13, 12, 49, 22, 373412),
        datetime.datetime(2020, 8, 14, 9, 49, 22, 373412),
    ),
    (
        13,
        213,
        statuses.Statuses.succeeded,
        datetime.datetime(2020, 8, 14, 9, 49, 22, 373412),
        datetime.datetime(2020, 8, 17, 12, 49, 22, 373412),
    ),
    # updated appoved statuses
    (
        14,
        214,
        statuses.Statuses.partially_completed,
        datetime.datetime(2020, 8, 14, 12, 49, 22, 373412),
        datetime.datetime(2020, 8, 18, 12, 49, 22, 373412),
    ),
    (
        15,
        215,
        statuses.Statuses.waiting_to_start,
        datetime.datetime(2020, 8, 14, 12, 49, 22, 373412),
        datetime.datetime(2020, 8, 19, 12, 49, 22, 373412),
    ),
    # update stopped statuses
    (
        16,
        216,
        statuses.Statuses.finished,
        datetime.datetime(2020, 8, 13, 12, 49, 22, 373412),
        datetime.datetime(2020, 8, 14, 9, 49, 22, 373412),
    ),
    (
        17,
        217,
        statuses.Statuses.finished,
        datetime.datetime(2020, 8, 14, 9, 49, 22, 373412),
        None,
    ),
    # update succeded statuses to waiting_to_stop
    # due to date_to - creation_lag < utcnow
    (
        18,
        218,
        statuses.Statuses.succeeded,
        datetime.datetime(2020, 8, 13, 12, 49, 22, 373412),
        datetime.datetime(2020, 8, 14, 11, 49, 22, 373412),
    ),
    (
        19,
        219,
        statuses.Statuses.waiting_to_stop,
        datetime.datetime(2020, 8, 13, 12, 49, 22, 373412),
        datetime.datetime(2020, 8, 14, 10, 49, 22, 373412),
    ),
    # as upper, but for with_push == true
    (
        20,
        220,
        statuses.Statuses.succeeded,
        datetime.datetime(2020, 8, 13, 12, 49, 22, 373412),
        datetime.datetime(2020, 8, 15, 10, 49, 22, 373412),
    ),
    (
        21,
        221,
        statuses.Statuses.waiting_to_stop,
        datetime.datetime(2020, 8, 13, 12, 49, 22, 373412),
        datetime.datetime(2020, 8, 15, 9, 49, 22, 373412),
    ),
    # case when only WAITING_TO_START suggest exists
    # and stop suggest approved
    (
        22,
        222,
        statuses.Statuses.stopped,
        datetime.datetime(2020, 8, 14, 9, 49, 22, 373412),
        datetime.datetime(2020, 8, 14, 10, 0),
    ),
    (
        23,
        223,
        statuses.Statuses.waiting_to_start,
        datetime.datetime(2020, 8, 14, 10, 49, 22, 373412),
        None,
    ),
    # case when WAITING_TO_START with WAITING_TO_STOP exists
    # and approved stop suggest
    (
        24,
        224,
        statuses.Statuses.waiting_to_stop,
        datetime.datetime(2020, 8, 13, 12, 49, 22, 373412),
        datetime.datetime(2020, 8, 14, 11, 49, 22, 373412),
    ),
    (
        25,
        225,
        statuses.Statuses.stopped,
        datetime.datetime(2020, 8, 14, 10, 49, 22, 373412),
        datetime.datetime(2020, 8, 14, 10, 0),
    ),
    (
        26,
        226,
        statuses.Statuses.waiting_to_start,
        datetime.datetime(2020, 8, 14, 11, 49, 22, 373412),
        None,
    ),
    # case when only WAITING_TO_START suggest exists
    # and new suggest approved
    (
        27,
        227,
        statuses.Statuses.stopped,
        datetime.datetime(2020, 8, 14, 9, 49, 22, 373412),
        datetime.datetime(2020, 8, 14, 10, 0),
    ),
    (
        28,
        228,
        statuses.Statuses.waiting_to_start,
        datetime.datetime(2020, 8, 14, 12, 49, 22, 373412),
        datetime.datetime(2020, 8, 18, 12, 49, 22, 373412),
    ),
    # case when WAITING_TO_START with WAITING_TO_STOP exists
    # and new suggest approved
    (
        29,
        229,
        statuses.Statuses.waiting_to_stop,
        datetime.datetime(2020, 8, 13, 12, 49, 22, 373412),
        datetime.datetime(2020, 8, 14, 12, 49, 22, 373412),
    ),
    (
        30,
        230,
        statuses.Statuses.stopped,
        datetime.datetime(2020, 8, 14, 10, 49, 22, 373412),
        datetime.datetime(2020, 8, 14, 10, 0),
    ),
    (
        31,
        231,
        statuses.Statuses.waiting_to_start,
        datetime.datetime(2020, 8, 14, 12, 49, 22, 373412),
        datetime.datetime(2020, 8, 18, 12, 49, 22, 373412),
    ),
]


@pytest.mark.now('2020-08-14 10:00:00')
@pytest.mark.pgsql(
    'discounts_operation_calculations', files=['fill_pg_suggests.sql'],
)
@pytest.mark.config(
    DISCOUNTS_OPERATION_CALCULATIONS_CRON_CONTROL={
        'discounts_operation_calculations': {
            'update_suggests_statuses': {'run_permission': True},
        },
    },
    DISCOUNTS_OPERATION_CALCULATIONS_PUSHES_CONFIG={
        'push_discounts_close_lag': 1440,
    },
)
async def test_update_statuses(pgsql, mock_taxi_approvals):
    @mock_taxi_approvals('/multidrafts/')
    async def handler(request):  # pylint: disable=W0612
        multidraft_id = int(request.query['id'])
        if multidraft_id == 123:
            response = {'id': multidraft_id, 'status': 'succeeded'}
        elif multidraft_id == 42:
            response = {'id': multidraft_id, 'status': 'rejected'}
        elif multidraft_id == 214:
            response = {'id': multidraft_id, 'status': 'partially_completed'}
        elif multidraft_id == 215:
            response = {'id': multidraft_id, 'status': 'succeeded'}
        elif multidraft_id == 216:
            response = {'id': multidraft_id, 'status': 'succeeded'}
        elif multidraft_id == 223:
            response = {'id': multidraft_id, 'status': 'succeeded'}
        elif multidraft_id == 226:
            response = {'id': multidraft_id, 'status': 'succeeded'}
        elif multidraft_id == 228:
            response = {'id': multidraft_id, 'status': 'succeeded'}
        elif multidraft_id == 231:
            response = {'id': multidraft_id, 'status': 'succeeded'}

        return web.json_response(response)

    await run_cron.main(
        [
            'discounts_operation_calculations.crontasks.update_suggests_statuses',  # noqa: E501
            '-t',
            '0',
        ],
    )

    cursor = pgsql['discounts_operation_calculations'].cursor()
    cursor.execute(
        'SELECT id, draft_id, status, date_from, date_to '
        'FROM discounts_operation_calculations.suggests ORDER BY id',
    )
    assert list(cursor) == EXPECTED_STATUSES

    cursor.close()
