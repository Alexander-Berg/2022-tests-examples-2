import pytest

from crm_admin.utils.summon import context


@pytest.mark.config(CRM_ADMIN_GROUPS_V2={'all_on': True})
@pytest.mark.parametrize('campaign_id', [1])
@pytest.mark.pgsql(
    'crm_admin', files=['init_campaigns.sql', 'init_groups.sql'],
)
async def test_context_serialization(web_context, load_json, campaign_id):
    summon_context = await context.SummonContextFactory.create_context(
        context=web_context, campaign_id=campaign_id,
    )

    data = await summon_context.serialize()
    expected = load_json('expected.json')

    assert data == expected
