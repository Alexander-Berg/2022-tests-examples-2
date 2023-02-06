# coding: utf-8

from __future__ import unicode_literals

import collections
import datetime
import json

import bson
from bson import json_util
from django import test as django_test
import pytest

from taxi import config
from taxi.core import async
from taxi.core import db
from taxi.internal import dbh
from taxi.internal.subvention_kit import bonus_pay_manager
from taxiadmin.api.views import subventions

import helpers


SUBVENTION_PAYMENTS_BULK_FILE = 'bulk_subventions_payments_data.csv'


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('driver_info_data,expected_rule_dict', [
    (
        {
            'num_days': 'full',
            'dict_row': {
                'end_date': datetime.datetime(2018, 4, 10, 21),
                'start_date': datetime.datetime(2018, 4, 8, 21),
                'orders_kpi': 30,
                'city': 'Москва',
                'tariff_zone': 'moscow',
                'geoareas': ['ttk'],
                'bonus_sum': 1000,
                'hour': [1, 2, 3],
            },
            'max_num_rides': None,
            'rule_id': 'p_some_rule_id',
            'group_id': 'some_group_id',
        },
        {
            '_id': 'p_some_rule_id',
            'class': [],
            'dayofweek': [],
            'has_fake_counterpart': False,
            'hour': [1, 2, 3],
            'is_fake': False,
            'paymenttype': None,
            'sub_commission': False,
            'is_once': True,
            'is_bonus': True,
            'branding_type': None,
            'type': 'add',
            'start': datetime.datetime(2018, 4, 9, 21),
            'end': datetime.datetime(2018, 4, 10, 21),
            'geoareas': ['ttk'],
            'tariffzone': ['moscow'],
            'sum': 1000,
            'dayridecount': [[30]],
            'dayridecount_days': 2,
            'dayridecount_is_for_any_category': True,
            'group_id': 'some_group_id',
            'group_member_id': 'p_some_rule_id',
            'analytics_id': None,
        }
    ),
    (
            {
                'num_days': None,
                'dict_row': {
                    'bonus_type': 'guarantee',
                    'end_date': datetime.datetime(2018, 4, 10, 21),
                    'start_date': datetime.datetime(2018, 4, 8, 21),
                    'orders_kpi': None,
                    'city': 'Москва',
                    'tariff_zone': 'moscow',
                    'geoareas': [],
                    'bonus_sum': 220,
                    'hour': [1, 2, 3, 4],
                    'is_bonus': False,
                    'is_once': False,
                    'sub_commission': True
                },
                'max_num_rides': None,
                'rule_id': 'p_guarantee_rule_id',
                'group_id': 'some_group_id',
            },
            {
                '_id': 'p_guarantee_rule_id',
                'class': [],
                'dayofweek': [],
                'has_fake_counterpart': False,
                'hour': [1, 2, 3, 4],
                'is_fake': False,
                'paymenttype': None,
                'sub_commission': True,
                'is_once': False,
                'is_bonus': False,
                'branding_type': None,
                'type': 'guarantee',
                'start': datetime.datetime(2018, 4, 8, 21),
                'end': datetime.datetime(2018, 4, 10, 21),
                'geoareas': [],
                'tariffzone': ['moscow'],
                'sum': 220,
                'dayridecount': [],
                'group_id': 'some_group_id',
                'group_member_id': 'p_guarantee_rule_id',
                'analytics_id': None,
            }
    ),
])
def test_make_rule_dict(driver_info_data, expected_rule_dict):
    assert subventions._make_rule_dict(driver_info_data) == expected_rule_dict


@pytest.mark.asyncenv('blocking')
def test_get_tariff_zones():
    def sort_key(item):
        return item['tariff_zone']

    response = django_test.Client().get('/api/subventions/tariff_zones/')
    assert response.status_code == 200
    expected_data = sorted(
        [
            {
                'tariff_zone': 'aprelevka',
            },
            {
                'tariff_zone': 'cheboksary',
            },
            {
                'tariff_zone': 'kamensk-shakhtinsky',
            },
            {
                'tariff_zone': 'moscow',
            },
        ],
        key=sort_key
    )
    actual_data = sorted(json.loads(response.content), key=sort_key)
    assert actual_data == expected_data


case = helpers.case_getter(
    'tariff_zone,response_status,zones_count,creator_login,created,'
    'error_message',
    response_status=200,
    zones_count=1,
    creator_login='nevladov',
    created='2018-07-15 11:00 +0300',
)


@pytest.mark.parametrize(
    case.params,
    [
        case(
            tariff_zone='cheboksary',
        ),
        # case with hyphen in tariff_zone
        case(
            tariff_zone='kamensk-shakhtinsky',
        ),
        # case with no rules in zone
        case(
            tariff_zone='empty_zone',
            zones_count=0,
        ),
        # case with absent zone
        case(
            tariff_zone='absent_zone',
            response_status=404,
            error_message='Wrong tariffzone: absent_zone '
                          '(no tariff settings found)'
        ),
    ]
)
@pytest.mark.asyncenv('blocking')
def test_get_subvention_rule(patch, tariff_zone, response_status, zones_count,
                             creator_login, created, error_message):
    @patch('taxi.internal.dbh.tariff_settings.Doc.find_many_by_home_zones')
    @async.inline_callbacks
    def find_many_by_home_zones(zone_names, fields):
        tz_by_zones = {
            'cheboksary': 'Europe/Moscow',
            'kamensk-shakhtinsky': 'Europe/Moscow',
            'empty_zone': 'Europe/Moscow',
        }

        yield
        async.return_value([
            dbh.tariff_settings.Doc({
                dbh.tariff_settings.Doc.tz: tz_by_zones[zone],
                dbh.tariff_settings.Doc.home_zone: zone
            }) for zone in tz_by_zones
            if zone in zone_names
        ])

    response = django_test.Client().get(
        '/api/subventions/rules/{}/'.format(tariff_zone)
    )
    assert response.status_code == response_status
    result = json.loads(response.content)
    if response_status == 200:
        assert len(result) == zones_count
        if zones_count:
            assert result[0]['login'] == creator_login
            assert result[0]['created'] == created
    else:
        message = result['message']
        assert message == error_message


@pytest.mark.filldb(subvention_rules='for_call_center')
@pytest.mark.asyncenv('blocking')
@pytest.mark.now('2018-10-16T21:00:00.0')
def test_get_subventions_csv_for_call_center(patch):
    @patch('taxi.internal.dbh.tariff_settings.Doc.find_by_home_zone')
    @async.inline_callbacks
    def find_one_by_home_zone(zone_name):
        tz_by_zones = {
            'vladikavkaz': 'Europe/Moscow',
            'prokopyevsk': 'Asia/Krasnoyarsk',
            'berdsk': 'Asia/Novosibirsk',
            'volgodonsk': 'Europe/Moscow'
        }
        yield
        doc = dbh.tariff_settings.Doc({'tz': tz_by_zones[zone_name]})
        async.return_value(doc)

    @patch('taxi.internal.dbh.tariff_settings.Doc.find_many_by_home_zones')
    @async.inline_callbacks
    def find_many_by_home_zones(zone_names, fields):
        tz_by_zones = {
            'vladikavkaz': 'Europe/Moscow',
            'prokopyevsk': 'Asia/Krasnoyarsk',
            'berdsk': 'Asia/Novosibirsk',
            'volgodonsk': 'Europe/Moscow'
        }

        yield
        async.return_value([
            dbh.tariff_settings.Doc({
                dbh.tariff_settings.Doc.tz: tz_by_zones[zone],
                dbh.tariff_settings.Doc.home_zone: zone
            }) for zone in tz_by_zones
        ])

    response = django_test.Client().get('/api/subventions/call_center_csv/')
    assert response.status_code == 200
    # I am sorry but the default CSV reader just can't read unicode anyhow
    lines = response.content.decode('utf-8').strip().split('\n')
    rows = []
    for line in lines:
        rows.append(line.strip().split(','))
    rows_without_header = rows[1:]
    assert rows_without_header == [
        [
            'berdsk',
            'гарантия',
            'econom',
            '1-5',
            '0-6',
            '90.00',
            '',
            '',
            '3-',
            '1',
            'Нет',
            'Нет',
            '2018-05-22 00:00 +0700',
            '2019-04-22 00:00 +0700',
            '',
            '',
        ],
        [
            'prokopyevsk',
            'доплата',
            'econom',
            '1-7',
            '',
            '100.00',
            '',
            '',
            '',
            '',
            'Нет',
            'Нет',
            '2018-05-17 01:00 +0700',
            '2019-04-17 01:00 +0700',
            '',
            ''
        ],
        [
            'vladikavkaz',
            'выплата скидки',
            'econom',
            '1-7',
            '',
            '70.00',
            '',
            '',
            '',
            '',
            'Нет',
            'Нет',
            '2018-08-23 00:00 +0300',
            '2019-07-23 00:00 +0300',
            '',
            ''
        ],
        [
            'volgodonsk',
            'гарантия',
            '',
            '',
            '',
            '1000.00',
            '',
            '40.0',
            '10-19',
            '1',
            'Да',
            'Да',
            '2018-09-17 00:00 +0300',
            '2018-12-17 00:00 +0300',
            'moscow-1|moscow-2',
            'tag-1|tag-2',
        ],
    ]


@pytest.mark.now('2018-10-16T21:00:00.0')
@pytest.mark.parametrize(
    'data,expected_group_id,old_rule_group_ids',
    [
        (
            # Not a goal rule
            {
                'rule_type': 'guarantee',
                'display_in_taximeter': True,
                'tariffzone': 'moscow',
                'rule_sum': 100,
                'start': '2018-10-18 00:00',
                'end': '2018-10-25 00:00',
                'paymenttype': 'card',
                'dayridecount_is_for_any_category': True,
                'ticket': 'TAXIRATE-10',
                'dayofweek': '1,2,3,4,5,6,7',
                'category': 'econom',
            },
            '',
            {
                '5bc88f843fd694cbb06bc340': 'old_rule_which_is_not_active_yet',
                '5bc89e2c3fd694d7702daf27': 'old_rule_which_is_already_active',
            },
        ),
        (
            # Existing group_id
            {
                'rule_type': 'guarantee',
                'display_in_taximeter': True,
                'tariffzone': 'moscow',
                'rule_sum': 100,
                'start': '2018-10-18 00:00',
                'end': '2018-10-25 00:00',
                'paymenttype': 'card',
                'dayridecount_is_for_any_category': True,
                'dayridecount': '10-',
                'dayridecount_days': 7,
                'ticket': 'TAXIRATE-10',
                'dayofweek': '1,2,3,4,5,6,7',
                'category': 'econom',
                'group_id': 'existing_group_id',
                'budget': {
                    'id': 'deadbeef',
                    'weekly': '100',
                    'rolling': True,
                    'threshold': 120,
                },
            },
            'f9daa3ebfc37fc270f200c32667209d118f05415',
            {
                '5bc88f843fd694cbb06bc340': 'old_rule_which_is_not_active_yet',
                '5bc89e2c3fd694d7702daf27': 'old_rule_which_is_already_active',
            },
        ),
        (
            {
                'rule_type': 'guarantee',
                'display_in_taximeter': True,
                'tariffzone': 'moscow',
                'rule_sum': 100,
                'start': '2018-10-18 00:00',
                'end': '2018-10-25 00:00',
                'paymenttype': 'card',
                'dayridecount_is_for_any_category': True,
                'dayridecount': '10-',
                'dayridecount_days': 7,
                'ticket': 'TAXIRATE-10',
                'dayofweek': '1,2,3,4,5,6,7',
                'category': 'econom',
                'budget': {
                    'id': 'deadbeef',
                    'weekly': '100',
                    'daily': '20',
                },
            },
            'f9daa3ebfc37fc270f200c32667209d118f05415',
            {
                '5bc88f843fd694cbb06bc340': 'old_rule_which_is_not_active_yet',
                '5bc89e2c3fd694d7702daf27': 'old_rule_which_is_already_active',
            },
        ),
        (
            {
                'rule_type': 'guarantee',
                'display_in_taximeter': True,
                'tariffzone': 'moscow',
                'rule_sum': 100,
                'start': '2018-10-21 00:00',
                'end': '2018-10-25 00:00',
                'paymenttype': 'card',
                'dayridecount_is_for_any_category': True,
                'dayridecount': '10-',
                'dayridecount_days': 7,
                'ticket': 'TAXIRATE-10',
                'dayofweek': '1,2,3,4,5,6,7',
                'category': 'econom',
                'close_previous_rules': True,
                'budget': {
                    'id': 'deadbeef',
                    'weekly': '60',
                },
            },
            'da4c68b973ec5eb7398060a3741589ccfbd7a2e8',
            {
                # Rule that starts before new rule start and ends after new rule
                # start and it did not start yet
                '5bc88f843fd694cbb06bc340': (
                    '774a8641d99b3199fbf5f19d3282d49c87acd6fd'
                ),
                # Rule that starts before new rule start and ends after new rule
                # start BUT it did start
                '5bc89e2c3fd694d7702daf27': 'old_rule_which_is_already_active',
            },
        ),
    ]
)
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_add_subvention_rule_happy_path(
        data, expected_group_id, old_rule_group_ids, disable_ticket_check,
        mock_tariff_list):
    response = django_test.Client().post(
        '/api/subventions/add/',
        json.dumps(data),
        'application/json',
        HTTP_X_YATAXI_DRAFT_TICKETS='RUPRICING-1,FPRICING-2',
        HTTP_X_YATAXI_DRAFT_APPROVALS='me, you',
    )
    content = json.loads(response.content)
    assert response.status_code == 200, content
    assert len(content['items']) == 1
    rule = content['items'][0]
    if expected_group_id:
        assert rule['group_id'] == expected_group_id, rule['group_id']
        db_rule = yield db.subvention_rules.find_one({
            '_id': bson.ObjectId(rule['rule_id'])
        })
        assert db_rule['group_member_id'] == str(db_rule['_id'])
        assert db_rule['log'][-1]['group_member_id'] == str(db_rule['_id'])
    for rule_id, group_id in old_rule_group_ids.iteritems():
        old_rule = yield db.subvention_rules.find_one({
            '_id': bson.ObjectId(rule_id)
        })
        assert old_rule['group_id'] == group_id, rule_id
        assert old_rule['group_member_id']
    rule_from_db = yield db.subvention_rules.find_one(
        {'_id': bson.ObjectId(rule['rule_id'])}
    )
    assert rule_from_db['currency'] == 'RUB'
    budget = data.get('budget')
    if budget is not None:
        budget.update({
                'tickets': ['RUPRICING-1', 'FPRICING-2'],
                'approvers': ['me', 'you'],
            })
    assert rule_from_db.get('budget') == budget


@pytest.mark.asyncenv('blocking')
@pytest.mark.now('2018-10-16T21:00:00.0')
@pytest.inline_callbacks
def test_add_personal_subvention_rule_no_once_allowed(open_file):
    data = {
        'rules': (yield open_file('personal_subventions.txt')),
        'ticket': 'TAXIRATE-20'
        }
    response = django_test.Client().post(
        '/api/subventions/bulk/add/rules/',
        data=data,
    )
    assert response.status_code == 200


@pytest.mark.asyncenv('blocking')
@pytest.mark.config(USE_PERSONAL_GUARANTEES=False)
@pytest.mark.now('2018-10-16T21:00:00.0')
@pytest.inline_callbacks
def test_add_personal_subvention_rule_no_once_forbidden(open_file):
    data = {
        'rules': (yield open_file('personal_subventions.txt')),
        'ticket': 'TAXIRATE-20'
        }
    response = django_test.Client().post(
        '/api/subventions/bulk/add/rules/',
        data=data,
    )
    assert response.status_code == 406


@pytest.mark.now('2018-10-16T21:00:00.0')
@pytest.mark.parametrize(
    'data',
    [
        # It's a step for a single order goal rule, and another step for the
        # same rule exists
        {
            'rule_type': 'guarantee',
            'display_in_taximeter': True,
            'region': 'Москва',
            'tariffzone': 'moscow',
            'rule_sum': 100,
            'start': '2018-10-18 00:00',
            'end': '2018-10-25 00:00',
            'paymenttype': 'card',
            'dayridecount_is_for_any_category': True,
            'dayridecount': '20-',
            'dayridecount_days': 7,
            'ticket': 'TAXIRATE-10',
            'dayofweek': '1,2,3,4,5,6,7',
            'category': 'econom',
        },
        # Single order goal rule with complex dayridecount
        {
            'rule_type': 'guarantee',
            'display_in_taximeter': True,
            'region': 'Пермь',
            'tariffzone': 'perm',
            'rule_sum': 100,
            'start': '2018-10-18 00:00',
            'end': '2018-10-25 00:00',
            'paymenttype': 'card',
            'dayridecount_is_for_any_category': True,
            'dayridecount': '20-40',
            'dayridecount_days': 7,
            'ticket': 'TAXIRATE-10',
            'dayofweek': '1,2,3,4,5,6,7',
            'category': 'econom',
        },
        # Single order goal rule with complex dayridecount and tags
        {
            'rule_type': 'guarantee',
            'display_in_taximeter': True,
            'region': 'Пермь',
            'tariffzone': 'perm',
            'tags': 'tag1,tag2,tag3',
            'rule_sum': 100,
            'start': '2018-10-18 00:00',
            'end': '2018-10-25 00:00',
            'paymenttype': 'card',
            'dayridecount_is_for_any_category': True,
            'dayridecount': '20-,40-',
            'dayridecount_days': 7,
            'ticket': 'TAXIRATE-10',
            'dayofweek': '1,2,3,4,5,6,7',
            'category': 'econom',
        }
    ]
)
@pytest.mark.filldb(
    subvention_rules='for_test_add_subvention_rule_sad_path'
)
@pytest.mark.asyncenv('blocking')
def test_add_subvention_rule_sad_path(
        data, disable_ticket_check, mock_tariff_list):
    response = django_test.Client().post(
        '/api/subventions/add/', json.dumps(data), 'application/json')
    assert response.status_code == 406


@pytest.mark.now('2018-10-16T21:00:00.0')
@pytest.mark.parametrize(
    'data,group_id_should_change,expected_group_id',
    [
        (
            # group_id does not change if rule is active
            {
                'rule_id': '5bc715db3fd69435fe75b0b8',
                'branding_type': None,
                'category': '',
                'dayofweek': '1,2,3,4,5,6,7',
                'dayridecount': '10-',
                'display_in_taximeter': True,
                'end': '2018-10-21 21:00',
                'geoareas': [],
                'tags': '',
                'group_id': 'existing_group_id',
                'has_fake_counterpart': False,
                'hour': '',
                'is_bonus': False,
                'is_fake': False,
                'is_once': False,
                'paymenttype': '',
                'start': '2018-10-14 21:00',
                'sub_commission': False,
                'rule_sum': 100.0,
                'tariffzone': 'moscow',
                'rule_type': 'guarantee',
                'ticket': 'TAXIRATE-10',
            },
            False,
            'existing_group_id',
        ),
        (
            # group_id changes if rule is not active yet
            {
                'rule_id': '5bc73af83fd69443ee512ce5',
                'branding_type': None,
                'category': '',
                'dayofweek': '1,2,3,4,5,6,7',
                'dayridecount': '10-',
                'dayridecount_days': 7,
                'display_in_taximeter': True,
                'end': '2018-10-25 21:00',
                'geoareas': [],
                'tags': '',
                'group_id': 'existing_group_id',
                'has_fake_counterpart': False,
                'hour': '',
                'is_bonus': False,
                'is_fake': False,
                'is_once': False,
                'paymenttype': '',
                'start': '2018-10-18 21:00',
                'sub_commission': False,
                'rule_sum': 100.0,
                'tariffzone': 'moscow',
                'rule_type': 'guarantee',
                'ticket': 'TAXIRATE-10',
            },
            True,
            '889cb7d7d5d94005c15790a3917abc7dcef66b92',
        ),
    ]
)
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_update_subvention_rule_happy_path(
        data, group_id_should_change, expected_group_id,
        disable_ticket_check, mock_tariff_list):
    response = django_test.Client().post(
        '/api/subventions/edit/',
        json.dumps(data),
        'application/json',
    )
    content = json.loads(response.content)
    assert response.status_code == 200, content
    assert len(content['items']) == 1
    rule = content['items'][0]
    if expected_group_id is not None:
        assert rule['group_id'] == expected_group_id, rule['group_id']
        db_rule = yield db.subvention_rules.find_one({
            '_id': bson.ObjectId(rule['rule_id'])
        })
        assert db_rule['group_member_id'] == str(db_rule['_id'])
        if group_id_should_change:
            assert db_rule['log'][-1]['group_id'] == expected_group_id
            assert db_rule['log'][-1]['group_member_id'] == str(db_rule['_id'])
            rule_from_db = yield db.subvention_rules.find_one(
                {'_id': bson.ObjectId(rule['rule_id'])}
            )
            assert rule_from_db['currency'] == 'RUB'


@pytest.mark.now('2018-10-16T21:00:00.0')
@pytest.mark.parametrize(
    'data',
    [
        # Try to change dayridecount of a single
        # order goal rule to an invalid value
        {
            'rule_id': '5bc715db3fd69435fe75b0b8',
            'branding_type': None,
            'category': '',
            'dayofweek': '1,2,3,4,5,6,7',
            'dayridecount': '10-,20-',
            'display_in_taximeter': True,
            'end': '2018-10-21 21:00',
            'geoareas': [],
            'tags': '',
            'group_id': 'existing_group_id',
            'has_fake_counterpart': False,
            'hour': '',
            'is_bonus': False,
            'is_fake': False,
            'is_once': False,
            'paymenttype': '',
            'region': 'Москва',
            'start': '2018-10-18 21:00',
            'sub_commission': False,
            'rule_sum': 100.0,
            'tariffzone': 'moscow',
            'rule_type': 'guarantee',
            'ticket': 'TAXIRATE-10',
        },
        # Try to change the rule so its group id changes to the id of a group
        # that already has a step
        {
            'rule_id': '5bc73af83fd69443ee512ce5',
            'branding_type': None,
            'category': '',
            'dayofweek': '1,2,3,4,5,6,7',
            'dayridecount': '10-',
            'dayridecount_days': 7,
            'display_in_taximeter': True,
            'end': '2018-10-25 21:00',
            'geoareas': [],
            'tags': '',
            'group_id': 'existing_group_id',
            'has_fake_counterpart': False,
            'hour': '',
            'is_bonus': False,
            'is_fake': False,
            'is_once': False,
            'paymenttype': '',
            'region': 'Москва',
            'start': '2018-10-18 21:00',
            'sub_commission': False,
            'rule_sum': 100.0,
            'tariffzone': 'moscow',
            'rule_type': 'guarantee',
            'ticket': 'TAXIRATE-10',
        },
    ]
)
@pytest.mark.filldb(
    subvention_rules='for_test_update_subvention_rule_sad_path'
)
@pytest.mark.asyncenv('blocking')
def test_update_subvention_rule_sad_path(
        data, disable_ticket_check, mock_tariff_list):
    response = django_test.Client().post(
        '/api/subventions/edit/', json.dumps(data), 'application/json')
    content = json.loads(response.content)
    assert response.status_code == 406, content


@pytest.mark.parametrize(
    'subvention_id,billing_response,expected_response',
    [
        # No region, with tags, rules from mongo
        (
            '5b4c53c8beb9bfe4757258c5',
            None,
            {
                'items': [
                    {
                        'dayofweek': '1-7',
                        'tariffzone_localized': 'aprelevka',
                        'dayridecount': '',
                        'tariffzone': 'aprelevka',
                        'is_once': False,
                        'sub_commission': False,
                        'is_bonus': False,
                        'category': '',
                        'end': '2018-07-16 11:00 +0300',
                        'is_fake': False,
                        'start': '2018-07-16 11:00 +0300',
                        'updated': '2018-07-16 11:00 +0300',
                        'tags': 'tag_1,tag_2',
                        'branding_type': None,
                        'ticket': 'TAXIRATE-10',
                        'rule_type': 'guarantee',
                        'has_fake_counterpart': False,
                        'display_in_taximeter': True,
                        'hour': '',
                        'rule_sum': 100.0,
                        'paymenttype': '',
                        'geoareas': [],
                        'login': 'nevladov',
                        'group_id': ''
                    }
                ],
                'amount': 1
            },
        ),
        # With region, with tags, rules from mongo
        (
            '5b4c5396beb9bfe47571e161',
            None,
            {
                'items': [
                    {
                        'dayofweek': '1-7',
                        'tariffzone_localized': 'cheboksary',
                        'dayridecount': '',
                        'tariffzone': 'cheboksary',
                        'is_once': False,
                        'sub_commission': False,
                        'is_bonus': False,
                        'category': '',
                        'end': '2018-07-16 11:00 +0300',
                        'is_fake': False,
                        'start': '2018-07-16 11:00 +0300',
                        'updated': '2018-07-15 11:00 +0300',
                        'tags': '',
                        'branding_type': None,
                        'ticket': 'TAXIRATE-10',
                        'rule_type': 'guarantee',
                        'has_fake_counterpart': False,
                        'display_in_taximeter': True,
                        'hour': '',
                        'region': 'Чебоксары',
                        'paymenttype': '',
                        'geoareas': [],
                        'login': 'nevladov',
                        'group_id': '',
                        'rule_sum': 100.0
                    },
                    {
                        'login': 'nevladov',
                        'updated': '2018-07-16 11:00 +0300',
                        'end': '2018-07-16 11:00 +0300',
                        'ticket': 'TAXIRATE-10'
                    }
                ],
                'amount': 2
            },
        ),
        # With region, without tags, rules from billing with log
        (
            '5b4c5396beb9bfe47571e161',
            {
                'subventions': [
                    {
                        'currency': 'RUB',
                        'cursor': '2018-07-16T11:00:00.000000+03:00/5b4c5396beb9bfe47571e161',
                        'end': '2018-07-16T11:00:00.000000+03:00',
                        'geoareas': [],
                        'has_comission': False,
                        'is_personal': False,
                        'min_activity_points': 1,
                        'min_online_minutes': 1,
                        'payment_type': 'add',
                        'rate_free_per_minute': '200',
                        'rate_on_order_per_minute': '200',
                        'is_relaxed_order_time_matching': True,
                        'is_relaxed_income_matching': False,
                        'start': '2018-07-16T11:00:00.000000+03:00',
                        'status': 'enabled',
                        'subvention_rule_id': '_id/5b4c5396beb9bfe47571e161',
                        'tags': [],
                        'tariff_classes': [],
                        'tariff_zones': [
                            'cheboksary',
                        ],
                        'taxirate': 'TAXIRATE-10',
                        'time_zone': {
                            'id': 'Europe/Moscow',
                            'offset': '+03:00',
                        },
                        'type': 'guarantee',
                        'updated': '2018-07-16T11:00:00.000000+03:00',
                        'log': [
                            {
                                'login': 'nevladov',
                                'updated': '2018-07-16T11:00:00.000000+03:00',
                                'end': '2018-07-16T11:00:00.000000+03:00',
                                'ticket': 'TAXIRATE-10'
                            },
                        ],
                    },
                ],
            },
            {
                'items': [
                    {
                        'login': 'nevladov',
                        'updated': '2018-07-16 11:00 +0300',
                        'end': '2018-07-16 11:00 +0300',
                        'ticket': 'TAXIRATE-10'
                    },
                ],
                'amount': 1
            },
        ),
        # With region, without tags, rules from billing but without log
        (
            '5b4c5396beb9bfe47571e161',
            {
                'subventions': [
                    {
                        'currency': 'RUB',
                        'cursor': '2018-07-16T11:00:00.000000+03:00/5b4c5396beb9bfe47571e161',
                        'end': '2018-07-16T11:00:00.000000+03:00',
                        'geoareas': [],
                        'has_comission': False,
                        'is_personal': False,
                        'min_activity_points': 1,
                        'min_online_minutes': 1,
                        'payment_type': 'add',
                        'rate_free_per_minute': '200',
                        'rate_on_order_per_minute': '200',
                        'is_relaxed_order_time_matching': True,
                        'is_relaxed_income_matching': False,
                        'start': '2018-07-16 11:00 +0300',
                        'status': 'enabled',
                        'subvention_rule_id': '_id/5b4c5396beb9bfe47571e161',
                        'tags': [],
                        'tariff_classes': [],
                        'tariff_zones': [
                            'cheboksary',
                        ],
                        'taxirate': 'TAXIRATE-10',
                        'time_zone': {
                            'id': 'Europe/Moscow',
                            'offset': '+03:00',
                        },
                        'type': 'guarantee',
                        "updated": "2018-07-16T11:00:00.000000+03:00",
                    },
                ],
            },
            {
                'items': [
                    {
                        'end': '',
                        'login': '',
                        'ticket': 'TAXIRATE-10'
                    },
                ],
                'amount': 1
            },
        ),
    ]
)
@pytest.mark.asyncenv('blocking')
def test_subvention_logs(patch, subvention_id, billing_response,
                         expected_response):
    config.ENABLE_SUBVENTIONS_LOGS_FROM_BILLING.save(
        billing_response is not None
    )

    @patch('taxi.internal.dbh.tariff_settings.Doc.find_by_home_zone')
    @async.inline_callbacks
    def find_one_by_home_zone(zone_name):
        tz_by_zones = {
            'aprelevka': 'Europe/Moscow',
            'cheboksary': 'Europe/Moscow'
        }
        yield
        doc = dbh.tariff_settings.Doc({'tz': tz_by_zones[zone_name]})
        async.return_value(doc)

    @patch('taxi.external.subventions.select_subvention_rules')
    @async.inline_callbacks
    def select_subvention_rules(request, **kwargs):
        assert 'rule_id' in request
        assert request['rule_id'] == subvention_id
        yield
        async.return_value(billing_response)

    response = django_test.Client().post(
        '/api/subventions/logs/',
        json.dumps({'rule_id': subvention_id}),
        'application/json'
    )
    assert response.status_code == 200
    assert json.loads(response.content) == expected_response


@pytest.mark.parametrize(
    'steps_csv, expected_error, expected_steps', [
        (
            'step,income\n10,100\n20,250\n30,500\n',
            None,
            [
                [10, '100'],
                [20, '250'],
                [30, '500']
            ]
        ),
        (
            '',
            'Empty steps CSV file',
            []
        ),
        (
            '10,100\n20,250\n30,500\n',
            'Steps CSV file has the wrong header: 10,100',
            []
        )
    ]
)
@pytest.mark.asyncenv('blocking')
def test_load_steps_csv(steps_csv, expected_error, expected_steps):
    error_msg = None
    steps = []

    try:
        steps = subventions._load_steps_csv(steps_csv)
    except ValueError as e:
        error_msg = e.message

    assert error_msg == expected_error
    assert steps == expected_steps


@pytest.fixture
def disable_ticket_check(patch):
    @patch('taxiadmin.audit.check_ticket')
    def check_ticket(ticket, login, **kwargs):
        return


@pytest.fixture
def mock_tariff_list(patch):
    @patch('taxi.internal.tariffs_manager.get_all_home_areas_at_moment')
    def get_all_home_areas_at_moment(*args, **kwargs):
        return ['moscow', 'perm']


@pytest.mark.parametrize('is_error', [
    True,
    False
])
@pytest.mark.asyncenv('blocking')
def test_check_payments(patch, is_error):

    @patch('taxiadmin.middleware.BBAuthMiddleware.check_tvm_ticket')
    @async.inline_callbacks
    def _check_ticket_middleware(*args, **kwargs):
        yield

    clid = 'not_existed' if is_error else 'park1'
    response = django_test.Client().post(
        '/api/approvals/subventions_payments_create/check/',
        json.dumps({
            'clid': clid,
            'date_from': '2016-09-26',
            'date_to': '2016-09-27',
        }),
        'application/json',
        HTTP_X_YANDEX_LOGIN='test_login'
    )

    content = json.loads(response.content)

    status_code = 404 if is_error else 200
    assert response.status_code == status_code
    if status_code == 200:
        assert content == {
            'change_doc_id': 'subvention_payments_park1',
            'data': {
                'clid': 'park1',
                'date_from': '2016-09-26',
                'date_to': '2016-09-27',
            },
            'diff': {
                'current': {},
                'new': {
                    'clid': 'park1',
                    'date_from': '2016-09-26',
                    'date_to': '2016-09-27',
                }
            }
        }


@pytest.mark.asyncenv('blocking')
def test_check_bulk_payments(patch, upload_download_mock):

    @patch('taxiadmin.middleware.BBAuthMiddleware.check_tvm_ticket')
    @async.inline_callbacks
    def _check_ticket_middleware(*args, **kwargs):
        yield

    @patch('taxi.internal.archive.get_order')
    @async.inline_callbacks
    def get_order(order_id, lookup_yt=True, log_extra=None):
        yield
        if order_id in ['test_order_id_4', 'test_order_id_5']:
            async.return_value({
                '_id': order_id,
                'performer': {
                    'tariff': {
                        'currency': 'AMD'
                    }
                }
            })
        else:
            async.return_value((yield db.orders.find_one({'_id': order_id})))

    @patch('taxi.internal.archive.get_many_orders')
    @async.inline_callbacks
    def get_many_orders(ids, log_extra=None):
        result = []
        for order_id in ids:
            if order_id in ['test_order_id_4', 'test_order_id_5']:
                result.append({
                    '_id': order_id,
                    'performer': {
                        'tariff': {
                            'currency': 'AMD'
                        }
                    }
                })
            else:
                result.append((yield db.orders.find_one({'_id': order_id})))
        async.return_value(result)

    response = django_test.Client().post(
        '/api/approvals/subventions_payments_bulk_create/check/',
        json.dumps({
            'mds_file_id': SUBVENTION_PAYMENTS_BULK_FILE,
        }),
        'application/json',
        HTTP_X_YANDEX_LOGIN='test_login'
    )

    content = json.loads(response.content)
    assert response.status_code == 200
    assert 'bulk_subvention_payments_' in content.pop('change_doc_id')
    assert content == {
        'data': {
            'mds_file_id': 'bulk_subventions_payments_data.csv',
        },
        'diff': {
            'current': {},
            'new': {
                'mds_file_id': 'bulk_subventions_payments_data.csv',
                'mds_file_url': 'https://tc.mobile.yandex.net/static/'
                                'images/bulk_subventions_payments_data.csv',
                'planned_currency_sums': {
                    'AMD': '23321.69',
                    'RUB': '123',
                    'USD': '234324',
                },
                'reason': 'bulk_bonus_pay',
            },
        },
    }


@pytest.mark.config(
    MIN_DUE_TO_SEND_SUBVENTIONS_TO_BO='2016-02-01T00:00:00+00:00',
)
@pytest.mark.now('2018-10-16T21:00:00.0')
@pytest.mark.asyncenv('blocking')
def test_apply_bulk_payments(patch, upload_download_mock):

    @patch('taxiadmin.middleware.BBAuthMiddleware.check_tvm_ticket')
    @async.inline_callbacks
    def _check_ticket_middleware(*args, **kwargs):
        yield

    @patch('taxi.external.billing_orders.send_doc')
    @async.inline_callbacks
    def send_doc(*args, **kwargs):
        yield async.return_value({})

    @patch('taxi.internal.archive.restore_many_orders')
    @async.inline_callbacks
    def restore_many_orders(order_ids, update=False, log_extra=None):
        yield db.orders.insert({
            '_id': order_ids[0],
            'request': {
                'due': datetime.datetime(2018, 10, 16, 21, 00, 00, 0),
            },
            'performer': {
                'taxi_alias': {
                    'id': 'test_alias_id_%s' % order_ids[0].split('_')[-1]
                },
                'tariff': {
                    'currency': 'AMD'
                }
            }
        })
        async.return_value([])

    @patch('taxi.internal.archive.get_many_orders')
    @async.inline_callbacks
    def get_many_orders(ids, log_extra=None):
        result = []
        for order_id in ids:
            if order_id in ['test_order_id_4', 'test_order_id_5']:
                result.append({
                    '_id': order_id,
                    'performer': {
                        'tariff': {
                            'currency': 'AMD'
                        }
                    }
                })
            else:
                result.append((yield db.orders.find_one({'_id': order_id})))
        async.return_value(result)

    @patch('taxi.internal.archive.restore_many_subvention_reasons')
    @async.inline_callbacks
    def restore_many_subvention_reasons(orders_ids, update=False,
                                        log_extra=None):
        result = []
        for order_id in orders_ids:
            if order_id == 'test_order_id_5':
                result.append('test_order_id_5')
            yield db.subvention_reasons.insert({
                'due': datetime.datetime(2018, 10, 16, 21, 00, 00, 0),
                'order_id': order_id,
                'alias_id': 'test_alias_id_%s' % order_id.split('_')[-1],
                'subvention_bonus': [],
                'version': 1,
            })
        async.return_value(result)

    @patch('taxi.core.async.sleep')
    def sleep(seconds):
        pass

    @patch('taxi.internal.archive.restore_many_mph_results')
    @async.inline_callbacks
    def restore_many_mph_results(orders_ids, update=False, log_extra=None):
        async.return_value([])

    put_check = {
        'checked': False
    }

    @patch('taxi_stq._client.put')
    @async.inline_callbacks
    def put(queue=None, eta=None, task_id=None, args=None, kwargs=None):
        put_check['checked'] = True
        yield bonus_pay_manager.subventions_bulk_payments_with_approvals(
            **kwargs
        )
        draft_info = dbh.drafts_info.Doc.find_one_by_id('draft_id')
        assert draft_info == {
            '_id': 'draft_id',
            'status': 'partially_completed',
            'update_data': {
                'failed_details': 'test_order_id_5;'
                                  'Subvention reason with order_id not found',
                'planned_currency_sums': {
                    'AMD': '23321.69',
                    'RUB': '123',
                    'USD': '234324',
                },
                'mds_file_id': SUBVENTION_PAYMENTS_BULK_FILE,
            },
            'updated': datetime.datetime(2018, 10, 16, 21, 00, 00)
        }

    response = django_test.Client().post(
        '/api/approvals/subventions_payments_bulk_create/apply/',
        json.dumps({
            'mds_file_id': SUBVENTION_PAYMENTS_BULK_FILE,
        }),
        'application/json',
        HTTP_X_YANDEX_LOGIN='test_login',
        HTTP_X_YATAXI_DRAFT_ID='draft_id',
    )

    assert json.loads(response.content) == {
        'status': 'applying'
    }
    assert response.status_code == 200
    assert put_check['checked']
    assert not restore_many_mph_results.calls


@pytest.mark.config(
    MIN_DUE_TO_SEND_SUBVENTIONS_TO_BO='2017-10-01T00:00:00+00:00',
    BILLING_SUBVENTIONS_DISABLE_SUBVENTION_REASONS=True,
)
@pytest.mark.now('2018-10-16T21:00:00.0')
@pytest.mark.asyncenv('blocking')
def test_apply_bulk_payments_wo_subvention_reasons(patch, upload_download_mock):

    @patch('taxiadmin.middleware.BBAuthMiddleware.check_tvm_ticket')
    @async.inline_callbacks
    def _check_ticket_middleware(*args, **kwargs):
        yield

    @patch('taxi.external.billing_orders.send_doc')
    @async.inline_callbacks
    def send_doc(*args, **kwargs):
        yield async.return_value({})

    @patch('taxi.internal.archive.restore_many_orders')
    @async.inline_callbacks
    def restore_many_orders(order_ids, update=False, log_extra=None):
        yield db.orders.insert({
            '_id': order_ids[0],
            'request': {
                'due': datetime.datetime(2018, 10, 16, 21, 00, 00, 0),
            },
            'performer': {
                'taxi_alias': {
                    'id': 'test_alias_id_%s' % order_ids[0].split('_')[-1]
                },
                'tariff': {
                    'currency': 'AMD'
                }
            }
        })
        async.return_value([])

    @patch('taxi.internal.archive.get_many_orders')
    @async.inline_callbacks
    def get_many_orders(ids, log_extra=None):
        result = []
        for order_id in ids:
            if order_id in ['test_order_id_4', 'test_order_id_5']:
                result.append({
                    '_id': order_id,
                    'performer': {
                        'tariff': {
                            'currency': 'AMD'
                        }
                    }
                })
            else:
                result.append((yield db.orders.find_one({'_id': order_id})))
        async.return_value(result)

    @patch('taxi.core.async.sleep')
    def sleep(seconds):
        pass

    @patch('taxi.internal.archive.restore_many_mph_results')
    @async.inline_callbacks
    def restore_many_mph_results(orders_ids, update=False, log_extra=None):
        async.return_value([])

    put_check = {
        'checked': False
    }

    @patch('taxi_stq._client.put')
    @async.inline_callbacks
    def put(queue=None, eta=None, task_id=None, args=None, kwargs=None):
        put_check['checked'] = True
        yield bonus_pay_manager.subventions_bulk_payments_with_approvals(
            **kwargs
        )
        draft_info = dbh.drafts_info.Doc.find_one_by_id('draft_id')
        assert draft_info == {
            '_id': 'draft_id',
            'status': 'partially_completed',
            'update_data': {
                'failed_details': 'test_order_id_1;Order is too old',
                'planned_currency_sums': {
                    'AMD': '23321.69',
                    'RUB': '123',
                    'USD': '234324',
                },
                'mds_file_id': SUBVENTION_PAYMENTS_BULK_FILE,
            },
            'updated': datetime.datetime(2018, 10, 16, 21, 00, 00)
        }

    response = django_test.Client().post(
        '/api/approvals/subventions_payments_bulk_create/apply/',
        json.dumps({
            'mds_file_id': SUBVENTION_PAYMENTS_BULK_FILE,
        }),
        'application/json',
        HTTP_X_YANDEX_LOGIN='test_login',
        HTTP_X_YATAXI_DRAFT_ID='draft_id',
    )

    assert json.loads(response.content) == {
        'status': 'applying'
    }
    assert response.status_code == 200
    assert put_check['checked']
    assert not restore_many_mph_results.calls


@pytest.fixture
def upload_download_mock(patch, open_file):

    @patch('taxi.external.mds.upload')
    @async.inline_callbacks
    def upload(
        image_file, namespace=None, key_suffix=None,
        headers=None, retry_on_fails=True, log_extra=None
    ):
        yield
        async.return_value(image_file)

    @patch('taxi.external.mds.download')
    @async.inline_callbacks
    def download(
            path, range_start=None, range_end=None,
            namespace=None, log_extra=None
    ):
        yield
        with open_file(SUBVENTION_PAYMENTS_BULK_FILE) as fp:
            async.return_value(fp.read())


@pytest.fixture
def mock_uuid(patch):
    @patch('uuid.uuid4')
    def uuid4():
        uuid4_ = collections.namedtuple('uuid4', 'hex')
        return uuid4_('d1739a1981634b88be3df266580728fa')


@pytest.fixture
def mock_check_tvm(patch):
    @patch('taxiadmin.middleware.BBAuthMiddleware.check_tvm_ticket')
    @async.inline_callbacks
    def _check_ticket_middleware(*args, **kwargs):
        yield


def _check_subventions(request, response, handle, load):
    doc = load(request)
    doc = json.loads(doc)

    expected = load(response)
    expected = json.loads(expected)

    response = django_test.Client().post(
        handle,
        json.dumps(doc),
        'application/json',
        HTTP_X_YANDEX_LOGIN='test_login',
        HTTP_X_YATAXI_DRAFT_ID='draft_id',
        HTTP_X_YATAXI_TICKET='TAXIRATE-52',
    )

    content = json.loads(response.content)
    assert response.status_code == 200
    assert content == expected


@pytest.mark.now('2018-10-16T21:00:00.0')
@pytest.mark.asyncenv('blocking')
def test_check_bulk_create_subventions(mock_check_tvm, mock_uuid, load):
    _check_subventions(
        'approvals/check_bulk_create_request.json',
        'approvals/check_bulk_create_response.json',
        '/api/approvals/subventions_bulk_create/check/',
        load,
    )


@pytest.mark.now('2018-06-16T21:00:00.0')
@pytest.mark.asyncenv('blocking')
def test_check_bulk_edit_subventions(mock_check_tvm, mock_uuid, load):
    _check_subventions(
        'approvals/bulk_edit_request.json',
        'approvals/check_bulk_edit_response.json',
        '/api/approvals/subventions_bulk_edit/check/',
        load,
    )


def _apply_subventions(request, handle, load):
    doc = load(request)
    doc = json.loads(doc)
    doc['ticket'] = 'TAXIRATE-52'

    response = django_test.Client().post(
        handle,
        json.dumps(doc),
        'application/json',
        HTTP_X_YANDEX_LOGIN='test_login',
        HTTP_X_YATAXI_DRAFT_ID='draft_id',
    )

    assert response.status_code == 200
    assert json.loads(response.content) == {
        'status': 'succeeded'
    }


@pytest.mark.now('2018-10-16T21:00:00.0')
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_apply_bulk_create_subventions(mock_check_tvm, load):
    _apply_subventions(
        'approvals/check_bulk_create_request.json',
        '/api/approvals/subventions_bulk_create/apply/',
        load,
    )
    yield _assert_areas(load, ['Zone 2', 'modcow'])


@pytest.mark.now('2018-06-16T21:00:00.0')
@pytest.mark.asyncenv('blocking')
def test_apply_bulk_edit_subventions(mock_check_tvm, load):
    _apply_subventions(
        'approvals/bulk_edit_request.json',
        '/api/approvals/subventions_bulk_edit/apply/',
        load,
    )


@async.inline_callbacks
def _assert_areas(load, areas):
    for area in areas:
        db_rule = yield db.subvention_rules.find_one({'geoareas.0': area})
        expected = _get_rule_db_doc(load, area)
        for field in ('start', 'end', 'updated'):
            db_rule_log = db_rule['log'][0]
            expected_log = expected['log'][0]
            db_rule_log_iso_time = db_rule_log.pop(field).isoformat()
            db_rule_iso_time = db_rule.pop(field).isoformat()
            assert db_rule_log_iso_time == expected_log.pop(field)
            assert db_rule_iso_time == expected.pop(field)

        assert db_rule.pop('_id')
        assert db_rule == expected


@pytest.mark.now('2018-10-16T21:00:00.0')
@pytest.mark.asyncenv('blocking')
def test_check_create_subventions(mock_check_tvm, mock_uuid, load):
    _check_subventions(
        'approvals/check_create_request.json',
        'approvals/check_create_response.json',
        '/api/approvals/subventions_create/check/',
        load,
    )


@pytest.mark.now('2018-10-16T21:00:00.0')
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_apply_create_subventions(mock_check_tvm, load):
    _apply_subventions(
        'approvals/check_create_request.json',
        '/api/approvals/subventions_create/apply/',
        load,
    )
    yield _assert_areas(load, ['Zone 2'])


@pytest.mark.now('2018-10-16T21:00:00.0')
@pytest.mark.asyncenv('blocking')
def test_check_edit_subventions(mock_check_tvm, mock_uuid, load):
    _check_subventions(
        'approvals/check_edit_request.json',
        'approvals/check_edit_response.json',
        '/api/approvals/subventions_edit/check/',
        load,
    )


@pytest.mark.now('2018-10-16T21:00:00.0')
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_apply_edit_subventions(mock_check_tvm, load):
    _apply_subventions(
        'approvals/check_edit_request.json',
        '/api/approvals/subventions_edit/apply/',
        load,
    )

    edited = yield db.subvention_rules.find_one(
        bson.ObjectId('5bc89e2c3fd694d7702daf27'),
    )
    expected = load('approvals/apply_edit_expected.json')
    expected = json.loads(expected)
    edited = json.loads(json_util.dumps(edited))
    assert edited == expected


def _get_rule_db_doc(load, geoarea):
    rule = load('approvals/db_rule.json')
    rule = json.loads(rule)
    rule['log'][0]['geoareas'] = [geoarea]
    rule['geoareas'] = [geoarea]
    return rule


@pytest.mark.now('2018-10-16T21:00:00.0')
@pytest.mark.parametrize(
    'data',
    [
        {
            'rule_type': 'guarantee',
            'display_in_taximeter': True,
            'region': 'Москва',
            'tariffzone': 'moscow',
            'rule_sum': 100,
            'start': '2019-10-18 00:00',
            'end': '2020-10-18 00:00',
            'paymenttype': 'card',
            'dayridecount_is_for_any_category': True,
            'dayridecount': '20-',
            'dayridecount_days': 7,
            'ticket': 'TAXIRATE-10',
            'dayofweek': '1,2,3,4,5,6,7',
            'category': 'econom',
        },
    ]
)
@pytest.mark.filldb(
    subvention_rules='for_test_add_subvention_rule_sad_path'
)
@pytest.mark.asyncenv('blocking')
def test_add_subvention_rule_too_long(
        data, disable_ticket_check, mock_tariff_list):
    response = django_test.Client().post(
        '/api/subventions/add/', json.dumps(data), 'application/json')
    assert response.status_code == 406
