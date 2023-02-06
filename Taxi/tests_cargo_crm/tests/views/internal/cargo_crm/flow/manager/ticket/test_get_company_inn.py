import pytest


OFFER_INFO_FORMS = {
    'rus': {
        'name': '_',
        'longname': '_',
        'postcode': '123456',
        'postaddress': '_',
        'legaladdress': '_',
        'kind': 'rus',
        'country': 'rus',
        'inn': '879571636629',
        'bik': '044525225',
        'account': '40703810938000010045',
    },
    'isr': {
        'name': '_',
        'longname': '_',
        'postcode': '1234567',
        'postaddress': '_',
        'legaladdress': '_',
        'kind': 'isr',
        'country': 'isr',
        'inn': '879576369',
        'bik': '044525225',
        'account': '40703810938000010045',
        'il-id': '5512345',
    },
}


@pytest.fixture(name='call_internal_ticket_get_company_inn')
def _call_internal_ticket_get_company_inn(taxi_cargo_crm):
    async def wrapper(*, ticket_id, expected_code=200):
        response = await taxi_cargo_crm.get(
            '/internal/cargo-crm/flow/manager/ticket/get-company-inn',
            params={'ticket_id': ticket_id},
        )

        assert response.status_code == expected_code

        return response.json()

    return wrapper


@pytest.mark.parametrize('kind', ['isr', 'rus'])
async def test_get_exists(
        kind, call_internal_ticket_get_company_inn, insert_ticket_data,
):
    offer_info = OFFER_INFO_FORMS[kind]

    ticket = insert_ticket_data(offer_info_form=offer_info)
    response_json = await call_internal_ticket_get_company_inn(
        ticket_id=ticket['ticket_id'],
    )
    assert response_json == {'company_inn': OFFER_INFO_FORMS[kind]['inn']}
