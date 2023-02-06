import datetime
import itertools
import operator as op

import pytest

from taxi.util import itertools_ext

from workforce_management.storage.postgresql import db as db_module


GET_SHIFT_URI = 'v1/operators/shift'
URI = 'v1/operator/shift/modify/apply'
HEADERS = {'X-Yandex-UID': 'uid1', 'X-WFM-Domain': 'taxi'}
REVISION_ID = '2020-08-25T21:00:00.000000 +0000'


ENTITY_RO_COMPARER = {
    'breaks': lambda x, y: len(x or []) == len(y or []) and all(
        [
            break_x[field] == break_y[field]
            for break_x, break_y in itertools.zip_longest(x or [], y or [])
            for field in ('start', 'duration_minutes', 'type')
        ],
    ),
}


@pytest.mark.now('2009-08-02T11:30:40')
@pytest.mark.pgsql(
    'workforce_management',
    files=[
        'simple_operators.sql',
        'simple_shifts.sql',
        'allowed_periods.sql',
        'simple_shifts_drafts.sql',
    ],
)
@pytest.mark.parametrize(
    'tst_request, expected_status, expected_res',
    [
        pytest.param(
            {
                'shift': {
                    'start': '2020-07-26T15:01:00+03:00',
                    'duration_minutes': 32,
                    'shift_id': 1,
                    'operator': {
                        'yandex_uid': 'uid1',
                        'revision_id': REVISION_ID,
                    },
                },
            },
            200,
            dict(
                unique_operator_id=1,
                shift_id=1,
                draft_id='1',
                start=datetime.datetime(
                    2020, 7, 26, 12, 0, tzinfo=datetime.timezone.utc,
                ),
                duration_minutes=30,
                status=1,
            ),
            id='modify',
        ),
        pytest.param(
            {
                'shift': {
                    'start': '2020-07-26T15:01:00+03:00',
                    'duration_minutes': 32,
                    'shift_id': 1,
                    'operator': {
                        'yandex_uid': 'uid1',
                        'revision_id': REVISION_ID,
                    },
                    'breaks': [
                        {
                            'start': '2020-07-26T15:11:00+03:00',
                            'duration_minutes': 15,
                            'type': 'technical',
                        },
                    ],
                },
                'option': 'save_provided',
            },
            200,
            dict(
                unique_operator_id=1,
                shift_id=1,
                draft_id='1',
                start=datetime.datetime(
                    2020, 7, 26, 12, 0, tzinfo=datetime.timezone.utc,
                ),
                duration_minutes=30,
                status=1,
            ),
            id='modify_with_breaks',
        ),
        pytest.param(
            {
                'shift': {
                    'start': '2020-07-26T15:00:00+03:00',
                    'duration_minutes': 32,
                    'shift_id': 10,
                    'operator': {
                        'yandex_uid': 'uid1',
                        'revision_id': REVISION_ID,
                    },
                },
            },
            404,
            None,
            id='non_existing_draft',
        ),
    ],
)
async def test_base(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_status,
        expected_res,
        mock_effrat_employees,
        stq3_context,
):
    mock_effrat_employees()
    res = await taxi_workforce_management_web.post(
        URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status
    success = res.status == 200

    operators_db = db_module.OperatorsRepo(stq3_context)

    async with operators_db.master.acquire() as conn:
        draft = itertools_ext.first(
            await operators_db.get_shifts_drafts(
                conn, draft_ids=[str(tst_request['shift']['shift_id'])],
            ),
        )
    if draft:
        draft = dict(draft)
        draft.pop('updated_at')
        draft.pop('id')
    assert draft == expected_res
    if not success:
        return

    res = await taxi_workforce_management_web.get(
        GET_SHIFT_URI,
        params={'id': tst_request['shift']['shift_id']},
        headers=HEADERS,
    )
    assert res.status == 200
    data = await res.json()

    fields_equal = all(
        (
            ENTITY_RO_COMPARER.get(field, op.eq)(
                data.get(field), tst_request['shift'].get(field),
            )
            for field in ('start', 'duration_minutes', 'breaks')
        ),
    )
    author_changed = (
        data['audit'].get('author_yandex_uid') == HEADERS['X-Yandex-UID']
    )
    assert fields_equal == success and author_changed == success
