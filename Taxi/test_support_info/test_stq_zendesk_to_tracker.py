import pytest

from support_info import stq_task


@pytest.mark.config(
    STARTRACK_ZENDESK_COPY={
        '__default__': {'queue': 'SUPPORT', 'enable': True},
        'park': {'queue': 'VODOPARK', 'enable': True},
        'not_important': {'queue': 'VODOPARK', 'enable': False},
    },
)
@pytest.mark.parametrize(
    'ticket_type,result_queue,is_create',
    [
        ('park', 'VODOPARK', True),
        ('some_ticket', 'SUPPORT', True),
        ('not_important', 'SUPPORT', False),
    ],
)
async def test_zendesk_to_tracker(
        support_info_app_stq, patch, ticket_type, is_create, result_queue,
):
    @patch('taxi.clients.startrack.StartrackAPIClient.create_ticket_from_data')
    async def _dummy_create(data, unique=None):
        return {'key': 'AWESOME-123'}

    zen_ticket = {
        'ticket': {
            'requester': {
                'email': '79057472715@taxi.yandex.ru',
                'name': 'user',
            },
            'subject': 'ticket subject',
            'comment': {'body': 'ticket body'},
            'tags': ['my', 'awesome', 'tag'],
            'form_id': 10,
            'group_id': 100500,
            'custom_fields': [
                {'id': 27946649, 'value': 'vip'},
                {'id': 32670029, 'value': '+79057472715'},
                {'id': 100, 'value': '1000value'},
                {'id': 9999, 'value': '999value'},
            ],
        },
    }
    await stq_task.zendesk_to_startrack(
        support_info_app_stq, zen_ticket, ticket_type,
    )

    calls = _dummy_create.calls
    if is_create:
        assert calls[0] == {
            'data': {
                'summary': 'ticket subject',
                'description': 'ticket body',
                'queue': {'key': result_queue},
                'tags': ['my', 'awesome', 'tag'],
                'requesterName': 'user',
                'emailFrom': '79057472715@taxi.yandex.ru',
                'userPhone': '+79057472715',
                'userType': 'vip',
                'zenFormId': 10,
                'zenGroupId': 100500,
                'zenTicketType': ticket_type,
            },
            'unique': None,
        }
    else:
        assert calls == []
