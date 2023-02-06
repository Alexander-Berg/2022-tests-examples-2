# pylint: disable=unused-variable
import pytest

from crm_admin import settings
from crm_admin import storage
from crm_admin.utils.state import state


@pytest.mark.config(
    CRM_ADMIN_STATE_SUMMON={
        'StateSummonConfigs': [
            {
                'state': 'READY',
                'users': ['user1', 'user2'],
                'message': (
                    '{% for user in users %}@{{ user }}, {% endfor %}\n'
                    '{{ state }}\n'
                    '{{ summon_context.campaign.name}}\n'
                    '{{ campaign_url }}\n'
                ),
                'channels': ['common'],
                'rule': {
                    'and': [
                        {'==': [{'var': 'campaign.entity_type'}, 'User']},
                        {'!': [{'var': 'campaign.is_regular'}]},
                    ],
                },
            },
            {
                'state': 'READY',
                'users': ['user1', 'user2'],
                'message': 'bad message',
                'channels': ['common'],
                'rule': {
                    'and': [
                        {'==': [{'var': 'campaign.entity_type'}, 'Driver']},
                        {'!': [{'var': 'campaign.is_regular'}]},
                    ],
                },
            },
            {
                'state': 'NEW',
                'users': ['user1', 'user2'],
                'message': 'bad message',
                'channels': ['common'],
                'rule': {
                    'and': [
                        {'==': [{'var': 'campaign.entity_type'}, 'User']},
                        {'!': [{'var': 'campaign.is_regular'}]},
                    ],
                },
            },
        ],
    },
)
@pytest.mark.pgsql('crm_admin', files=['init_campaign.sql'])
async def test_state_summon(web_context, patch):
    expected_names = ['common']
    expected_message = (
        '@user1, @user2, \n'
        'READY\n'
        'Первая кампания\n'
        'https://campaign-management-unstable.taxi.'
        'tst.yandex-team.ru/campaigns/1/\n'
    )

    @patch('crm_admin.utils.telegram_util.TelegramSender.send')
    async def send(names, message):
        assert names == expected_names
        assert message == expected_message

    db_campaign = storage.DbCampaign(web_context)
    campaign = await db_campaign.fetch(1)

    await state.transit(
        web_context, campaign, [], settings.SEGMENT_EXPECTED_STATE,
    )
