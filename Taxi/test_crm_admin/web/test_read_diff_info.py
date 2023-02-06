import pytest

CRM_ADMIN_GROUPS_V2 = {'all_on': True}


@pytest.mark.config(CRM_ADMIN_GROUPS_V2=CRM_ADMIN_GROUPS_V2)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_read_diff_info(web_app_client, load_json):
    response = await web_app_client.get(
        '/v1/campaigns/diff_info', params={'id': 1},
    )

    expected = load_json('diff_info.json')

    assert (await response.json()) == expected
