import pytest

from crm_admin.utils.summon import config

CRM_ADMIN_SUMMON_RULES = {
    'SummonConfigs': [
        {
            'approval_object': 'approval_object_1',
            'conditions': {'or': [True, False]},
            'messages': {
                'value': 'messages_templates_1',
                'mode': 'named_list',
            },
            'approvers': [
                {'approvers': 'approvers_properties_1', 'mode': 'named_list'},
                {'approvers': 'approvers_properties_2', 'mode': 'named_list'},
            ],
        },
        {
            'approval_object': 'approval_object_2',
            'conditions': {'or': [True, False]},
            'messages': {
                'value': [
                    'template2 {{campaign_context.something}} {{logins}}',
                ],
                'mode': 'exact_list',
            },
            'approvers': [
                {'approvers': ['approver_1'], 'mode': 'exact_list'},
                {
                    'approvers': ['approver_2', 'approver_3'],
                    'mode': 'exact_list',
                },
            ],
        },
    ],
}

CRM_ADMIN_SUMMON_PROPERTIES = {
    'messages_templates_1': [
        'template1 {{campaign_context.something}} {{logins}}',
    ],
    'approvers_properties_1': ['approver_property_1'],
    'approvers_properties_2': ['approver_property_2', 'approver_property_3'],
}

CAMPAIGN_CONTEXT = {'something': 'something'}


@pytest.mark.config(
    CRM_ADMIN_SUMMON_RULES=CRM_ADMIN_SUMMON_RULES,
    CRM_ADMIN_SUMMON_PROPERTIES=CRM_ADMIN_SUMMON_PROPERTIES,
)
async def test_summon_util(web_context):
    summon_configs = config.collect_summon_configs(web_context)

    existed_result = []

    for summon_config in summon_configs:
        existed_result.append(
            {
                'approval_object': summon_config.approval_object,
                'approvers': summon_config.approvers,
                'conditions': summon_config.conditions,
                'messages': summon_config.create_messages(CAMPAIGN_CONTEXT),
            },
        )

    expected_result = [
        {
            'approval_object': 'approval_object_1',
            'approvers': [
                ['approver_property_1'],
                ['approver_property_2', 'approver_property_3'],
            ],
            'conditions': {'or': [True, False]},
            'messages': [
                'template1 something [\'approver_property_1\', '
                '\'approver_property_2\', \'approver_property_3\']',
            ],
        },
        {
            'approval_object': 'approval_object_2',
            'approvers': [['approver_1'], ['approver_2', 'approver_3']],
            'conditions': {'or': [True, False]},
            'messages': [
                'template2 something [\'approver_1\', '
                '\'approver_2\', \'approver_3\']',
            ],
        },
    ]

    assert expected_result == existed_result
