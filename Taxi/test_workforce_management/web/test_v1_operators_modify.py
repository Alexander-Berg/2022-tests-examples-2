import pytest

from workforce_management.storage.postgresql import db

URI = 'v1/operators/modify'
TST_UID = 'uid1'
TST_UID_2 = 'uid123'
REVISION_ID = '2020-08-25T21:00:00.000000 +0000'
UID5_REVISION_ID = '2020-08-25T21:00:00.000000 +0000'
WRONG_REVISION_ID = '2020-06-25T21:00:00.000000 +0000'


@pytest.mark.now('2020-07-27T00:00:00')
@pytest.mark.pgsql('workforce_management', files=['simple_operators.sql'])
@pytest.mark.parametrize(
    'tst_request, expected_status',
    [
        ({'yandex_uid': TST_UID, 'skills': ['hokage']}, 409),
        (
            {
                'yandex_uid': TST_UID,
                'skills': ['hokage'],
                'revision_id': WRONG_REVISION_ID,
            },
            409,
        ),
        (
            {
                'yandex_uid': TST_UID,
                'skills': ['hokage', 'tatarin'],
                'revision_id': REVISION_ID,
                'tags': ['naruto'],
            },
            200,
        ),
        ({'yandex_uid': TST_UID, 'rate': 0.6}, 409),
        (
            {'yandex_uid': TST_UID, 'revision_id': REVISION_ID, 'rate': 0.5},
            200,
        ),
        ({'yandex_uid': TST_UID_2, 'rate': 0.5}, 200),
        (
            {
                'yandex_uid': 'uid5',
                'revision_id': UID5_REVISION_ID,
                'rate': 0.5,
            },
            200,
        ),
    ],
)
async def test_base(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_status,
):
    res = await taxi_workforce_management_web.post(URI, json=tst_request)
    assert res.status == expected_status
    success = True
    if expected_status > 200:
        success = False

    operators_db = db.OperatorsRepo(web_context)
    master_pool = await operators_db.master
    yandex_uid = tst_request['yandex_uid']

    async with master_pool.acquire() as conn:
        res = await operators_db.get_operator_data(conn, [yandex_uid])
        operator_not_found_on_fail = yandex_uid not in res and not success
        if operator_not_found_on_fail:
            return
        for key, value in res[yandex_uid].items():
            if key in tst_request and key != 'yandex_uid':
                if success:
                    assert value == tst_request[key]
                else:
                    assert value != tst_request[key]
