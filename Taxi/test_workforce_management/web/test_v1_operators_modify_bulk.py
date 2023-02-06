import pytest

from workforce_management.storage.postgresql import db


URI = 'v1/operators/modify/bulk'
TST_UID_1 = 'uid1'
TST_UID_2 = 'uid123'
REVISION_ID = '2020-08-25T21:00:00.000000 +0000'
WRONG_REVISION_ID = '2020-06-25T21:00:00.000000 +0000'


@pytest.mark.pgsql('workforce_management', files=['simple_operators.sql'])
@pytest.mark.parametrize(
    'tst_request, expected_status',
    [
        (
            {
                'operators': [
                    {
                        'yandex_uid': TST_UID_2,
                        'rate': 0.5,
                        'tags': ['i_am_tag'],
                    },
                    {
                        'yandex_uid': TST_UID_1,
                        'rate': 0.1,
                        'revision_id': REVISION_ID,
                    },
                ],
            },
            200,
        ),
        (
            {
                'operators': [
                    {'yandex_uid': '123123', 'rate': 0.5},
                    {
                        'yandex_uid': TST_UID_1,
                        'revision_id': WRONG_REVISION_ID,
                    },
                ],
            },
            409,
        ),
        (
            {
                'operators': [
                    {
                        'yandex_uid': TST_UID_1,
                        'revision_id': REVISION_ID,
                        'rate': 0.5,
                    },
                ],
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
    asked_uids = {
        operator['yandex_uid']: operator
        for operator in tst_request['operators']
    }

    async with master_pool.acquire() as conn:
        res = await operators_db.get_operator_data(
            conn, list(asked_uids.keys()),
        )
        for uid in asked_uids:
            operator_not_found_on_fail = uid not in res and not success
            if operator_not_found_on_fail:
                continue

            for key, value in res[uid].items():
                if key in asked_uids[uid] and key != 'yandex_uid':
                    if success:
                        assert value == asked_uids[uid][key]
                    else:
                        assert value != asked_uids[uid][key]
