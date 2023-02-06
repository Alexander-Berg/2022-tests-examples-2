# pylint: disable=unused-variable,unused-argument
import pytest


@pytest.mark.pgsql('crm_admin', files=['init.sql'])
@pytest.mark.parametrize(
    'campaign_id, group_id, expected_code, expected_result',
    [
        (
            1,
            1,
            400,
            {
                'errors': [
                    {
                        'code': 'unable_to_cancel_publication',
                        'details': {
                            'reason': (
                                'group sending either '
                                'not exists or not cancelled'
                            ),
                        },
                    },
                ],
            },
        ),
        (2, 2, 200, None),
    ],
)
async def test_cancel_publication(
        web_context,
        web_app_client,
        patch,
        campaign_id,
        group_id,
        expected_code,
        expected_result,
):
    @patch('generated.clients.crm_hub.CrmHubClient.v1_publication_cancel_post')
    async def post(*args, **kwargs):
        pass

    @patch('crm_admin.storage.group_adapters.check_campaign_new_groups')
    def newgrp(*args, **kwargs):
        return True

    response = await web_app_client.post(
        f'/v1/publications/cancel'
        f'?campaign_id={campaign_id}&group_id={group_id}',
    )
    assert expected_code == response.status
    if expected_result:
        assert expected_result == await response.json()
