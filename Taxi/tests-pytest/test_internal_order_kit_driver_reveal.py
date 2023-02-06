import json as Json

import pytest

from taxi.core import async
from taxi.core import arequests
from taxi.external import experiments3
from taxi.internal import experiments
from taxi.internal.order_kit import driver_reveal
from taxi.internal import dbh


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('value, ar, dp, zone, expected', [
    ({}, 1.0, 100, 'moscow', False),
    ({}, None, None, None, False),
    ({'moscow': {'min_driver_points': 0}}, None, None, 'moscow', False),
    ({'moscow': {'min_driver_points': 0}}, None, 0, 'moscow', True),
    ({'moscow': {'min_driver_points': 0}}, None, 0, 'mos', False),
    ({'moscow': {'min_acceptance_rate': 0.9, 'min_driver_points': 90}},
     0.8, 80, 'moscow', False),
    ({'moscow': {'min_acceptance_rate': 0.9, 'min_driver_points': 90}},
     1.0, None, 'moscow', False),
    ({'moscow': {'min_acceptance_rate': 0.9, 'min_driver_points': 90}},
     None, 100, 'moscow', True),
    ({'moscow': {'min_acceptance_rate': 0.9, 'min_driver_points': 90}},
     0.9, 90, 'moscow', True),
    ({'moscow': {'min_acceptance_rate': 0.9, 'min_driver_points': 90}},
     0.9, 80, 'moscow', False),
    ({'moscow': {'min_acceptance_rate': 0.9, 'min_driver_points': 90}},
     0.8, 90, 'moscow', True),
    ({'moscow': {'min_acceptance_rate': 0.9}}, 0.8, 80, 'moscow', False),
    ({'moscow': {'min_acceptance_rate': 0.9}}, 0.9, 80, 'moscow', False),
    ({'moscow': {'min_driver_points': 90}}, 0.8, 80, 'moscow', False),
    ({'moscow': {'min_driver_points': 90}}, 0.8, 90, 'moscow', True),
    ({'moscow': {}}, 0.9, 90, 'moscow', False),
    ({'moscow': {'min_driver_points': 90, 'min_acceptance_rate': 0.9}},
     0.8, 90, 'moscow', True),
    ({'moscow': {'min_driver_points': 10}}, 1.0, 100, 'spb', False),
    ({'__default__': {'min_driver_points': 0}}, 1.0, 100, 'moscow', False),
])
def test_reveal_by_driver_rates(value, ar, dp, zone, expected):
    candidate = dbh.order_proc.Doc().candidates.new()
    candidate.acceptance_rate = ar
    candidate.driver_points = dp

    reveal = driver_reveal._should_reveal_by_driver_rates(
        reveal_config=value, chosen=candidate, nearest_zone=zone
    )
    assert expected == reveal


@pytest.inline_callbacks
@pytest.mark.config(
    LOYALTY_CHECK_POINT_B=True,
    LOYALTY_PY2_CLIENTS_TIMEOUTS={
        '__default__': {
            'timeout': 0.5,
            'retry_on_fails': True,
        },
        '/service/loyalty/v1/rewards': {
            'timeout': 0.5,
            'retry_on_fails': False,
        },
    },
)
@pytest.mark.parametrize('show', [
    True,
    False,
])
def test_reveal_by_driver_loyalty_status(patch, show):
    @patch('taxi.core.arequests.request')
    @async.inline_callbacks
    def request(
        method, url, headers, timeout, json, retry_on_fails, params=None,
        **kwargs
    ):
        assert json.get('driver_rewards')
        assert json['data']['park_id'] == 'park_id'
        assert json['data']['driver_profile_id'] == 'driverid'

        body = {
            'matched_driver_rewards': {
                'point_b': {'show_point_b': show},
            },
        }
        response = arequests.Response(
            content=Json.dumps(body), status_code=200,
        )
        yield
        async.return_value(response)

    candidate = dbh.order_proc.Doc().candidates.new()
    candidate.udid = 'test_udid'
    candidate.db_id = 'park_id'
    candidate.driver_id = 'clid_driverid'
    candidate.driver_points = 50

    reveal = (
        yield driver_reveal._need_show_destination_by_driver_loyalty_status(
            candidate, 'moscow',
        )
    )
    assert reveal == show


@pytest.inline_callbacks
@pytest.mark.config(
    DRIVER_REVEAL_CHECK_POINT_B_BY_TAGS=True,
    DRIVER_REVEAL_POINT_B_BY_ACTIVITY_AND_TAGS={
        '__default__': {
            'activity': 95,
            'blocking_tags': ['default_block'],
            'allowing_tags': ['default_allow'],
        },
        'moscow': {
            'activity': 85,
            'blocking_tags': ['msc_block'],
            'allowing_tags': ['msc_allow'],
        },
    },
)
@pytest.mark.parametrize('zone, activity, tags, expected', [
    ('spb', 95, [], False),
    ('spb', 94, [], False),
    ('spb', 95, ['default_block'], False),
    ('spb', 95, ['default_no_block'], False),
    ('spb', 95, ['default_allow'], True),
    ('spb', 95, ['default_no_block', 'default_allow'], True),
    ('moscow', 85, [], False),
    ('moscow', 84, [], False),
    ('moscow', 85, ['msc_block'], False),
    ('moscow', 85, ['msc_no_block'], False),
    ('moscow', 85, ['msc_allow'], True),
    ('moscow', 85, ['msc_no_block', 'msc_allow'], True),
])
def test_reveal_by_driver_activity_and_tags(
        patch, zone, activity, tags, expected,
):
    candidate = dbh.order_proc.Doc().candidates.new()
    candidate.driver_points = activity
    candidate.tags = tags

    reveal = (
        yield driver_reveal._need_show_destination_by_driver_activity_and_tags(
            chosen=candidate, nearest_zone=zone,
        )
    )
    assert expected == reveal


@pytest.inline_callbacks
@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize(
    'rates_pass, experiments, zone, expected_fixed_price, '
    'expected_destination', [
        (False, [], 'moscow', False, False),
        (True, [], 'moscow', False, False),
        (True, [experiments.REVEAL_FIXED_PRICE_BY_RATES_EXPERIMENT],
         'moscow', True, False),
        (False, [experiments.REVEAL_FIXED_PRICE_BY_RATES_EXPERIMENT],
         'moscow', False, False),
        (True, [experiments.REVEAL_FIXED_PRICE_BY_RATES_EXPERIMENT,
                'reveal_moscow'], 'moscow', True, True),
        (True, ['reveal_moscow', 'reveal_default'], 'moscow', False, True),
        (True, ['reveal_default'], 'moscow', False, False),
        (True, [], 'spb', False, True),
        (True, [], 'kazan', False, False),
        (True, ['reveal_default'], 'kazan', False, True),
        (True, None, 'moscow', False, False),
        (None, None, 'moscow', False, False),
    ])
@pytest.mark.config(REVEAL_DESTINATION_TO_DRIVER={
    'moscow': {
        'min_acceptance_rate': 0.9,
        'min_driver_points': 90
    },
    'spb': {
        'min_acceptance_rate': 0.9,
        'min_driver_points': 90
    },
    'kazan': {
        'min_acceptance_rate': 0.9,
        'min_driver_points': 90
    }
}, REVEAL_DESTINATION_TO_DRIVER_EXPERIMENT={
    '__default__': 'reveal_default',
    'moscow': 'reveal_moscow',
    'spb': '',
})
def test_reveal_with_experiments(rates_pass, experiments, zone,
                                 expected_fixed_price, expected_destination):
    if rates_pass is not None:
        candidate = dbh.order_proc.Doc().candidates.new()
        candidate.acceptance_rate = 1.0 if rates_pass else 0.5
        candidate.driver_points = 100 if rates_pass else 50
        candidate.driver_experiments = experiments
    else:
        candidate = None

    destination = (
        yield driver_reveal._need_show_destination_by_driver_rates(
            chosen=candidate, nearest_zone=zone
        )
    )
    assert expected_destination == destination


@pytest.inline_callbacks
@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize(
    'zone, tariff, experiments, is_long_order, expected', [
        ('spb', 'econom',
         [experiments.REVEAL_DESTINATION_FOR_LONG_TRIP_EXPERIMENT],
         False, False),
        ('spb', 'econom',
         [experiments.REVEAL_DESTINATION_FOR_LONG_TRIP_EXPERIMENT],
         True, True),
        ('spb', 'business',
         [experiments.REVEAL_DESTINATION_FOR_LONG_TRIP_EXPERIMENT],
         True, False),
        ('spb', 'econom', [], True, False),
        ('moscow', 'econom',
         [experiments.REVEAL_DESTINATION_FOR_LONG_TRIP_EXPERIMENT],
         True, False),
        ('moscow', 'business',
         [experiments.REVEAL_DESTINATION_FOR_LONG_TRIP_EXPERIMENT],
         True, True),
        (None, None, None, None, False),
        ('moscow', None, None, None, False),
        ('moscow', 'business', None, True, False),
        (None, 'business', [], True, False),
    ]
)
@pytest.mark.config(LONG_TRIP_SHOW_DESTINATION={
    '__default__': {
        '__default__': False,
        'business': True,
    },
    'spb': {
        '__default__': True,
        'business': False,
    }
})
def test_show_destination(zone, tariff, experiments, is_long_order, expected):
    candidate = dbh.order_proc.Doc().candidates.new()
    candidate.tariff_class = tariff
    candidate.driver_experiments = experiments

    show = yield driver_reveal._need_show_destination_by_long_order(
        chosen=candidate, nearest_zone=zone, is_long_order=is_long_order
    )
    assert expected == show


def _chosen_with_tariff(tariff):
    class _Chosen:
        def __init__(self, tariff_class):
            self.tariff_class = tariff_class

    return _Chosen(tariff)


@pytest.inline_callbacks
@pytest.mark.filldb(tariff_settings='b_point')
@pytest.mark.parametrize(
    'zone,chosen,expected', [
        ('zone1', None, True),
        ('zone1', _chosen_with_tariff('econom'), True),
        ('zone1', _chosen_with_tariff('comfort'), True),
        ('zone2', None, False),
        ('zone2', _chosen_with_tariff('econom'), False),
        ('zone2', _chosen_with_tariff('comfort'), False),
        ('zone3', None, True),
        ('zone3', _chosen_with_tariff('econom'), True),
        ('zone3', _chosen_with_tariff('comfort'), True),
        ('zone4', None, True),
        ('zone4', _chosen_with_tariff('econom'), False),
        ('zone4', _chosen_with_tariff('comfort'), True),
        ('zone5', None, False),
        ('zone5', _chosen_with_tariff('econom'), True),
        ('zone5', _chosen_with_tariff('comfort'), False),
        ('zone6', None, False),
        ('zone6', _chosen_with_tariff('econom'), False),
        ('zone6', _chosen_with_tariff('comfort'), False),
    ]
)
def test_need_hide_destination_by_tariff(zone, chosen, expected):
    tariff_settings = yield dbh.tariff_settings.Doc.find_by_home_zone(
        zone,
        fields=[
            dbh.tariff_settings.Doc.hide_dest_for_driver,
            dbh.tariff_settings.Doc.hide_dest_for_driver_by_class,
        ]
    )
    result = driver_reveal._need_hide_destination_by_tariff(
        tariff_settings, chosen
    )
    assert result == expected


ZONES_TO_CITIES = {
    'spb': 'Saint-Petersburg',
    'moscow': 'Moscow',
    'kazan': 'Kazan',
    'ekb': 'Ekaterinburg',
}


@pytest.inline_callbacks
@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize(
    'experiments, zone, tariff, expected', [
        ([], 'moscow', 'econom', False),
        ([experiments.SHOW_LOCALIZED_TARIFF], 'moscow', 'econom', True),
        ([experiments.SHOW_LOCALIZED_TARIFF], 'moscow', 'business', True),
        ([experiments.SHOW_LOCALIZED_TARIFF], 'ekb', 'econom', False),
        ([experiments.SHOW_LOCALIZED_TARIFF], 'ekb', 'vip', True),
        ([experiments.SHOW_LOCALIZED_TARIFF], 'spb', 'econom', False),
        ([experiments.SHOW_LOCALIZED_TARIFF], 'spb', 'business', True),
    ]
)
@pytest.mark.config(SHOW_LOCALIZED_TARIFF_TO_DRIVER={
    '__default__': {
        '__default__': False,
        'vip': True,
    },
    'moscow': {
        '__default__': True,
    },
    'spb': {
        '__default__': True,
        'econom': False,
    }
})
def test_show_localized_tariff(experiments, zone, tariff, expected):
    candidate = dbh.order_proc.Doc().candidates.new()
    candidate.tariff_class = tariff
    candidate.driver_experiments = experiments

    show_localized_tariff = (
        yield driver_reveal.show_localized_tariff(
            chosen=candidate, tariff_class=tariff, nearest_zone=zone
        )
    )
    assert show_localized_tariff == expected


@pytest.fixture
def mock_experiments3(patch):
    @patch('taxi.external.experiments3.get_values')
    @async.inline_callbacks
    def _dummy_get_values(consumer, args, **kwargs):
        yield
        assert consumer == 'stq/order_push'
        if args[0].value == 'first':
            async.return_value([])
        else:
            async.return_value([
                experiments3.ExperimentsArg(
                    name='show_b_point_by_tag',
                    type='string',
                    value='unknown',
                )
            ])

    return _dummy_get_values


@pytest.inline_callbacks
@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize(
    "tags, udid, call_exp3, expected", [
        ([], '', False, False),
        (['another_tag'], '', False, False),
        (['show_b_by_3_exp_tag'], 'first', True, False),
        (['show_b_by_3_exp_tag'], 'second', True, True),
    ]
)
def test_go_in_experiments_3(tags, udid, call_exp3, expected,
                             mock_experiments3):
    result = yield driver_reveal._show_point_by_tags_and_experiments_3(udid, tags)
    assert result == expected
    if call_exp3:
        assert mock_experiments3.calls
    else:
        assert not mock_experiments3.calls
