import pytest

from workforce_management.storage.postgresql import db


URI = 'v1/operators/shift/delete'
GET_URI = 'v2/shifts/values'
REVISION_ID = '2020-08-25T21:00:00.000000 +0000'
REVISION_ID2 = '2020-08-26T22:00:00.000000 +0000'
WRONG_REVISION_ID = '2020-06-25T21:00:00.000000 +0000'
HEADERS = {'X-Yandex-UID': 'uid1', 'X-WFM-Domain': 'taxi'}


@pytest.mark.pgsql(
    'workforce_management',
    files=['simple_operators.sql', 'simple_shifts.sql'],
)
@pytest.mark.parametrize(
    'tst_request, expected_status, revision',
    [
        pytest.param(
            {
                'datetime_from': '2020-07-26 11:59:00.0 +0000',
                'datetime_to': '2020-07-26 17:00:00.0 +0000',
                'yandex_uids': ['uid1'],
                'limit': 10,
            },
            200,
            None,
            id='bulk_delete',
        ),
        pytest.param(
            {
                'datetime_from': '2020-07-26 11:59:00.0 +0000',
                'datetime_to': '2020-07-26 13:00:00.0 +0000',
                'yandex_uids': ['uid1'],
                'limit': 10,
            },
            409,
            WRONG_REVISION_ID,
            id='wrong_revision',
        ),
    ],
)
async def test_base(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_status,
        revision,
        mock_effrat_employees,
):
    mock_effrat_employees()
    res = await taxi_workforce_management_web.post(
        GET_URI, json=tst_request, headers=HEADERS,
    )
    data = await res.json()

    modify_shifts = [
        {
            'shift_id': operator_and_shift['shift']['shift_id'],
            'revision_id': (
                revision or operator_and_shift['operator']['revision_id']
            ),
        }
        for operator_and_shift in data['records']
    ]

    res = await taxi_workforce_management_web.post(
        URI, json={'shifts': modify_shifts}, headers=HEADERS,
    )
    assert res.status == expected_status
    success = True
    if expected_status > 200:
        success = False

    tst_request.update(
        {
            'datetime_from': '2000-01-01T00:00:00Z',
            'datetime_to': '2100-01-01T00:00:00Z',
        },
    )
    res = await taxi_workforce_management_web.post(
        GET_URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == 200
    data = await res.json()
    for requested_shift in modify_shifts:
        found = False
        for operator_and_shift in data['records']:
            shift = operator_and_shift['shift']
            operator = operator_and_shift['operator']
            if shift['shift_id'] == requested_shift['shift_id']:
                assert operator['revision_id'] == REVISION_ID
                found = True
                break
            if found:
                break
        if success:
            assert not found
        else:
            assert found

    operators_db = db.OperatorsRepo(web_context)
    master_pool = await operators_db.master

    async with master_pool.acquire() as conn:
        res = await operators_db.get_deleted_operators_shifts(
            conn, ids=[record['shift_id'] for record in modify_shifts],
        )
        assert res and success or not (res or success)


@pytest.mark.now('2020-07-25T11:30:40')
@pytest.mark.pgsql(
    'workforce_management',
    files=['simple_operators.sql', 'simple_shifts.sql', 'allowed_periods.sql'],
)
@pytest.mark.parametrize(
    'tst_request, expected_notify',
    [
        ({'shifts': [{'shift_id': 5, 'revision_id': REVISION_ID2}]}, None),
        (
            {'shifts': [{'shift_id': 1, 'revision_id': REVISION_ID}]},
            {'messages': {'uid1': [{'message_key': 'new_shifts'}]}},
        ),
    ],
)
async def test_trigger_telegram_delete_shift(
        taxi_workforce_management_web,
        mock_effrat_employees,
        stq,
        tst_request,
        expected_notify,
):
    mock_effrat_employees()
    res = await taxi_workforce_management_web.post(
        URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == 200
    if not expected_notify:
        assert not stq.workforce_management_bot_sending.times_called
    else:
        assert (
            stq.workforce_management_bot_sending.next_call()['kwargs']
            == expected_notify
        )
