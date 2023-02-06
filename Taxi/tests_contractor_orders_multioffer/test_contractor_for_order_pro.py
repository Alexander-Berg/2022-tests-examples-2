import pytest

from tests_contractor_orders_multioffer import contractor_for_order as cfo
from tests_contractor_orders_multioffer import pg_helpers as pgh


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
@pytest.mark.now('2020-03-20T11:22:33.123456Z')
@pytest.mark.parametrize('match_pro', [True, False])
async def test_contractor_for_order_pro(
        taxi_contractor_orders_multioffer,
        taxi_contractor_orders_multioffer_monitor,
        taxi_config,
        experiments3,
        match_pro,
):
    taxi_config.set_values(cfo.create_version_settings('1.00'))
    experiments3.add_config(
        **cfo.experiment3(
            tag='!some_missing_tag' if match_pro else '!uberdriver',
            enable_doaa=True,
        ),
    )

    await taxi_contractor_orders_multioffer.tests_control(reset_metrics=True)
    response = await taxi_contractor_orders_multioffer.post(
        '/v1/contractor-for-order', json=cfo.DEFAULT_PARAMS,
    )

    expect_message = 'delayed' if match_pro else 'irrelevant'
    assert response.status_code == 200
    assert response.json()['message'] == expect_message

    metrics = await taxi_contractor_orders_multioffer_monitor.get_metric(
        'multioffer_match',
    )
    assert metrics['total_orders'] == 1
    assert metrics['orders_unmatched'] == int(not match_pro)
    assert metrics['other_offers_matched'] == int(match_pro)

    assert metrics['moscow']
    assert metrics['moscow']['total_orders'] == 1
    assert metrics['moscow']['orders_unmatched'] == int(not match_pro)


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
@pytest.mark.now('2020-03-20T11:22:33.123456Z')
@pytest.mark.parametrize('limit_all', [True, False], ids=['limit_all', ''])
@pytest.mark.parametrize('limit_uber', [True, False], ids=['limit_uber', ''])
@pytest.mark.parametrize('mixed', [True, False], ids=['mixed', ''])
async def test_contractor_for_order_additional_pro(
        taxi_contractor_orders_multioffer,
        taxi_contractor_orders_multioffer_monitor,
        taxi_config,
        experiments3,
        pgsql,
        limit_all,
        limit_uber,
        mixed,
):
    tags_limit = [('uberdriver', 1 if limit_uber else 2)]
    if mixed:
        tags_limit.append(('!uberdriver', 1))

    taxi_config.set_values(cfo.create_version_settings('1.00'))
    experiments3.add_config(
        **cfo.experiment3(
            tag='uberdriver',
            contractor_limit=2 if limit_all else 10,
            tags_limit=tags_limit,
            enable_doaa=True,
        ),
    )

    await taxi_contractor_orders_multioffer.tests_control(reset_metrics=True)
    response = await taxi_contractor_orders_multioffer.post(
        '/v1/contractor-for-order', json=cfo.DEFAULT_PARAMS,
    )

    matched = not limit_uber or mixed
    matched_mixed = mixed and (limit_uber or not limit_all)
    tags_to_play = (2 if matched_mixed else 1) if matched else 0
    assert response.status_code == 200
    assert response.json()['message'] == 'delayed' if matched else 'irrelevant'

    multioffer = pgh.select_recent_multioffer(pgsql)
    assert multioffer
    assert multioffer['status'] == 'in_progress' if matched else 'irrelevant'

    drivers = pgh.select_multioffer_drivers(pgsql, multioffer['id'])
    candidates_to_play = 0
    if matched:
        driver_uber1 = '4bb5a0018d9641c681c1a854b21ec9ab'
        driver_uber2 = 'e26e1734d70b46edabe993f515eda54e'
        driver_pro = 'fc7d65d48edd40f9be1ced0f08c98dcd'
        assert drivers
        assert drivers.pop(0)['driver_profile_id'] == driver_uber1
        candidates_to_play += 1
        if not limit_uber:
            assert drivers.pop(0)['driver_profile_id'] == driver_uber2
            candidates_to_play += 1
        if matched_mixed:
            assert drivers.pop(0)['driver_profile_id'] == driver_pro
            candidates_to_play += 1
    assert not drivers

    metrics = await taxi_contractor_orders_multioffer_monitor.get_metric(
        'multioffer_match',
    )

    assert metrics['total_orders'] == 1
    assert metrics['orders_unmatched'] == 0
    assert metrics['other_offers_matched'] == 0
    assert metrics['mixed_offers_matched'] == int(matched_mixed)

    assert metrics['moscow']
    assert metrics['moscow']['total_orders'] == 1
    assert metrics['moscow']['orders_unmatched'] == 0
    assert metrics['moscow']['mixed_offers_matched'] == int(matched_mixed)

    segment_metrics = metrics['moscow']['test_multioffer']
    assert segment_metrics['matched'] == int(matched)
    assert segment_metrics['mixed'] == int(matched_mixed)
    assert segment_metrics['candidates_to_play_avg'] == candidates_to_play
    assert segment_metrics['tags_to_play_avg'] == tags_to_play
