import pytest

from tests_billing_subventions_x import dbhelpers as db

MOCK_NOW = '2021-05-15T19:10:00+03:00'


@pytest.mark.config(
    BILLING_SUBVENTIONS_DRAFTS_CLEANING_CONTROL={
        'remove_stale': True,
        'days_to_keep': 10,
    },
)
@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize(
    'start,expected',
    (
        ('2021-05-05T19:09:59+03:00', True),
        ('2021-05-05T19:10:01+03:00', False),
    ),
)
async def test_periodic_clean_drafts_drops_stale_drafts(
        taxi_billing_subventions_x, pgsql, make_draft_with, start, expected,
):
    draft = make_draft_with(start=start)
    await taxi_billing_subventions_x.run_periodic_task('clean-drafts')
    deleted = db.get_draft_spec(pgsql, draft['internal_draft_id']) is None
    assert deleted is expected


@pytest.mark.config(
    BILLING_SUBVENTIONS_DRAFTS_CLEANING_CONTROL={'clean_approved': True},
)
@pytest.mark.now(MOCK_NOW)
async def test_periodic_clean_drafts_cleans_approved_drafts(
        taxi_billing_subventions_x, pgsql, make_draft_with,
):
    draft = make_draft_with(approved_at='2021-05-14T19:10:00+03:00')
    await taxi_billing_subventions_x.run_periodic_task('clean-drafts')
    assert db.select_rule_drafts(pgsql, draft['internal_draft_id']) == []


@pytest.fixture(name='make_draft_with')
def _make_draft(create_drafts, a_draft, a_single_ride):
    def _build(*, start=None, approved_at=None):
        draft = a_draft(
            spec={'rule': {'start': start or MOCK_NOW}},
            rules=[a_single_ride()],
            draft_id='fake_draft_id',
            budget_id='fake_budget_id',
            approved_at=approved_at,
        )
        create_drafts(draft)
        return draft

    return _build
