# pylint: disable=unused-variable,unused-argument

import pytest

from test_crm_admin.utils import audience_cfg


@pytest.mark.config(CRM_ADMIN_SETTINGS=audience_cfg.CRM_ADMIN_SETTINGS)
async def test_get_audience_list(web_app_client):
    response = await web_app_client.get('/v1/dictionaries/audiences')
    assert response.status == 200

    items = await response.json()
    items = {item['id'] for item in items}
    assert items == {'User', 'Driver', 'EatsUser', 'LavkaUser'}
