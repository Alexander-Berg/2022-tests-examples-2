import pytest

from tests_contractor_orders_multioffer import contractor_for_order as cfo
from tests_contractor_orders_multioffer import pg_helpers as pgh


PAID_SUPPLY_PARAMS = {
    'allowed_classes': ['econom'],
    'order_id': 'order_id',
    'order': {
        'nearest_zone': 'moscow',
        'user_phone_id': 'user_phone_id',
        'request': {'class': ['econom']},
        'fixed_price': {
            'price': 429.0,
            'paid_supply_info': {'distance': 9468, 'time': 718},
            'paid_supply_price': 154.0,
        },
    },
    'point': [50.276871024, 53.233412039],
    'lookup': {
        'generation': 1,
        'start_eta': 1604055148.006,
        'version': 2,
        'next_call_eta': 1604055164.614,
        'wave': 2,
    },
    'callback': {'url': 'some_url', 'timeout_ms': 500, 'attempts': 2},
}

AIRPORT_PARAMS = {
    'allowed_classes': ['econom'],
    'order_id': 'order_id',
    'order': {
        'nearest_zone': 'moscow',
        'user_phone_id': 'user_phone_id',
        'request': {'class': ['econom']},
    },
    'point': [26, 16],
    'lookup': {
        'generation': 1,
        'start_eta': 1604055148.006,
        'version': 2,
        'next_call_eta': 1604055164.614,
        'wave': 2,
    },
    'callback': {'url': 'some_url', 'timeout_ms': 500, 'attempts': 2},
}

BAD_PARAMS_NZ = {
    'allowed_classes': ['econom'],
    'order_id': 'order_id',
    'order': {
        'nearest_zone': 'perm',
        'user_phone_id': 'user_phone_id',
        'request': {'class': ['econom']},
    },
    'lookup': {
        'generation': 1,
        'start_eta': 1604055148.006,
        'version': 2,
        'next_call_eta': 1604055164.614,
        'wave': 2,
    },
    'callback': {'url': 'some_url', 'timeout_ms': 500, 'attempts': 2},
}

BAD_PARAMS_ORDER = {
    'allowed_classes': ['econom'],
    'order_id': 'order_id_bad',
    'order': {
        'nearest_zone': 'moscow',
        'user_phone_id': 'user_phone_id',
        'request': {'class': ['econom']},
    },
    'lookup': {
        'generation': 1,
        'start_eta': 1604055148.006,
        'version': 2,
        'next_call_eta': 1604055164.614,
        'wave': 2,
    },
    'callback': {'url': 'some_url', 'timeout_ms': 500, 'attempts': 2},
}

BAD_PARAMS_USER_PHONE = {
    'allowed_classes': ['econom'],
    'order_id': 'order_id',
    'order': {
        'nearest_zone': 'moscow',
        'user_phone_id': 'user_phone_id_bad',
        'request': {'class': ['econom']},
    },
    'lookup': {
        'generation': 1,
        'start_eta': 1604055148.006,
        'version': 2,
        'next_call_eta': 1604055164.614,
        'wave': 2,
    },
    'callback': {'url': 'some_url', 'timeout_ms': 500, 'attempts': 2},
}

BAD_PARAMS_CLASS = {
    'allowed_classes': ['econom'],
    'order_id': 'order_id',
    'order': {
        'nearest_zone': 'moscow',
        'user_phone_id': 'user_phone_id',
        'request': {'class': ['vip']},
    },
    'lookup': {
        'generation': 1,
        'start_eta': 1604055148.006,
        'version': 2,
        'next_call_eta': 1604055164.614,
        'wave': 2,
    },
    'callback': {'url': 'some_url', 'timeout_ms': 500, 'attempts': 2},
}


@pytest.mark.driver_tags_match(
    dbid='7f74df331eb04ad78bc2ff25ff88a8f2',
    uuid='4bb5a0018d9641c681c1a854b21ec9ab',
    tags=['uberdriver', 'some_other_tag'],
)
@pytest.mark.parametrize('match_tag', ['uberdriver', 'some_missing_tag'])
@pytest.mark.parametrize('enable_doaa_call', [True, False])
@pytest.mark.parametrize(
    'multioffer_version, version_check', [('8.00', True), ('10.00', False)],
)
@pytest.mark.parametrize(
    'chain_version, chain_version_check', [('8.00', True), ('10.00', False)],
)
@pytest.mark.parametrize('enable_freeze', [True, False])
async def test_contractor_for_order_single_uber_driver(
        taxi_config,
        taxi_contractor_orders_multioffer,
        taxi_contractor_orders_multioffer_monitor,
        pgsql,
        match_tag,
        enable_doaa_call,
        enable_freeze,
        multioffer_version,
        version_check,
        chain_version,
        chain_version_check,
        experiments3,
):
    taxi_config.set_values(
        cfo.create_version_settings(multioffer_version, chain_version),
    )
    taxi_config.set_values(cfo.create_freeze_settings(enable_freeze))
    experiments3.add_config(
        **cfo.experiment3(tag=match_tag, enable_doaa=enable_doaa_call),
    )

    await taxi_contractor_orders_multioffer.tests_control(reset_metrics=True)
    response = await taxi_contractor_orders_multioffer.post(
        '/v1/contractor-for-order', json=cfo.DEFAULT_PARAMS,
    )

    uber_matched = match_tag == 'uberdriver'
    assert response.status_code == 200
    assert response.json()['message'] == 'irrelevant'

    metrics = await taxi_contractor_orders_multioffer_monitor.get_metric(
        'multioffer_match',
    )
    assert metrics['total_orders'] == 1
    assert metrics['orders_unmatched'] == int(
        not uber_matched or not version_check or not chain_version_check,
    )
    assert metrics['uber_offers_matched'] == 0
    assert metrics['uber_offers_not_enough_candidates'] == int(
        uber_matched and version_check and chain_version_check,
    )
    assert metrics['other_offers_matched'] == 0

    assert metrics['moscow']
    assert metrics['moscow']['total_orders'] == 1
    assert metrics['moscow']['orders_unmatched'] == int(
        not uber_matched or not version_check or not chain_version_check,
    )
    assert metrics['moscow']['uber_offers_matched'] == 0
    assert metrics['moscow']['uber_offers_not_enough_candidates'] == int(
        uber_matched and version_check and chain_version_check,
    )

    multioffer = pgh.select_recent_multioffer(pgsql)
    if enable_doaa_call:
        assert multioffer
        assert multioffer['status'] == 'irrelevant'


@pytest.mark.driver_tags_match(
    dbid='7f74df331eb04ad78bc2ff25ff88a8f2',
    uuid='4bb5a0018d9641c681c1a854b21ec9ab',
    tags=['uberdriver', 'some_other_tag'],
)
@pytest.mark.driver_tags_match(
    dbid='a3608f8f7ee84e0b9c21862beef7e48d',
    uuid='e26e1734d70b46edabe993f515eda54e',
    tags=['uberdriver', 'some_other_tag'],
)
@pytest.mark.parametrize('match_tag', ['uberdriver', 'some_missing_tag'])
@pytest.mark.parametrize(
    'enable_doaa_call, is_airport, params, paid_supply_drivers',
    [
        (True, False, cfo.DEFAULT_PARAMS, None),
        (False, False, BAD_PARAMS_NZ, None),
        (False, False, BAD_PARAMS_ORDER, None),
        (False, False, BAD_PARAMS_USER_PHONE, None),
        (False, True, AIRPORT_PARAMS, None),
        (
            True,
            False,
            PAID_SUPPLY_PARAMS,
            ['e26e1734d70b46edabe993f515eda54e'],
        ),
    ],
)
@pytest.mark.parametrize(
    'multioffer_version, version_check', [('8.00', True), ('10.00', False)],
)
@pytest.mark.config(
    LOOKUP_PAID_SUPPLY_SETTINGS={
        'moscow': {
            'econom': {
                'disabled': False,
                'min_distance': 400,
                'min_time': 100,
                'max_price': 200,
            },
        },
    },
)
@pytest.mark.geoareas(filename='airport_geoareas.json')
@pytest.mark.config(
    DISPATCH_AIRPORT_ZONES={
        'moscow': {
            'airport_title_key': 'moscow_airport_key',
            'enabled': True,
            'main_area': 'moscow_airport',
            'notification_area': 'moscow_airport_notification',
            'old_mode_enabled': False,
            'tariff_home_zone': 'moscow_home',
            'update_interval_sec': 5,
            'use_queue': True,
            'waiting_area': 'moscow_airport_waiting',
            'whitelist_classes': {
                'econom': {'reposition_enabled': False, 'nearest_mins': 60},
            },
        },
    },
)
async def test_contractor_for_order_two_uber_driver(
        taxi_config,
        taxi_contractor_orders_multioffer,
        taxi_contractor_orders_multioffer_monitor,
        pgsql,
        stq,
        match_tag,
        enable_doaa_call,
        is_airport,
        params,
        paid_supply_drivers,
        multioffer_version,
        version_check,
        experiments3,
):
    taxi_config.set_values(cfo.create_version_settings(multioffer_version))
    experiments3.add_config(
        **cfo.experiment3(tag=match_tag, enable_doaa=enable_doaa_call),
    )

    await taxi_contractor_orders_multioffer.tests_control(reset_metrics=True)
    response = await taxi_contractor_orders_multioffer.post(
        '/v1/contractor-for-order', json=params,
    )
    uber_matched = match_tag == 'uberdriver' and (not is_airport)
    assert response.status_code == 200
    assert response.json()['message'] == (
        'delayed'
        if uber_matched and enable_doaa_call and version_check
        else 'irrelevant'
    )

    metrics = await taxi_contractor_orders_multioffer_monitor.get_metric(
        'multioffer_match',
    )
    multioffer_matched = uber_matched and version_check
    multioffer_unmatched = not is_airport and (
        not uber_matched or not version_check
    )
    assert metrics['total_orders'] == int(not is_airport)
    assert metrics['airport_orders'] == int(is_airport)
    assert metrics['orders_unmatched'] == int(multioffer_unmatched)
    assert metrics['uber_offers_matched'] == int(multioffer_matched)
    assert metrics['uber_offers_not_enough_candidates'] == 0
    assert metrics['other_offers_matched'] == 0

    nearest_zone = params['order']['nearest_zone']
    assert metrics[nearest_zone]
    assert metrics[nearest_zone]['total_orders'] == int(not is_airport)
    assert metrics[nearest_zone]['airport_orders'] == int(is_airport)
    assert metrics[nearest_zone]['orders_unmatched'] == int(
        multioffer_unmatched,
    )
    assert metrics[nearest_zone]['uber_offers_matched'] == int(
        multioffer_matched,
    )
    assert metrics[nearest_zone]['uber_offers_not_enough_candidates'] == 0

    if multioffer_matched:
        segment_metrics = metrics[nearest_zone]['test_multioffer']
        assert segment_metrics['matched'] == 1
        assert segment_metrics['candidates_to_play_avg'] == 2
        assert segment_metrics['tags_to_play_avg'] == 1

    if uber_matched and enable_doaa_call and version_check:
        assert stq.contractor_orders_multioffer_assign.times_called == 1
        kwargs = stq.contractor_orders_multioffer_assign.next_call()['kwargs']
        assert kwargs['order_id'] == 'order_id'
        assert kwargs['multioffer_timeout'] == cfo.MULTIOFFER_TIMEOUT
        assert len(kwargs['drivers']) == 2

    multioffer = pgh.select_recent_multioffer(pgsql)
    if enable_doaa_call:
        assert multioffer
        if uber_matched and version_check:
            assert multioffer['status'] == 'in_progress'
            assert multioffer['settings'] == {
                'multioffer_timeout': cfo.MULTIOFFER_TIMEOUT,
                'offer_timeout': cfo.OFFER_TIMEOUT,
                'play_timeout': cfo.PLAY_TIMEOUT,
                'lag_compensation_timeout': cfo.LAG_COMPENSATION_TIMEOUT,
                'max_waves': 1,
                'dispatch_type': cfo.DISPATCH_TYPE,
            }
        else:
            assert multioffer['status'] == 'irrelevant'

        if uber_matched and version_check:
            pgh.check_paid_supply_drivers(
                pgsql, paid_supply_drivers, multioffer['id'],
            )


@pytest.mark.parametrize('enable_doaa_call', [True, False])
async def test_contractor_for_order_single_driver_from_candidates(
        taxi_contractor_orders_multioffer,
        taxi_contractor_orders_multioffer_monitor,
        pgsql,
        enable_doaa_call,
        experiments3,
        candidates,
):
    candidates.ids = set([candidates.ids.pop()])
    experiments3.add_config(
        **cfo.experiment3(tag='uberdriver', enable_doaa=enable_doaa_call),
    )

    await taxi_contractor_orders_multioffer.tests_control(reset_metrics=True)
    response = await taxi_contractor_orders_multioffer.post(
        '/v1/contractor-for-order', json=cfo.DEFAULT_PARAMS,
    )

    assert response.status_code == 200
    assert response.json()['message'] == 'irrelevant'

    metrics = await taxi_contractor_orders_multioffer_monitor.get_metric(
        'multioffer_match',
    )
    assert metrics['one_candidate_orders'] == 1
    assert metrics['moscow']['one_candidate_orders'] == 1

    multioffer = pgh.select_recent_multioffer(pgsql)
    if enable_doaa_call:
        assert multioffer
        assert multioffer['status'] == 'irrelevant'
