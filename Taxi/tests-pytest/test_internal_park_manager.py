# -*- coding: utf-8 -*-
import collections
import datetime
import json
import xmlrpclib
import pprint

from bson import json_util
import pytest
from twisted.internet import defer

from taxi.conf import settings
from taxi.core import async
from taxi.core import db
from taxi.external import billing as external_billing
from taxi.internal import park_manager
from taxi.internal import dbh
from taxi.internal.park_kit import park_helpers
from taxi.util import decimal


@pytest.mark.filldb(parks='get_contract')
@pytest.inline_callbacks
def test_get_contracts(mock, load, monkeypatch):
    mgcc = _mock_get_client_contracts(mock, load)
    monkeypatch.setattr(
        'taxi.external.billing.get_client_contracts', mgcc
    )

    expected_contract_info = {
        'park_0': [{'id': 123400, 'is_prepaid': True,
                    'client_id': '100000', 'rebate_percent': None}],
        'park_1': [{'id': 123401, 'is_prepaid': True,
                    'client_id': '100001', 'rebate_percent': None}],
        'park_2': [{'id': 123402, 'is_prepaid': True,
                    'client_id': '100002', 'rebate_percent': None}],
        'park_5': [{'id': 123405, 'is_prepaid': False,
                    'client_id': '100005', 'rebate_percent': None}],
        'park_6': [{'id': 123406, 'is_prepaid': False, 'client_id': '100006',
                    'rebate_percent': decimal.Decimal('0.155')}],
        'park_rebate_1': [{'id': 123410, 'is_prepaid': False,
                           'client_id': '100010',
                           'rebate_percent': decimal.Decimal('0.125')}],
    }

    parks = yield db.parks.find(
        {'_id': {'$in': expected_contract_info.keys()}}
    ).run()
    for park in parks:
        park_contracts = yield park_manager.fetch_contracts_from_billing(
            park
        )
        active_contracts = park_manager.select_active_contracts(park_contracts)
        for (contract, expected) in zip(active_contracts,
                                        expected_contract_info[park['_id']]):
            assert expected['id'] == contract.id
            assert expected['is_prepaid'] == contract.is_prepaid
            assert expected['client_id'] == contract.client_id
            assert expected['rebate_percent'] == contract.rebate_percent
            assert park['_id'] == contract.park_id


@pytest.mark.filldb(parks='get_contract')
@pytest.mark.config(
    BILLING_UPDATE_SOURCES={
        'balances': 'billing',
        'contracts': {
            'general': 'both',
            'spendable': 'billing'
        },
        'persons': 'billing'
    }
)
@pytest.inline_callbacks
def test_get_contracts_count_diffs(mock, load, monkeypatch):
    mgcc = _mock_get_client_contracts(mock, load)
    monkeypatch.setattr(
        'taxi.external.billing.get_client_contracts', mgcc
    )
    monkeypatch.setattr(
        'taxi.external.billing_replication.get_client_contracts', mgcc
    )

    compare_mock = _mock_compare_and_report_diff(mock)
    monkeypatch.setattr(
        'taxi.internal.park_manager.compare_and_report_diff', compare_mock
    )

    park = yield db.parks.find_one({'_id': 'park_0'})
    yield park_manager.fetch_contracts_from_billing(
        park, consider_replica=True
    )

    assert len(compare_mock.calls) == 1


@pytest.mark.filldb(parks='get_contract')
@pytest.mark.config(
    BILLING_UPDATE_SOURCES={
        'balances': 'billing',
        'contracts': {
            'general': 'billing',
            'spendable': 'billing'
        },
        'persons': 'both'
    }
)
@pytest.inline_callbacks
def test_get_account_details_count_diffs(mock, load, monkeypatch):
    mgcp = _mock_get_client_persons(mock, load)
    monkeypatch.setattr(
        'taxi.external.billing.get_client_persons', mgcp
    )
    monkeypatch.setattr(
        'taxi.external.billing_replication.get_client_persons', mgcp
    )

    compare_mock = _mock_compare_and_report_diff(mock)
    monkeypatch.setattr(
        'taxi.internal.park_manager.compare_and_report_diff', compare_mock
    )
    park = yield db.parks.find_one({'_id': 'park_0'})
    billing_client_id = park_helpers.get_billing_client_id(park)
    yield park_manager.fetch_account_details_from_billing(
        billing_client_id, [], consider_replica=True
    )
    assert len(compare_mock.calls) == 1


@pytest.mark.filldb(parks='get_contract')
@pytest.mark.config(
    BILLING_UPDATE_SOURCES={
        'balances': 'billing',
        'contracts': {
            'general': 'billing',
            'spendable': 'billing'
        },
        'persons': 'both'
    }
)
@pytest.mark.parametrize('consider_replica,billing_calls,replica_calls', [
    (True, 1, 1),
    (False, 1, 0),
])
@pytest.inline_callbacks
def test_get_account_details_consider_replica(
        mock, load, monkeypatch, consider_replica, billing_calls, replica_calls
):
    billing_mock = _mock_get_client_persons(mock, load)
    replica_mock = _mock_get_client_persons(mock, load)
    monkeypatch.setattr(
        'taxi.external.billing.get_client_persons', billing_mock
    )
    monkeypatch.setattr(
        'taxi.external.billing_replication.get_client_persons', replica_mock
    )

    park = yield db.parks.find_one({'_id': 'park_0'})
    billing_client_id = park_helpers.get_billing_client_id(park)

    yield park_manager.fetch_account_details_from_billing(
        billing_client_id, [], consider_replica=consider_replica
    )
    assert len(billing_mock.calls) == billing_calls
    assert len(replica_mock.calls) == replica_calls


@pytest.mark.parametrize('park_id, expected_exception', [
    # Uid exists, no phones: exception raised
    ('park_3', park_manager.BillingParkNotRegistered),
    ('park_4', park_manager.BillingContractAbsent),
    ('park_7', park_manager.BillingDataIncorrect),
    ('park_8', park_manager.BillingDataIncorrect),
])
@pytest.mark.filldb(parks='get_contract')
@pytest.inline_callbacks
def test_get_contracts_errors(
        park_id, expected_exception,
        mock, load, monkeypatch):
    mgcc = _mock_get_client_contracts(mock, load)
    monkeypatch.setattr(
        'taxi.external.billing.get_client_contracts', mgcc
    )

    park = yield db.parks.find_one({'_id': park_id})
    with pytest.raises(expected_exception):
        contracts = yield park_manager.fetch_contracts_from_billing(
            park
        )
        park_manager.select_active_contracts(contracts)


@pytest.mark.filldb(parks='get_contract')
@pytest.mark.config(
    BILLING_UPDATE_SOURCES={
        'balances': 'billing',
        'contracts': {
            'general': 'both',
            'spendable': 'billing'
        },
        'persons': 'billing'
    }
)
@pytest.mark.parametrize('consider_replica,billing_calls,replica_calls', [
    (True, 1, 1),
    (False, 1, 0),
])
@pytest.inline_callbacks
def test_fetch_contracts_from_billing_consider_replica(
        mock, load, monkeypatch, consider_replica, billing_calls, replica_calls
):
    billing_mock = _mock_get_client_contracts(mock, load)
    replica_mock = _mock_get_client_contracts(mock, load)
    monkeypatch.setattr(
        'taxi.external.billing.get_client_contracts', billing_mock
    )
    monkeypatch.setattr(
        'taxi.external.billing_replication.get_client_contracts', replica_mock
    )

    park = yield db.parks.find_one({'_id': 'park_0'})

    yield park_manager.fetch_contracts_from_billing(
        park, consider_replica=consider_replica
    )
    assert len(billing_mock.calls) == billing_calls
    assert len(replica_mock.calls) == replica_calls


@pytest.mark.config(SAVE_PARK_ACCOUNT_HISTORY=True)
@pytest.mark.filldb(parks='get_contract')
@pytest.inline_callbacks
def test_get_and_refresh_contracts(mock, load, monkeypatch):
    mgcc = _mock_get_client_contracts(mock, load)
    monkeypatch.setattr(
        'taxi.external.billing.get_client_contracts', mgcc
    )
    mgcp = _mock_get_client_persons(mock, load)
    monkeypatch.setattr(
        'taxi.external.billing.get_client_persons', mgcp
    )

    # because round-trip of datetime.datetime.max to mongo and back to python
    # transforms 999999 microseconds to 999000 microseconds
    _MAX_DATE = datetime.datetime.max.replace(microsecond=999000)
    park_1_contract = {
        'id': 123401, 'is_prepaid': True, 'client_id': '100001',
        'is_of_card': False, 'is_of_cash': True, 'is_of_corp': False,
        'is_of_uber': False,
        'external_id': '00001/01',
        'person_id': '1000001',
        'is_active': True,
        'is_cancelled': False,
        'is_deactivated': False,
        'is_faxed': False,
        'is_signed': True,
        'is_suspended': False,
        'link_contract_id': None,
        'begin': datetime.datetime(2014, 4, 30, 20),
        'end': _MAX_DATE,
        'type': 0,
        'vat': None,
        'acquiring_percent': None,
        'currency': 'RUB',
        'services': [111],
        'nds_for_receipt': None,
        'netting': False,
        'netting_pct': None,
        'offer_accepted': False,
        'rebate_percent': None,
        'ind_bel_nds_percent': None,
    }

    expected_contract_info = {
        'park_0': {
            'id': 123400, 'is_prepaid': True, 'client_id': '100000',
            'is_of_card': True, 'is_of_cash': False, 'is_of_corp': False,
            'is_of_uber': False,
            'external_id': '00000/00',
            'person_id': '1000000',
            'is_active': True,
            'is_cancelled': False,
            'is_deactivated': False,
            'is_faxed': False,
            'is_signed': True,
            'is_suspended': False,
            'link_contract_id': None,
            'begin': datetime.datetime(2014, 4, 30, 20),
            'end': _MAX_DATE,
            'type': 0,
            'vat': None,
            'acquiring_percent': None,
            'currency': 'RUB',
            'services': [124],
            'nds_for_receipt': None,
            'netting': False,
            'netting_pct': None,
            'offer_accepted': True,
            'rebate_percent': None,
            'ind_bel_nds_percent': None,
        },
        'park_1': park_1_contract,
        'park_2': {
            'id': 123402, 'is_prepaid': True, 'client_id': '100002',
            'is_of_card': True, 'is_of_cash': True, 'is_of_corp': False,
            'is_of_uber': True,
            'external_id': '00002/02',
            'person_id': '1000002',
            'is_active': True,
            'is_cancelled': False,
            'is_deactivated': False,
            'is_faxed': False,
            'is_signed': True,
            'is_suspended': False,
            'link_contract_id': None,
            'begin': datetime.datetime(2014, 4, 30, 20),
            'end': _MAX_DATE,
            'type': 0,
            'vat': 0,
            'acquiring_percent': None,
            'currency': 'RUB',
            'services': [605, 111],
            'nds_for_receipt': None,
            'netting': False,
            'netting_pct': None,
            'offer_accepted': False,
            'rebate_percent': None,
            'ind_bel_nds_percent': None,
        },
        'park_6': {
            'id': 123406, 'is_prepaid': False, 'client_id': '100006',
            'is_of_card': True, 'is_of_cash': True, 'is_of_corp': False,
            'is_of_uber': True,
            'external_id': '00006/06',
            'person_id': '1000006',
            'is_active': True,
            'is_cancelled': True,
            'is_deactivated': True,
            'is_faxed': True,
            'is_signed': True,
            'is_suspended': False,
            'link_contract_id': 999,
            'begin': datetime.datetime(2014, 4, 30, 20),
            'end': _MAX_DATE,
            'type': 0,
            'vat': 18,
            'acquiring_percent': '0.055',
            'currency': 'RUB',
            'services': [128, 125, 111],
            'nds_for_receipt': None,
            'netting': False,
            'netting_pct': None,
            'offer_accepted': False,
            'rebate_percent': '0.155',
            'ind_bel_nds_percent': '0.2',
        },
        # next two parks have contract's cache in park['account']
        'park_7': {
            'id': 123407, 'is_prepaid': True, 'client_id': '100007',
            'external_id': '00007/07', 'offer_accepted': False, "type": 9
        },
        'park_8': {
            'id': 123408, 'is_prepaid': False, 'client_id': '100008',
            'external_id': '00008/08', 'offer_accepted': False, "type": 9
        }
    }
    expected_account_history_info = {
        'park_1': {
            'general_contracts': [park_1_contract]
        }
    }
    expected_currency_info = {
        'park_0': {
            'cash_contract_currency': None,
            'card_contract_currency': None,
            'acquiring_percent': None,
        },
        'park_1': {
            'cash_contract_currency': 'RUB',
            'card_contract_currency': None,
            'acquiring_percent': None,
        },
        'park_2': {
            'cash_contract_currency': 'RUB',
            'card_contract_currency': None,
            'acquiring_percent': None,
        },
        'park_6': {
            'cash_contract_currency': 'RUB',
            'card_contract_currency': 'RUB',
            'acquiring_percent': '0.055',
        },
    }
    deactivated_parks = ['park_3', 'park_4', 'park_9']

    parks = yield db.parks.find().run()
    contracts = dict(
        (contract.park_id, contract) for contract in
        (yield park_manager.get_and_refresh_contracts(
            parks, check_contracts=True))[0].values()
    )

    refreshed_parks = yield db.parks.find().run()
    for park_doc in refreshed_parks:
        park_id = park_doc['_id']
        if park_id in expected_contract_info:
            expected_info = expected_contract_info[park_doc['_id']]
            billing_client_id = expected_info.pop('client_id')
            park_contract = park_doc['account']['contracts'][0]
            assert expected_info == park_contract
            assert contracts[park_id].client_id == billing_client_id
            if 'offer_accepted' in expected_info:
                assert (contracts[park_id].offer_accepted ==
                        expected_info['offer_accepted'])
            if 'person_id' in expected_info:
                park_account_details = park_doc['account']['details']
                expected_person_id = str(expected_info['person_id'])
                assert park_account_details['id'] == expected_person_id
        elif park_id in deactivated_parks:
            park = yield db.parks.find_one(
                {'_id': park_id},
                ['account']
            )
            assert park['account']['deactivated']
            if park_id == 'park_9':
                deactivation_reason = park['account']['deactivated']['reason']
                assert deactivation_reason == park_manager.LOW_BALANCE
            else:
                assert 'balances' not in park['account']
                assert 'contracts' not in park['account']

        if park_id in expected_currency_info:
            expected_info = expected_currency_info[park_doc['_id']]
            account = park_doc.get('account', {})
            cash_currency = account.get('cash_contract_currency')
            card_currency = account.get('card_contract_currency')
            acquiring_percent = account.get('acquiring_percent')
            assert cash_currency == expected_info['cash_contract_currency']
            assert card_currency == expected_info['card_contract_currency']
            assert acquiring_percent == expected_info['acquiring_percent']
        if park_id in expected_account_history_info:
            assert (
                park_doc['account']['history'] ==
                expected_account_history_info[park_id]
            )


@pytest.mark.filldb(parks='get_contract')
@pytest.inline_callbacks
def test_get_and_refresh_contracts_error(mock, monkeypatch):
    @mock
    def get_client_contracts(billing_client_id, dt=None, contract_kind=None,
                             contract_signed=True, log_extra=None):
        raise external_billing.TimeoutError

    monkeypatch.setattr(
        'taxi.external.billing.get_client_contracts', get_client_contracts
    )

    expected_contract_info = {
        # these parks have contract's cache in park['account']
        'park_4': {
            'id': 123404, 'is_prepaid': True, 'client_id': '100004',
            'external_id': '00004/04', 'offer_accepted': False, "type": 9
        },
        'park_5': {
            'id': 123405, 'is_prepaid': True, 'client_id': '100005',
            'external_id': '00005/05', 'offer_accepted': False, "type": 9
        },
        'park_7': {
            'id': 123407, 'is_prepaid': True, 'client_id': '100007',
            'external_id': '00007/07', 'offer_accepted': False, "type": 9
        },
        'park_8': {
            'id': 123408, 'is_prepaid': False, 'client_id': '100008',
            'external_id': '00008/08', 'offer_accepted': False, "type": 9
        },
    }
    # other parks have no contract's cache and thus are marked as deactivated
    deactivated_parks = [
        'park_%s' % park_id for park_id in [0, 1, 2, 3, 4, 5, 6, 9]
    ]

    parks = yield db.parks.find().run()

    contracts = dict(
        (contract.park_id, contract) for contract in
        (yield park_manager.get_and_refresh_contracts(
            parks, check_contracts=True))[0].values()
    )

    refreshed_parks = yield db.parks.find().run()
    for park_doc in refreshed_parks:
        park_id = park_doc['_id']
        if park_id in expected_contract_info:
            expected_info = expected_contract_info[park_doc['_id']]
            billing_client_id = expected_info.pop('client_id')
            park_account = park_doc['account']['contracts'][0]
            assert expected_info == park_account
            assert contracts[park_id].client_id == billing_client_id
        elif park_id in deactivated_parks:
            park = yield db.parks.find_one(
                {'_id': park_id},
                ['account']
            )
            assert park['account']['deactivated']


@pytest.mark.filldb(parks='get_contract')
@pytest.inline_callbacks
def test_get_and_refresh_contracts_error_without_check(
        patch, mock, monkeypatch):
    @mock
    def get_client_contracts(
            billing_client_id, dt=None, contract_kind=None,
            contract_signed=True, log_extra=None):
        raise external_billing.TimeoutError

    @async.inline_callbacks
    def update(self, spec, update):
        if '$set' in update and not update['$set']:
            raise ValueError('$set should not be empty')
        yield None

    monkeypatch.setattr('taxi.core.db.CollectionWrapper.update', update)
    monkeypatch.setattr(
        'taxi.external.billing.get_client_contracts', get_client_contracts
    )

    parks = yield db.parks.find().run()
    yield park_manager.get_and_refresh_contracts(parks, check_contracts=False)


@pytest.mark.filldb(parks='get_contract')
@pytest.mark.config(
    BILLING_UPDATE_SOURCES={
        'balances': 'billing',
        'contracts': {
            'general': 'both',
            'spendable': 'billing'
        },
        'persons': 'both'
    }
)
@pytest.mark.parametrize(
    'consider_replica,billing_mgcc_calls,replica_mgcc_calls,'
    'billing_mgcp_calls,replica_mgcp_calls', [
        (True, 1, 1, 1, 1),
        (False, 1, 0, 1, 0),
])
@pytest.inline_callbacks
def test_get_and_refresh_contracts_consider_replica(
        mock, load, monkeypatch, consider_replica,
        billing_mgcc_calls, replica_mgcc_calls,
        billing_mgcp_calls, replica_mgcp_calls
):
    billing_mgcc = _mock_get_client_contracts(mock, load)
    replica_mgcc = _mock_get_client_contracts(mock, load)
    billing_mgcp = _mock_get_client_persons(mock, load)
    replica_mgcp = _mock_get_client_persons(mock, load)

    monkeypatch.setattr(
        'taxi.external.billing.get_client_contracts', billing_mgcc
    )
    monkeypatch.setattr(
        'taxi.external.billing_replication.get_client_contracts', replica_mgcc
    )
    monkeypatch.setattr(
        'taxi.external.billing.get_client_persons', billing_mgcp
    )
    monkeypatch.setattr(
        'taxi.external.billing_replication.get_client_persons', replica_mgcp
    )

    park = yield db.parks.find_one({'_id': 'park_0'})

    yield park_manager.get_and_refresh_contracts(
        [park], consider_replica=consider_replica
    )
    assert len(billing_mgcc.calls) == billing_mgcc_calls
    assert len(replica_mgcc.calls) == replica_mgcc_calls
    assert len(billing_mgcp.calls) == billing_mgcp_calls
    assert len(replica_mgcp.calls) == replica_mgcp_calls


@pytest.mark.filldb(parks='get_contract')
@pytest.inline_callbacks
def test_bulk_get_park_balances(mock, load, monkeypatch):
    gccm = _mock_get_client_contracts(mock, load)
    monkeypatch.setattr(
        'taxi.external.billing.get_client_contracts', gccm
    )
    mgcp = _mock_get_client_persons(mock, load)
    monkeypatch.setattr(
        'taxi.external.billing.get_client_persons', mgcp
    )

    @mock
    def get_parks_balances(contract_ids, log_extra=None):
        if len(contract_ids) == 1:
            filename = 'get_parks_balances_%s.json' % contract_ids[0]
        else:
            filename = 'get_parks_balances.json'
        response_json = load(filename)
        response = json.loads(response_json)
        return async.call(
            lambda: defer.succeed(response), lambda: response
        )
    monkeypatch.setattr(
        'taxi.external.billing.get_parks_balances', get_parks_balances
    )

    expected_balances = {
        '100000': {
            'current_balance': 1000.39,
            'commissions': 10000.95,
            'current_bonus': 0,
            'bonus_left': 0,
            'contract_id': 123400,
            'currency': 'RUB',
            'netting_last_dt': None,
            'personal_account_external_id': None,
        },
        '100001': {
            'current_balance': 1100.39,
            'commissions': 11000.95,
            'current_bonus': 0,
            'bonus_left': 0,
            'contract_id': 123401,
            'currency': 'RUB',
            'netting_last_dt': None,
            'personal_account_external_id': None,
        },
        '100002': {
            'current_balance': 1200.39,
            'commissions': 12000.95,
            'current_bonus': 0,
            'bonus_left': 0,
            'contract_id': 123402,
            'currency': 'RUB',
            'netting_last_dt': None,
            'personal_account_external_id': None,
        },
        '100006': {
            'current_balance': None,
            'commissions': 16000,
            'current_bonus': 0,
            'bonus_left': 0,
            'contract_id': 123406,
            'currency': 'RUB',
            'netting_last_dt': None,
            'personal_account_external_id': None,
        },
        '100005': {
            'current_balance': None,
            'commissions': 15000,
            'current_bonus': 0,
            'bonus_left': 0,
            'contract_id': 123405,
            'currency': 'RUB',
            'netting_last_dt': None,
            'personal_account_external_id': None,
        },
        '100007': {
            'current_balance': 1700.39,
            'commissions': 17000.95,
            'current_bonus': 0,
            'bonus_left': 0,
            'contract_id': 123407,
            'currency': 'RUB',
            'netting_last_dt': None,
            'personal_account_external_id': None,
        },
        '100008': {
            'current_balance': None,
            'commissions': 18000,
            'current_bonus': 0,
            'bonus_left': 0,
            'contract_id': 123408,
            'currency': 'RUB',
            'netting_last_dt': None,
            'personal_account_external_id': None,
        },
        '100009': {
            'current_balance': None,
            'commissions': 19000,
            'current_bonus': 0,
            'bonus_left': 0,
            'contract_id': 123409,
            'currency': 'RUB',
            'netting_last_dt': None,
            'personal_account_external_id': None,
        },
        '100010': {
            'current_balance': None,
            'commissions': 10100,
            'current_bonus': 0,
            'bonus_left': 0,
            'contract_id': 123410,
            'currency': 'RUB',
            'netting_last_dt': None,
            'personal_account_external_id': None,
        },
    }

    parks = yield db.parks.find().run()
    contracts = (yield park_manager.get_and_refresh_contracts(
        parks, check_contracts=True
    ))[0]
    balances = yield park_manager.bulk_get_park_balances(contracts)
    for balance in balances:
        assert balance.as_dict() == expected_balances[balance.client_id]


@pytest.mark.filldb(parks='ids_for_city')
@pytest.inline_callbacks
def test_get_docs_for_city(patch):
    docs = yield park_manager.get_docs_for_city('moscow')
    ids = sorted(i['_id'] for i in docs)
    assert ids == ['park1', 'park2']


@pytest.mark.filldb(parks='get_doc')
@pytest.inline_callbacks
def test_get_doc():
    doc_from_api = yield park_manager.get_doc('park1')
    doc_from_db = yield db.parks.find_one({'_id': 'park1'})
    assert doc_from_api == doc_from_db

    with pytest.raises(park_manager.NotFoundError) as excinfo:
        yield park_manager.get_doc('unknown_park')
    assert 'park \'unknown_park\' not found' in excinfo.value


@pytest.mark.filldb(parks='ids_for_city')
@pytest.mark.parametrize('city_id,expected_ids', [
    ('moscow', ['park1', 'park2']),
    ('spb', ['park3']),
    ('voronezh', []),
])
@pytest.inline_callbacks
def test_get_park_ids_for_city(city_id, expected_ids):
    ids = yield park_manager.get_park_ids_for_city(city_id)
    assert set(ids) == set(expected_ids)


def _make_contract(contract_id):
    contract_dict = collections.defaultdict((lambda: 0), {'id': contract_id})
    return park_manager.Contract(contract_dict, None)


@pytest.mark.filldb(_fill=False)
def test_merge_with_new_contracts():
    current = _make_contract('current_id')
    new = _make_contract('new_id')
    new_with_current_id = _make_contract('current_id')
    assert park_manager.merge_with_new_contracts(
        [], [new]) == [new]
    assert park_manager.merge_with_new_contracts(
        [current], [new]) == [current, new]
    assert park_manager.merge_with_new_contracts(
        [current], [new_with_current_id]) == [new_with_current_id]


@pytest.mark.parametrize('park_doc,expected', [
    ({}, []),
    (
        {
            'account': {
                'history': {
                    'general_contracts': [{'id': 'general_id'}],
                    'spendable_contracts': [{'id': 'spendable_id'}],
                }
            }},
        [{'id': 'general_id'}]
    ),
])
@pytest.mark.filldb(_fill=False)
def test_get_general_contracts_history(park_doc, expected):
    assert park_manager.get_general_contracts_history(park_doc) == expected


@pytest.mark.parametrize('park_doc,expected', [
    ({}, []),
    (
            {
                'account': {
                    'history': {
                        'general_contracts': [{'id': 'general_id'}],
                        'spendable_contracts': [{'id': 'spendable_id'}],
                    }
                }},
            [{'id': 'spendable_id'}]
    ),
])
@pytest.mark.filldb(_fill=False)
def test_get_spendable_contracts_history(park_doc, expected):
    assert park_manager.get_spendable_contracts_history(park_doc) == expected


def _park_doc_with_offer(
        automate_marketing_payments, offer_confirmed,
        pay_donations_without_offer, offer_contracts=None):
    if offer_contracts is None:
        offer_contracts = []
    park_doc = {
        '_id': 'some_park_id',
        'account': {
            'offer_contracts': offer_contracts,
        }
    }
    if automate_marketing_payments is not None:
        park_doc['automate_marketing_payments'] = automate_marketing_payments
    if offer_confirmed is not None:
        park_doc['account']['offer_confirmed'] = offer_confirmed
    park_doc['pay_donations_without_offer'] = pay_donations_without_offer

    return park_doc


def _make_offer_contract_from_currency(currency):
    if currency is None:
        return {}
    return {
        'currency': currency,
        'type': 87,
    }


def _mock_compare_and_report_diff(mock):
    @mock
    def compare_and_report_diff(
            data_type, billing_data, billing_replication_data, log_extra
    ):
        return True
    return compare_and_report_diff


def _mock_get_client_contracts(mock, load):
    @mock
    def get_client_contracts(
            billing_client_id, dt=None, contract_kind=None,
            contract_signed=True, log_extra=None):
        if contract_kind == external_billing.SPENDABLE_CONTRACT:
            sample = 'get_client_contracts_spendable_%s.json'
        else:
            sample = 'get_client_contracts_%s.json'
        response_json = load(sample % billing_client_id)
        response = json.loads(response_json)
        for contract in response:
            contract['DT'] = xmlrpclib.DateTime(str(contract['DT']))
        return async.call(
            lambda: defer.succeed(response), lambda: response
        )
    return get_client_contracts


def _mock_get_client_persons(mock, load):
    @mock
    def get_client_persons(billing_client_id, log_extra=None):
        response_json = load(
            'get_client_persons_%s.json' % billing_client_id
        )
        response = json.loads(response_json)
        return async.call(
            lambda: defer.succeed(response), lambda: response
        )
    return get_client_persons


def _make_park_doc_with_contracts(contracts):
    for contract in contracts:
        # setting not interesting required fields
        contract['id'] = object()
        contract['external_id'] = object()
        contract['is_prepaid'] = True
    return {
        '_id': object(),
        'account': {
            'contracts': contracts,
        }
    }

_CASH = settings.BILLING_SERVICE_ID
_CARD = settings.BILLING_CARD_SERVICE_ID


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('park_doc,expected_result', [
    # one card contracts - easy peasy
    (
        _make_park_doc_with_contracts(
            [
                dict(services=[_CARD], currency='RUR'),
            ]
        ),
        'RUB',
    ),
    # one card contract, one cash contract - different currencies - pick card
    (
        _make_park_doc_with_contracts(
            [
                dict(services=[_CARD], currency='USD'),
                dict(services=[_CASH], currency='RUR'),
            ]
        ),
        'USD',
    ),
    # two card contracts, same currency - pick anything - they're the same
    # probably impossible case in prod, but couldn't hurt to test it.
    (
        _make_park_doc_with_contracts(
            [
                dict(services=[_CARD], currency='USD'),
                dict(services=[_CARD], currency='USD'),
            ]
        ),
        'USD',
    ),
    # two card contracts, one with None currency - pick another
    # probably impossible case in prod, but couldn't hurt to test it.
    (
        _make_park_doc_with_contracts(
            [
                dict(services=[_CARD], currency='USD'),
                dict(services=[_CARD], currency=None),
            ]
        ),
        'USD',
    ),
])
def test_get_contract_currency(park_doc, expected_result):
    actual_result = park_manager.get_service_contract_currency(park_doc, _CARD)
    assert actual_result == expected_result


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('park_doc,expected_exception', [
    # no contracts at all
    (
        _make_park_doc_with_contracts(
            [

            ]
        ),
        park_manager.NoCurrencyError,
    ),
    # one card contract, but with None currency - same as no contracts
    (
        _make_park_doc_with_contracts(
            [
                dict(services=[_CARD], currency=None),
            ]
        ),
        park_manager.NoCurrencyError,
    ),
    # no card contracts
    (
        _make_park_doc_with_contracts(
            [
                dict(services=[_CASH], currency='RUR'),
            ]
        ),
        park_manager.NoCurrencyError,
    ),
    # two card contracts, different currency
    (
        _make_park_doc_with_contracts(
            [
                dict(services=[_CARD], currency='USD'),
                dict(services=[_CARD], currency='RUR'),
            ]
        ),
        park_manager.MultipleCurrenciesError,
    ),
])
def test_get_card_contract_currency_failure(park_doc, expected_exception):
    with pytest.raises(expected_exception):
        park_manager.get_service_contract_currency(park_doc, _CARD)


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('park_doc,expected_percent', [
    (
        _make_park_doc_with_contracts(
            [
                dict(is_of_card=True, acquiring_percent='0.055'),
            ]
        ),
        '0.055'
    ),

    (
        _make_park_doc_with_contracts(
            [
                dict(is_of_card=False, acquiring_percent='0.044'),
                dict(is_of_card=True, acquiring_percent='0.055'),
            ]
        ),
        '0.055'
    ),
])
def test_get_acquiring_percent(park_doc, expected_percent):
    expected_decimal_percent = decimal.Decimal(expected_percent)
    actual_percent = park_manager.get_acquiring_percent(park_doc)
    assert actual_percent == expected_decimal_percent


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('park_doc', [
    # no acquiring percent
    _make_park_doc_with_contracts(
        [
            dict(is_of_card=True),
        ]
    ),
    # no card contract
    _make_park_doc_with_contracts(
        [
            dict(is_of_card=False, acquiring_percent='5.50'),
        ]
    ),
])
def test_get_acquiring_percent_failure(park_doc):
    with pytest.raises(park_manager.NoAcquiringPercent):
        park_manager.get_acquiring_percent(park_doc)


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('park_doc,expected_result', [
    # yep
    (
        _make_park_doc_with_contracts(
            [
                dict(services=[_CARD], currency='RUR')
            ]
        ),
        True,
    ),
    # nope - only cash contract
    (
        _make_park_doc_with_contracts(
            [
                dict(services=[_CASH], currency='RUR')
            ]
        ),
        False,
    ),
    # nope - no contracts
    (
        _make_park_doc_with_contracts(
            [
                dict(services=[], currency='RUR')
            ]
        ),
        False,
    ),
])
def test_has_card_contract_currency(park_doc, expected_result):
    actual_result = park_manager.has_card_contract_currency(park_doc)
    assert actual_result is expected_result


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('park_doc,expected_result', [
    # yep
    (
        _make_park_doc_with_contracts(
            [
                dict(services=[_CASH], currency='RUR')
            ]
        ),
        True,
    ),
    # nope - only card contract
    (
        _make_park_doc_with_contracts(
            [
                dict(services=[_CARD], currency='RUR')
            ]
        ),
        False,
    ),
    # nope - no contracts
    (
        _make_park_doc_with_contracts(
            [
                dict(services=[], currency='RUR')
            ]
        ),
        False,
    ),
])
def test_has_cash_contract_currency(park_doc, expected_result):
    actual_result = park_manager.has_cash_contract_currency(park_doc)
    assert actual_result is expected_result


@pytest.mark.filldb(parks='refund_mail')
@pytest.mark.parametrize(
    'order_id,park_id,success,code,park_name,real_clid,currency,country_id', [
    ('order_id', 'park_success', True, 'CODE', u'"Реал Парк"', 'rc_0001', 'RUB', 'rus'),
    (None, 'park_success', False, 'CODE', None, None, None, None),
    ('order_id', 'park_no_email', False, 'CODE', None, None, None, None),
    ('order_id', 'park_billing_email', True, 'CODE', u'Биллинговый', None, 'GBP', 'rus'),
    ('order_id', 'park_success', True, 'OTHER',
     u'"Реал Парк"', 'rc_0001', 'RUB', 'rus'),
    ('order_id', 'park_kazakh', True, 'CODE', u'Казахский', None, 'KZT', 'kaz'),
])
@pytest.mark.config(
    REFUND_MAIL_SENDER_BY_COUNTRY={
        '__default__': {
            'sender_key': 'park_refund_mail.sender.yandex',
            'sender_email_key': 'support_email',
        },
        'kaz': {
            'sender_key': 'park_refund_mail.sender.uber',
            'sender_email_key': 'support_email_uber',
        },
    }
)
@pytest.mark.translations([
    (
        'notify', 'park_refund_mail.CODE.body', 'ru',
        u'%(sender)s заказ: %(order_id)s | парк: %(park_name)s, сумма: %(refund_sum)s'
    ),
    ('notify', 'park_refund_mail.CODE.subject', 'ru', u'subject:%(order_id)s'),
    ('notify', 'park_refund_mail.OTHER.subject', 'ru',
     u'subject:%(order_id)s'),
    (
        'notify', 'park_refund_mail.OTHER.body', 'ru',
        u'%(sender)s заказ: %(order_id)s | '
        u'парк: %(park_name)s, сумма: %(refund_sum)s'
    ),
    ('notify', 'park_refund_mail.sender.yandex', 'ru', u'Яндекс.Такси'),
    ('notify', 'park_refund_mail.sender.uber', 'ru', u'Uber'),
    ('notify', 'support_email', 'ru', u'email <support@email.ru>'),
    ('notify', 'support_email_uber', 'ru', u'email <support_uber@email.ru>'),
    ('notify', 'park_refund_mail.read_below_alert', 'ru', u'Текст на русском ниже'),
    (
        'notify', 'park_refund_mail.CODE.body', 'kk',
        u'%(sender)s тапсырыс: %(order_id)s | парк: %(park_name)s, сомасы: %(refund_sum)s'
    ),
    ('notify', 'park_refund_mail.CODE.subject', 'kk', u'Казакша:%(order_id)s'),
    (
        'notify', 'park_refund_mail.OTHER.body', 'kk',
        u'%(sender)s тапсырыс: %(order_id)s | '
        u'парк: %(park_name)s, сомасы: %(refund_sum)s'
    ),
    ('notify', 'park_refund_mail.OTHER.subject', 'kk',
     u'Казакша:%(order_id)s'),
    ('notify', 'park_refund_mail.read_below_alert', 'kk', u'Казакша нижы etc'),
    ('tariff', 'currency_with_sign.default', 'ru', u'$VALUE$ $SIGN$$CURRENCY$'),
    ('tariff', 'currency_with_sign.default', 'kk', u'$VALUE$ $SIGN$$CURRENCY$'),
    ('notify', 'park_refund_mail.sender.yandex', 'kk', u'Яндекс.Такси-kz'),
    ('notify', 'park_refund_mail.sender.uber', 'kk', u'Uber-kz'),
    ('notify', 'support_email', 'kk', u'email <support@email.kz>'),
    ('notify', 'support_email_uber', 'kk', u'email <support_uber@email.kz>'),
    ('tariff', 'currency_with_sign.gbp', 'ru', u'$SIGN$$VALUE$ $CURRENCY$'),
    ('tariff', 'currency_sign.rub', 'ru', u'₽'),
    ('tariff', 'currency_sign.kzt', 'ru', u'₸'),
    ('tariff', 'currency_sign.gbp', 'ru', u'£'),
])
@pytest.inline_callbacks
def test_send_refund_mail(order_id, park_id, success, code, park_name,
                          real_clid, currency, country_id, patch, mock):
    @patch('taxi.internal.email_sender.send')
    @mock
    def send(email_message, log_extra=None):
        pass

    mail_info = park_manager.RefundMailInfo(
        alias_id=order_id,
        park_id=park_id,
        reason_code=code,
        refund_sum=100,
        real_clid=real_clid,
        currency=currency,
        country_id=country_id,
    )
    park_manager.REASON_CODES_DICT['CODE'] = u'Просто так'
    yield park_manager.send_refund_mail(mail_info)

    if success:
        email_message = send.call['email_message']
        assert u'заказ: %s |' % order_id in email_message.body
        if park_id == 'park_kazakh':
            assert u'тапсырыс:' in email_message.body
            assert u'subject:' + order_id in email_message.subject
            assert u'Казакша:' + order_id in email_message.subject
            assert u'Текст на русском ниже' in email_message.body
        else:
            assert email_message.subject == u'subject:' + order_id
        if currency == 'RUB':
            assert u'сумма: 100 RUB' in email_message.body
        elif currency == 'KZT':
            assert u'сомасы: 100 KZT' in email_message.body
        else:
            assert u'сумма: 100 GBP' in email_message.body
        if country_id == 'rus':
            assert u'Яндекс.Такси' in email_message.body
            assert email_message.sender == 'email <support@email.ru>'
        else:
            assert u'Uber-kz' in email_message.body
            assert email_message.sender == 'email <support_uber@email.kz>'
        assert u'парк: %s' % park_name in email_message.body
        assert email_message.to == 'park@example.com'
        assert send.calls == []
    else:
        assert send.calls == []


def _make_account_details(
        offer_confirmed,
        link_contract_id=-1,
        previous_offer_confirmed=datetime.datetime(2016, 11, 11),
        offer_confirmed_unset_delay=None,
        log_extra=None):
    return {
        'ID': 'some_ID',
        'NAME': 'some_NAME',
        'offer_confirmed': offer_confirmed,
        'link_contract_id': link_contract_id,
        'previous_offer_confirmed': previous_offer_confirmed,
        'offer_confirmed_unset_delay': offer_confirmed_unset_delay
    }


@pytest.mark.now('2018-12-20 00:00:00 +03')
@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize(
    'park_doc,update,offer_contracts,account_details,'
    'confirmed,expected_result', [
        (
            {'_id': '1'},
            {},
            [],
            {},
            None,
            (False, '', ''),
        ),
        (
            {
                '_id': '1',
                'account': _make_account_details(
                    offer_confirmed=True,
                    offer_confirmed_unset_delay=datetime.datetime(2016, 11, 11)
                ),
            },
            {},
            [],
            {},
            None,
            (True, 'no_offer_contracts', 'gone'),
        ),
        (
            {
                '_id': '1',
                'account': _make_account_details(
                    offer_confirmed=True,
                ),
            },
            {},
            [{}],
            {},
            True,
            (False, '', ''),
        ),
        (
            {
                '_id': '1',
                'account': _make_account_details(
                    offer_confirmed=True,
                    offer_confirmed_unset_delay=datetime.datetime(2016, 11, 11)
                ),
            },
            {},
            [{}],
            {},
            False,
            (True, 'contracts_change', 'gone'),
        ),
        (
            {
                '_id': '1',
                'account': _make_account_details(
                    offer_confirmed=False,
                ),
            },
            {},
            [{}],
            {},
            False,
            (False, '', ''),
        ),
        # not empty offer contracts
        (
            {
                '_id': '1',
                'account': _make_account_details(
                    offer_confirmed=True,
                ),
            },
            {},
            [{}],
            {},
            None,
            (False, '', ''),
        ),
        (
            {
                '_id': '1',
                'account': _make_account_details(
                    offer_confirmed=False,
                ),
            },
            {},
            [],
            {},
            None,
            (False, '', ''),
        ),
        (
            {
                '_id': '1',
                'account': _make_account_details(
                    offer_confirmed=False,
                    link_contract_id=1
                ),
            },
            {},
            [{'link_contract_id': 2}],
            {},
            None,
            (False, '', ''),
        ),
        (
            {
                '_id': '1',
                'account': _make_account_details(
                    offer_confirmed=False,
                    link_contract_id=1
                ),
            },
            {},
            [{'link_contract_id': 1}],
            {},
            None,
            (True, 'reveal_by_activate_linked_contract', 'reveal'),
        ),
        (
            {
                '_id': '1',
                'account': _make_account_details(
                    offer_confirmed=True,
                ),
            },
            {},
            [{}],
            {},
            False,
            (False, '', ''),
        ),
        (
            {
                '_id': '1',
                'account': _make_account_details(
                    offer_confirmed=True,
                    offer_confirmed_unset_delay=datetime.datetime(2019, 11, 11)
                ),
            },
            {},
            [{}],
            {},
            False,
            (False, '', ''),
        ),
])
def test_update_offer_changes(
        park_doc, update, offer_contracts, account_details, confirmed,
        expected_result):
    actual_result = park_manager.update_offer_changes(
        park_doc=park_doc,
        update=update,
        delay=1000,
        offer_contracts=offer_contracts,
        account_details=account_details,
        confirmed=confirmed,
    )
    assert actual_result == expected_result


@pytest.mark.parametrize('park_doc,expected_nds', [
    (
        {
            'account': {
                'contracts': []
            }
        },
        None
    ),
    (
        {
            '_id': 0,
            'account': {
                'contracts': [
                    {
                        'id': 1234,
                        'external_id': '1234',
                        'is_prepaid': False,
                    }
                ]
            }
        },
        None
    ),
    (
        {
            '_id': 0,
            'account': {
                'contracts': [
                    {
                        'id': 1234,
                        'external_id': '1234',
                        'is_prepaid': False,
                        'nds_for_receipt': 0,
                    }
                ]
            }
        },
        0
    ),
    (
        {
            '_id': 0,
            'account': {
                'contracts': [
                    {
                        'id': 1234,
                        'external_id': '1234',
                        'is_prepaid': False,
                        'nds_for_receipt': 18,
                    }
                ]
            }
        },
        18
    ),
])
@pytest.mark.filldb(_fill=False)
def test_get_nds_for_receipt(park_doc, expected_nds):
    if expected_nds is None:
        with pytest.raises(park_manager.NoNdsForReceipt):
            park_manager.get_nds_for_receipt(park_doc)
    else:
        nds = park_manager.get_nds_for_receipt(park_doc)
        assert expected_nds == nds


def _make_park_doc_with_offer_contracts(currencies):
    offer_contracts = map(_make_offer_contract_from_currency, currencies)
    return {
        '_id': 'some_park_id',
        'account': {
            'offer_contracts': offer_contracts
        }
    }


@pytest.mark.parametrize('park_doc,expected_currency', [
    (_make_park_doc_with_offer_contracts(['RUB']), 'RUB'),
    (_make_park_doc_with_offer_contracts(['USD']), 'USD'),
    (_make_park_doc_with_offer_contracts(['RUB', 'RUB']), 'RUB'),
])
@pytest.mark.filldb(_fill=False)
def test_get_offer_contract_currency(park_doc, expected_currency):
    actual_currency = park_manager.get_offer_contract_currency(park_doc)
    assert actual_currency == expected_currency


@pytest.mark.parametrize('park_doc', [
    # different currencies
    _make_park_doc_with_offer_contracts(['RUB', 'USD']),
    # no currency in offer contract
    _make_park_doc_with_offer_contracts([None]),
    # no offer contracts
    _make_park_doc_with_offer_contracts([]),
])
@pytest.mark.filldb(_fill=False)
def test_get_offer_contract_currency_failure(park_doc):
    with pytest.raises(park_manager.ContractCurrencyError):
        park_manager.get_offer_contract_currency(park_doc)


@pytest.mark.parametrize('park_doc,expected_currencies', [
    (_make_park_doc_with_offer_contracts(['RUB']), ['RUB']),
    (_make_park_doc_with_offer_contracts([]), []),
    (_make_park_doc_with_contracts(
        [dict(services=[_CARD], currency='USD')]
    ), ['USD']),
])
@pytest.mark.filldb(_fill=False)
def test_get_all_contract_currencies(park_doc, expected_currencies):
    actual_currencies = park_manager.get_all_contract_currencies(park_doc)
    assert set(actual_currencies) == set(expected_currencies)


@pytest.mark.now('2015-04-06 23:59:00 +03')
@pytest.mark.parametrize('park_doc, expected', [
    (
        {
            '_id': 'park_1',
            'account': {
                'threshold': -500
            }
        },
        -520.0
    ),
    (
        {
            '_id': 'park_2',
            'account': {
                'threshold': -500
            }
        },
        -500
    ),
    (
        {
            '_id': 'park_3',
        },
        0.0
    )
])
@pytest.mark.filldb(cashless_payments_stats='dthreshold')
@pytest.inline_callbacks
def test_dynamic_thresholds(patch, park_doc, expected):
    id = park_doc['_id']
    dyn_threshold = yield park_manager.get_dynamic_thresholds(
        [park_doc],
        {id: datetime.datetime.utcnow()},
        {}
    )
    eps = 1e-5
    dt = dyn_threshold[id]
    assert (dt > expected - eps) and (dt < expected + eps)
    assert dyn_threshold[id] <= park_doc.get('account', {}).get('threshold', 0)


@pytest.inline_callbacks
def test_dynamic_thresholds_empty_payment(patch):
    @patch('taxi.internal.payments_stats.aggregate_payments')
    def ap_mocked(clids_with_lower_boundary, log_extra=None):
        return {}

    park_doc = {
        '_id': 'park',
    }

    dyn_threshold = yield park_manager.get_dynamic_thresholds(
        [park_doc],
        {},
        {}
    )
    assert dyn_threshold['park'] == 0.0


@pytest.mark.config(SAVE_PARK_ACCOUNT_HISTORY=True)
@pytest.mark.filldb(parks='get_contract_spendable')
@pytest.inline_callbacks
def test_update_spendable_contracts(mock, load, monkeypatch):
    @mock
    def warn_on_important_change(*args, **kwargs):
        return
    monkeypatch.setattr(
        'taxi.internal.park_manager.warn_on_important_change',
        warn_on_important_change
    )
    monkeypatch.setattr(
        'taxi.external.billing.get_client_contracts',
        _mock_get_client_contracts(mock, load)
    )
    park_0_corporate_contract = {
        u'acquiring_percent': None,
        u'begin': datetime.datetime(2014, 4, 30, 20, 0),
        u'currency': u'RUB',
        u'end': datetime.datetime(9999, 12, 31, 23, 59, 59, 999000),
        u'external_id': u'\u0420\u0410\u0421-96843',
        u'id': 436110,
        u'ind_bel_nds_percent': None,
        u'is_active': True,
        u'is_cancelled': False,
        u'is_deactivated': False,
        u'is_faxed': False,
        u'is_of_card': False,
        u'is_of_cash': False,
        u'is_of_corp': True,
        u'is_of_uber': False,
        u'is_prepaid': False,
        u'is_signed': True,
        u'is_suspended': False,
        u'link_contract_id': None,
        u'nds_for_receipt': None,
        u'netting': False,
        u'netting_pct': None,
        u'offer_accepted': False,
        u'person_id': u'6088333',
        u'rebate_percent': None,
        u'services': [135],
        u'type': 81,
        u'vat': 0
    }
    park_0_offer_contract = {
        u'acquiring_percent': None,
        u'begin': datetime.datetime(2014, 4, 30, 20, 0),
        u'currency': u'RUB',
        u'end': datetime.datetime(9999, 12, 31, 23, 59, 59, 999000),
        u'external_id': u'O\u0424-113854/18',
        u'id': 436111,
        u'ind_bel_nds_percent': None,
        u'is_active': True,
        u'is_cancelled': False,
        u'is_deactivated': False,
        u'is_faxed': False,
        u'is_of_card': False,
        u'is_of_cash': False,
        u'is_of_corp': False,
        u'is_of_uber': False,
        u'is_prepaid': False,
        u'is_signed': True,
        u'is_suspended': False,
        u'link_contract_id': 436109,
        u'nds_for_receipt': None,
        u'netting': False,
        u'netting_pct': None,
        u'offer_accepted': False,
        u'person_id': u'6088333',
        u'rebate_percent': None,
        u'services': [137],
        u'type': 87,
        u'vat': 0
    }
    expected_spendable_contracts = {
        'park_0': {
            'corporate_contracts': [park_0_corporate_contract],
            'offer_contracts': [],
            'history': {
                'spendable_contracts': [
                    park_0_corporate_contract,
                    park_0_offer_contract,
                ]
            },
            'requirements': {'corp': False}
        },
        'park_1': {
            'corporate_contracts': [{
                u'acquiring_percent': None,
                u'begin': datetime.datetime(2014, 4, 30, 20, 0),
                u'currency': u'RUB',
                u'end': datetime.datetime(9999, 12, 31, 23, 59, 59, 999000),
                u'external_id': u'\u0420\u0410\u0421-96843',
                u'id': 436110,
                u'ind_bel_nds_percent': None,
                u'is_active': True,
                u'is_cancelled': False,
                u'is_deactivated': False,
                u'is_faxed': False,
                u'is_of_card': False,
                u'is_of_cash': False,
                u'is_of_corp': True,
                u'is_of_uber': False,
                u'is_prepaid': False,
                u'is_signed': True,
                u'is_suspended': False,
                u'link_contract_id': None,
                u'nds_for_receipt': None,
                u'netting': False,
                u'netting_pct': None,
                u'offer_accepted': False,
                u'person_id': u'6088333',
                u'rebate_percent': None,
                u'services': [135],
                u'type': 81,
                u'vat': 0
            }],
            'offer_contracts': [],
            'requirements': {'corp': False}
        },
        'park_2': {
            'corporate_contracts': [{
                u'acquiring_percent': None,
                u'begin': datetime.datetime(2014, 4, 30, 20, 0),
                u'currency': u'RUB',
                u'end': datetime.datetime(9999, 12, 31, 23, 59, 59, 999000),
                u'external_id': u'\u0420\u0410\u0421-96843',
                u'id': 436110,
                u'ind_bel_nds_percent': None,
                u'is_active': True,
                u'is_cancelled': False,
                u'is_deactivated': False,
                u'is_faxed': False,
                u'is_of_card': False,
                u'is_of_cash': False,
                u'is_of_corp': True,
                u'is_of_uber': False,
                u'is_prepaid': False,
                u'is_signed': True,
                u'is_suspended': False,
                u'link_contract_id': None,
                u'nds_for_receipt': None,
                u'netting': False,
                u'netting_pct': None,
                u'offer_accepted': False,
                u'person_id': u'6088333',
                u'rebate_percent': None,
                u'services': [135],
                u'type': 81,
                u'vat': 0
            }],
            'offer_contracts': [],
            'requirements': {'corp': False}
        },
        'park_3': {
            'corporate_contracts': [],
            'offer_contracts': [],
            'requirements': {'corp': False}
        },
        'park_4': {
            'corporate_contracts': [{
                u'acquiring_percent': None,
                u'begin': datetime.datetime(2014, 4, 30, 20, 0),
                u'currency': u'RUB',
                u'end': datetime.datetime(9999, 12, 31, 23, 59, 59, 999000),
                u'external_id': u'\u0420\u0410\u0421-96843',
                u'id': 436110,
                u'ind_bel_nds_percent': None,
                u'is_active': True,
                u'is_cancelled': False,
                u'is_deactivated': False,
                u'is_faxed': False,
                u'is_of_card': False,
                u'is_of_cash': False,
                u'is_of_corp': True,
                u'is_of_uber': False,
                u'is_prepaid': False,
                u'is_signed': True,
                u'is_suspended': False,
                u'link_contract_id': None,
                u'nds_for_receipt': None,
                u'netting': False,
                u'netting_pct': None,
                u'offer_accepted': False,
                u'person_id': u'6088333',
                u'rebate_percent': None,
                u'services': [135],
                u'type': 81,
                u'vat': 0
            }],
            'offer_contracts': [{
                u'currency': u'RUB',
                u'external_id': u'O\u0424-113854/18',
                u'id': 436111,
                u'link_contract_id': 123404,
                u'offer_accepted': False
            }],
            'requirements': {'corp': False}
        },
        'park_5': {
            'corporate_contracts': [{
                u'acquiring_percent': None,
                u'begin': datetime.datetime(2014, 4, 30, 20, 0),
                u'currency': u'RUB',
                u'end': datetime.datetime(9999, 12, 31, 23, 59, 59, 999000),
                u'external_id': u'\u0420\u0410\u0421-96843',
                u'id': 436110,
                u'ind_bel_nds_percent': None,
                u'is_active': True,
                u'is_cancelled': False,
                u'is_deactivated': False,
                u'is_faxed': False,
                u'is_of_card': False,
                u'is_of_cash': False,
                u'is_of_corp': True,
                u'is_of_uber': False,
                u'is_prepaid': False,
                u'is_signed': True,
                u'is_suspended': False,
                u'link_contract_id': None,
                u'nds_for_receipt': None,
                u'netting': False,
                u'netting_pct': None,
                u'offer_accepted': False,
                u'person_id': u'6088333',
                u'rebate_percent': None,
                u'services': [135],
                u'type': 81,
                u'vat': 0
            }],
            'offer_contracts': [{
                u'currency': u'RUB',
                u'external_id': u'O\u0424-113854/18',
                u'id': 436111,
                u'link_contract_id': 123405,
                u'offer_accepted': False
            }],
            'requirements': {'corp': True}
        },
        'park_6': {
            'corporate_contracts': [{
                u'acquiring_percent': None,
                u'begin': datetime.datetime(2014, 4, 30, 20, 0),
                u'currency': u'RUB',
                u'end': datetime.datetime(9999, 12, 31, 23, 59, 59, 999000),
                u'external_id': u'\u0420\u0410\u0421-96843',
                u'id': 436110,
                u'ind_bel_nds_percent': None,
                u'is_active': True,
                u'is_cancelled': False,
                u'is_deactivated': False,
                u'is_faxed': False,
                u'is_of_card': False,
                u'is_of_cash': False,
                u'is_of_corp': True,
                u'is_of_uber': False,
                u'is_prepaid': False,
                u'is_signed': True,
                u'is_suspended': False,
                u'link_contract_id': None,
                u'nds_for_receipt': None,
                u'netting': False,
                u'netting_pct': None,
                u'offer_accepted': False,
                u'person_id': u'6088333',
                u'rebate_percent': None,
                u'services': [135],
                u'type': 81,
                u'vat': 0
            }],
            'offer_contracts': [],
            'requirements': {'corp': False}
        },
        'park_7': {
            'corporate_contracts': [{
                u'acquiring_percent': None,
                u'begin': datetime.datetime(2014, 4, 30, 20, 0),
                u'currency': u'RUB',
                u'end': datetime.datetime(9999, 12, 31, 23, 59, 59, 999000),
                u'external_id': u'\u0420\u0410\u0421-96843',
                u'id': 436110,
                u'ind_bel_nds_percent': None,
                u'is_active': True,
                u'is_cancelled': False,
                u'is_deactivated': False,
                u'is_faxed': False,
                u'is_of_card': False,
                u'is_of_cash': False,
                u'is_of_corp': True,
                u'is_of_uber': False,
                u'is_prepaid': False,
                u'is_signed': True,
                u'is_suspended': False,
                u'link_contract_id': None,
                u'nds_for_receipt': None,
                u'netting': False,
                u'netting_pct': None,
                u'offer_accepted': False,
                u'person_id': u'6088333',
                u'rebate_percent': None,
                u'services': [135],
                u'type': 81,
                u'vat': 0
            }],
            'offer_contracts': [{
                u'currency': u'RUB',
                u'external_id': u'O\u0424-113854/18',
                u'id': 436111,
                u'link_contract_id': 123407,
                u'offer_accepted': False
            }],
            'requirements': {'corp': False}
        },
        'park_8': {
            'corporate_contracts': [{
                u'acquiring_percent': None,
                u'begin': datetime.datetime(2014, 4, 30, 20, 0),
                u'currency': u'RUB',
                u'end': datetime.datetime(9999, 12, 31, 23, 59, 59, 999000),
                u'external_id': u'\u0420\u0410\u0421-96843',
                u'id': 436110,
                u'ind_bel_nds_percent': None,
                u'is_active': True,
                u'is_cancelled': False,
                u'is_deactivated': False,
                u'is_faxed': False,
                u'is_of_card': False,
                u'is_of_cash': False,
                u'is_of_corp': True,
                u'is_of_uber': False,
                u'is_prepaid': False,
                u'is_signed': True,
                u'is_suspended': False,
                u'link_contract_id': None,
                u'nds_for_receipt': None,
                u'netting': False,
                u'netting_pct': None,
                u'offer_accepted': False,
                u'person_id': u'6088333',
                u'rebate_percent': None,
                u'services': [135],
                u'type': 81,
                u'vat': 0
            }],
            'offer_contracts': [{
                u'currency': u'RUB',
                u'external_id': u'O\u0424-113854/18',
                u'id': 436111,
                u'link_contract_id': 123408,
                u'offer_accepted': False
            }],
            'requirements': {'corp': True}
        },
    }
    parks = yield db.parks.find({
        '_id': {
            '$in': expected_spendable_contracts.keys()
        }
    }).run()
    for park in parks:
        yield park_manager.update_spendable_contracts(park)
    parks = yield db.parks.find({
        '_id': {
            '$in': expected_spendable_contracts.keys()
        }
    }).run()
    for park in parks:
        for key, value in expected_spendable_contracts[park['_id']].items():
            assert value == (
                park['account'][key] if _is_account_key(key) else park[key]
            ), '{}, {}, {}'.format(park['_id'], key, pprint.pprint(park))


def _is_account_key(key):
    return ('_contract' in key) or (key == 'history')


@pytest.mark.parametrize('park_id,date,expected_vats', [
    (
        'moscow_park',
        datetime.datetime(2018, 12, 30, 21),
        [
            [datetime.datetime(2016, 1, 1, 21, 0), None, 11800]
        ]
    ),
    (
        'moscow_park',
        datetime.datetime(2018, 12, 31, 21),
        [
            [
                datetime.datetime(2016, 1, 1, 21, 0),
                datetime.datetime(2018, 12, 31, 21, 0),
                11800
            ],
            [datetime.datetime(2018, 12, 31, 21, 0), None, 12000]
        ]
    ),
])
@pytest.mark.filldb(parks='update_corp_vat')
@pytest.inline_callbacks
def test_update_corp_vat(park_id, date, expected_vats, mock, load, monkeypatch):
    mgcc = _mock_get_client_contracts(mock, load)
    monkeypatch.setattr(
        'taxi.external.billing.get_client_contracts', mgcc
    )

    park_doc = yield db.parks.find_one({'_id': park_id})
    yield park_manager.update_corp_vat(park_doc, date)

    park_doc = yield db.parks.find_one({'_id': park_id})
    assert park_doc['corp_vats'] == expected_vats


@pytest.mark.parametrize(
    'billing_object, replica_object, expected', [
        (
            # Sanity check
            {
                'Balance': '150',
                'BonusLeft': '0',
                'ClientID': 39195349,
                'ContractID': 328369,
                'CurrMonthBonus': '0',
                'CurrMonthCharge': 0,
                'Currency': 'RUB',
                'DT': '2019-05-30T18:14:08.315747',
                'NettingLastDt': '2019-05-30T00:00:00',
                'OfferAccepted': 1,
                'PersonalAccountExternalID': 'ЛСТ-615450947-1',
                'SubscriptionBalance': 0,
                'SubscriptionRate': '0',
            },
            {
                'Balance': '150',
                'BonusLeft': '0',
                'ClientID': 39195349,
                'ContractID': 328369,
                'CurrMonthBonus': '0',
                'CurrMonthCharge': 0,
                'Currency': 'RUB',
                'DT': '2019-05-30T18:14:08.315747',
                'NettingLastDt': '2019-05-30T00:00:00',
                'OfferAccepted': 1,
                'PersonalAccountExternalID': 'ЛСТ-615450947-1',
                'SubscriptionBalance': 0,
                'SubscriptionRate': '0',
            },
            []
        ),
        (
            # None values missing from billing response aren't diffs,
            # as well as keys straight up missing from the
            # replication response (billing can return extra data as much
            # as it wants)
            {
                'a': 1,
                'b': {'x': 1, 'y': 'z'},
                'd': [1, 2, 3]
            },
            {
                'a': 1,
                'b': {'x': 1, 'y': 'z'},
                'c': None
            },
            []
        ),
        (
            # Non-null missing values ARE
            {
                'Key': 'value',
                'TYPE': 1,
                'InnerArray': ['a', 'b', 'c']
            },
            {
                'key': 'value',
                'TYPE': 1,
                'InnerArray': ['a', 'b', 'c']
            },
            [
                park_manager.BillingReplicaDiff(
                    field='key', billing=None, replica='value'
                )
            ]
        ),
        (
            # Different values in internal collections;
            # Billing data doesn't go deeper that 1 level, so it's OK to
            # test only that. The same logic as with missing upper-level keys
            # doesn't apply, since it would be too bothersome for what it's
            # worth
            {
                'Key': 'value',
                'TYPE': 1,
                'InnerArray': ['a', 'b'],
                'inner_dict': {'a': 1, 'b': 'xyz'}
            },
            {
                'Key': 'value',
                'TYPE': 1,
                'InnerArray': ['a', 'c'],
                'inner_dict': {'a': 1, 'c': 123}
            },
            [
                park_manager.BillingReplicaDiff(
                    field='InnerArray', billing=['a', 'b'], replica=['a', 'c']
                ),
                park_manager.BillingReplicaDiff(
                    field='inner_dict',
                    billing={'a': 1, 'b': 'xyz'},
                    replica={'a': 1, 'c': 123}
                )
            ]
        ),
        (
            # Datetime values from billing can be returned as DateTime,
            # regular datetime in replica responses aren't diffs
            {
                'datetime': xmlrpclib.DateTime('20180830T00:00:00')
            },
            {
                'datetime': datetime.datetime(2018, 8, 30, 0, 0, 0)
            },
            []
        ),
        (
            # Real life case for persons
            {
                'ACCOUNT': '40802810903000074366',
                'OGRN': '318169000179898',
                'STREET': 'Гудованцева',
                'POSTCODE': '420091',
                'CLIENT_ID': '49355029',
                'DT': '2018-12-12 18:12:39',
                'EMAIL': 'test@yandex.ru',
                'SIGNER_PERSON_NAME': 'Шаров Евгений Васильевич',
                'BIK': '042202803',
                'PHONE': '+71111111111',
                'SIGNER_PERSON_GENDER': 'M',
                'LONGNAME': (
                        'Индивидуальный предприниматель '
                        'Шаров Евгений Васильевич'
                ),
                'POSTSUFFIX': '43,корп 1, кв 137',
                'AUTHORITY_DOC_DETAILS': (
                        'Записи о регистрации в ЕГРИП № 318169000179898 от '
                        '03.10.2018 г.'
                ),
                'REPRESENTATIVE': 'Шаров Евгений Васильевич',
                'LIVE_SIGNATURE': '1',
                'ID': '6392592',
                'CITY': 'г Казань',
                'SIGNER_POSITION_NAME': 'Индивидуальный Предприниматель',
                'NAME': 'ИП Шаров Е.В.',
                'INN': '111111111111',
                'FIAS_GUID': '93b3df57-4c89-44df-ac42-96f05e9cd3b9',
                'LEGALADDRESS': '420091,Казань,Гудованцева,43,корп 1, кв 137',
                'TYPE': 'ur'
            },
            {
                'ACCOUNT': '40802810903000074366',
                'OGRN': '318169000179898',
                'STREET': 'Гудованцева',
                'POSTCODE': '12345',
                'CLIENT_ID': '49355029',
                'DT': '2018-12-12 18:12:39',
                'EMAIL': 'test@yandex.ru',
                'SIGNER_PERSON_NAME': 'Шаров Евгений Васильевич',
                'BIK': '042202803',
                'PHONE': '+71111111111',
                'SIGNER_PERSON_GENDER': 'NB',
                'LONGNAME': (
                        'Индивидуальный предприниматель '
                        'Шаров Евгений Васильевич'
                ),
                'POSTSUFFIX': '43,корп 1, кв 137',
                'AUTHORITY_DOC_DETAILS': (
                        'Записи о регистрации в ЕГРИП № 318169000179898 от '
                        '03.10.2018 г.'
                ),
                'REPRESENTATIVE': 'Шаров Евгений Васильевич',
                'LIVE_SIGNATURE': '1',
                'ID': '6392592',
                'CITY': 'г Казань',
                'SIGNER_POSITION_NAME': 'Индивидуальный Предприниматель',
                'NAME': 'ИП Шаров Е.В.',
                'INN': '111111111111',
                'FIAS_GUID': '93b3df57-4c89-44df-ac42-96f05e9cd3b9',
                'LEGALADDRESS': '420091,Казань,Гудованцева,43,корп 1, кв 137',
                'TYPE': 'ur'
            },
            [
                park_manager.BillingReplicaDiff(
                    field='SIGNER_PERSON_GENDER', billing='M', replica='NB'
                ),
                park_manager.BillingReplicaDiff(
                    field='POSTCODE', billing='420091', replica='12345'
                ),
            ]
        ),
        (
            # Real life case for contracts
            {
                'CONTRACT_TYPE': 9,
                'COUNTRY': 225,
                'CURRENCY': 'RUR',
                'DT': xmlrpclib.DateTime('20190402T00:00:00'),
                'EXTERNAL_ID': '216421/19',
                'FINISH_DT': xmlrpclib.DateTime('20190511T00:00:00'),
                'ID': 703271,
                'IS_ACTIVE': 1,
                'IS_CANCELLED': 0,
                'IS_DEACTIVATED': 0,
                'IS_FAXED': 0,
                'IS_SIGNED': 1,
                'IS_SUSPENDED': 0,
                'MANAGER_CODE': 33108,
                'NDS_FOR_RECEIPT': -1,
                'NETTING': 1,
                'NETTING_PCT': '100',
                'OFFER_ACCEPTED': 1,
                'PAYMENT_TYPE': 2,
                'PERSON_ID': 7352733,
                'SERVICES': [128, 124, 125, 605, 111]
            },
            {
                'CONTRACT_TYPE': 9,
                'CURRENCY': 'RUR',
                'DT': datetime.datetime(2019, 4, 2, 0, 0, 0),
                'END_DT': None,
                'EXTERNAL_ID': '216421/19',
                'FINISH_DT': None,
                'ID': 703271,
                'IND_BEL_NDS': None,
                'IND_BEL_NDS_PERCENT': None,
                'IS_ACTIVE': 0,
                'IS_SIGNED': 1,
                'IS_SUSPENDED': 1,
                'LINK_CONTRACT_ID': None,
                'NDS': None,
                'NDS_FOR_RECEIPT': -1,
                'NETTING': 1,
                'NETTING_PCT': '100',
                'OFFER_ACCEPTED': 0,
                'PARTNER_COMMISSION_PCT': None,
                'PARTNER_COMMISSION_PCT2': None,
                'PAYMENT_TYPE': 2,
                'PERSON_ID': 7352733,
                'SERVICES': [128, 124, 605, 111]
            },
            [
                park_manager.BillingReplicaDiff(
                    field='SERVICES',
                    billing=[128, 124, 125, 605, 111],
                    replica=[128, 124, 605, 111],
                ),
                park_manager.BillingReplicaDiff(
                    field='FINISH_DT',
                    billing=xmlrpclib.DateTime('20190511T00:00:00'),
                    replica=None
                ),
                park_manager.BillingReplicaDiff(
                    field='IS_ACTIVE',
                    billing=1,
                    replica=0,
                ),
                park_manager.BillingReplicaDiff(
                    field='OFFER_ACCEPTED',
                    billing=1,
                    replica=0,
                ),
                # park_manager.BillingReplicaDiff(
                #     field='IS_ACTIVE',
                #     billing=1,
                #     replica=0,
                # ),
                park_manager.BillingReplicaDiff(
                    field='IS_SUSPENDED',
                    billing=0,
                    replica=1,
                ),
            ]
        ),
        (
            # Real life case for balances
            {
                'Balance': '0',
                'BonusLeft': '0',
                'ClientID': 107491999,
                'ContractID': 968323,
                'CurrMonthBonus': '0',
                'CurrMonthCharge': 0,
                'Currency': 'USD',
                'DT': '2019-05-30T16:06:09.446130',
                'NettingLastDt': '2019-10-21T15:00:01',
                'PersonalAccountExternalID': 'PAT-1721998525-1',
                'SubscriptionBalance': 0,
                'SubscriptionRate': 0
            },
            {
                'Balance': '0',
                'BonusLeft': '0',
                'ClientID': 107491999,
                'ContractID': 968323,
                'CurrMonthBonus': '0',
                'CurrMonthCharge': '7635.7',
                'Currency': 'USD',
                'DT': '2019-05-29T10:00:01.223436',
                'NettingLastDt': None,
                'PersonalAccountExternalID': 'PAT-1721998525-1',
                'SubscriptionBalance': 0,
                'SubscriptionRate': 0
            },
            [
                park_manager.BillingReplicaDiff(
                    field='CurrMonthCharge',
                    billing=0,
                    replica='7635.7',
                ),
                park_manager.BillingReplicaDiff(
                    field='NettingLastDt',
                    billing='2019-10-21T15:00:01',
                    replica=None,
                ),
                park_manager.BillingReplicaDiff(
                    field='DT',
                    billing='2019-05-30T16:06:09.446130',
                    replica='2019-05-29T10:00:01.223436',
                )
            ]
        ),
    ]
)
@pytest.mark.asyncenv('blocking')
def test_get_billing_and_replica_object_diffs(
        billing_object, replica_object, expected
):
    field_diffs = park_manager.get_billing_and_replica_object_diffs(
        billing_object, replica_object
    )

    assert sorted(field_diffs) == sorted(expected)


@pytest.mark.parametrize(
    'data_json, expected_trust_status', [
        ('test_get_trust_status/no_park.json', 'no_park'),
        ('test_get_trust_status/no_city.json', 'no_city'),
        (
            'test_get_trust_status/no_automate_payments.json',
            'init',
        ),
        (
            'test_get_trust_status/no_country_automation.json',
            'no_offer_by_country_confirmed_date',
        ),
        (
            'test_get_trust_status/no_offer_contract.json',
            'no_offer_contract',
        ),
        (
            'test_get_trust_status/has_offer_contract.json',
            'init',
        ),
    ]
)
@pytest.inline_callbacks
def test_get_trust_status(load, data_json, expected_trust_status):
    data = json_util.loads(load(data_json))
    trust_status = yield park_manager.get_trust_status(
        maybe_convert(data['park'], dbh.parks.Doc),
        maybe_convert(data['city'], dbh.cities.Doc),
        data['stamp'].replace(tzinfo=None))
    assert trust_status == expected_trust_status


def maybe_convert(data, converter):
    if data is None:
        return data
    return converter(data)
