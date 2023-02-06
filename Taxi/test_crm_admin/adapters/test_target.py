import pytest

from crm_admin import storage


@pytest.mark.parametrize(
    'campaigns_ids, expected_answer',
    [
        ([1, 2], [(1, 1), (1, 2), (2, 1), (2, 4)]),
        ([1, 3], [(1, 1), (1, 2)]),
        ([], []),
    ],
)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_fetch_by_campaigns_ids(
        web_context, campaigns_ids, expected_answer,
):
    db_target = storage.DbTarget(context=web_context)
    records = await db_target.fetch_by_campaigns_ids(campaigns_ids)

    assert len(records) == len(expected_answer)
    for campaign_id, target in records:
        assert (campaign_id, target.target_id) in expected_answer
