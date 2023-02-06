import pytest

DETECTORS_CONFIG = {
    'proxy_lateness': {
        'events_settings': [
            {'enabled': True, 'delay_sec': 0, 'order_event': 'created'},
            {
                'enabled': True,
                'delay_sec': 0,
                'order_event': 'promise_changed',
            },
        ],
    },
}

LATENESS_SETTINGS = {
    'first_interval_before_promise_sec': 600,
    'second_interval_before_promise_sec': 300,
    'maximal_courier_eta_delay_sec': 180,
    'maximal_fast_orders_lifetime_sec': 1260,  # 21 minutes
}

CONFIG_LATENESS_ON = pytest.mark.experiments3(
    name='eats_proactive_support_lateness_detector',
    consumers=['eats_proactive_support/lateness_detector'],
    default_value={'enabled': True},
    is_config=True,
)

CONFIG_LATENESS_OFF = pytest.mark.experiments3(
    name='eats_proactive_support_lateness_detector',
    consumers=['eats_proactive_support/lateness_detector'],
    default_value={'enabled': False},
    is_config=True,
)


def assert_db_problems(psql, expected_db_problems_count):
    cursor = psql.cursor()
    cursor.execute('SELECT * FROM eats_proactive_support.problems;')
    db_problems = cursor.fetchall()
    assert len(db_problems) == expected_db_problems_count


def assert_db_actions(psql, expected_db_actions_count):
    cursor = psql.cursor()
    cursor.execute('SELECT * FROM eats_proactive_support.actions;')
    db_actions = cursor.fetchall()
    assert len(db_actions) == expected_db_actions_count


@pytest.mark.config(EATS_PROACTIVE_SUPPORT_DETECTORS_SETTINGS=DETECTORS_CONFIG)
@pytest.mark.config(EATS_PROACTIVE_SUPPORT_PROBLEM_LATENESS=LATENESS_SETTINGS)
@CONFIG_LATENESS_ON
@pytest.mark.pgsql('eats_proactive_support', files=['fill_orders.sql'])
@pytest.mark.parametrize(
    """order_nr,expected_stq_detections_count""",
    [('123', 1)],
    ids=['lateness_enabled'],
)
async def test_proxy_lateness_detector_enabled(
        stq_runner, pgsql, stq, order_nr, expected_stq_detections_count,
):
    await stq_runner.eats_proactive_support_detections.call(
        task_id='123',
        kwargs={
            'order_nr': order_nr,
            'event_name': 'created',
            'detector_name': 'proxy_lateness',
        },
    )

    assert_db_problems(pgsql['eats_proactive_support'], 0)
    assert_db_actions(pgsql['eats_proactive_support'], 0)

    assert stq.eats_proactive_support_actions.times_called == 0
    assert (
        stq.eats_proactive_support_detections.times_called
        == expected_stq_detections_count
    )

    if stq.eats_proactive_support_detections.times_called != 0:
        task = stq.eats_proactive_support_detections.next_call()
        assert task['queue'] == 'eats_proactive_support_detections'
        assert task['kwargs']['order_nr'] == order_nr
        assert (
            task['kwargs']['promised_at_for_lateness_detector']
            == '2020-04-28T09:00:00+00:00'
        )
        assert task['kwargs']['detector_name'] == 'lateness'
        assert task['kwargs']['event_name'] == 'lateness'


@pytest.mark.config(EATS_PROACTIVE_SUPPORT_DETECTORS_SETTINGS=DETECTORS_CONFIG)
@CONFIG_LATENESS_OFF
@pytest.mark.pgsql('eats_proactive_support', files=['fill_orders.sql'])
@pytest.mark.parametrize(
    """order_nr,expected_stq_detections_count""",
    [('124', 0)],
    ids=['lateness_disabled'],
)
async def test_proxy_lateness_detector_disabled(
        stq_runner, pgsql, stq, order_nr, expected_stq_detections_count,
):
    await stq_runner.eats_proactive_support_detections.call(
        task_id='123',
        kwargs={
            'order_nr': order_nr,
            'event_name': 'created',
            'detector_name': 'proxy_lateness',
        },
    )

    assert_db_problems(pgsql['eats_proactive_support'], 0)
    assert_db_actions(pgsql['eats_proactive_support'], 0)

    assert stq.eats_proactive_support_actions.times_called == 0
    assert (
        stq.eats_proactive_support_detections.times_called
        == expected_stq_detections_count
    )

    if stq.eats_proactive_support_detections.times_called != 0:
        task = stq.eats_proactive_support_detections.next_call()
        assert task['queue'] == 'eats_proactive_support_detections'
        assert task['kwargs']['order_nr'] == order_nr
        assert task['kwargs']['detector_name'] == 'lateness'
        assert task['kwargs']['event_name'] == 'lateness'


@pytest.mark.config(EATS_PROACTIVE_SUPPORT_DETECTORS_SETTINGS=DETECTORS_CONFIG)
@pytest.mark.config(EATS_PROACTIVE_SUPPORT_PROBLEM_LATENESS=LATENESS_SETTINGS)
@CONFIG_LATENESS_ON
@pytest.mark.pgsql('eats_proactive_support', files=['fill_orders.sql'])
@pytest.mark.parametrize(
    """order_nr,expected_stq_detections_count""",
    [('125', 1)],
    ids=['lateness_enabled'],
)
async def test_proxy_lateness_detector_enabled_slots(
        mockserver,
        stq_runner,
        pgsql,
        stq,
        order_nr,
        expected_stq_detections_count,
):
    @mockserver.json_handler(
        '/eats-core-orders/internal-api/v1/order/125/metainfo',
    )
    def _eda_core_order_metainfo_(request):
        return {
            'order_nr': '220222-504325',
            'location_latitude': 55.754638,
            'location_longitude': 37.621642,
            'is_asap': False,
            'place_id': '305715',
            'region_id': '1',
            'place_delivery_zone_id': '1534846',
            'app': 'web',
            'status': 'payed',
            'city': 'Москва',
            'street': 'Красная площадь',
            'house': '3',
            'currency': 'RUB',
            'order_status_history': {
                'call_center_confirmed_at': '2022-02-22T12:28:27+03:00',
                'created_at': '2022-02-22T12:28:24+03:00',
            },
            'order_integration_info': {'origin_id': '19949'},
            'order_user_information': {
                'eater_id': '177017614',
                'yandex_uid': '4078350126',
                'personal_phone_id': '68d08b8bb4f84030a6805e7d7b74549a',
                'personal_email_id': '608255a5b09d49dca6a722949c406aaf',
                'device_id': 'kr3ava66-17mtzn8cdwi-rxmqor1f4d-k6s0w4hf9qm',
            },
            'order_delivery_timing_offers': {
                'cooking_time_minutes': 32,
                'total_delivery_time_minutes': 62,
                'route_time_minutes': 30,
                'delivery_date': '2022-02-22T15:30:00+03:00',
            },
            'order_meta_information': {
                'meta_information': {
                    'type': 'slot_interval',
                    'decimal_price': True,
                    'our_pickup_type': 'dedicated_picker',
                    'delivery_slot_started_at': '2022-02-22T15:30:00+03:00',
                    'delivery_slot_finished_at': '2022-02-22T16:30:00+03:00',
                },
            },
            'business_type': 'retail',
            'shipping_type': 'native',
            'assembly_type': 'our_picker',
        }

    await stq_runner.eats_proactive_support_detections.call(
        task_id='125',
        kwargs={
            'order_nr': order_nr,
            'event_name': 'created',
            'detector_name': 'proxy_lateness',
        },
    )

    assert_db_problems(pgsql['eats_proactive_support'], 0)
    assert_db_actions(pgsql['eats_proactive_support'], 0)

    assert stq.eats_proactive_support_actions.times_called == 0
    assert _eda_core_order_metainfo_.times_called == 1
    assert (
        stq.eats_proactive_support_detections.times_called
        == expected_stq_detections_count
    )

    if stq.eats_proactive_support_detections.times_called != 0:
        task = stq.eats_proactive_support_detections.next_call()
        assert task['queue'] == 'eats_proactive_support_detections'
        assert task['kwargs']['order_nr'] == order_nr
        assert (
            task['kwargs']['promised_at_for_lateness_detector']
            == '2022-02-22T13:30:00+00:00'
        )
        assert task['kwargs']['detector_name'] == 'lateness'
        assert task['kwargs']['event_name'] == 'lateness'
