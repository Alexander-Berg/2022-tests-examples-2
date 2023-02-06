import pytest

from testsuite.utils import matching

from tests_cargo_crm.flow_manager import const


@pytest.fixture(name='fxt_mg_ticket_init')
def _fxt_mg_ticket_init(taxi_cargo_crm):
    async def wrapper(json):
        response = await taxi_cargo_crm.post(
            '/internal/cargo-crm/flow/manager/ticket/init', json=json,
        )
        return response

    return wrapper


FORM = {
    'company_info_form': {
        'country': const.COUNTRY_RUS,
        'name': const.COMPANY_NAME,
        'phone': const.PHONE,
        'email': const.EMAIL,
    },
    'offer_info_form': {
        'account': '40703810938000010045',
        'authority-doc-type': '0',
        'bik': '044525225',
        'city': 'Москва',
        'country': const.COUNTRY_RUS,
        'inn': '879571636629',
        'kind': const.COUNTRY_RUS,
        'kpp': '123456789',
        'legaladdress': '362013, Владикавказ, ул П 6-я, 5Б',
        'longname': 'ООО "ЯНДЕКС.ТАКСИ"',
        'name': 'ООО "ЯНДЕКС.ТАКСИ"',
        'postaddress': '362013, Владикавказ, ул П 6-я, 5Б',
        'postcode': '362013',
        'signer-person-gender': 'M',
        'signer-person-name': 'Тестов Тест Тестович',
        'signer-position-name': 'Генеральный директор',
    },
    'manager_info_form': {},
    'contract_traits_form': {'kind': 'offer', 'payment_type': 'prepaid'},
}


@pytest.mark.parametrize('initial_form', [FORM])
async def test_manager_ticket_init(
        fxt_mg_ticket_init, procaas_handler_create_event, initial_form,
):
    response = await fxt_mg_ticket_init(json=initial_form)
    assert response.status_code == 200
    assert response.json() == {'ticket_id': matching.any_string}

    assert procaas_handler_create_event.times_called == 1
