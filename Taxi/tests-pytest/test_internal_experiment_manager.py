import pytest
import random

from taxi.core import db
from taxi.internal import dbh
from taxi.internal import experiment_manager
from taxi.internal.order_kit import order_helpers


@pytest.inline_callbacks
def test_getting_experiment_configurations():
    confs = yield experiment_manager.get_list_of_all_experiments(
        experiment_manager.CONFIG_SET_EXPERIMENTS
    )
    expected_confs = [
        {"name": "xy", "cities": ["Moscow"]},
        {"name": "xx", "order_id_last_digits": ["31"]},
        {"name": "zx", "user_phone_id_last_digits": ["b5", "b6"]},
        {"name": "orders_yandex", "yandex_staff": True},
    ]
    assert confs == expected_confs

    confs = yield experiment_manager.get_list_of_all_experiments(
        experiment_manager.CONFIG_SET_USER_EXPERIMENTS
    )
    expected_confs = [
        {
            "name": "user1", "user_phone_id_last_digits": ["b5", "b6"],
            "platforms": ["android"]
        },
        {"name": "staff", "yandex_staff": True},
        {"name": "all"}
    ]
    assert confs == expected_confs


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('config,expected', [
    ({}, False),
    ({'cities': ['Moscow', 'Smolensk']}, False),
    ({'cities': ['Omsk', 'Orlando']}, True),
    ({'cities': ['Omsk', 'Orlando'], 'order_id_last_digits': ['3']}, False),
    ({'cities': ['Omsk', 'Orlando'], 'order_id_last_digits': ['3', '1']}, True),
    ({'order_id_last_digits': ['3', '1']}, True),
    ({'order_id_last_digits': ['3', '9']}, False),
    ({'user_phone_id_last_digits': ['311']}, False),
    ({'user_phone_id_last_digits': ['312']}, True),
    ({'unknown_option': True}, False),
    ({'cities': ['Orlando'], 'unknown_option': True}, False),
    ({'yandex_staff': True}, True),
    ({'yandex_staff': True, 'order_id_last_digits': ['2', '4']}, True),
    ({
         'user_phone_id_last_digits': ['312'],
         'order_id_last_digits': ['2', '4']
     }, True),
])
@pytest.inline_callbacks
def test_config_interpretation(config, expected):
    order_doc = {
        '_id': 'abd2131',
        'user_phone_id': '31312',
        'city': 'Orlando',
    }
    phone_doc = {
        '_id': '31312',
        'phone': '+79213280718',
        'yandex_staff': True
    }
    application_mapping = {}
    result = yield experiment_manager._should_be_switched_on(
        order_helpers.get_proc_like_obj_for_experiments(order_doc),
        config,
        application_mapping,
        phone_doc=phone_doc,
    )
    assert result == expected


@pytest.mark.filldb()
@pytest.mark.parametrize('user_id,expected', [
    ('user1', True),
    ('user2', False),
    ('user3', False),
    ('user4', False),
    ('user5', True),
])
@pytest.inline_callbacks
def test_config_interpretation_user(user_id, expected):
    user_doc = yield db.users.find_one({'_id': user_id})
    config = {
        'name': 'user_rule',
        'user_phone_id_last_digits': ['b6'],
        'user_id_last_digits': ['1'],
        'platforms': ['android'],
    }
    application_mapping = {}
    result = yield experiment_manager._should_be_switched_on_for_user(
        user_doc, config, application_mapping
    )
    assert result is expected


@pytest.mark.filldb()
@pytest.mark.parametrize('user_id,expected', [
    ('user1', ['user1', 'staff', 'all']),
    ('user2', ['staff', 'all']),
    ('user4', ['all']),
    ('unknown', ['all'])
])
@pytest.inline_callbacks
def test_get_experiments_for_user(user_id, expected):
    user_doc = (yield db.users.find_one({'_id': user_id})) or {}
    result = yield experiment_manager.get_experiments_for_user(user_doc)
    assert result == expected


@pytest.mark.filldb()
@pytest.mark.parametrize('order_id,expected', [
    ('order1', ['xy', 'zx', 'orders_yandex']),
    ('order2', []),
    ('order3', ['orders_yandex']),
])
@pytest.inline_callbacks
def test_get_experiments(order_id, expected):
    order = yield dbh.orders.Doc.find_one_by_id(order_id)
    result = yield experiment_manager.get_experiments(
        order_helpers.get_proc_like_obj_for_experiments(order)
    )
    assert result == expected

    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    result = yield experiment_manager.get_experiments(
        order_helpers.get_proc_like_obj_for_experiments(proc, from_proc=True)
    )
    assert result == expected


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('percent', range(101))
def test_generate_last_digits(percent):
    last_digits = experiment_manager.generate_last_digits(percent)
    phone_id_restrictions = experiment_manager.PhoneIdRestrictions(
        last_digits
    )
    assert phone_id_restrictions.percent == percent


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('percent', range(101))
def test_change_percent(percent):
    last_digits = experiment_manager.generate_last_digits(percent)
    phone_id_restrictions = experiment_manager.PhoneIdRestrictions(
        last_digits
    )
    new_percents = random.sample(range(101), 101)
    for new_percent in new_percents:
        phone_id_restrictions.change_percent(new_percent)
        assert new_percent == phone_id_restrictions.percent
        digits = phone_id_restrictions.last_digits
        one_digits = [digit for digit in digits if len(digit) == 1]
        two_digits = [digit for digit in digits if len(digit) == 2]
        if two_digits:
            tails = set([d[-1] for d in two_digits])
            assert len(tails) == 1
            for digit in one_digits:
                assert digit not in tails


@pytest.mark.filldb(_fill=False)
def test_wrong_percent():
    percent = random.randint(0, 100)
    last_digits = experiment_manager.generate_last_digits(percent)
    phone_id_restrictions = experiment_manager.PhoneIdRestrictions(
        last_digits
    )
    with pytest.raises(AssertionError):
        phone_id_restrictions.change_percent(100500)


@pytest.mark.filldb()
@pytest.mark.parametrize('config,phone_id,phone_doc,expected', [
    # percent of all users
    ({
        'phone_id_percent': {'from': 45, 'to': 50},
        'salt': 'd9bc81b5545647f595d16d075b4fbc6e'
     },
     '9c75c928529b42289bdb83ba9ffd8a93',
     None,
     True),
    # percent of vip users
    ({
        'vip_percent': {'from': 45, 'to': 50},
        'salt': 'd9bc81b5545647f595d16d075b4fbc6e'
     },
     '9c75c928529b42289bdb83ba9ffd8a93',
     None,
     True),
    ({
         'vip_percent': {'from': 0, 'to': 20},
         'salt': 'd9bc81b5545647f595d16d075b4fbc6e'
     },
     '9c75c928529b42289bdb83ba9ffd8a93',
     None,
     False),
    # percent of all yandex
    ({
         'yandex_staff': True,
         'staff_percent': {'from': 0, 'to': 50},
         'salt': '71c85e8129884b89a9cbc488b8873d55'
     },
     '519726e88b9b4e97a98e58cc49b9efba',
     {"yandex_staff": True},
     True),
    ({
         'yandex_staff': True,
         'staff_percent': {'from': 50, 'to': 100},
         'salt': '71c85e8129884b89a9cbc488b8873d55'
     },
     '519726e88b9b4e97a98e58cc49b9efba',
     {"yandex_staff": True},
     False),
    # phones
    ({
         'user_phone_id_last_digits': [
             '519726e88b9b4e97a98e58cc49b9efba',
             '63a8049e6b87470685bd4ae0efa56e4c'
         ],
         'salt': '71c85e8129884b89a9cbc488b8873d55'
     },
     '519726e88b9b4e97a98e58cc49b9efba',
     None,
     True),
    # percent of taxi
    ({
         'taxi_staff': True,
         'staff_percent': {'from': 20, 'to': 30},
         'salt': '71c85e8129884b89a9cbc488b8873d55'
     },
     '519726e88b9b4e97a98e58cc49b9efba',
     {"taxi_staff": True},
     True),
    ({
         'taxi_staff': True,
         'staff_percent': {'from': 30, 'to': 100},
         'salt': '71c85e8129884b89a9cbc488b8873d55'
     },
     '519726e88b9b4e97a98e58cc49b9efba',
     {"taxi_staff": True},
     False),
])
@pytest.inline_callbacks
def test_check_any_optional_filters(config, phone_id, phone_doc, expected):
    should_be_switched = yield experiment_manager._check_any_optional_filters(
        config, phone_id, phone_doc=phone_doc
    )
    assert should_be_switched == expected


@pytest.mark.parametrize(
    'args,params,doc_fields',
    [
        (
            (experiment_manager.CONFIG_SET_EXPERIMENTS, 'name1'),
            {'user_phone_id_last_digits': ['a', 'bb', 'ccd']},
            {'name': 'name1', 'user_phone_id_last_digits': ['a', 'bb', 'ccd']}
        ),
        (
            (experiment_manager.CONFIG_SET_EXPERIMENTS, 'name1'),
            {
                'user_phone_id_restrictions':
                    experiment_manager.PHONE_ID_RESTRICTION_NOBODY,
                'user_phone_id_last_digits': ['a', 'bb', 'ccd']
            },
            {'name': 'name1', 'user_phone_id_last_digits': ['NOBODY']}
        ),
    ]
)
@pytest.mark.filldb(static='for_set_experiments_params')
@pytest.inline_callbacks
def test_set_experiments_params(args, params, doc_fields):
    experiment_type, experiment_name = args
    yield experiment_manager.set_experiments_params(
        experiment_type, experiment_name, **params
    )
    experiments = (yield db.static.find_one({'_id': experiment_type}))['rules']
    assert len(experiments) == 1
    experiment = experiments[0]
    for field_name, field_value in doc_fields.iteritems():
        assert experiment.get(field_name) == field_value
