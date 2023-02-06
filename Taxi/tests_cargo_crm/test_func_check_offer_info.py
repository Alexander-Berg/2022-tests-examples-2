import pytest

from tests_cargo_crm import const


MANAGER_REQ_PARAMS = {'ticket_id': const.TICKET_ID, 'flow': 'phoenix'}


@pytest.fixture(name='offer_forms')
def _load_offer_forms(load_json):
    return load_json('offer_forms.json')


@pytest.mark.parametrize(
    ['test_fields', 'forbidden_data_config', 'expected_details'],
    (
        pytest.param(
            {'country': None},
            {'inns': []},
            {'country': 'Country should be filled.'},
            id='no_country',
        ),
        pytest.param(
            {'inn': const.INN_10, 'kpp': '123456789'},
            {'inns': []},
            {},
            id='inn_OK_10_syms',
        ),
        pytest.param({}, {'inns': []}, {}, id='inn_OK_12_syms'),
        pytest.param(
            {'inn': '1234567890', 'kpp': '123456789'},
            {'inns': []},
            {'inn': 'Checksum fail.'},
            id='inn_checksum_fail_10_sym',
        ),
        pytest.param(
            {'inn': '123456789012'},
            {'inns': []},
            {'inn': 'Checksum fail.'},
            id='inn_checksum_fail_12_sym',
        ),
        pytest.param(
            {'inn': const.INN_10, 'kpp': '123456789'},
            {'inns': [const.INN_10]},
            {'inn': 'Value is forbidden.'},
            id='inn_forbidden',
        ),
        pytest.param(
            {'inn': '12345678901', 'kpp': '123456789'},
            {'inns': []},
            {'inn': 'Invalid length: 11.'},
            id='inn_invalid_length',
        ),
        pytest.param(
            {'legaladdress': '123456;Super City, Super Street, 10'},
            {'inns': []},
            {},
            id='address_OK',
        ),
        pytest.param(
            {'legaladdress': '123456, Super City, Super Street, 10'},
            {'inns': []},
            {
                'legaladdress': (
                    'Address should start with postcode followed by \';\'.'
                ),
            },
            id='address_FAIL_1',
        ),
        pytest.param(
            {'postaddress': 'Super City, Super Street, 10'},
            {'inns': []},
            {
                'postaddress': (
                    'Address should start with postcode followed by \';\'.'
                ),
            },
            id='address_FAIL_2',
        ),
        pytest.param(
            {'postaddress': '123456'},
            {'inns': []},
            {
                'postaddress': (
                    'Address should start with postcode followed by \';\'.'
                ),
            },
            id='address_FAIL_3',
        ),
        pytest.param(
            {'inn': const.INN_10},
            {'inns': []},
            {'kpp': 'KPP is mandatory for not entrepreneurs.'},
            id='10_sym_inn_without_kpp',
        ),
        pytest.param(
            {'postcode': None},
            {'inns': []},
            {'missing_fields': 'Field \'postcode\' is missing'},
            id='required_field_missing',
        ),
        pytest.param(
            {'postcode': '1234567'},
            {'inns': []},
            {
                'invalid_format': (
                    'Value of \'postcode\': value (1234567) '
                    'doesn\'t match pattern \'^\\d{6}$\''
                ),
            },
            id='required_field_missing',
        ),
    ),
)
async def test_check_offer_info_rus(
        taxi_cargo_crm,
        taxi_config,
        offer_forms,
        test_fields,
        forbidden_data_config,
        expected_details,
):
    taxi_config.set_values(
        {'CARGO_CRM_FORBIDDEN_REGISTRY_DATA': forbidden_data_config},
    )
    offer_info_draft_form = offer_forms['rus'].copy()
    offer_info_draft_form.update(**test_fields)

    request = {'offer_info_draft_form': offer_info_draft_form}
    response = await taxi_cargo_crm.post(
        '/functions/by-flow/check-offer-info',
        params=MANAGER_REQ_PARAMS,
        json=request,
    )
    assert response.status_code == 200
    if not expected_details:
        assert response.json() == {}
        return
    assert response.json()['fail_reason']['details'] == expected_details


@pytest.mark.parametrize(
    ['test_fields', 'forbidden_data_config', 'expected_details'],
    (
        pytest.param({}, {'inns': []}, {}, id='OK'),
        pytest.param(
            {'country': None},
            {'inns': []},
            {'country': 'Country should be filled.'},
            id='no_country',
        ),
        pytest.param(
            {'inn': '5512345', 'il-id': '5512345'},
            {'inns': []},
            {
                'il_id': (
                    'Registration number is mandatory if VAT starts with 55.'
                ),
            },
            id='invalid_il_id',
        ),
        pytest.param(
            {'postcode': None},
            {'inns': []},
            {'missing_fields': 'Field \'postcode\' is missing'},
            id='required_field_missing',
        ),
    ),
)
async def test_check_offer_info_isr(
        taxi_cargo_crm,
        taxi_config,
        offer_forms,
        test_fields,
        forbidden_data_config,
        expected_details,
):
    taxi_config.set_values(
        {'CARGO_CRM_FORBIDDEN_REGISTRY_DATA': forbidden_data_config},
    )
    offer_info_draft_form = offer_forms['isr'].copy()
    offer_info_draft_form.update(**test_fields)

    request = {'offer_info_draft_form': offer_info_draft_form}
    response = await taxi_cargo_crm.post(
        '/functions/by-flow/check-offer-info',
        params=MANAGER_REQ_PARAMS,
        json=request,
    )
    assert response.status_code == 200
    if not expected_details:
        assert response.json() == {}
        return
    assert response.json()['fail_reason']['details'] == expected_details
