import uuid

import pytest


@pytest.mark.parametrize(
    'since,till,geonode,expected',
    (
        (  # too early
            '2021-08-31T20:00:00+00:00',
            '2021-08-31T20:59:59.999999+00:00',
            'galaxy/far/far/away',
            [],
        ),
        (  # too late
            '2021-10-01T21:00:00+00:00',
            '2021-10-01T21:00:00.000001+00:00',
            'galaxy/far/far/away',
            [],
        ),
        (  # geonode miss
            '2021-09-01T18:00:00+03:00',
            '2021-09-30T18:00:00+03:00',
            'galaxy/milky/way',
            [],
        ),
        (
            '2021-09-01T18:00:00+03:00',
            '2021-09-30T18:00:00+03:00',
            'galaxy/far/far/away',
            [{'id': '11111', 'source': '//path/to/table'}],
        ),
    ),
)
async def test_v2_rules_personal_goal_drafts_returns_filtered_drafts(
        with_response, since, till, geonode, expected,
):
    response = await with_response(since=since, till=till, geonode=geonode)
    assert response == {'drafts': expected}


@pytest.fixture(name='with_response')
def _make_request(taxi_billing_subventions_x):
    async def _request(*, since, till, geonode):
        query = {
            'time_range': {'start': since, 'end': till},
            'geonode': geonode,
        }
        url = 'v2/rules/personal_goal/drafts'
        response = await taxi_billing_subventions_x.post(url, query)
        assert response.status_code == 200, response.text
        return response.json()

    return _request


@pytest.fixture(autouse=True)
def _fill_db(a_goal, a_draft, create_drafts):
    create_drafts(
        a_draft(
            spec={'path': '//path/to/table'},
            approved_at='2021-08-01T17:00:00Z',
            draft_id='11111',
            budget_id='fake_budget_id',
            rules=[
                a_goal(
                    geonode='galaxy/far/far/away',
                    start='2021-09-01T00:00:00+03:00',
                    end='2021-10-01T00:00:00+03:00',
                    unique_driver_id=str(uuid.uuid4()),
                ),
            ],
        ),
    )
