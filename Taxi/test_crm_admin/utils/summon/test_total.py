import pytest

from crm_admin.utils import json_logic
from crm_admin.utils.summon import config
from crm_admin.utils.summon import context

CONDITIONS = {
    'and': [
        {'==': [{'var': 'campaign.entity_type'}, 'Driver']},
        {'!': {'var': 'campaign.efficiency'}},
        {'>=': [{'var': 'segment.aggregate_info.size'}, 1000]},
        {
            '>=': [
                {
                    'reduce': [
                        {'var': 'groups'},
                        {
                            '+': [
                                {
                                    'if': [
                                        {
                                            'in': [
                                                'sms',
                                                {
                                                    'var': 'current.creative.params.channel_name',  # noqa: E501 pylint: disable=line-too-long
                                                },
                                            ],
                                        },
                                        {'var': 'current.params.limit'},
                                        0,
                                    ],
                                },
                                {'var': 'accumulator'},
                            ],
                        },
                        0,
                    ],
                },
                7507,
            ],
        },
    ],
}

CRM_ADMIN_SUMMON_RULES = {
    'SummonConfigs': [
        {
            'approval_object': 'object1',
            'conditions': CONDITIONS,
            'messages': {
                'value': [
                    'Campaign: {{ campaign_context.campaign.entity_type }}. '
                    'Segment: {{ campaign_context.segment.segment_id }}. '
                    'Groups number: {{ campaign_context.groups|length }}. '
                    'Logins: {{ logins|join(", ") }}.',
                ],
                'mode': 'exact_list',
            },
            'approvers': [
                {
                    'approvers': ['approver_1', 'approver_2'],
                    'mode': 'exact_list',
                },
            ],
        },
    ],
}


@pytest.mark.config(
    CRM_ADMIN_SUMMON_RULES=CRM_ADMIN_SUMMON_RULES,
    CRM_ADMIN_SUMMON_PROPERTIES={},
    CRM_ADMIN_GROUPS_V2={'all_on': True},
)
@pytest.mark.parametrize(
    'campaign_id, expected_result',
    [
        (
            1,
            [
                (
                    True,
                    [
                        'Campaign: Driver. Segment: 10. Groups number: 3. '
                        'Logins: approver_1, approver_2.',
                    ],
                ),
            ],
        ),
    ],
)
@pytest.mark.pgsql(
    'crm_admin', files=['init_campaigns.sql', 'init_groups.sql'],
)
async def test_context_config_integration(
        web_context, campaign_id: int, expected_result: list,
):
    summon_configs = config.collect_summon_configs(web_context)
    summon_context = await context.SummonContextFactory.create_context(
        context=web_context, campaign_id=campaign_id,
    )
    serialized_context = await summon_context.serialize()

    existed_result = []
    for summon_config in summon_configs:
        condition_result = json_logic.json_logic(
            tests=summon_config.conditions, data=serialized_context,
        )
        message = summon_config.create_messages(serialized_context)
        existed_result.append((condition_result, message))

    assert existed_result == expected_result
