# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

import pytest

from taxi.core import async
from taxi.internal import car_manager
from taxi.internal import dbh


@pytest.mark.filldb(_fill=False)
def test_name_matcher():
    matcher = car_manager._NameMatcher('Mersedes Benz')
    assert matcher.matches('Mersedes Benz')
    assert matcher.matches('mersedes BENZ')
    assert not matcher.matches('Mersedes Benz S-class')

    matcher = car_manager._NameMatcher('mersedes benz *')
    # Space after Benz is required
    assert not matcher.matches('Mersedes Benz')
    assert matcher.matches('MerSedeS benz ')
    assert matcher.matches('Mersedes Benz S-class AMG 600')
    # Prefix if prohibited
    assert not matcher.matches('My Mersedes Benz S-class')

    assert 'mersedes benz *' == unicode(matcher)


@pytest.mark.filldb(_fill=False)
def test_add_by_price_rule():
    rule = car_manager.CarClassifier.AddByPriceRule(350000, 5)
    assert ['add', 350000, 5] == rule.serialize()

    for current_status in (True, False):
        # Age is Ok, Price is Ok. So car becomes true always.
        car = car_manager.Car(1, 1000000, 'Honda', '')
        assert rule.process_car(car, current_status)

        # Age is Ok, price is low. So car preserves it's status.
        car = car_manager.Car(1, 150000, 'Great Wall', '')
        assert current_status == rule.process_car(car, current_status)

        # Age is high, price is Ok. So car preserves it's status.
        car = car_manager.Car(50, 50000000, 'Chevrole Elvis Edition', '')
        assert current_status == rule.process_car(car, current_status)

        # Age is high, price is low. So car preserves it's status.
        car = car_manager.Car(50, 10000, 'ZAZ', '')
        assert current_status == rule.process_car(car, current_status)


@pytest.mark.filldb(_fill=False)
def test_add_by_name():
    rule = car_manager.CarClassifier.AddByNameRule('SUBARU *', 3)
    assert ['add', 'SUBARU *', 3] == rule.serialize()

    for current_status in (True, False):
        # Age is Ok, Name matches. So car becomes true always.
        car = car_manager.Car(3, 120000, 'subaru forester', '')
        assert rule.process_car(car, current_status)

        # Age is Ok, Name does not match. So car preserves it's status.
        car = car_manager.Car(1, 120000, 'Isuzu Trooper', '')
        assert current_status == rule.process_car(car, current_status)

        # Age is high, Name matches. So car preserves it's status.
        car = car_manager.Car(4, 120000, 'Subaru Forester', '')
        assert current_status == rule.process_car(car, current_status)

        # Age is high, Name does not match. So car preserves it's status.
        car = car_manager.Car(10, 120000, 'Isuzu Trooper', '')
        assert current_status == rule.process_car(car, current_status)


@pytest.mark.filldb(_fill=False)
def test_remove_by_price():
    rule = car_manager.CarClassifier.DeleteByPriceRule(400000, 7)
    assert ['delete', 400000, 7] == rule.serialize()

    for current_status in (True, False):
        # Age is Ok, Price is Ok. So car preserves it's status.
        car = car_manager.Car(1, 1000000, 'Honda', '')
        assert current_status == rule.process_car(car, current_status)

        # Age is Ok, price is low. So car will be removed.
        car = car_manager.Car(1, 150000, 'Great Wall', '')
        assert not rule.process_car(car, current_status)

        # Age is high, price is Ok. So car will be removed.
        car = car_manager.Car(50, 50000000, 'Chevrolet Elvis Edition', '')
        assert not rule.process_car(car, current_status)

        # Age is high, price is low. So car will be removed.
        car = car_manager.Car(50, 10000, 'ZAZ', '')
        assert not rule.process_car(car, current_status)


@pytest.mark.filldb(_fill=False)
def test_remove_by_name():
    rule = car_manager.CarClassifier.DeleteByNameRule('Honda *', 7)
    assert ['delete', 'Honda *', 7] == rule.serialize()

    for current_status in (True, False):
        # Age is low, Name matches. So car preserves it's status.
        car = car_manager.Car(3, 1000000, 'Honda CR-V', '')
        assert current_status == rule.process_car(car, current_status)

        # Age is low, Name does not match. So car preserves it's status.
        car = car_manager.Car(2, 1000000, 'Aston Martin', '')
        assert current_status == rule.process_car(car, current_status)

        # Age is high, Name matches. So car will be removed.
        car = car_manager.Car(10, 100000, 'Honda Civic', '')
        assert not rule.process_car(car, current_status)

        # Age is high, Name does not match. So car preserves it's status.
        car = car_manager.Car(20, 1000000, 'Aston Martin', '')
        assert current_status == rule.process_car(car, current_status)


@pytest.inline_callbacks
def test_classifier():
    classifier = car_manager.CarClassifier()
    yield classifier.initialize([
        ['econom', 'delete', '350000', 7],
        ['econom', 'add', '*SoLaRiS', 20],
        ['business', 'delete', '*', 0],
        ['business', 'add', 'mersedes *', 4],
        ['business', 'add', '1000000', 5],
    ], u'Москва')

    # No rule can be applied to econom. Removed from business.
    car = car_manager.Car(5, 500000, u'\u041b\u0430\u0434\u0430', '')
    classes = classifier.get_suitable_classes(car)
    assert classes == ['econom']

    # Solaris is old and cheap. But a rule should add it to econom.
    car = car_manager.Car(15, 50000, 'Hyndai Solaris', '')
    classes = classifier.get_suitable_classes(car)
    assert classes == ['econom']

    # ZAZ is old and cheap. No classes could be assigned.
    car = car_manager.Car(15, 50000, 'ZAZ', '')
    classes = classifier.get_suitable_classes(car)
    assert classes == []

    # Mersedes is quite old and will not get business.
    car = car_manager.Car(5, 800000, 'Mersedes Benz', '')
    classes = classifier.get_suitable_classes(car)
    assert classes == ['econom']

    # Mersedes is new enough. Econom and business.
    car = car_manager.Car(4, 800000, 'Mersedes Benz', '')
    classes = classifier.get_suitable_classes(car)
    assert set(classes) == set(['econom', 'business'])

    # Car is very expensive but old
    car = car_manager.Car(6, 30000000, 'Volga', '')
    classes = classifier.get_suitable_classes(car)
    assert classes == ['econom']

    # Car is expensive and new.
    car = car_manager.Car(2, 3000000, 'Rower', '')
    classes = classifier.get_suitable_classes(car)
    assert set(classes) == set(['econom', 'business'])


@pytest.mark.filldb(_fill=None)
@pytest.mark.parametrize('now,year_of_manufacture,expected_result', [
    (datetime.datetime(2015, 1, 1), 2015, 0),
    (datetime.datetime(2015, 9, 1), 2015, 0),
    (datetime.datetime(2016, 1, 1), 2015, 0),
    (datetime.datetime(2016, 8, 25), 2015, 0),
    (datetime.datetime(2016, 9, 5), 2015, 1),
])
def test_get_age_by_year_of_production(now,
                                       year_of_manufacture,
                                       expected_result,
                                       sleep, mock, stub, monkeypatch):
    @mock
    def utcnow():
        return now

    monkeypatch.setattr('datetime.datetime.utcnow', utcnow)

    assert (car_manager.year_of_manufacture_to_age(year_of_manufacture) ==
            expected_result)


@pytest.mark.filldb(_fill=None)
def test_by_model_multiplication():
    raw_db_data = [
        [4, 'Nissan Teana', 'business', 40.0],
        [3, 'Nissan Teana', 'vip', 0.3],
        [1, 'Toyota *', 'econom', 5.0],
    ]
    weight_multiplier = car_manager.CarWeightMultiplier(raw_db_data)

    # Case 1:
    car = car_manager.Car(3, None, 'Nissan Teana', None)
    r = weight_multiplier.get_multipliers_for_car(car)
    assert r == {
        'business': 40.0,
        'vip': 0.3,
    }

    # Case 2:
    car = car_manager.Car(5, None, 'Nissan Teana', None)
    r = weight_multiplier.get_multipliers_for_car(car)
    assert r == {}

    # Case 3:
    car = car_manager.Car(0, None, 'Toyota Rav 4', None)
    r = weight_multiplier.get_multipliers_for_car(car)
    assert r == {
        'econom': 5.0,
    }

    # Case 4:
    raw_db_data = []
    weight_multiplier = car_manager.CarWeightMultiplier(raw_db_data)
    car = car_manager.Car(3, None, 'Nissan Teana', None)
    r = weight_multiplier.get_multipliers_for_car(car)
    assert r == {}


@pytest.inline_callbacks
@pytest.mark.filldb(_specified=True, auto_dictionary='',
                    auto_dictionary_special='',
                    classification_rules='')
def test_classifier_rules_wildcard_expansion():
    yield car_manager.expand_classifiers_wildcard(False)
    classifiers = yield dbh.classification_rules.Doc.find_many()
    assert len(classifiers) == 3
    for classifier in classifiers:
        classifier_name = classifier['_id']
        # assert dbh.classification_rules.Doc.updated in classifier
        assert dbh.classification_rules.Doc.extended_rules_updated in classifier
        if classifier_name == 'Новороссийск':
            assert classifier['rules'] == [
                {
                    'price': 0,
                    'age': 99,
                    'class': 'econom',
                    'allowing': True
                },
                {
                    'price': 10000000,
                    'age': 0,
                    'class': 'minivan',
                    'allowing': False
                },
                {
                    'model': 'Mercedes-Benz C-klasse*',
                    'age': 7,
                    'class': 'minivan',
                    'allowing': True
                }
            ]
            assert len(classifier['extended_rules']) == 4
            assert classifier['extended_rules'][:2] == [
                {
                    'price': 0,
                    'age': 99,
                    'class': 'econom',
                    'allowing': True
                },
                {
                    'price': 10000000,
                    'age': 0,
                    'class': 'minivan',
                    'allowing': False
                }
            ]
            expected_extension = [
                {
                    'model': 'Mercedes-Benz C-klasse',
                    'age': 7,
                    'class': 'minivan',
                    'allowing': True
                },
                {
                    'model': 'Mercedes-Benz C-klasse AMG',
                    'age': 7,
                    'class': 'minivan',
                    'allowing': True
                }
            ]
            assert ([
                classifier['extended_rules'][2],
                classifier['extended_rules'][3]
            ] == expected_extension) or ([
                classifier['extended_rules'][3],
                classifier['extended_rules'][2]
            ] == expected_extension)

        elif classifier_name == 'Москва':
            expected_extension = [
                {
                    'allowing': False,
                    'model': u'ВАЗ (Lada) Kalina',
                    'age': 7,
                    'class': 'econom'
                },
                {
                    'allowing': False,
                    'model': u'ВАЗ (Lada) X-Ray',
                    'age': 7,
                    'class': 'econom'
                },
            ]
            assert classifier['rules'] == [
                {
                    'model': '*Lada*',
                    'age': 7,
                    'class': 'econom',
                    'allowing': False
                }
            ]
            assert len(classifier['extended_rules']) == 2
            assert ([
                classifier['extended_rules'][0],
                classifier['extended_rules'][1]
            ] == expected_extension) or ([
                classifier['extended_rules'][1],
                classifier['extended_rules'][0]
            ] == expected_extension)

        elif classifier_name == 'Железнодорожный':
            expected_extension = [
                {
                    'allowing': True,
                    'model': u'Renault Logan',
                    'age': 3,
                    'class': 'vip'
                },
                {
                    'allowing': True,
                    'model': u'Renault Laguna',
                    'age': 3,
                    'class': 'vip'
                },
            ]
            assert classifier['rules'] == [
              {
                'model': 'renAULt*l*',
                'age': 3,
                'class': 'vip',
                'allowing': True
              }
            ]
            assert len(classifier['extended_rules']) == 2
            assert ([
                classifier['extended_rules'][0],
                classifier['extended_rules'][1]
            ] == expected_extension) or ([
                classifier['extended_rules'][1],
                classifier['extended_rules'][0]
            ] == expected_extension)


@pytest.mark.filldb(_fill=False)
def test_should_extend_classifier_no_updated():
    classifier = dbh.classification_rules.Doc()
    classifier.rules = [{'class': 'econom', 'allowing': True, 'price': 100}]
    assert car_manager._classifier_rule_is_outdated(classifier, False) is True
    assert car_manager._classifier_rule_is_outdated(classifier, True) is True


@pytest.mark.filldb(_fill=False)
def test_should_extend_classifier_no_extended_rules_updated():
    classifier = dbh.classification_rules.Doc()
    classifier.rules = [{'class': 'econom', 'allowing': True, 'price': 100}]
    classifier.rules_updated = datetime.datetime.utcnow()
    assert car_manager._classifier_rule_is_outdated(classifier, False) is True
    assert car_manager._classifier_rule_is_outdated(classifier, True) is True


@pytest.mark.filldb(_fill=False)
def test_should_extend_classifier_is_older():
    classifier = dbh.classification_rules.Doc()
    classifier.rules = [{'class': 'econom', 'allowing': True, 'price': 100}]
    classifier.rules_updated = datetime.datetime.utcnow()
    classifier.extended_rules_updated = (
        classifier.rules_updated - datetime.timedelta(minutes=1)
    )
    assert car_manager._classifier_rule_is_outdated(classifier, False) is True
    assert car_manager._classifier_rule_is_outdated(classifier, True) is True


@pytest.mark.filldb(_fill=False)
def test_should_extend_classifier_no():
    classifier = dbh.classification_rules.Doc()
    classifier.rules = [{'class': 'econom', 'allowing': True, 'price': 100}]
    classifier.rules_updated = datetime.datetime.utcnow()
    classifier.extended_rules_updated = classifier.rules_updated
    assert car_manager._classifier_rule_is_outdated(classifier, False) is False
    assert car_manager._classifier_rule_is_outdated(classifier, True) is True


@pytest.mark.filldb(_fill=False)
def test_should_run_rule_extension_empty_classifiers():
    assert not car_manager._classifier_rules_extension_should_run([], False)
    assert not car_manager._classifier_rules_extension_should_run([], True)


@pytest.mark.filldb(_fill=False)
def test_should_run_rule_extension_check_force(patch):
    @patch('taxi.internal.car_manager._classifier_rule_is_outdated')
    def rule_is_outdated(rules, force):
        return False

    assert not car_manager._classifier_rules_extension_should_run(
        [0, 1, 2, 3, 4], False)


@pytest.mark.filldb(_fill=False)
def test_should_run_rule_extension_check_natural(patch):
    scope = [0]

    @patch('taxi.internal.car_manager._classifier_rule_is_outdated')
    def rule_is_outdated(rules, force):
        scope[0] += 1
        return scope[0] == 2

    assert car_manager._classifier_rules_extension_should_run(
        [0, 1, 2, 3, 4], False)


@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_models_are_not_fetched_from_db_until_required(patch):
    @patch('taxi.internal.dbh.classification_rules.Doc.find_many')
    @async.inline_callbacks
    def find_classifiers(fields=None, secondary=None):
        yield
        first_classifier = dbh.classification_rules.Doc()
        first_classifier.rules = [{'class': 'econom', 'allowing': True,
                                   'price': 100}]
        first_classifier.rules_updated = datetime.datetime.utcnow()
        first_classifier.extended_rules_updated = \
            first_classifier.rules_updated

        second_classifier = dbh.classification_rules.Doc()
        second_classifier.rules = [{'class': 'econom', 'allowing': True,
                                    'price': 100}]
        second_classifier.rules_updated = datetime.datetime.utcnow()
        second_classifier.extended_rules_updated = \
            second_classifier.rules_updated
        async.return_value([first_classifier, second_classifier])

    @patch('taxi.internal.car_manager.collect_model_names')
    @async.return_value
    def collect_model_names():
        yield
        assert False, 'This should not be called'

    @patch('taxi.internal.dbh.classification_rules.Doc._update')
    @async.inline_callbacks
    def update(what, how):
        yield
        assert False, 'This should not be called'

    yield car_manager.expand_classifiers_wildcard()


@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_only_outdated_rules_are_updated(patch):
    @patch('taxi.internal.dbh.classification_rules.Doc.find_many')
    @async.inline_callbacks
    def find_classifiers(fields=None, secondary=None):
        yield
        first_classifier = dbh.classification_rules.Doc()
        first_classifier._id = 'outdated'
        first_classifier.rules = [{'class': 'econom', 'allowing': True,
                                   'price': 100}]
        first_classifier.rules_updated = datetime.datetime.utcnow()
        first_classifier.extended_rules_updated = datetime.datetime.min

        second_classifier = dbh.classification_rules.Doc()
        second_classifier._id = 'actual'
        second_classifier.rules = [{'class': 'econom', 'allowing': True,
                                    'price': 100}]
        second_classifier.rules_updated = datetime.datetime.utcnow()
        second_classifier.extended_rules_updated = \
            second_classifier.rules_updated
        async.return_value([first_classifier, second_classifier])

    @patch('taxi.internal.car_manager.collect_model_names')
    @async.return_value
    def collect_model_names():
        yield
        async.return_value({'Model 1', 'Model 2'})

    @patch('taxi.internal.dbh.classification_rules.Doc._update')
    @async.inline_callbacks
    def update(what, how):
        yield
        assert {'_id': 'actual'} == what

    yield car_manager.expand_classifiers_wildcard()
