import pytest


@pytest.fixture(name='order_meta_info_mock')
def _order_meta_info_mock(mock_eats_core_orders, mockserver, load_json):
    @mock_eats_core_orders(
        r'/internal-api/v1/order/(?P<order_nr>\w+)/metainfo$', regex=True,
    )
    async def _order_get(request, order_nr='order_nr'):
        responses = load_json('order_meta_info.json')

        return responses


@pytest.fixture(name='eats_eaters_mock')
def _eats_eaters_data_mock(mock_eats_eaters, mockserver, load_json):
    @mock_eats_eaters('/v1/eaters/find-by-id')
    async def _get_eater_data(request, eater_id='eater_id'):
        resp = load_json('eater_data.json')
        return resp


@pytest.fixture(name='personal_mock')
def _personal_mock(mock_personal, mockserver, load_json):
    @mock_personal('/v1/phones/retrieve')
    async def _get_phone(request, phone_id='personal_phone_id'):
        resp = load_json('phone_data.json')
        return resp


@pytest.fixture(name='eats_core_order_integration_mock')
def _eats_core_order_integration_mock(
        mock_eats_core_order_integration, mockserver, load_json,
):
    @mock_eats_core_order_integration(
        r'/v1/order-additional-info/(?P<order_nr>\w+)$', regex=True,
    )
    async def _get_additional_info(request, order_nr='order_nr'):
        resp = load_json('additional_info.json')
        return resp


@pytest.fixture(name='eats_order_revision_mock')
def _eats_order_revision_mock(mock_eats_order_revision, mockserver, load_json):
    @mock_eats_order_revision('/v1/revision/latest/customer-services/details')
    async def _get_revision(request, order_nr='order_nr'):
        resp = load_json('revision.json')
        return resp
