import pytest

from tests_cargo_crm.flow_manager import const


@pytest.fixture(name='fxt_update_idx_data')
def _fxt_update_idx_data(taxi_cargo_crm):
    async def wrapper(json, ticket_id=const.TICKET_ID):
        response = await taxi_cargo_crm.post(
            '/internal/cargo-crm/flow/manager/ticket/update-index-data',
            params={'ticket_id': ticket_id},
            json=json,
        )
        return response

    return wrapper


@pytest.mark.parametrize(
    'request_json',
    (
        pytest.param({'is_successful': False}, id='close'),
        pytest.param({'country': const.COUNTRY_RUS}, id='country'),
        pytest.param({'company_name': const.COMPANY_NAME}, id='company_name'),
    ),
)
async def test_manager_ticket_update_idx_data(
        fxt_update_idx_data, request_json,
):
    response = await fxt_update_idx_data(json=request_json)
    assert response.status_code == 200
    assert response.json() == {}
