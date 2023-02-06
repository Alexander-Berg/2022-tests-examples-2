import pytest

from tests_grocery_invoices import consts


@pytest.fixture(name='personal', autouse=True)
def mock_personal(mockserver):
    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def _mock_retrieve(request):
        phone_id = request.json['id']

        return {'id': phone_id, 'value': consts.USER_PHONE}

    @mockserver.json_handler('/personal/v1/tins/retrieve')
    def _mock_tins_retrieve(request):
        tin = request.json['id']

        return {'id': tin, 'value': consts.COURIER_TIN}
