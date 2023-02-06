import pytest


@pytest.fixture(name='crm_admin_get_meta_list', autouse=True)
def _crm_admin_get_list(mockserver):
    @mockserver.json_handler('/crm-admin/v1/campaigns/meta/list')
    def _mock_crm_admin(request):
        return {'campaigns': [], 'actual_ts': '2021-12-01T00:00:00Z'}
