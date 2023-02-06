import pytest


@pytest.mark.parametrize(
    'rule_id, response_json',
    [
        ('cf730f12-c02b-11ea-acc8-ab6ac87f7711', 'response.json'),
        ('679e3407-b52d-49a4-bc46-075887755ff3', 'response_no_draft.json'),
    ],
)
async def test_v2_rules_changelog_returns_changes_history(
        taxi_billing_subventions_x, load_json, rule_id, response_json,
):
    response = await taxi_billing_subventions_x.get(
        '/v2/rules/changelog', params={'rule_id': rule_id},
    )
    assert response.status_code == 200, response.json()
    assert response.json() == load_json(response_json)


@pytest.fixture(autouse=True)
def _fill_db(create_drafts, a_draft, a_single_ride, pgsql):
    create_drafts(
        a_draft(
            spec={'rule': {'end': '2020-12-31T21:00:00+00:00'}},
            rules=[
                a_single_ride(
                    id='cf730f12-c02b-11ea-acc8-ab6ac87f7711',
                    end='2020-12-31T21:00:00+00:00',
                ),
                a_single_ride(
                    id='679e3407-b52d-49a4-bc46-075887755ff3',
                    end='2020-12-31T21:00:00+00:00',
                ),
            ],
            draft_id='12345',
            budget_id='fake_budget_id',
            approved_at='2020-12-31T21:00:00+00:00',
        ),
    )
    create_drafts(
        a_draft(
            spec={'close_at': '2020-12-21T21:00:00+00:00'},
            rules_to_close=['cf730f12-c02b-11ea-acc8-ab6ac87f7711'],
            draft_id='54321',
            budget_id='fake_budget_id',
            approved_at='2020-12-31T21:00:00+00:00',
        ),
        a_draft(
            spec={'close_at': '2020-12-25T21:00:00+00:00'},
            rules_to_close=['679e3407-b52d-49a4-bc46-075887755ff3'],
            draft_id='nonexistent',
            budget_id='fake_budget_id',
            approved_at='2020-12-31T21:00:00+00:00',
        ),
    )
    cursor = pgsql['billing_subventions'].cursor()
    cursor.execute(
        'DELETE FROM subventions.draft_spec WHERE draft_id = \'nonexistent\'',
    )
