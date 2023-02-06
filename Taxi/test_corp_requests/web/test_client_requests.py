# pylint: disable=redefined-outer-name

import pytest

from taxi.util import cleaners
from taxi.util import dates


@pytest.fixture
def mock_mds(mockserver):
    @mockserver.json_handler(
        r'/mds/get-taxi/598/725bb76df6fb42b191a1db00dd9b275e',
    )
    def _redirect(request):
        return mockserver.make_response(
            '598/725bb76df6fb42b191a1db00dd9b275e', status=200,
        )


@pytest.mark.parametrize(
    ['request_id', 'expected_result', 'status_code'],
    [
        pytest.param(
            'f4d44610f5894352817595f6311d95cc',
            {
                'id': 'f4d44610f5894352817595f6311d95cc',
                'client_id': '477a5ef7ffbc43f8af7945837fec466a1',
                'autofilled_fields': [],
                'is_active': False,
                'status': 'accepted',
                'created': '2018-04-19T15:20:19.160000+03:00',
                'reason': 'тест',
                'references': {'gclid': '123456', 'yakassa': '1'},
                'readonly_fields': [
                    'company_tin',
                    'country',
                    'offer_agreement',
                    'processing_agreement',
                    'proxy_scan',
                ],
                'contact_name': 'тест235',
                'contract_type': 'taxi',
                'enterprise_name': 'ОАО "ВСПМК-3"',
                'contact_phone': '+79263301676',
                'company_ogrn': '1021500673050',
                'contract_by_proxy': True,
                'company_name': '123',
                'country': 'rus',
                'promo_id': 'promo_id1',
                'signer_name': 'example',
                'enterprise_name_short': 'ОАО "ВСПМК-3"',
                'bank_name': 'ПУБЛИЧНОЕ АКЦИОНЕРНОЕ ОБЩЕСТВО РОСБАНК',
                'legal_address': 'Владикавказ;362013;ул П 6-я;5Б',
                'legal_address_info': {
                    'city': 'Владикавказ',
                    'post_index': '362013',
                    'street': 'ул П 6-я',
                    'house': '5Б',
                },
                'bank_bic': '044525256',
                'contact_emails': ['osiei@yandex-team.ru'],
                'offer_agreement': True,
                'signer_position': 'Генеральный директор',
                'legal_form': 'ОАО',
                'company_cio': '151601001',
                'signer_gender': 'male',
                'mailing_address': 'Владикавказ;362013;ул П 6-я;5Б',
                'mailing_address_info': {
                    'city': 'Владикавказ',
                    'post_index': '362013',
                    'street': 'ул П 6-я',
                    'house': '5Б',
                },
                'company_tin': '1503009019',
                'processing_agreement': True,
                'proxy_scan': '598/725bb76df6fb42b191a1db00dd9b275e',
                'yandex_login': 'osiei13',
                'bank_account_number': '40802810087340000053',
                'enterprise_name_full': 'example',
                'city': 'Москва',
                'company_registration_date': '2017-12-30T06:00:00+03:00',
                'updated': '2018-04-19T19:24:16.309000+03:00',
                'last_error': None,
            },
            200,
        ),
        pytest.param(
            '95b3c932435f4f008a635faccb6454f6',
            {
                'id': '95b3c932435f4f008a635faccb6454f6',
                'client_id': 'isr_client_id',
                'autofilled_fields': [],
                'references': {},
                'readonly_fields': [
                    'company_tin',
                    'country',
                    'offer_agreement',
                    'processing_agreement',
                ],
                'city': 'Тель Авив',
                'legal_form': 'isr-legal-form',
                'company_name': 'Isr company_name',
                'contract_type': 'taxi',
                'contact_emails': ['engineer@yandex-team.ru'],
                'contact_name': 'Василий',
                'contact_phone': '+79263452242',
                'country': 'isr',
                'enterprise_name_short': 'example_short',
                'enterprise_name_full': 'example',
                'legal_address_info': {
                    'city': 'Tel Aviv',
                    'house': '1',
                    'post_index': '12345',
                    'street': 'street1',
                },
                'mailing_address_info': {
                    'city': 'Tel Aviv',
                    'house': '1',
                    'post_index': '12345',
                    'street': 'street2',
                },
                'offer_agreement': True,
                'processing_agreement': True,
                'status': 'pending',
                'company_tin': '1503009017',
                'yandex_login': 'semeynik',
                'signer_name': 'signer_name_isr',
                'signer_position': 'signer_position_isr',
                'signer_gender': 'female',
                'created': '2019-11-12T11:49:33.368000+03:00',
                'updated': '2019-11-12T11:49:33.368000+03:00',
                'is_active': True,
                'last_error': None,
            },
            200,
            id='israel offer company',
        ),
        pytest.param(
            'rejected',
            {
                'id': 'rejected',
                'client_id': '477a5ef7ffbc43f8af7945837fec466a1',
                'autofilled_fields': [],
                'is_active': False,
                'status': 'rejected',
                'created': '2018-04-19T15:20:19.160000+03:00',
                'updated': '2018-04-20T15:20:19+03:00',
                'reason': 'тест',
                'formal_reason': 'crapy offer',
                'references': {'gclid': '123456', 'yakassa': '1'},
                'readonly_fields': [
                    'company_tin',
                    'country',
                    'offer_agreement',
                    'processing_agreement',
                    'proxy_scan',
                ],
                'contact_name': 'тест235',
                'enterprise_name': 'ОАО "ВСПМК-3"',
                'contact_phone': '+79263301676',
                'company_ogrn': '1021500673050',
                'contract_by_proxy': True,
                'company_name': '123',
                'country': 'rus',
                'contract_type': 'taxi',
                'promo_id': 'promo_id1',
                'signer_name': 'example',
                'enterprise_name_short': 'ОАО "ВСПМК-3"',
                'bank_name': 'ПУБЛИЧНОЕ АКЦИОНЕРНОЕ ОБЩЕСТВО РОСБАНК',
                'legal_address': 'Владикавказ;362013;ул П 6-я;5Б',
                'legal_address_info': {
                    'city': 'Владикавказ',
                    'post_index': '362013',
                    'street': 'ул П 6-я',
                    'house': '5Б',
                },
                'bank_bic': '044525256',
                'contact_emails': ['osiei@yandex-team.ru'],
                'offer_agreement': True,
                'signer_position': 'Генеральный директор',
                'legal_form': 'ОАО',
                'company_cio': '151601001',
                'signer_gender': 'male',
                'mailing_address': 'Владикавказ;362013;ул П 6-я;5Б',
                'mailing_address_info': {
                    'city': 'Владикавказ',
                    'post_index': '362013',
                    'street': 'ул П 6-я',
                    'house': '5Б',
                },
                'company_tin': '1503009666',
                'processing_agreement': True,
                'proxy_scan': '598/725bb76df6fb42b191a1db00dd9b275e',
                'yandex_login': 'osiei13',
                'bank_account_number': '40802810087340000053',
                'enterprise_name_full': 'example',
                'city': 'Москва',
                'company_registration_date': '2017-12-30T06:00:00+03:00',
                'last_error': {
                    'datetime': '2019-01-14T15:25:58.034000+03:00',
                    'error': 'Неизвестная ошибка',
                    'error_reason': 'some reason',
                },
            },
            200,
            id='rejected',
        ),
        pytest.param(
            'non_exist_id',
            {
                'message': 'client request not found',
                'code': 'request-not-found',
                'details': {},
            },
            404,
        ),
    ],
)
@pytest.mark.config(TVM_RULES=[{'dst': 'personal', 'src': 'corp-requests'}])
async def test_client_requests_get_one(
        mock_personal,
        mock_mds,
        taxi_corp_requests_web,
        request_id,
        expected_result,
        status_code,
):

    response = await taxi_corp_requests_web.get(
        '/v1/client-requests', params={'request_id': request_id},
    )
    response_json = await response.json()

    assert response.status == status_code
    assert response_json == expected_result


@pytest.mark.parametrize(
    ['request_id', 'request_params'],
    [
        pytest.param(
            'f4d44610f5894352817595f6311d95cc',
            {
                'autofilled_fields': [],
                'contact_name': 'тест235',
                'enterprise_name': 'ОАО "ВСПМК-3"',
                'contact_phone': '+79263301676',
                'company_ogrn': '1021500673050',
                'contract_by_proxy': False,
                'company_name': '123',
                'country': 'rus',
                'signer_name': 'example',
                'enterprise_name_short': 'ОАО "ВСПМК-3"',
                'bank_name': 'ПУБЛИЧНОЕ АКЦИОНЕРНОЕ ОБЩЕСТВО РОСБАНК',
                'legal_address': 'Владикавказ;362013;ул П 6-я;5Б',
                'bank_bic': '044525256',
                'contact_emails': ['osiei@yandex-team.ru'],
                'offer_agreement': True,
                'signer_position': 'Генеральный директор',
                'legal_form': 'ОАО',
                'company_cio': '151601001',
                'signer_gender': 'male',
                'mailing_address': 'Владикавказ;362013;ул П 6-я;5Б',
                'company_tin': '500100732259',
                'processing_agreement': True,
                'bank_account_number': '40802810087340000053',
                'enterprise_name_full': 'example',
                'city': 'Москва',
                'company_registration_date': '2017-12-30T03:00:00+00:00',
            },
        ),
        pytest.param(
            '95b3c932435f4f008a635faccb6454f6',
            {
                'city': 'Тель Авив',
                'contact_emails': ['engineer@yandex-team.ru'],
                'company_name': 'example',
                'enterprise_name_short': 'example2_short',
                'enterprise_name_full': 'example2',
                'offer_agreement': True,
                'processing_agreement': True,
                'contact_name': 'Василий',
                'contact_phone': '+79263452242',
                'country': 'isr',
                'legal_address_info': {
                    'city': 'Tel Aviv',
                    'house': '1',
                    'post_index': '12345',
                    'street': 'street1234',
                },
                'mailing_address_info': {
                    'city': 'Tel Aviv',
                    'house': '1',
                    'post_index': '12345',
                    'street': 'street2',
                },
                'legal_form': 'isr-legal-form',
                'registration_number': '502901001',
                'company_tin': '502901001',
                'signer_name': 'signer_name_isr_2',
                'signer_position': 'signer_position_isr_2',
                'signer_gender': 'female',
            },
            id='Israel company',
        ),
        pytest.param(
            '95b3c932435f4f008a635faccb6454f7',
            {
                'city': 'Бишкек',
                'contact_emails': ['eblackbu@yandex-team.ru'],
                'company_name': 'Бишкек',
                'enterprise_name_short': 'Бишкек_short',
                'enterprise_name_full': 'Бишкек',
                'offer_agreement': True,
                'processing_agreement': True,
                'contact_name': 'Василий',
                'contact_phone': '+79263452242',
                'country': 'kgz',
                'legal_address_info': {
                    'city': 'Бишкек',
                    'house': '1',
                    'post_index': '12345',
                    'street': 'street1234',
                },
                'mailing_address_info': {
                    'city': 'Бишкек',
                    'house': '1',
                    'post_index': '12345',
                    'street': 'street2',
                },
                'legal_form': 'kgz-legal-form',
                'registration_number': '502901001',
                'company_tin': '50290100112312',
                'signer_name': 'signer_name_kgz',
                'signer_position': 'signer_position_kgz',
                'signer_gender': 'female',
            },
            id='KGZ company',
        ),
        pytest.param(
            'f4d44610f5894352817595f6311d95cc',
            {
                'autofilled_fields': ['contact_phone', 'company_ogrn'],
                'contact_name': 'тест235',
                'country': 'rus',
                'enterprise_name': 'ОАО "ВСПМК-3"',
                'contact_phone': '+79263301676',
                'company_ogrn': '1021500673050',
                'contract_by_proxy': False,
                'company_name': '123',
                'signer_name': 'example',
                'enterprise_name_short': 'ОАО "ВСПМК-3"',
                'bank_name': 'ПУБЛИЧНОЕ АКЦИОНЕРНОЕ ОБЩЕСТВО РОСБАНК',
                'legal_address': 'Владикавказ;362013;ул П 6-я;5Б',
                'bank_bic': '044525256',
                'contact_emails': ['oSiEi@yandex-team.ru'],
                'offer_agreement': True,
                'signer_position': 'Генеральный директор',
                'legal_form': 'ОАО',
                'company_cio': '151601001',
                'signer_gender': 'male',
                'mailing_address': 'Владикавказ;362013;ул П 6-я;5Б',
                'company_tin': '500100732259',
                'processing_agreement': True,
                'bank_account_number': '40802810087340000053',
                'enterprise_name_full': 'example',
                'city': 'Москва',
                'company_registration_date': '2017-12-30T03:00:00+00:00',
            },
            id='try to set readonly field (ignored)',
        ),
        pytest.param(
            'f4d44610f5894352817595f6311d95cc',
            {
                'autofilled_fields': [],
                'contact_name': 'тест235',
                'enterprise_name': 'ОАО "ВСПМК-3"',
                'contact_phone': '+79263301676',
                'company_ogrn': '1021500673050',
                'contract_by_proxy': False,
                'company_name': '123',
                'country': 'rus',
                'signer_name': 'example',
                'enterprise_name_short': 'ОАО "ВСПМК-3"',
                'bank_name': 'ПУБЛИЧНОЕ АКЦИОНЕРНОЕ ОБЩЕСТВО РОСБАНК',
                'legal_address_info': {
                    'city': 'Владикавказ',
                    'post_index': '362013',
                    'street': 'ул П 6-я',
                    'house': '5Б',
                },
                'bank_bic': '044525256',
                'contact_emails': ['osiei@yandex-team.ru'],
                'offer_agreement': True,
                'signer_position': 'Генеральный директор',
                'legal_form': 'ОАО',
                'company_cio': '151601001',
                'signer_gender': 'male',
                'mailing_address_info': {
                    'city': 'Владикавказ',
                    'post_index': '362013',
                    'street': 'ул П 6-я',
                    'house': '5Б',
                },
                'company_tin': '500100732259',
                'processing_agreement': True,
                'bank_account_number': '40802810087340000053',
                'enterprise_name_full': 'example',
                'city': 'Москва',
                'company_registration_date': None,
            },
            id='remove company_registration_date',
        ),
    ],
)
@pytest.mark.config(TVM_RULES=[{'dst': 'personal', 'src': 'corp-requests'}])
async def test_client_request_update(
        mock_personal,
        mock_mds,
        taxi_corp_requests_web,
        db,
        request_id,
        request_params,
):

    response = await taxi_corp_requests_web.get(
        '/v1/client-requests', params={'request_id': request_id},
    )
    assert response.status == 200, await response.json()
    data = await response.json()
    readonly_fields = data['readonly_fields']

    original_item = await db.corp_client_requests.find_one({'_id': request_id})
    response = await taxi_corp_requests_web.put(
        '/v1/client-requests',
        params={'request_id': request_id},
        json=request_params,
    )

    assert response.status == 200, await response.json()

    db_item = await db.corp_client_requests.find_one({'_id': request_id}) or {}
    if db_item['country'] == 'rus':
        for address_type in ['legal_address', 'mailing_address']:
            if (
                    address_type in db_item
                    or f'{address_type}_info' in request_params
            ):
                city, post_index, street, house = db_item[address_type].split(
                    ';',
                )
                address_info = db_item[f'{address_type}_info']
                assert (city, post_index, street, house) == (
                    address_info['city'],
                    address_info['post_index'],
                    address_info['street'],
                    address_info['house'],
                )

    if 'contact_emails' in request_params:
        request_params['contact_emails'] = cleaners.normalize_emails(
            request_params['contact_emails'],
        )
    if request_params.get('company_registration_date'):
        registration_date = dates.parse_timestring(
            request_params['company_registration_date'],
        )
        request_params['company_registration_date'] = registration_date

    for field, value in request_params.items():
        if field not in readonly_fields:
            if value is None:
                assert field not in db_item
            else:
                assert db_item[field] == value, (field, value)

    if original_item and db_item:

        for field in readonly_fields:
            assert db_item.get(field) == original_item.get(field)
