import pytest

from tests_subventions_candidates_reader import common

# Feel free to provide your custom implementation to override generated tests.

# pylint: disable=import-error,wildcard-import
from subventions_candidates_reader_plugins.generated_tests import *  # noqa


def _gen_one_subvention_rule(geoareas, type_, tags, profile_tariff_classes):
    return {
        'tariff_zones': ['moscow'],
        'geoareas': geoareas,
        'status': 'enabled',
        'start': '2018-08-01T12:59:23.231000+00:00',
        'end': '2018-08-10T12:59:23.231000+00:00',
        'type': type_,
        'is_personal': False,
        'taxirate': 'TAXIRATE-21',
        'subvention_rule_id': '_id/1',
        'cursor': '1',
        'tags': tags,
        'time_zone': {'id': 'Europe/Moscow', 'offset': '+03'},
        'currency': 'RUB',
        'updated': '2018-08-01T12:59:23.231000+00:00',
        'visible_to_driver': True,
        'week_days': ['mon'],
        'hours': [],
        'log': [],
        'workshift': {'start': '08:00', 'end': '18:00'},
        'payment_type': 'add',
        'profile_payment_type_restrictions': 'none',
        'profile_tariff_classes': profile_tariff_classes,
        'rates': [
            {'week_day': 'mon', 'start': '12:00', 'rate_per_minute': '500'},
        ],
        'min_online_minutes': 0,
        'rate_free_per_minute': '1.23',
        'rate_on_order_per_minute': '1.23',
        'is_relaxed_order_time_matching': False,
        'is_relaxed_income_matching': False,
        'commission_rate_if_fraud': '0.2',
    }


def _gen_subventions_rules(wished_types=('geo_booking', 'driver_fix')):
    params = [
        {
            'geoareas': ['zone1'],
            'type': 'geo_booking',
            'tags': ['tag1'],
            'profile_tariff_classes': ['econom'],
        },
        {
            'geoareas': ['zone1'],
            'type': 'driver_fix',
            'tags': ['driver-fix-tag'],
            'profile_tariff_classes': ['econom'],
        },
        {
            'geoareas': ['zone2'],
            'type': 'driver_fix',
            'tags': ['driver-fix-tag'],
            'profile_tariff_classes': ['econom'],
        },
        {
            'geoareas': ['zone3', 'zone4'],
            'type': 'geo_booking',
            'tags': ['tag3', 'tag4'],
            'profile_tariff_classes': ['econom'],
        },
        {
            'geoareas': ['zone2'],
            'type': 'driver_fix',
            'tags': ['tag4'],
            'profile_tariff_classes': ['shuttle'],
        },
    ]
    return [
        _gen_one_subvention_rule(
            p['geoareas'], p['type'], p['tags'], p['profile_tariff_classes'],
        )
        for p in params
        if p['type'] in wished_types
    ]


def _make_config(bs_shuttle_rule_classes=None):
    value = {
        'bs_rules_select_active_from_now': 60,
        'bs_rules_select_limit': 1000,
        'service_enabled': True,
        'bs_workmode_based_rule_types': ['driver_fix'],
        'bs_tags_based_rule_types': ['geo_booking'],
    }
    if bs_shuttle_rule_classes is not None:
        value['bs_shuttle_rule_classes'] = bs_shuttle_rule_classes
    return value


@pytest.fixture(name='billing_subventions', autouse=True)
def mock_billing_subventions(mockserver):
    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _rules_select(request):
        doc = request.json
        rules = _gen_subventions_rules(doc['types'])
        return {'subventions': rules}

    return _rules_select


@pytest.mark.parametrize(
    'shuttle_rule_classes,expected_tasks',
    [
        (
            # shuttle_rule_classes
            None,
            # expected_tasks
            [
                ('zone1', 'tags_based'),
                ('zone1', 'workmode_based'),
                ('zone2', 'workmode_based'),
                ('zone3', 'tags_based'),
                ('zone4', 'tags_based'),
            ],
        ),
        (
            # shuttle_rule_classes
            ['shuttle'],
            # expected_tasks
            [
                ('zone1', 'tags_based'),
                ('zone1', 'workmode_based'),
                ('zone2', 'workmode_based'),
                ('zone3', 'tags_based'),
                ('zone4', 'tags_based'),
                ('zone2', 'shuttle'),
            ],
        ),
    ],
)
@pytest.mark.parametrize(
    'not_empty_db',
    [
        pytest.param(False, id='empty_db'),
        pytest.param(True, id='not_empty_db'),
    ],
)
@pytest.mark.config(SUBVENTIONS_CANDIDATES_READER_SETTINGS=_make_config())
async def test_subvention_loading(
        taxi_subventions_candidates_reader,
        pgsql,
        testpoint,
        taxi_config,
        billing_subventions,
        not_empty_db,
        shuttle_rule_classes,
        expected_tasks,
):
    if shuttle_rule_classes:
        taxi_config.set_values(
            {
                'SUBVENTIONS_CANDIDATES_READER_SHUTTLE_SPECIFIC': {
                    'enabled': True,
                    'default_payment_type': 'none',
                    'bs_shuttle_rule_classes': shuttle_rule_classes,
                },
            },
        )
        await taxi_subventions_candidates_reader.invalidate_caches()

    if not_empty_db:
        common.init_reader_tasks(
            pgsql,
            [
                common.ReaderTask('zone_to_remove', 'workmode_based'),
                common.ReaderTask('zone1', 'tags_based'),
            ],
        )

    await common.run_subvention_loader(taxi_subventions_candidates_reader)

    bs_call = billing_subventions.next_call()['request'].json
    assert (
        'geo_booking' in bs_call['types'] and 'driver_fix' in bs_call['types']
    )
    assert bs_call['status'] == 'enabled'

    cursor = common.get_postgres_cursor(pgsql)
    cursor.execute(
        'SELECT geoarea, processing_type FROM '
        'subventions_candidates_reader.reader_tasks;',
    )
    result = list(cursor)
    assert sorted(result) == sorted(expected_tasks)


@pytest.mark.config(SUBVENTIONS_CANDIDATES_READER_SETTINGS=_make_config())
async def test_store_allowed_tags(
        taxi_subventions_candidates_reader, pgsql, testpoint,
):
    await common.run_subvention_loader(taxi_subventions_candidates_reader)

    cursor = common.get_postgres_cursor(pgsql)
    cursor.execute(
        'SELECT zone_name, allowed_tags FROM '
        'subventions_candidates_reader.allowed_tags;',
    )
    result = list(cursor)

    assert sorted(result) == [
        ('zone1', [['tag1']]),
        ('zone3', [['tag3', 'tag4']]),
        ('zone4', [['tag3', 'tag4']]),
    ]
