import datetime
import logging

import pytest


logger = logging.getLogger(__name__)

MOCK_ID = 'client_request1'

DRAFT_FILEDS_TO_POP = [
    '_id',
    'created',
    'updated',
    'test_extra_field',
    'draft_status',
    'contract_type',
    'services',
    'without_vat_contract',
]

DEFAULT_DADATA_FIELDS = {
    'hid': 'abc',
    'inn': '123',
    'kpp': '1234',
    'ogrn': '123',
    'ogrn_date': 1469998800000,
    'name': {
        'full': 'рогаИкопыта',
        'short': 'рогаИкопыта',
        'full_with_opf': (
            'ОБЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ ' 'рогаИкопыта'
        ),
        'short_with_opf': 'ООО рогаИкопыта',
    },
    'okved': '123',
    'okved_type': '2014',
    'address': {
        'value': 'г Калуга, ул Вишневского, д 17, кв 55',
        'unrestricted_value': (
            '248007, Калужская обл, ' 'г Калуга, ул Вишневского, д 17, кв 55'
        ),
        'data': {
            'source': '',
            'qc': '0',
            'city_with_type': 'г Калуга',
            'street_with_type': 'ул Вишневского',
            'house': '17',
            'postal_code': '248007',
        },
    },
    'state': {
        'actuality_date': 1469998800000,
        'registration_date': 1469998800000,
        'status': 'ACTIVE',
    },
}


@pytest.mark.config(
    CORP_CLIENT_REQUESTS_AUTO_ACCEPT=True,
    TVM_RULES=[
        {'dst': 'personal', 'src': 'corp-requests'},
        {'dst': 'stq-agent', 'src': 'corp-requests'},
    ],
)
@pytest.mark.parametrize(
    ['params', 'expected_contract_type'],
    [
        pytest.param({'client_id': 'triad'}, 'multi', id='Full pack'),
        pytest.param(
            {'client_id': 'small_client_id'}, 'taxi', id='Minimal pack',
        ),
        pytest.param(
            {'client_id': 'multi_client_id'},
            'multi',
            id='Minimal pack for multi contract',
        ),
        pytest.param(
            {'client_id': 'without_vat_client_id'},
            'without_vat',
            id='without_vat',
        ),
        pytest.param(
            {'client_id': 'multi_client_id'},
            'multi',
            id='Minimal pack for multi contract',
        ),
        pytest.param(
            {'client_id': 'multi_client_id_2'},
            'multi_without_tanker',
            id='Minimal pack for multi contract 2',
        ),
        pytest.param({'client_id': 'triad'}, 'multi', id='Full pack'),
        pytest.param(
            {'client_id': 'small_client_id'}, 'taxi', id='Minimal pack',
        ),
        pytest.param(
            {'client_id': 'full_isr_draft'}, 'taxi', id='Test isr commit',
        ),
        pytest.param(
            {'client_id': 'full_blr_draft'}, 'taxi', id='Test blr commit',
        ),
        pytest.param(
            {'client_id': 'full_kaz_draft'}, 'taxi', id='Test kaz commit',
        ),
        pytest.param(
            {'client_id': 'full_kgz_draft'}, 'taxi', id='Test kgz commit',
        ),
    ],
)
@pytest.mark.config(
    CORP_WITHOUT_VAT_TARIFF_PLANS={
        'rus': {'is_active': True, 'tariff_plan_series_id': 'some_id'},
    },
)
async def test_client_requests_create(
        mockserver,
        web_app_client,
        mock_personal,
        db,
        stq,
        params,
        expected_contract_type,
):
    response = await web_app_client.post(
        f'/v1/client-request-draft/commit', params=params,
    )
    response_json = await response.json()

    draft = await db.corp_client_request_drafts.find_one(
        {'client_id': params['client_id']},
    )

    assert response.status == 200, response_json
    request = await db.corp_client_requests.find_one(
        {'client_id': params['client_id']},
    )
    assert isinstance(request.get('created'), datetime.datetime)
    assert isinstance(request.get('updated'), datetime.datetime)
    assert request['updated'] >= request['created']
    assert request['status'] == 'pending'
    assert request['is_active'] is True
    assert request['contract_type'] == expected_contract_type

    assert stq.corp_notices_process_event.times_called == 1

    call = stq.corp_notices_process_event.next_call()
    assert call['kwargs']['event_name'] == 'ClientRequestCreated'
    assert call['kwargs']['data']['client_id'] == params['client_id']

    if expected_contract_type != 'without_vat':
        assert stq.corp_accept_client_request.times_called == 1
    for field in DRAFT_FILEDS_TO_POP:
        draft.pop(field, None)

    request_draft_fields = {k: v for k, v in request.items() if k in draft}
    assert request_draft_fields == draft


@pytest.mark.parametrize(
    ['client_id', 'status_code', 'field_errors', 'expected_code'],
    [
        pytest.param(
            'schema_errors_client_id',
            400,
            [
                {
                    'field': '_schema',
                    'messages': [
                        'KPP is mandatory for not entrepreneurs',
                        'proxy scan is mandatory for not owners',
                    ],
                },
            ],
            'draft-validation-failed',
            id='Schema_errors',
        ),
        pytest.param(
            'empty_doc_client_id',
            400,
            [
                {
                    'field': 'city',
                    'messages': ['Shorter than minimum length 1.'],
                },
                {
                    'field': 'company_name',
                    'messages': ['Missing data for required field.'],
                },
                {
                    'field': 'contact_emails',
                    'messages': ['Missing data for required field.'],
                },
                {
                    'field': 'contact_name',
                    'messages': ['Missing data for required field.'],
                },
                {
                    'field': 'contact_phone',
                    'messages': ['Missing data for required field.'],
                },
                {
                    'field': 'contract_by_proxy',
                    'messages': ['Missing data for required field.'],
                },
                {
                    'field': 'enterprise_name_full',
                    'messages': ['Shorter than minimum length 1.'],
                },
                {
                    'field': 'enterprise_name_short',
                    'messages': ['Shorter than minimum length 1.'],
                },
                {
                    'field': 'legal_address',
                    'messages': [
                        'Address should comprise four parts separated by '
                        'semicolons',
                    ],
                },
                {
                    'field': 'legal_form',
                    'messages': ['Shorter than minimum length 1.'],
                },
                {
                    'field': 'mailing_address',
                    'messages': [
                        'Address should comprise four parts separated by '
                        'semicolons',
                    ],
                },
                {
                    'field': 'offer_agreement',
                    'messages': ['Missing data for required field.'],
                },
                {
                    'field': 'yandex_login',
                    'messages': ['Missing data for required field.'],
                },
                {
                    'field': 'processing_agreement',
                    'messages': ['Missing data for required field.'],
                },
                {
                    'field': 'signer_name',
                    'messages': ['Shorter than minimum length 1.'],
                },
                {
                    'field': 'signer_position',
                    'messages': ['Shorter than minimum length 1.'],
                },
                {
                    'field': 'signer_gender',
                    'messages': ['Missing data for required field.'],
                },
            ],
            'draft-validation-failed',
            id='Empty doc, missing required values',
        ),
        pytest.param(
            'incomplete_isr_draft',
            400,
            [
                {
                    'field': 'mailing_address_info.city',
                    'messages': ['Missing data for required field.'],
                },
                {
                    'field': 'mailing_address_info.post_index',
                    'messages': ['Missing data for required field.'],
                },
                {
                    'field': 'mailing_address_info.street',
                    'messages': ['Missing data for required field.'],
                },
                {
                    'field': 'mailing_address_info.house',
                    'messages': ['Missing data for required field.'],
                },
                {
                    'field': 'processing_agreement',
                    'messages': ['Missing data for required field.'],
                },
                {
                    'field': 'offer_agreement',
                    'messages': ['Missing data for required field.'],
                },
                {
                    'field': 'enterprise_name_short',
                    'messages': ['Shorter than minimum length 1.'],
                },
                {
                    'field': 'enterprise_name_full',
                    'messages': ['Shorter than minimum length 1.'],
                },
                {
                    'field': 'legal_form',
                    'messages': ['Shorter than minimum length 1.'],
                },
                {
                    'field': 'signer_name',
                    'messages': ['Shorter than minimum length 1.'],
                },
                {
                    'field': 'signer_position',
                    'messages': ['Shorter than minimum length 1.'],
                },
                {
                    'field': 'company_tin',
                    'messages': ['String does not match expected pattern.'],
                },
            ],
            'draft-validation-failed',
            id='Isr test',
        ),
    ],
)
@pytest.mark.config(TVM_RULES=[{'dst': 'personal', 'src': 'corp-requests'}])
async def test_client_requests_validatation(
        taxi_corp_requests_web,
        mock_personal,
        client_id,
        status_code,
        field_errors,
        expected_code,
):

    response = await taxi_corp_requests_web.post(
        f'/v1/client-request-draft/commit', params={'client_id': client_id},
    )
    assert response.status == status_code
    response_json = await response.json()

    assert response_json['code'] == expected_code
    if field_errors is not None:
        assert {
            f['field']: f['messages']
            for f in response_json['details']['fields']
        } == {f['field']: f['messages'] for f in field_errors}


@pytest.mark.parametrize(
    ('client_id', 'without_vat_contract', 'suggestions_data', 'is_activated'),
    [
        # если клиент ИП выбирает НДС - автоакцепт
        pytest.param(
            'client_no_vat_ip',
            False,
            {'finance': None, 'type': 'INDVIDUAL'},
            True,
        ),
        # если клиент ИП выбирает безНДС - ручная модерация
        pytest.param(
            'client_no_vat_ip',
            True,
            {'finance': None, 'type': 'INDVIDUAL'},
            False,
        ),
        # если клиент ООО выбирает НДС - автоакцепт
        pytest.param(
            'client_no_vat_ooo',
            False,
            {'finance': {'tax_system': 'USN'}, 'type': 'LEGAL'},
            True,
        ),
        # если клиент ООО выбирает безНДС после проверки в дадате - автоакцепт
        pytest.param(
            'client_no_vat_ooo',
            True,
            {'finance': {'tax_system': 'USN'}, 'type': 'LEGAL'},
            True,
        ),
        # если клиент ООО создает драфт на спецстранице - ручная модерация
        pytest.param(
            'client_no_vat_ooo',
            True,
            {'finance': {'tax_system': None}, 'type': 'LEGAL'},
            False,
        ),
    ],
)
@pytest.mark.config(
    CORP_CLIENT_REQUESTS_AUTO_ACCEPT=True,
    TVM_RULES=[
        {'dst': 'personal', 'src': 'corp-requests'},
        {'dst': 'stq-agent', 'src': 'corp-requests'},
    ],
)
async def test_client_requests_auto_accept(
        db,
        stq,
        web_app_client,
        mock_personal,
        mock_dadata_suggestions,
        client_id,
        without_vat_contract,
        suggestions_data,
        is_activated,
):
    mock_dadata_suggestions.data.find_by_id_response = {
        'suggestions': [
            {
                'data': {**suggestions_data, **DEFAULT_DADATA_FIELDS},
                'unrestricted_value': client_id,
                'value': client_id,
            },
        ],
    }

    params = {'client_id': client_id}
    if without_vat_contract:
        await db.corp_client_request_drafts.find_one_and_update(
            {'client_id': client_id},
            {
                '$set': {
                    'without_vat_contract': without_vat_contract,
                    'contract_type': 'without_vat',
                },
            },
        )

    response = await web_app_client.post(
        f'/v1/client-request-draft/commit', params=params,
    )
    assert response.status == 200

    if is_activated:
        assert stq.corp_accept_client_request.has_calls
        stq_call = stq.corp_accept_client_request.next_call()
        assert stq_call['kwargs']['status'] == 'accepted'
    else:
        assert not stq.corp_accept_client_request.has_calls
