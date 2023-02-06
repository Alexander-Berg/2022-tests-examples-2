import pytest


CREATE_CLIENT_RESPONSE_OK = (
    '<methodResponse>\n<params>\n'
    '<param>\n<value><int>0</int></value>\n</param>\n'
    '<param>\n<value><string>SUCCESS</string></value>\n</param>\n'
    '<param>\n<value><int>1359114838</int></value>\n</param>\n'
    '</params>\n</methodResponse>\n'
)
CREATE_OFFER_RESPONSE_OK = (
    '<methodResponse>\n<params>\n'
    '<param>\n<value>'
    '<struct>'
    '<member>'
    '<name>ID</name><value><i4>456</i4></value>'
    '</member>'
    '<member>'
    '<name>EXTERNAL_ID</name><value><string>OLOLO</string></value>'
    '</member>'
    '</struct>'
    '</value>\n</param>\n'
    '</params>\n</methodResponse>\n'
)
GET_PARTNER_BALANCE_RESPONSE_OK = (
    '<?xml version=\'1.0\'?>\n'
    '<methodResponse>\n<params>\n'
    '<param>\n<value><array><data>\n'
    '<value><struct>\n'
    '<member>\n<name>DT</name>\n'
    '<value><string>2022-06-29T02:06:58.692022</string></value>\n</member>\n'
    '<member>\n<name>PersonalAccounts</name>\n'
    '<value><array><data>\n'
    '<value><struct>\n'
    '<member>\n'
    '<name>external_id</name>\n'
    '<value><string>\xd0\x9b\xd0\xa1\xd0\x9b-3839536216-1</string></value>\n'
    '</member>\n'
    '<member>\n'
    '<name>id</name>\n<value><int>150499937</int></value>\n'
    '</member>\n'
    '<member>\n'
    '<name>service_code</name>\n'
    '<value><string>YANDEX_SERVICE</string></value>\n'
    '</member>\n'
    '</struct></value>\n'
    '</data></array></value>\n</member>\n'
    '</struct></value>\n'
    '</data></array></value>\n</param>\n'
    '</params>\n</methodResponse>\n'
)


@pytest.fixture(name='balance_xmlrpc', autouse=True)
def _balance_xmlrpc(mockserver):
    class Context:
        def __init__(self):
            self.responses = {'default': {'code': 200, 'response': ''}}

    context = Context()

    @mockserver.json_handler('/ext-yandex-balance/xmlrpctvm')
    def _handler(request):
        data = str(request.get_data())
        method = data[26 : data.find('</methodName>')]
        response = context.responses[method]
        return mockserver.make_response(
            status=response['code'], json=response['response'],
        )

    return context


async def test_create_client(taxi_cargo_crm, balance_xmlrpc):
    balance_xmlrpc.responses['Balance.CreateClient'] = {
        'response': CREATE_CLIENT_RESPONSE_OK,
        'code': 200,
    }
    response = await taxi_cargo_crm.post(
        '/functions/create-balance-client', json={'operator_uid': 1234},
    )
    assert response.status_code == 200
    assert response.json() == {'result': {'client_id': 1359114838}}


@pytest.mark.parametrize(
    ['balance_response', 'handler_response', 'status_code'],
    (
        pytest.param(
            'fault_balance_contracts.xml',
            {'code': '500', 'message': 'Internal Server Error'},
            500,
            id='fault',
        ),
        pytest.param(
            'empty_balance_contracts.xml',
            {'result': {'contract_id': 456, 'external_id': 'OLOLO'}},
            200,
            id='created',
        ),
        pytest.param(
            'found_balance_contracts.xml',
            {'result': {'contract_id': 17923141, 'external_id': '5648811/22'}},
            200,
            id='found',
        ),
    ),
)
async def test_create_offer(
        taxi_cargo_crm,
        balance_xmlrpc,
        balance_response,
        handler_response,
        status_code,
        load,
):
    balance_xmlrpc.responses['Balance.CreateOffer'] = {
        'response': CREATE_OFFER_RESPONSE_OK,
        'code': 200,
    }
    balance_xmlrpc.responses['Balance.GetClientContracts'] = {
        'response': load(balance_response),
        'code': 200,
    }
    response = await taxi_cargo_crm.post(
        '/functions/create-balance-trucks-offer',
        json={
            'operator_uid': 1234,  # passport_id робота,
            'client_id': 4321,
            'country_id': 225,
            'currency': 'RUB',
            'firm_id': 130,
            'manager_uid': 321321,
            'payment_type': 2,
            'person_id': 1234,
            'personal_account': 1,
            'services': [1189, 1191],
            'signed': 1,
            'start_dt': '2022-03-01T00:00:00+00:00',
        },
    )
    assert response.status_code == status_code
    assert response.json() == handler_response


async def test_get_partner_balance(taxi_cargo_crm, balance_xmlrpc):
    balance_xmlrpc.responses['Balance.GetPartnerBalance'] = {
        'response': GET_PARTNER_BALANCE_RESPONSE_OK,
        'code': 200,
    }
    response = await taxi_cargo_crm.post(
        '/functions/balance-personal-accounts',
        json={'service_id': 1234, 'contract_ids': [321]},
    )
    assert response.status_code == 200
    assert response.json() == {
        'accounts_by_contracts': [
            {
                'personal_accounts': [
                    {
                        'id': 150499937,
                        'external_id': '\xd0\x9b\xd0\xa1\xd0\x9b-3839536216-1',
                        'service_code': 'YANDEX_SERVICE',
                    },
                ],
            },
        ],
    }


@pytest.mark.parametrize(
    ['balance_response', 'handler_response'],
    (
        pytest.param(
            '<methodResponse><fault><value><struct><member><name>faultCode</name><value><int>-1</int></value></member><member><name>faultString</name><value><string>&lt;error&gt;&lt;msg&gt;Email address "editor@localhost" is invalid&lt;/msg&gt;&lt;email&gt;editor@localhost&lt;/email&gt;&lt;wo-rollback&gt;0&lt;/wo-rollback&gt;&lt;method&gt;Balance.CreatePerson&lt;/method&gt;&lt;code&gt;WRONG_EMAIL&lt;/code&gt;&lt;parent-codes&gt;&lt;code&gt;INVALID_PARAM&lt;/code&gt;&lt;code&gt;EXCEPTION&lt;/code&gt;&lt;/parent-codes&gt;&lt;contents&gt;Email address "editor@localhost" is invalid&lt;/contents&gt;&lt;/error&gt;</string></value></member></struct></value></fault></methodResponse>',
            {
                'fail_reason': {
                    'code': 'balance person registration exception',
                    'details': {},
                    'message': '<error><msg>Email address \\"editor@localhost\\" is invalid</msg><email>editor@localhost</email><wo-rollback>0</wo-rollback><method>Balance.CreatePerson</method><code>WRONG_EMAIL</code><parent-codes><code>INVALID_PARAM</code><code>EXCEPTION</code></parent-codes><contents>Email address \\"editor@localhost\\" is invalid</contents></error>',
                },
            },
            id='email',
        ),
        pytest.param(
            '<methodResponse><fault><value><struct><member><name>faultCode</name><value><int>-1</int></value></member><member><name>faultString</name><value><string>&lt;error&gt;&lt;msg&gt;Invalid INN&lt;/msg&gt;&lt;wo-rollback&gt;0&lt;/wo-rollback&gt;&lt;method&gt;Balance.CreatePerson&lt;/method&gt;&lt;code&gt;INVALID_INN&lt;/code&gt;&lt;parent-codes&gt;&lt;code&gt;INVALID_PARAM&lt;/code&gt;&lt;code&gt;EXCEPTION&lt;/code&gt;&lt;/parent-codes&gt;&lt;contents&gt;Invalid INN&lt;/contents&gt;&lt;/error&gt;</string></value></member></struct></value></fault></methodResponse>',
            {
                'fail_reason': {
                    'code': 'balance person registration exception',
                    'details': {},
                    'message': '<error><msg>Invalid INN</msg><wo-rollback>0</wo-rollback><method>Balance.CreatePerson</method><code>INVALID_INN</code><parent-codes><code>INVALID_PARAM</code><code>EXCEPTION</code></parent-codes><contents>Invalid INN</contents></error>',
                },
            },
            id='inn',
        ),
    ),
)
async def test_create_person_fault(
        taxi_cargo_crm, balance_xmlrpc, balance_response, handler_response,
):
    balance_xmlrpc.responses['Balance.CreatePerson'] = {
        'response': balance_response,
        'code': 200,
    }
    response = await taxi_cargo_crm.post(
        '/functions/create-balance-person',
        json={
            'operator_uid': 321,
            'client_id': 1234,
            'type': 'ur',
            'is-partner': '0',
            'inn': '7851428075',
            'kpp': '767726208',
            'ogrn': '379956466494603',
            'name': 'Краткое название организации',
            'phone': '+7 812 3990776',
            'longname': 'Полное название организации',
            'email': 'm-SC@qCWF.rKU',
            'fax': '+7 812 5696286',
            'country_id': 225,
            'representative': 'Контактное лицо',
            'legaladdress': 'Avenue 5',
            'postsuffix': 'а/я 123',
            'postcode': '111000',
            'bik': '044525440',
            'account': '40702810926912490095',
        },
    )
    assert response.status_code == 200
    assert response.json() == handler_response
