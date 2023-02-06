# coding: utf-8

import datetime
import json
import xmlrpclib
from pprint import pprint

import pytest

from taxi.core import async
from taxi.core import db

from taxi_maintenance.stuff import update_parks_balances


@pytest.mark.now('2015-04-06 23:59:00 +03')
@pytest.mark.config(ENABLE_DYNAMIC_PARK_THRESHOLD=True)
@pytest.mark.asyncenv('blocking')
@pytest.mark.filldb()
@pytest.inline_callbacks
def test_update_parks_balances_single_city(mock, load, monkeypatch):

    def patch_contracts_getter(filename_suffix=''):
        @mock
        def get_client_contracts(
                billing_client_id, dt=None, contract_kind=None,
                contract_signed=True, log_extra=None):
            if contract_kind is not None:
                return async.call(lambda: async.succeed([]), lambda: [])
            try:
                response_json = load(
                    'get_client_contracts_%s%s.json' % (
                        billing_client_id, filename_suffix
                    )
                )
            except ValueError:
                response_json = load(
                    'get_client_contracts_%s.json' % billing_client_id
                )
            response = json.loads(response_json)
            for contract in response:
                contract['DT'] = xmlrpclib.DateTime(str(contract['DT']))
            return async.call(
                lambda: async.succeed(response), lambda: response
            )
        monkeypatch.setattr(
            'taxi.external.billing.get_client_contracts', get_client_contracts
        )

        @mock
        def get_parks_balances(contract_ids, log_extra=None):
            if len(contract_ids) == 1:
                filename = 'get_parks_balances_%s.json' % contract_ids[0]
            else:
                filename = 'get_parks_balances%s.json' % filename_suffix
            response_json = load(filename)
            response = json.loads(response_json)
            return async.call(
                lambda: async.succeed(response), lambda: response
            )
        monkeypatch.setattr(
            'taxi.external.billing.get_parks_balances', get_parks_balances
        )

        @mock
        def get_client_persons(billing_client_id, log_extra=None):
            response_json = load(
                'get_client_persons_%s.json' % billing_client_id
            )
            response = json.loads(response_json)
            return async.call(
                lambda: async.succeed(response), lambda: response
            )
        monkeypatch.setattr(
            'taxi.external.billing.get_client_persons', get_client_persons
        )

        @mock
        def warn_on_important_change(*args, **kwargs):
            print '{} {}'.format(args, kwargs)
            return
        monkeypatch.setattr(
            'taxi.internal.park_manager.warn_on_important_change',
            warn_on_important_change
        )

    patch_contracts_getter()

    now = datetime.datetime(2015, 4, 6, 20, 59)
    promised_payment_valid = now + datetime.timedelta(seconds=7200)

    # because round-trip of datetime.datetime.max to mongo and back to python
    # transforms 999999 microseconds to 999000 microseconds
    _MAX_DATE = datetime.datetime.max.replace(microsecond=999000)

    expected_accounts = {
        # this is normal park on prepay without contract cache
        # check that everything is filled correctly
        'park_0': {
            'account': {
                'balances': [{
                    'bonus_left': 0.0,
                    'commissions': 10000.95,
                    'currency': 'RUB',
                    'current_balance': 1000.39,
                    'current_bonus': 0.0,
                    'contract_id': 123400,
                    'netting_last_dt': None,
                    'personal_account_external_id': None,
                }],
                "corporate_contracts": [{
                    "id": 123456,
                    "is_active": True,
                    "external_id": "PAC-13345",
                    "is_prepaid": False,
                    "services": [135]
                }],
                'card_contract_currency': 'RUB',
                'cash_contract_currency': 'RUB',
                'contracts': [{
                    'id': 123400,
                    'is_prepaid': True,
                    'is_active': True,
                    'is_cancelled': False,
                    'is_deactivated': False,
                    'is_faxed': False,
                    'is_signed': True,
                    'is_suspended': False,
                    'is_of_card': True,
                    'is_of_cash': False,
                    'is_of_corp': False,
                    'is_of_uber': False,
                    'external_id': '00000/00',
                    'link_contract_id': None,
                    'person_id': '1000000',
                    'begin': datetime.datetime(2014, 4, 30, 20),
                    'end': _MAX_DATE,
                    'type': 9,
                    'vat': None,
                    'currency': 'RUB',
                    'services': [124, 128],
                    'acquiring_percent': None,
                    'nds_for_receipt': None,
                    'netting': False,
                    'netting_pct': None,
                    'offer_accepted': True,
                    'rebate_percent': None,
                    'ind_bel_nds_percent': None,
                }, {
                    'id': 123423,
                    'is_prepaid': True,
                    'is_active': True,
                    'is_cancelled': False,
                    'is_deactivated': False,
                    'is_faxed': False,
                    'is_signed': True,
                    'is_suspended': False,
                    'is_of_card': False,
                    'is_of_cash': True,
                    'is_of_corp': False,
                    'is_of_uber': False,
                    'external_id': '00000/14',
                    'link_contract_id': None,
                    'person_id': '1000000',
                    'begin': datetime.datetime(2014, 4, 30, 20),
                    'end': _MAX_DATE,
                    'type': 9,
                    'vat': None,
                    'currency': 'RUB',
                    'services': [111],
                    'acquiring_percent': None,
                    'nds_for_receipt': None,
                    'netting': False,
                    'netting_pct': None,
                    'offer_accepted': True,
                    'rebate_percent': None,
                    'ind_bel_nds_percent': None,
                }],
                'details': {
                    'bank_city': '',
                    'bank_name': '',
                    'bik': 'bik_100000',
                    'cor_account': '',
                    'fio': u'Таксистов Иван Петрович',
                    'id': '1000000',
                    'inn': 'inn_100000',
                    'kpp': 'kpp_100000',
                    'legal_address': (
                        u'100000, г. Москва, ул. Таксистов, д. 1, корп. 0'
                    ),
                    'long_name': u'OOO "name_100000"',
                    'ogrn': 'ogrn_100000',
                    'op_account': 'account_100000',
                    'short_name': 'name_100000',
                    'invalid_bankprops': False,
                },
                'recommended_payments': [70999.61],
                'threshold_dynamic': 0,
            },
            'requirements': {'corp': True}
        },
        # initially this park is deactivated,
        # expected that positive balance reactivates it
        'park_1': {
            'account': {
                'balances': [{
                    'bonus_left': 0.0,
                    'commissions': 11000.95,
                    'currency': 'RUB',
                    'current_balance': 1100.39,
                    'current_bonus': 0.0,
                    'contract_id': 123401,
                    'netting_last_dt': None,
                    'personal_account_external_id': None,
                }],
                'cash_contract_currency': 'RUB',
                'contracts': [{
                    'id': 123401,
                    'is_prepaid': True,
                    'is_active': True,
                    'is_cancelled': False,
                    'is_deactivated': False,
                    'is_faxed': False,
                    'is_signed': True,
                    'is_suspended': False,
                    'is_of_card': False,
                    'is_of_cash': True,
                    'is_of_corp': False,
                    'is_of_uber': False,
                    'external_id': '00001/01',
                    'link_contract_id': None,
                    'person_id': '1000001',
                    'begin': datetime.datetime(2014, 4, 30, 20),
                    'end': _MAX_DATE,
                    'type': 9,
                    'vat': None,
                    'currency': 'RUB',
                    'services': [111],
                    'acquiring_percent': None,
                    'nds_for_receipt': None,
                    'netting': False,
                    'netting_pct': None,
                    'offer_accepted': False,
                    'rebate_percent': None,
                    'ind_bel_nds_percent': None,
                }],
                "corporate_contracts": [{
                    "id": 123457,
                    "is_active": True,
                    "external_id": "PAC-13346",
                    "is_prepaid": False,
                    "services": [135]
                }],
                'details': {
                    'bank_city': '',
                    'bank_name': '',
                    'bik': 'bik_100001',
                    'cor_account': '',
                    'fio': u'Таксистов Иван Петрович',
                    'id': '1000001',
                    'inn': 'inn_100001',
                    'kpp': 'kpp_100001',
                    'legal_address': (
                        u'100001, г. Москва, ул. Таксистов, д. 1, корп. 1'
                    ),
                    'long_name': u'OOO "name_100001"',
                    'ogrn': 'ogrn_100001',
                    'op_account': 'account_100001',
                    'short_name': 'name_100001',
                    'invalid_bankprops': True,
                },
                'recommended_payments': [70899.61],
                'threshold_dynamic': 0,
            },
            "requirements": {"corp": False}
        },
        # initially this park has promised payment,
        # expected that positive balance does not remove promised_payment_till
        'park_2': {
            'account': {
                'balances': [{
                    'bonus_left': 0.0,
                    'commissions': 12000.95,
                    'currency': 'RUB',
                    'current_balance': 1200.39,
                    'current_bonus': 0.0,
                    'contract_id': 123402,
                    'netting_last_dt': None,
                    'personal_account_external_id': None,
                }],
                'cash_contract_currency': 'RUB',
                'contracts': [{
                    'id': 123402,
                    'is_prepaid': True,
                    'is_of_card': True,
                    'is_of_cash': True,
                    'is_of_corp': False,
                    'is_of_uber': False,
                    'is_active': True,
                    'is_cancelled': False,
                    'is_deactivated': False,
                    'is_faxed': False,
                    'is_signed': True,
                    'is_suspended': False,
                    'external_id': '00002/02',
                    'link_contract_id': None,
                    'person_id': '1000002',
                    'begin': datetime.datetime(2014, 4, 30, 20),
                    'end': _MAX_DATE,
                    'type': 9,
                    'vat': 0,
                    'currency': 'RUB',
                    'services': [124, 111],
                    'acquiring_percent': None,
                    'nds_for_receipt': None,
                    'netting': False,
                    'netting_pct': None,
                    'offer_accepted': False,
                    'rebate_percent': None,
                    'ind_bel_nds_percent': None,
                }],
                'details': {
                    'bank_city': '',
                    'bank_name': '',
                    'bik': 'bik_100002',
                    'cor_account': '',
                    'fio': u'Таксистов Иван Петрович',
                    'id': '1000002',
                    'inn': 'inn_100002',
                    'kpp': 'kpp_100002',
                    'legal_address': (
                        u'100002, г. Москва, ул. Таксистов, д. 1, корп. 2'
                    ),
                    'long_name': u'OOO "name_100002"',
                    'ogrn': 'ogrn_100002',
                    'op_account': 'account_100002',
                    'short_name': 'name_100002',
                    'invalid_bankprops': False,
                },
                'promised_payment_till': promised_payment_valid,
                'recommended_payments': [70799.61],
                'threshold_dynamic': 0,
            }
        },
        # next three parks are deactivated
        # because they have no valid contract in billing
        'park_3': {
            'account': {
                'deactivated': {
                    'reason': 'park not registered in billing',
                },
            }
        },
        'park_4': {
            'account': {
                'deactivated': {
                    'reason': 'active contract is absent',
                },
                'fetched_contracts': [],
            }
        },
        # do not deactivate because of absence of prepaid contract
        # since `is_on_prepay` is no more considered -
        # we determine prepaidness from contract's info
        'park_5': {
            'account': {
                'balances': [{
                    'bonus_left': 0.0,
                    'commissions': 15000.0,
                    'currency': 'RUB',
                    'current_balance': None,
                    'current_bonus': 0.0,
                    'contract_id': 123405,
                    'netting_last_dt': None,
                    'personal_account_external_id': None,
                }],
                'cash_contract_currency': 'RUB',
                'contracts': [{
                    'id': 123405,
                    'is_of_card': True,
                    'is_of_cash': True,
                    'is_of_corp': False,
                    'is_of_uber': False,
                    'is_active': True,
                    'is_cancelled': False,
                    'is_deactivated': False,
                    'is_faxed': False,
                    'is_signed': True,
                    'is_suspended': False,
                    'is_prepaid': False,
                    'external_id': '00005/05',
                    'link_contract_id': None,
                    'person_id': '1000005',
                    'begin': datetime.datetime(2014, 4, 30, 20),
                    'end': _MAX_DATE,
                    'type': 9,
                    'vat': None,
                    'currency': 'RUB',
                    'services': [124, 111],
                    'acquiring_percent': None,
                    'nds_for_receipt': None,
                    'netting': False,
                    'netting_pct': None,
                    'offer_accepted': False,
                    'rebate_percent': None,
                    'ind_bel_nds_percent': None,
                }],
                'details': {
                    'bank_city': '',
                    'bank_name': '',
                    'bik': 'bik_100005',
                    'cor_account': '',
                    'fio': u'Таксистов Иван Петрович',
                    'id': '1000005',
                    'inn': 'inn_100005',
                    'kpp': 'kpp_100005',
                    'legal_address': (
                        u'100005, г. Москва, ул. Таксистов, д. 1, корп. 5'
                    ),
                    'long_name': u'OOO "name_100005"',
                    'ogrn': 'ogrn_100005',
                    'op_account': 'account_100005',
                    'short_name': 'name_100005',
                    'invalid_bankprops': False,
                },
                'recommended_payments': [0],
                'threshold_dynamic': 0,
            }
        },
        # park is not on prepay, contract cache is absent in park doc
        # but it is filled from billing response
        'park_6': {
            'account': {
                'balances': [{
                    'bonus_left': 0.0,
                    'commissions': 16000.0,
                    'currency': 'RUB',
                    'current_balance': None,
                    'current_bonus': 0.0,
                    'contract_id': 123406,
                    'netting_last_dt': None,
                    'personal_account_external_id': None,
                }],
                'cash_contract_currency': 'RUB',
                'contracts': [{
                    'id': 123406,
                    'is_of_card': True,
                    'is_of_cash': True,
                    'is_of_corp': False,
                    'is_of_uber': False,
                    'is_active': True,
                    'is_cancelled': False,
                    'is_deactivated': False,
                    'is_faxed': False,
                    'is_signed': True,
                    'is_suspended': False,
                    'is_prepaid': False,
                    'external_id': '00006/06',
                    'link_contract_id': None,
                    'person_id': '1000006',
                    'begin': datetime.datetime(2014, 4, 30, 20),
                    'end': _MAX_DATE,
                    'type': 9,
                    'vat': 18,
                    'currency': 'RUB',
                    'services': [124, 111],
                    'acquiring_percent': None,
                    'nds_for_receipt': None,
                    'netting': False,
                    'netting_pct': None,
                    'offer_accepted': False,
                    'rebate_percent': None,
                    'ind_bel_nds_percent': None,
                }],
                'details': {
                    'bank_city': '',
                    'bank_name': '',
                    'bik': 'bik_100006',
                    'cor_account': '',
                    'fio': u'Таксистов Иван Петрович',
                    'id': '1000006',
                    'inn': 'inn_100006',
                    'kpp': 'kpp_100006',
                    'legal_address': (
                        u'100006, г. Москва, ул. Таксистов, д. 1, корп. 6'
                    ),
                    'long_name': u'OOO "name_100006"',
                    'ogrn': 'ogrn_100006',
                    'op_account': 'account_100006',
                    'short_name': 'name_100006',
                    'invalid_bankprops': False,
                },
                'recommended_payments': [0],
                'threshold_dynamic': 0,
            }
        },

        # next two parks have contract cache which is used
        # when billing sends incomplete data in contract

        # this park is deactivated due to low balance
        'park_7': {
            'account': {
                'balances': [{
                    'bonus_left': 0.0,
                    'commissions': 17000.95,
                    'currency': 'RUB',
                    'current_balance': -1700.39,
                    'current_bonus': 0.0,
                    'contract_id': 123407,
                    'netting_last_dt': None,
                    'personal_account_external_id': None,
                }],
                'contracts': [{
                    'id': 123407,
                    'is_prepaid': True,
                    'external_id': '00007/07',
                    'type': 9
                }],
                'deactivated': {
                    'reason': 'low balance',
                },
                'recommended_payments': [73700.39],
                'threshold_dynamic': 0,
            }
        },
        # this park is not on prepay, so it is not deactivated
        'park_8': {
            'account': {
                'balances': [{
                    'bonus_left': 0.0,
                    'commissions': 18000.0,
                    'currency': 'RUB',
                    'current_balance': None,
                    'current_bonus': 0.0,
                    'contract_id': 123408,
                    'netting_last_dt': None,
                    'personal_account_external_id': None,
                }],
                'contracts': [{
                    'id': 123408,
                    'is_prepaid': False,
                    'external_id': '00008/08',
                    u'services': [111],
                    'type': 9
                }],
                'recommended_payments': [0],
                'threshold_dynamic': 0,
            }
        },
        # this park had `deactivated` field
        # which is removed because of `threshold`
        'park_9': {
            'account': {
                'balances': [{
                    'bonus_left': 0.0,
                    'commissions': 19000.95,
                    'currency': 'RUB',
                    'current_balance': -1900.39,
                    'current_bonus': 0.0,
                    'contract_id': 123409,
                    'netting_last_dt': None,
                    'personal_account_external_id': None,
                }],
                'contracts': [{
                    'id': 123409,
                    'is_prepaid': True,
                    'external_id': '00009/09',
                    'type': 9
                }],
                'recommended_payments': [77908.39],
                'threshold': -10000,
                'threshold_dynamic': -10000,
            }
        },
        # this park has promised payment (not expired)
        # so it is not deactivated despite of low balance
        'park_10': {
            'account': {
                'balances': [{
                    'bonus_left': 0.0,
                    'commissions': 20000.95,
                    'currency': 'RUB',
                    'current_balance': -2000.39,
                    'current_bonus': 0.0,
                    'contract_id': 123410,
                    'netting_last_dt': None,
                    'personal_account_external_id': None,
                }],
                'contracts': [{
                    'id': 123410,
                    'is_prepaid': True,
                    'external_id': '00010/10',
                    'type': 9
                }],
                'promised_payment_till': promised_payment_valid,
                'recommended_payments': [82016.39],
                'threshold_dynamic': 0,
            }
        },
        # this park has promised payment but is deactivated
        # because promised payment has expired.
        # Expected, that promise payment is removed because it's expired
        'park_11': {
            'account': {
                'balances': [{
                    'bonus_left': 0.0,
                    'commissions': 21000.95,
                    'currency': 'RUB',
                    'current_balance': -2100.39,
                    'current_bonus': 0.0,
                    'contract_id': 123411,
                    'netting_last_dt': None,
                    'personal_account_external_id': None,
                }],
                'contracts': [{
                    'id': 123411,
                    'is_prepaid': True,
                    'external_id': '00011/11',
                    'type': 9
                }],
                'deactivated': {
                    'reason': 'low balance',
                },
                'recommended_payments': [86124.39],
                'threshold_dynamic': 0,
            }
        },
        # this park should have updated dynamic threshold
        # and must be  not  deactivated
        'park_12': {
            'account': {
                'balances': [{
                    'bonus_left': 0.0,
                    'commissions': 22000.95,
                    'current_balance': -2200.39,
                    'current_bonus': 0.0,
                    'currency': 'RUB',
                    'contract_id': 123412,
                    'netting_last_dt': datetime.datetime(2015, 4, 4, 21, 0, 0),
                    'personal_account_external_id': None,
                }],
                'cash_contract_currency': 'RUB',
                'contracts': [{
                    'id': 123412,
                    'is_of_card': True,
                    'is_of_cash': True,
                    'is_of_corp': False,
                    'is_of_uber': False,
                    'is_active': True,
                    'is_cancelled': False,
                    'is_deactivated': False,
                    'is_faxed': False,
                    'is_signed': True,
                    'is_suspended': False,
                    'link_contract_id': None,
                    'person_id': '100012',
                    'begin': datetime.datetime(2014, 4, 30, 20),
                    'end': _MAX_DATE,
                    'type': 9,
                    'vat': None,
                    'currency': 'RUB',
                    'services': [124, 111],
                    'acquiring_percent': None,
                    'nds_for_receipt': None,
                    'netting': True,
                    'netting_pct': 3,
                    'is_prepaid': True,
                    'external_id': '00012/12',
                    'offer_accepted': False,
                    'rebate_percent': None,
                    'ind_bel_nds_percent': None,
                }],
                'details': {
                    'bank_city': '',
                    'bank_name': '',
                    'bik': 'bik_100012',
                    'cor_account': '',
                    'fio': u'Таксистов Иван Петрович',
                    'id': '100012',
                    'inn': 'inn_100012',
                    'kpp': 'kpp_100012',
                    'legal_address': u'100012, г. Москва, '
                                     u'ул. Таксистов, д. 1, корп. 12',
                    'long_name': u'OOO "name_100012"',
                    'ogrn': 'ogrn_100012',
                    'op_account': 'account_100012',
                    'short_name': 'name_100012',
                    'invalid_bankprops': False,
                },
                'recommended_payments': [90208.39],
                'threshold': -1000,
                'threshold_dynamic': -2316,
            }
        },
        # this park should have updated dynamic threshold
        # and must be deactivated due to low balance
        'park_13': {
            'account': {
                'balances': [{
                    'bonus_left': 0.0,
                    'commissions': 23000.95,
                    'current_balance': -2300.39,
                    'current_bonus': 0.0,
                    'currency': 'RUB',
                    'contract_id': 123413,
                    'netting_last_dt': datetime.datetime(2015, 4, 4, 21, 0, 0),
                    'personal_account_external_id': None,
                }],
                'cash_contract_currency': 'RUB',
                'contracts': [{
                    'id': 123413,
                    'is_of_card': True,
                    'is_of_cash': True,
                    'is_of_corp': False,
                    'is_of_uber': False,
                    'is_active': True,
                    'is_cancelled': False,
                    'is_deactivated': False,
                    'is_faxed': False,
                    'is_signed': True,
                    'is_suspended': False,
                    'link_contract_id': None,
                    'person_id': '100013',
                    'begin': datetime.datetime(2014, 4, 30, 20),
                    'end': _MAX_DATE,
                    'type': 9,
                    'vat': None,
                    'currency': 'RUB',
                    'services': [124, 111],
                    'acquiring_percent': None,
                    'nds_for_receipt': None,
                    'netting': True,
                    'netting_pct': 3,
                    'is_prepaid': True,
                    'external_id': '00013/13',
                    'offer_accepted': False,
                    'rebate_percent': None,
                    'ind_bel_nds_percent': None,
                }],
                'details': {
                    'bank_city': '',
                    'bank_name': '',
                    'bik': 'bik_100013',
                    'cor_account': '',
                    'fio': u'Таксистов Иван Петрович',
                    'id': '100013',
                    'inn': 'inn_100013',
                    'kpp': 'kpp_100013',
                    'legal_address': u'100013, г. Москва, '
                                     u'ул. Таксистов, д. 1, корп. 13',
                    'long_name': u'OOO "name_100013"',
                    'ogrn': 'ogrn_100013',
                    'op_account': 'account_100013',
                    'short_name': 'name_100013',
                    'invalid_bankprops': False,
                },
                'recommended_payments': [94316.39],
                'threshold': -1000,
                'threshold_dynamic': -1306,
                'deactivated': {'reason': 'low balance'},
            }
        },
        # exactly as 13-th but have old balance from deprecated contract
        'park_14': {
            'account': {
                'balances': [{
                    'bonus_left': 0.0,
                    'commissions': 23000.95,
                    'current_balance': -2300.39,
                    'current_bonus': 0.0,
                    'currency': 'RUB',
                    'contract_id': 123414,
                    'netting_last_dt': datetime.datetime(2015, 4, 4, 21, 0, 0),
                    'personal_account_external_id': None,
                }],
                'cash_contract_currency': 'RUB',
                'contracts': [{
                    'id': 123414,
                    'is_of_card': True,
                    'is_of_cash': True,
                    'is_of_corp': False,
                    'is_of_uber': False,
                    'is_active': True,
                    'is_cancelled': False,
                    'is_deactivated': False,
                    'is_faxed': False,
                    'is_signed': True,
                    'is_suspended': False,
                    'link_contract_id': None,
                    'person_id': '100014',
                    'begin': datetime.datetime(2014, 4, 30, 20),
                    'end': _MAX_DATE,
                    'type': 9,
                    'vat': None,
                    'currency': 'RUB',
                    'services': [124, 111],
                    'acquiring_percent': None,
                    'nds_for_receipt': None,
                    'netting': True,
                    'netting_pct': 3,
                    'is_prepaid': True,
                    'external_id': '00014/14',
                    'offer_accepted': False,
                    'rebate_percent': None,
                    'ind_bel_nds_percent': None,
                }],
                'details': {
                    'bank_city': '',
                    'bank_name': '',
                    'bik': 'bik_100014',
                    'cor_account': '',
                    'fio': u'Таксистов Иван Петрович',
                    'id': '100014',
                    'inn': 'inn_100014',
                    'kpp': 'kpp_100014',
                    'legal_address': u'100014, г. Москва, '
                                     u'ул. Таксистов, д. 1, корп. 14',
                    'long_name': u'OOO "name_100014"',
                    'ogrn': 'ogrn_100014',
                    'op_account': 'account_100014',
                    'short_name': 'name_100014',
                    'invalid_bankprops': False,
                },
                'recommended_payments': [94316.39],
                'threshold': -1000,
                'threshold_dynamic': -1306,
                'deactivated': {'reason': 'low balance'},
            }
        },
        # exactly as 14-th but netting_last_dt is None for one of balances
        'park_15': {
            'account': {
                'balances': [
                    {
                        'bonus_left': 0.0,
                        'commissions': 23000.95,
                        'current_balance': -2300.39,
                        'current_bonus': 0.0,
                        'currency': 'RUB',
                        'contract_id': 123415,
                        'netting_last_dt': datetime.datetime(2015, 4, 4, 21, 0, 0),
                        'personal_account_external_id': None,
                    },
                    {
                        'bonus_left': 0.0,
                        'commissions': 23000.95,
                        'current_balance': -2300.39,
                        'current_bonus': 0.0,
                        'currency': 'RUB',
                        'contract_id': 123415,
                        'netting_last_dt': None,
                        'personal_account_external_id': None,
                    },
                ],
                'cash_contract_currency': 'RUB',
                'contracts': [{
                    'id': 123415,
                    'is_of_card': True,
                    'is_of_cash': True,
                    'is_of_corp': False,
                    'is_of_uber': False,
                    'is_active': True,
                    'is_cancelled': False,
                    'is_deactivated': False,
                    'is_faxed': False,
                    'is_signed': True,
                    'is_suspended': False,
                    'link_contract_id': None,
                    'person_id': '100015',
                    'begin': datetime.datetime(2014, 4, 30, 20),
                    'end': _MAX_DATE,
                    'type': 9,
                    'vat': None,
                    'currency': 'RUB',
                    'services': [124, 111],
                    'acquiring_percent': None,
                    'nds_for_receipt': None,
                    'netting': True,
                    'netting_pct': 3,
                    'is_prepaid': True,
                    'external_id': '00015/15',
                    'offer_accepted': False,
                    'rebate_percent': None,
                    'ind_bel_nds_percent': None,
                }],
                'details': {
                    'bank_city': '',
                    'bank_name': '',
                    'bik': 'bik_100015',
                    'cor_account': '',
                    'fio': u'Таксистов Иван Петрович',
                    'id': '100015',
                    'inn': 'inn_100015',
                    'kpp': 'kpp_100015',
                    'legal_address': u'100015, г. Москва, '
                                     u'ул. Таксистов, д. 1, корп. 15',
                    'long_name': u'OOO "name_100015"',
                    'ogrn': 'ogrn_100015',
                    'op_account': 'account_100015',
                    'short_name': 'name_100015',
                    'invalid_bankprops': False,
                },
                'recommended_payments': [94316.39, 94316.39],
                'threshold': -1000,
                'threshold_dynamic': -1000.0,
                'deactivated': {'reason': 'low balance'},
            }
        },
    }

    city = yield db.secondary.cities.find_one()
    yield update_parks_balances._update_parks_balances_single_city(city['_id'])

    for park_doc in (yield db.parks.find().run()):
        park_account = park_doc.get('account', {})
        park_account.pop('log', None)
        park_account.pop('updated', None)
        assert (
            park_account == expected_accounts[park_doc['_id']]['account'],
            park_doc['_id']
        )
        assert (
            park_doc['requirements'].get(
                'corp', False
            ) == expected_accounts[park_doc['_id']].get('requirements', {}).get(
                'corp', False
            )
        )

    # now check undeactivation logics
    # without active_drivers_count parks 3, 4, 5, 7, 9, 11 are deactivated
    # let's check that active_drivers_count change this behaviour
    drivers_counts = {
        'park_0': 100,
        'park_1': 50,
        'park_2': 500,
        'park_3': 100,
        'park_4': 500,
        'park_5': 50,
        'park_6': 100,
        'park_7': 1000,
        'park_8': 500,
        'park_9': 50,
        'park_10': 0,
        'park_11': 50,
        'park_12': 50,
        'park_13': 50,
        'park_14': 50,
        'park_15': 50,
    }
    for park_id, drivers_count in drivers_counts.items():
        yield db.parks.update(
            {'_id': park_id},
            {
                '$set': {'active_drivers_count': drivers_count},
                '$currentDate': {'updated_ts': {'$type': 'timestamp'}}
            }
        )

    yield update_parks_balances._update_parks_balances_single_city(city['_id'])

    for park_doc in (yield db.parks.find().run()):
        park_account = park_doc.get('account', {})
        park_account.pop('log', None)
        park_account.pop('updated', None)
        assert (
            park_account == expected_accounts[park_doc['_id']]['account'], park_doc['_id']
        )

    # now let's check that changing in contracts and balances
    # (that still deactivate parks) is explained correctly
    patch_contracts_getter('_later')
    yield db.parks.update(
        {'_id': 'park_3'},
        {
            '$currentDate': {'updated_ts': {'$type': 'timestamp'}},
            '$set': {
                'billing_client_ids': [[None, None, '100003']],
                'account.corporate_contracts': [{
                    "id": 123458,
                    "is_active": True,
                    "external_id": "PAC-13347",
                    "is_prepaid": True,
                    "services": [135]
                }],
                'requirements.corp': True
            }
        }
    )

    expected_accounts.update({
        'park_3': {
            'account': {
                'deactivated': {
                    'reason': 'active contract is absent',
                },
                'fetched_contracts': [{
                    'id': 123403,
                    'is_prepaid': True,
                    'is_of_card': True,
                    'is_of_cash': True,
                    'is_of_corp': False,
                    'is_of_uber': False,
                    'is_active': False,
                    'is_cancelled': False,
                    'is_deactivated': False,
                    'is_faxed': False,
                    'is_signed': False,
                    'is_suspended': True,
                    'external_id': '00003/03',
                    'link_contract_id': None,
                    'person_id': '1000003',
                    'begin': datetime.datetime(2014, 4, 30, 20),
                    'end': _MAX_DATE,
                    'type': 9,
                    'vat': 0,
                    'currency': 'RUB',
                    'services': [124, 111],
                    'acquiring_percent': None,
                    'nds_for_receipt': None,
                    'netting': False,
                    'netting_pct': None,
                    'offer_accepted': False,
                    'rebate_percent': None,
                    'ind_bel_nds_percent': None,
                }],
                'corporate_contracts': [{
                    'id': 123458,
                    'is_active': True,
                    'external_id': 'PAC-13347',
                    'is_prepaid': True,
                    'services': [135]
                }]
            },
            'requirements': {'corp': True}
        },
        'park_4': {
            'account': {
                'balances': [{
                    'bonus_left': 0.0,
                    'commissions': 14000.95,
                    'current_balance': -1400.39,
                    'current_bonus': 0.0,
                    'currency': 'RUB',
                    'contract_id': 123404,
                    'netting_last_dt': None,
                    'personal_account_external_id': None,
                }],
                'cash_contract_currency': 'RUB',
                'contracts': [{
                    'id': 123404,
                    'is_prepaid': True,
                    'is_of_card': True,
                    'is_of_cash': True,
                    'is_of_corp': False,
                    'is_of_uber': False,
                    'is_active': True,
                    'is_cancelled': False,
                    'is_deactivated': False,
                    'is_faxed': False,
                    'is_signed': True,
                    'is_suspended': False,
                    'external_id': '00004/04',
                    'link_contract_id': None,
                    'person_id': '1000004',
                    'begin': datetime.datetime(2014, 4, 30, 20),
                    'end': _MAX_DATE,
                    'type': 9,
                    'vat': 0,
                    'currency': 'RUB',
                    'services': [124, 111],
                    'acquiring_percent': None,
                    'nds_for_receipt': None,
                    'netting': False,
                    'netting_pct': None,
                    'offer_accepted': False,
                    'rebate_percent': None,
                    'ind_bel_nds_percent': None,
                }],
                'details': {
                    'bank_city': '',
                    'bank_name': '',
                    'bik': 'bik_100004',
                    'cor_account': '',
                    'fio': u'Таксистов Иван Петрович',
                    'id': '1000004',
                    'inn': 'inn_100004',
                    'kpp': 'kpp_100004',
                    'legal_address': u'100004, г. Москва, ул. Таксистов, д. 1, корп. 4',
                    'long_name': u'OOO "name_100004"',
                    'ogrn': 'ogrn_100004',
                    'op_account': 'account_100004',
                    'short_name': 'name_100004',
                    'invalid_bankprops': False,
                },
                'deactivated': {
                    'reason': 'low balance',
                },
                'recommended_payments': [73400.39],
                'threshold_dynamic': 0,
            },
        }
    })

    yield update_parks_balances._update_parks_balances_single_city(city['_id'])

    for park_doc in (yield db.parks.find().run()):
        park_account = park_doc.get('account', {})
        park_account.pop('log', None)
        park_account.pop('updated', None)
        for key, value in park_account.items():
            if value != expected_accounts[park_doc['_id']]['account'][key]:
                print key
                pprint(value)
                pprint(expected_accounts[park_doc['_id']]['account'][key])
        assert park_account == expected_accounts[park_doc['_id']]['account'], park_doc['_id']
        assert (
            park_doc['requirements'].get(
                'corp', False
            ) == expected_accounts[park_doc['_id']].get('requirements', {}).get(
                'corp', False
            )
        )
