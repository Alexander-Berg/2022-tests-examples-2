import datetime

import pytest

from workforce_management.common import utils
from workforce_management.storage.postgresql import db


URI = 'v1/operators/plan/modify'
REVISION_ID = '2020-08-26T12:00:00.000000 +0000'
WRONG_REVISION_ID = '2020-09-26T12:00:00.000000 +0000'
DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%f %z'
START = datetime.datetime(year=1970, month=1, day=1)
END = datetime.datetime(year=2100, month=1, day=1)
HEADERS = {'X-Yandex-UID': 'uid1', 'X-WFM-Domain': 'taxi'}


@pytest.mark.pgsql('workforce_management', files=['simple_plan.sql'])
@pytest.mark.parametrize(
    'tst_request, expected_status',
    [
        (
            {
                'plan_id': 1,
                'revision_id': REVISION_ID,
                'records': [{'start': '2020-09-09 20:00:00.0Z', 'value': 10}],
            },
            200,
        ),
        (
            {
                'plan_id': 1,
                'revision_id': REVISION_ID,
                'records': [
                    {'start': '2020-09-09 20:00:00.0Z', 'value': 10},
                    {'start': '2020-09-09 20:29:00.0Z', 'value': 10},
                ],
            },
            400,  # intersection
        ),
        (
            {
                'plan_id': 1,
                'revision_id': REVISION_ID,
                'records': [
                    {'start': '2020-09-09 20:00:00.0Z', 'value': 10},
                    {'start': '2020-09-09 20:00:00.0Z', 'value': 20},
                ],
            },
            400,
        ),
        (
            {
                'plan_id': 1,
                'revision_id': WRONG_REVISION_ID,
                'records': [{'start': '2020-09-09 20:00:00.0Z', 'value': 10}],
            },
            409,
        ),
    ],
)
async def test_base(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_status,
):
    res = await taxi_workforce_management_web.post(
        URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status

    if expected_status > 200:
        return

    operators_db = db.OperatorsRepo(web_context)
    master_pool = await operators_db.master
    plan_id = tst_request['plan_id']

    async with master_pool.acquire() as conn:
        res = await operators_db.get_operators_plan(conn, plan_id, START, END)
        provided_records = sorted(
            tst_request['records'], key=lambda x: x['start'],
        )
        actual_records = sorted(res, key=lambda x: x['start'])
        for record in provided_records:
            found = False
            record['start'] = utils.parse_and_localize(record['start'])
            for actual_record in actual_records:
                if record['start'] == actual_record['start']:
                    assert record['value'] == actual_record['value']
                    found = True
                    break
            assert found


@pytest.mark.pgsql('workforce_management', files=['simple_plan.sql'])
@pytest.mark.parametrize(
    'tst_request, expected_status',
    [
        ({'plan_id': 1, 'revision_id': REVISION_ID}, 200),
        ({'plan_id': 1, 'revision_id': WRONG_REVISION_ID}, 409),
        (
            {'plan_id': 2, 'revision_id': WRONG_REVISION_ID},
            409,  # TODO: provide 404
        ),
    ],
)
async def test_delete(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_status,
):
    res = await taxi_workforce_management_web.delete(
        URI, params=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status
    success = True
    if expected_status > 200:
        success = False

    operators_db = db.OperatorsRepo(web_context)
    master_pool = await operators_db.master
    plan_id = tst_request['plan_id']

    async with master_pool.acquire() as conn:
        res = await operators_db.get_operators_plan_entity(conn, ids=[plan_id])
        assert not res or not success
        #  cascade delete
        res = await operators_db.get_operators_plan(conn, plan_id, START, END)
        assert not res or not success
        res = await operators_db.get_del_operators_plan_entity(
            conn, ids=[plan_id],
        )
        plan_records = await operators_db.get_del_operators_plan_records(
            conn, ids=[plan_id],
        )
        if success:
            assert res
            assert plan_records
        else:
            assert not res
            assert not plan_records


@pytest.mark.pgsql(
    'workforce_management', files=['simple_plan_granularity.sql'],
)
@pytest.mark.parametrize(
    'tst_request, expected_status, expected_plan_records',
    [
        (
            {
                'plan_id': 1,
                'revision_id': REVISION_ID,
                'records': [
                    {'start': '2020-09-09 20:00:00.0Z', 'value': 10.5},
                ],
                'step_minutes': 5,
            },
            200,
            [
                {'start': '2020-08-26T12:00:00.000000 +0000', 'value': 1},
                {'start': '2020-08-26T13:00:00.000000 +0000', 'value': 2},
                {'start': '2020-08-26T14:00:00.000000 +0000', 'value': 3},
                {'start': '2020-09-09T20:00:00.000000 +0000', 'value': 10.5},
            ],
        ),
        (
            {
                'plan_id': 1,
                'revision_id': REVISION_ID,
                'records': [
                    {'start': '2020-08-26T12:00:00.000000 +0000', 'value': 1},
                    {'start': '2020-08-26T13:00:00.000000 +0000', 'value': 2},
                    {'start': '2020-08-26T14:00:00.000000 +0000', 'value': 3},
                    {'start': '2020-08-26T20:00:00.000000 +0000', 'value': 10},
                    {'start': '2020-08-26T21:01:00.000000 +0000', 'value': 15},
                ],
                'step_minutes': 15,
            },
            200,
            [
                {'start': '2020-08-26T12:00:00.000000 +0000', 'value': 1},
                {'start': '2020-08-26T13:00:00.000000 +0000', 'value': 2},
                {'start': '2020-08-26T14:00:00.000000 +0000', 'value': 3},
                {'start': '2020-08-26T20:00:00.000000 +0000', 'value': 10},
                {'start': '2020-08-26T21:01:00.000000 +0000', 'value': 15},
            ],
        ),
        (
            {
                'plan_id': 1,
                'revision_id': REVISION_ID,
                'records': [
                    {'start': '2020-08-26 11:50:00.0Z', 'value': 10},
                    {'start': '2020-08-26 20:29:00.0Z', 'value': 15},
                ],
                'step_minutes': 15,
            },
            400,  # intersection
            [],
        ),
        (
            {
                'plan_id': 1,
                'revision_id': REVISION_ID,
                'records': [
                    {'start': '2020-08-27 11:50:00.0Z', 'value': 1},
                    {'start': '2020-08-27 12:50:00.0Z', 'value': 2},
                ],
                'step_minutes': 60,
            },
            200,
            [
                {'start': '2020-08-26T12:00:00.000000 +0000', 'value': 1},
                {'start': '2020-08-26T13:00:00.000000 +0000', 'value': 2},
                {'start': '2020-08-26T14:00:00.000000 +0000', 'value': 3},
                {'start': '2020-08-27T11:50:00.000000 +0000', 'value': 0.5},
                {'start': '2020-08-27T12:20:00.000000 +0000', 'value': 0.5},
                {'start': '2020-08-27T12:50:00.000000 +0000', 'value': 1},
                {'start': '2020-08-27T13:20:00.000000 +0000', 'value': 1},
            ],
        ),
        (
            {
                'plan_id': 1,
                'revision_id': REVISION_ID,
                'records': [
                    {'start': '2020-08-27 12:00:00.0Z', 'value': 1},
                    {'start': '2020-08-27 12:59:00.0Z', 'value': 2},
                ],
                'step_minutes': 60,
            },
            400,  # intersection
            [],
        ),
        (
            {
                'plan_id': 2,
                'revision_id': REVISION_ID,
                'records': [
                    {'start': '2020-08-26 09:53:00.0Z', 'value': 1},
                    {'start': '2020-08-26 11:00:00.0Z', 'value': 2},
                ],
                'step_minutes': 8,
            },
            200,
            [
                {'start': '2020-08-26T09:53:00.000000 +0000', 'value': 1},
                {'start': '2020-08-26T11:00:00.000000 +0000', 'value': 2},
                {'start': '2020-08-26T15:00:00.000000 +0000', 'value': 300},
            ],
        ),
        (
            {
                'plan_id': 3,
                'revision_id': REVISION_ID,
                'records': [
                    {'start': '2020-08-26 09:50:00.0Z', 'value': 1},
                    {'start': '2020-08-26 10:00:00.0Z', 'value': 2},
                    {'start': '2020-08-26 10:05:00.0Z', 'value': 3},
                    {'start': '2020-08-26 10:10:00.0Z', 'value': 4},
                    {'start': '2020-08-26 10:45:00.0Z', 'value': 5},
                    {'start': '2020-08-26 11:00:00.0Z', 'value': 6},
                    {'start': '2020-08-26 12:10:00.0Z', 'value': 7},
                    {'start': '2020-08-26 12:15:00.0Z', 'value': 8},
                    {'start': '2020-08-26 13:45:00.0Z', 'value': 9},
                    {'start': '2020-08-26 13:55:00.0Z', 'value': 10},
                ],
                'step_minutes': 5,
            },
            200,
            [
                {'start': '2020-08-26T09:50:00.000000 +0000', 'value': 21},
                {'start': '2020-08-26T12:10:00.000000 +0000', 'value': 34},
            ],
        ),
        (
            {
                'plan_id': 1,
                'revision_id': REVISION_ID,
                'records': [
                    {'start': '2020-08-27 11:50:00.0Z', 'value': 1},
                    {'start': '2020-08-27 12:50:00.0Z', 'value': 2},
                ],
                'step_minutes': 60,
                'measure': 'man_count',
            },
            200,
            [
                {'start': '2020-08-26T12:00:00.000000 +0000', 'value': 1},
                {'start': '2020-08-26T13:00:00.000000 +0000', 'value': 2},
                {'start': '2020-08-26T14:00:00.000000 +0000', 'value': 3},
                {'start': '2020-08-27T11:50:00.000000 +0000', 'value': 0.5},
                {'start': '2020-08-27T12:20:00.000000 +0000', 'value': 0.5},
                {'start': '2020-08-27T12:50:00.000000 +0000', 'value': 1},
                {'start': '2020-08-27T13:20:00.000000 +0000', 'value': 1},
            ],
        ),
        (
            {
                'plan_id': 1,
                'revision_id': REVISION_ID,
                'records': [
                    {'start': '2020-08-27 11:50:00.0Z', 'value': 1},
                    {'start': '2020-08-27 12:50:00.0Z', 'value': 2},
                ],
                'step_minutes': 15,
                'measure': 'man_count',
            },
            200,
            [
                {'start': '2020-08-26T12:00:00.000000 +0000', 'value': 1},
                {'start': '2020-08-26T13:00:00.000000 +0000', 'value': 2},
                {'start': '2020-08-26T14:00:00.000000 +0000', 'value': 3},
                {'start': '2020-08-27T11:50:00.000000 +0000', 'value': 0.25},
                {'start': '2020-08-27T12:50:00.000000 +0000', 'value': 0.5},
            ],
        ),
    ],
)
async def test_plan_granuality_changing(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_status,
        expected_plan_records,
):
    res = await taxi_workforce_management_web.post(
        URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status

    if expected_status > 200:
        return

    operators_db = db.OperatorsRepo(web_context)
    master_pool = await operators_db.master
    plan_id = tst_request['plan_id']

    async with master_pool.acquire() as conn:
        res = await operators_db.get_operators_plan(conn, plan_id, START, END)
        res = [
            {
                'start': row['start'].strftime(DATE_FORMAT),
                'value': row['value'],
            }
            for row in res
        ]
        actual_records = sorted(res, key=lambda x: x['start'])
        assert actual_records == expected_plan_records
