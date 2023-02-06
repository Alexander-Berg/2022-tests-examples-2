import collections
import json
import xmlrpclib

from django import test as django_test
import pytest

from taxi import config
from taxi.conf import settings
from taxi.core import async
from taxi.external import billing
from taxi.internal import dbh
from taxi.internal.city_kit import country_manager
from taxiadmin.api.views import partners


@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_register_partner_park(patch):
    class BBPatched(object):
        def userinfo(*args, **kwargs):
            return {'uid': 1001}

    @patch('blackbox.Blackbox')
    def bb_patched(*args, **kwargs):
        return BBPatched()

    @patch('taxi.external.billing.create_partner')
    def create_partner_patched(*args, **kwargs):
        return 26

    @patch('taxi.external.billing.link_passport_login')
    def link_passport_login_patched(*args, **kwargs):
        return 1, 'result'

    @patch('taxi.external.billing.create_client_person')
    def create_client_person_patched(*args, **kwargs):
        return 2

    @patch('taxi.external.billing._call_balance')
    def create_offer_patched(*args, **kwargs):
        return {'ID': 10, 'EXTERNAL_ID': 20}

    @patch('taxi.external.billing.get_client_contracts')
    def get_client_contracts_patched(*args, **kwargs):
        return [{
            'CONTRACT_TYPE': 9,
            'COUNTRY': 225,
            'CURRENCY': 'RUR',
            'DT': xmlrpclib.DateTime(123400),
            'EXTERNAL_ID': '123769/18',
            'ID': 10,
            'IS_ACTIVE': 1,
            'IS_CANCELLED': 0,
            'IS_DEACTIVATED': 0,
            'IS_FAXED': 0,
            'IS_SIGNED': 1,
            'IS_SUSPENDED': 0,
            'MANAGER_CODE': 28179,
            'NDS_FOR_RECEIPT': 18,
            'NETTING': 1,
            'NETTING_PCT': '100',
            'PAYMENT_TYPE': 2,
            'PERSON_ID': 2,
            'SERVICES': [128, 124, 111]
        }]

    @patch('taxi.external.billing.get_client_persons')
    def get_client_persons_patched(*args, **kwargs):
        return [{
            'ACCOUNT': '40702810510000089782',
            'AUTHORITY_DOC_TYPE': u'\u0423\u0441\u0442\u0430\u0432',
            'BIK': '044525974',
            'CITY': u'\u0433 \u041c\u043e\u0441\u043a\u0432\u0430',
            'CLIENT_ID': '26',
            'DT': '2018-03-05 16:42:06',
            'EMAIL': 'thaumaturge@yandex.ru',
            'FIAS_GUID': '0c5b2444-70a0-4932-980c-b4dc0d3f02b5',
            'ID': '2',
            'INN': '7724411632',
            'INVOICE_COUNT': '1',
            'KPP': '772401001',
            'LEGALADDRESS': u'119019, address',
            'LIVE_SIGNATURE': '1',
            'LONGNAME': u'Name',
            'NAME': u'longname',
            'OGRN': '1177746542611',
            'PHONE': '+79651310099',
            'POSTCODE': '119019',
            'POSTSUFFIX': '15',
            'REPRESENTATIVE': u'reper',
            'SIGNER_PERSON_GENDER': 'W',
            'SIGNER_PERSON_NAME': u'Ntcn',
            'SIGNER_POSITION_NAME': u'Ntect',
            'STREET': u'sssp',
            'TYPE': 'ur'
        }]

    @patch('taxi.external.billing.get_partner_balances')
    def get_partner_balances_patched(*args, **kwargs):
        return [{
            'Balance': '0',
            'BonusLeft': '0',
            'ClientID': 26,
            'ContractID': 10,
            'CurrMonthBonus': '0',
            'CurrMonthCharge': 0,
            'Currency': 'RUB',
            'DT': '2018-05-11T10:06:06.471812',
            'NettingLastDt': None,
            'PersonalAccountExternalID': u'\u041b\u0421\u0422-755060826-1',
            'SubscriptionBalance': 0,
            'SubscriptionRate': '0'
        }]

    @patch('taxi.external.billing.accept_taxi_offer')
    def accept_taxi_offer_patched(*args, **kwargs):
        return {'EXTERNAL_ID': 56}

    @patch('taxi.internal.park_manager.get_balance_for_general_contract')
    def get_bill_for_payment_patched(*args, **kwargs):
        return collections.namedtuple('Test', ['personal_account_external_id'])(
            '1234'
        )

    @patch('taxi.external.billing.create_service_product')
    def create_service_product_patched(*args, **kwargs):
        pass

    @patch('taxi.external.amocrm.auth')
    def auth_patched(*args, **kwargs):
        return {}, {}

    @patch('taxi.external.amocrm.get_leads')
    def get_leads_patched(*args, **kwargs):
        return {
            '_embedded': {
                'items': [{
                    'custom_fields': [
                        {
                            'name': 'UID',
                            'values': [{
                                'value': '00000000000000000000000000000000'
                            }],
                            'id': 3
                        },
                        {
                            'values': [{'enum': '1009978', 'value': '3'}],
                            'id': 445810
                        },
                        {
                            'values': [{'enum': '1009978', 'value': '3'}],
                            'id': 453820
                        },
                        {
                            'values': [{'enum': '1009978', 'value': '3'}],
                            'id': 453822
                        },
                        {
                            'values': [{'enum': '1009978', 'value': '3'}],
                            'id': 453824
                        },
                        {
                            'values': [{'enum': '1009978', 'value': '3'}],
                            'id': 453826
                        },
                        {
                            'values': [{'enum': '1009978', 'value': '3'}],
                            'id': 453834
                        },
                        {
                            'values': [{'enum': '1009978', 'value': '3'}],
                            'id': 453830
                        },
                        {
                            'values': [{'enum': '1009978', 'value': '3'}],
                            'id': 454650
                        },
                        {
                            'values': [{'enum': '1009978', 'value': '3'}],
                            'id': 453832
                        },
                        {
                            'values': [{'enum': '1009978', 'value': '3'}],
                            'id': 453842
                        },
                        {
                            'values': [{'enum': '1009978', 'value': '3'}],
                            'id': 453828
                        }
                    ],
                    'company': {'id': 8808},
                    'pipeline': {'id': 807402},
                    'id': 12345,
                    'main_contact': {'id': 1}
                }]
            }
        }

    @patch('taxi.external.amocrm.get_contact_by_id')
    def get_contact_by_id_patched(*args, **kwargs):
        return {
            '_embedded': {
                'items': [{
                    'custom_fields': [
                        {
                            'name': 'UID',
                            'values': [{
                                'value': '00000000000000000000000000000000'
                            }],
                            'id': 3
                        },
                        {
                            'values': [{'enum': '1009978', 'value': 3}],
                            'id': 445810
                        },
                        {
                            'values': [{'enum': '1009978', 'value': 3}],
                            'id': 219657
                        }
                    ],
                    'name': 'A B C'
                }]
            }
        }

    @patch('taxi.external.amocrm.add_note_to_element')
    def update_add_note_to_element_patched(*args, **kwargs):
        return {}

    @patch('taxi.external.amocrm.update_entity_data')
    def update_entity_data_patched(*args, **kwargs):
        return {}

    @patch('taxi.external.taximeter.create_park')
    def create_park_patched(*args, **kwargs):
        return {'park_id': '1234b'}

    @patch('taxi.external.taximeter.create_driver')
    def create_driver_patched(*args, **kwargs):
        return {'DriverId': '12344566'}

    @patch('taxi.internal.email_sender.send')
    def send_patched(*args, **kwargs):
        pass

    client = django_test.Client()
    data = {'rewrite': False}
    response = client.post(
        '/api/partner/{}/registration/'.format('0' * 32),
        data=json.dumps(data), content_type='application/json'
    )
    assert response.status_code == 200, response.content
    response_data = json.loads(response.content)
    park = yield dbh.parks.Doc.find_one_by_id(response_data['clid'])
    assert park.is_individual_entrepreneur is True


@pytest.mark.parametrize(
    'manager_uid_setting,partner_id,call_balance_params_expected_part',
    [
        (
            None, '0' * 32,
            {'offer_confirmation_type': billing.OFFER_CONFIRM_TYPE_NO}
        ),
        (
            12, '0' * 31 + '1',
            {
                'manager_uid': 12,
                'offer_confirmation_type':
                    billing.OFFER_CONFIRM_TYPE_MIN_PAYMENT,
                'offer_activation_due_term':
                    config.PARK_DAYS_FOR_OFFER_CONFIRM.get(),
                'offer_activation_payment_amount':
                    config.PARK_MONEY_FOR_OFFER_CONFIRM.get()
            }
        ),
        (
            None, '0' * 31 + '1',
            {
                'manager_uid': 0,
                'offer_confirmation_type':
                    billing.OFFER_CONFIRM_TYPE_MIN_PAYMENT,
                'offer_activation_due_term':
                    config.PARK_DAYS_FOR_OFFER_CONFIRM.get(),
                'offer_activation_payment_amount':
                    config.PARK_MONEY_FOR_OFFER_CONFIRM.get()
            }
        ),
    ]
)
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_create_billing_offer_call_balance(
        patch, manager_uid_setting, partner_id,
        call_balance_params_expected_part
):
    partner = yield dbh.partners.Doc.find_one_by_id(partner_id)
    country_rus = yield country_manager.get_doc('rus')

    @patch('taxi.external.billing._call_balance')
    @pytest.inline_callbacks
    def _call_balance_patched(*args, **kwargs):
        async.return_value({'ID': 10, 'EXTERNAL_ID': 20})

    settings.PARTNERS_REGISTRATION_MANAGER_UID = manager_uid_setting

    yield partners.create_billing_offer(
        partner, 'login', 0, country_rus, billing.GENERAL_CONTRACT,
        dbh.partners.Doc.contract_id,
        dbh.partners.Doc.external_id,
        rewrite=True
    )
    partner = yield dbh.partners.Doc.find_one_by_id(partner_id)
    assert partner.contract_id == 10
    assert partner.external_id == 20

    calls = _call_balance_patched.calls
    assert len(calls) == 1
    params = calls[0]['args'][1][1]
    for param_name, param_value in (
            call_balance_params_expected_part.iteritems()
    ):
        assert params.get(param_name) == param_value
