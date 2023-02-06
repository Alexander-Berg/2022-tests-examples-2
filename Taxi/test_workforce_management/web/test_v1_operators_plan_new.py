import pytest

from workforce_management.storage.postgresql import db


URI = 'v1/operators/plan/new'


@pytest.mark.pgsql('workforce_management', files=['simple_plan.sql'])
@pytest.mark.parametrize(
    'tst_request, expected_status',
    [
        ({'name': 'super_plan', 'step_minutes': 60, 'skill': 'hokage'}, 200),
        ({'name': 'mega_plan', 'step_minutes': 30, 'skill': 'order'}, 400),
        ({'name': 'super_plan', 'step_minutes': -30, 'skill': 'order'}, 400),
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

    if expected_status > 200:
        return

    operators_db = db.OperatorsRepo(web_context)
    master_pool = await operators_db.master
    name = tst_request['name']

    async with master_pool.acquire() as conn:
        res = await operators_db.get_operators_plan_entity(conn, [name])
        assert len(res) == 1
        record = res[0]
        assert tst_request['skill'] == record['skill']
        assert tst_request['step_minutes'] == record['step_minutes']
