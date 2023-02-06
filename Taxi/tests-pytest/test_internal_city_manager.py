# -*- coding: utf-8 -*-

import copy
import datetime

import pytest

from taxi.core import db
from taxi.internal import city_manager


@pytest.mark.filldb()
@pytest.inline_callbacks
def test_get_rules_for_city_with_rules():
    city_doc = yield db.cities.find_one(
        {'_id': u'\u041a\u0435\u043c\u0435\u0440\u043e\u0432\u043e'},
        ['classification_rules']
    )
    rules = yield city_manager.get_car_classification_rules(city_doc)
    assert rules._rules.keys() == ['econom']


@pytest.mark.filldb()
@pytest.inline_callbacks
def test_get_rules_for_city_without_rules():
    city_doc = yield db.cities.find_one(
        {'_id': u'\u0422\u043e\u043c\u0441\u043a'},
        ['classification_rules']
    )
    rules = yield city_manager.get_car_classification_rules(city_doc)
    assert rules._rules.keys() == ['business']


@pytest.mark.filldb(cities='get_doc')
@pytest.inline_callbacks
def test_get_all_docs():
    # Check function works
    docs = yield city_manager.get_all_docs()
    assert len(docs) == 2


@pytest.mark.filldb(cities='get_doc')
@pytest.inline_callbacks
def test_get_doc():
    # Check function works (call it few times to be sure)
    for i in range(3):
        for city_id in ['moscow', 'spb']:
            doc = yield city_manager.get_doc(city_id)
            assert doc['_id'] == city_id
            assert doc['eng'] == city_id


@pytest.mark.filldb(cities='get_doc')
@pytest.inline_callbacks
def test_get_doc_not_found():
    with pytest.raises(city_manager.NotFoundError) as excinfo:
        yield city_manager.get_doc('unknown')
    assert 'city \'unknown\' not found' in excinfo.value


@pytest.mark.filldb(cities='service_levels')
@pytest.inline_callbacks
def test_get_service_levels():
    obj = yield city_manager.get_service_levels('moscow')
    assert obj == {0: 'params0', 1: 'params1'}
    obj = yield city_manager.get_service_levels('spb')
    assert obj == {0: 'params0', 1: 'params1'}


@pytest.inline_callbacks
def test_get_city_ids():
    ids = yield city_manager.get_city_ids()
    assert {u'Томск', u'Кемерово'} == set(ids)


_NOW = datetime.datetime(2016, 3, 7)


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('city_doc,contract_type,end,expected_city_doc', [
    # active cash contract - we change its end
    ({
        'commission_contracts': {
            'cash': [
                {
                    'begin': datetime.datetime(2016, 1, 1),
                    'end': datetime.datetime(2016, 2, 1),
                },
                {
                    'begin': datetime.datetime(2016, 2, 1),
                    'end': datetime.datetime(2016, 12, 31),
                }
            ]
        }
     },
     'cash', datetime.datetime(2016, 3, 9),
     {
         'commission_contracts': {
             'cash': [
                 {
                     'begin': datetime.datetime(2016, 1, 1),
                     'end': datetime.datetime(2016, 2, 1),
                 },
                 {
                     'begin': datetime.datetime(2016, 2, 1),
                     'end': datetime.datetime(2016, 3, 9),
                 }
             ]
         }
     }),

    # no commission contracts - we do nothing
    ({},
     'cash', datetime.datetime(2016, 3, 9),
     None),

    # no cash commission contract - we do nothing
    ({
         'commission_contracts': {
            'card': [{}]
        }
     }, 'cash', datetime.datetime(2016, 3, 9),
     None),

    # no active cash commission contract - we do nothing
    ({
        'commission_contracts': {
            # not an active contract - because end is in the past
            'cash': [
                {
                    'begin': datetime.datetime(2016, 3, 1),
                    'end': datetime.datetime(2016, 3, 6)
                }
            ]
        }
    }, 'cash', datetime.datetime(2016, 3, 7),
    None),
])
def test_set_end_of_active_commission_contract(city_doc, contract_type, end,
                                               expected_city_doc):
    city_doc = copy.deepcopy(city_doc)
    if expected_city_doc is None:
        expected_city_doc = copy.deepcopy(city_doc)
    city_manager.set_end_of_active_commission_contract(
        city_doc, contract_type, end
    )
    assert city_doc == expected_city_doc


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('city_doc,contract_type,contract_data,'
                         'expected_city_doc', [
    # have cash commission contracts - we add new
    ({
        'commission_contracts': {
            'cash': [
                {
                    'commission': 'initial value'
                }
            ]
        }
    }, 'cash', {'commission': 'new value'},
     {
         'commission_contracts': {
             'cash': [
                 {
                     'commission': 'initial value'
                 },
                 {
                     'commission': 'new value'
                 }
             ]
         }
     }),

    # no commission contracts - we add new
    ({},
     'cash', {'commission': 'new value'},
     {
         'commission_contracts': {
             'cash': [
                 {
                     'commission': 'new value',
                 }
             ]
         }
     }),

    # no cash commission contract - we add new
    ({
        'commission_contracts': {}
    }, 'cash', {'commission': 'new value'},
     {
         'commission_contracts': {
             'cash': [
                 {
                     'commission': 'new value'
                 }
             ]
         }
     }),
])
def test_add_commission_contract(city_doc, contract_type, contract_data,
                                 expected_city_doc):
    city_doc = copy.deepcopy(city_doc)
    city_manager.add_commission_contract(
        city_doc, contract_type, contract_data
    )
    assert city_doc == expected_city_doc
