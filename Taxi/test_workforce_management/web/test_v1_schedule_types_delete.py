import pytest

from workforce_management.storage.postgresql import db


URI = 'v1/schedule/types'
DELETE_URI = 'v1/schedule/types/delete'
REVISION_ID = '2020-08-26T09:00:00.000000 +0000'
WRONG_REVISION_ID = '2020-08-26T13:00:00.000000 +0000'
HEADERS = {'X-Yandex-UID': 'uid1'}


@pytest.mark.pgsql('workforce_management', files=['simple_operators.sql'])
@pytest.mark.parametrize(
    'tst_request, expected_status,',
    [
        ({'id': 5}, 400),
        ({'id': 1, 'revision_id': REVISION_ID}, 400),
        ({'id': 5, 'revision_id': WRONG_REVISION_ID}, 409),
        ({'id': 5, 'revision_id': REVISION_ID}, 200),
    ],
)
async def test_delete(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_status,
):
    res = await taxi_workforce_management_web.post(
        DELETE_URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status
    success = True
    if expected_status > 200:
        success = False

    res = await taxi_workforce_management_web.post(
        URI, json={'schedule': [4, 2]},
    )
    assert res.status == 200

    data = await res.json()

    found = any(
        [
            schedule_types['schedule_type_id'] == tst_request['id']
            for schedule_types in data['schedule_types']
        ],
    )

    assert not found or not success

    operators_db = db.OperatorsRepo(web_context)
    master_pool = await operators_db.master
    async with master_pool.acquire() as conn:
        res = await operators_db.get_deleted_schedule_types(
            conn, schedule_type_ids=[tst_request['id']],
        )
        if success:
            assert res
        else:
            assert not res
