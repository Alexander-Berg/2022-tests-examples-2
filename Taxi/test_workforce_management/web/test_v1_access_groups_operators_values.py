import pytest

from . import data

URI = '/v1/access-groups/operators/values'
HEADERS = {'X-WFM-Domain': 'taxi'}


@pytest.mark.now('2020-07-27T00:00:00')
@pytest.mark.pgsql(
    'workforce_management', files=['simple_operators.sql', 'simple_roles.sql'],
)
@pytest.mark.parametrize(
    'tst_request, expected_status, expected_res',
    [
        (
            {'limit': 100, 'group': 'group1'},
            200,
            {
                'operators': [
                    data.FIRST_OPERATOR,
                    data.SECOND_OPERATOR,
                    data.THIRD_OPERATOR,
                ],
                'full_count': 3,
            },
        ),
        (
            {'limit': 1, 'group': 'group1'},
            200,
            {'operators': [data.FIRST_OPERATOR], 'full_count': 3},
        ),
        (
            {'limit': 1, 'group': 'group1', 'offset': 1},
            200,
            {'operators': [data.SECOND_OPERATOR], 'full_count': 3},
        ),
        (
            {'limit': 1, 'group': 'group1', 'filters': {'login': 'abd-damir'}},
            200,
            {'operators': [data.FIRST_OPERATOR], 'full_count': 1},
        ),
        (
            {
                'limit': 100,
                'group': 'group1',
                'filters': {'supervisors': ['abd-damir']},
            },
            200,
            {
                'operators': [data.SECOND_OPERATOR, data.THIRD_OPERATOR],
                'full_count': 2,
            },
        ),
    ],
)
async def test_access_groups_base(
        taxi_workforce_management_web,
        tst_request,
        expected_status,
        expected_res,
):
    res = await taxi_workforce_management_web.post(
        URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status
    if expected_status > 200:
        return
    json = await res.json()
    assert json == expected_res
