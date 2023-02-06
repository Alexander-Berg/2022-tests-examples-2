import pytest


URI = 'v1/operators/plan/info'
FIRST_PLAN_ENTITY = {
    'plan_id': 1,
    'name': 'mega_plan',
    'skill': 'order',
    'step_minutes': 60,
    'revision_id': '2020-08-26T12:00:00.000000 +0000',
}
SECOND_PLAN_ENTITY = {
    'plan_id': 2,
    'name': 'tatarskoe_igo',
    'skill': 'horse_archer',
    'step_minutes': 60 * 24 * 365,
    'revision_id': '2020-08-26T12:00:00.000000 +0000',
}


@pytest.mark.pgsql('workforce_management', files=['simple_plan.sql'])
@pytest.mark.parametrize(
    'tst_request, expected_status, expected_res',
    [
        ({'names': ['mega_plan']}, 200, [FIRST_PLAN_ENTITY]),
        (
            {'names': ['mega_plan', 'tatarskoe_igo']},
            200,
            [FIRST_PLAN_ENTITY, SECOND_PLAN_ENTITY],
        ),
        ({}, 200, [FIRST_PLAN_ENTITY, SECOND_PLAN_ENTITY]),
        ({'skills': ['horse_archer']}, 200, [SECOND_PLAN_ENTITY]),
    ],
)
async def test_base(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_status,
        expected_res,
):
    res = await taxi_workforce_management_web.post(URI, json=tst_request)
    assert res.status == expected_status

    if expected_status > 200:
        return
    data = await res.json()

    assert data['items'] == expected_res
