import pytest


@pytest.fixture(name='crm_admin_get_list', autouse=True)
def _crm_admin_get_list(mockserver):
    @mockserver.json_handler('/crm-admin/v1/trigger-campaigns/list')
    def _mock_crm_admin(request):
        resp = []
        return resp
