# pylint: disable=redefined-outer-name,unused-variable
import pytest

from test_crm_admin.utils import audience_cfg


@pytest.mark.parametrize('_id', [1, 2, 3, 4])
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
@pytest.mark.config(CRM_ADMIN_SETTINGS=audience_cfg.CRM_ADMIN_SETTINGS)
async def test_retrieve_version_info(web_app_client, load_json, _id):
    response = await web_app_client.get(
        '/v1/campaigns/item', params={'id': _id},
    )
    retrieved_campaign = await response.json()

    assert response.status == 200
    assert 'version_info' in retrieved_campaign

    retrieved_version_info = retrieved_campaign['version_info']

    expected_version_info = load_json('response.json')[str(_id)]

    for key, val in expected_version_info.items():
        if val:
            assert key in retrieved_version_info
            assert val == retrieved_version_info[key]
        else:
            assert key not in retrieved_version_info
