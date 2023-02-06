# pylint: disable=import-error
import datetime
import json

import pytest
import reposition_api.fbs.v1.airport_queue.state.Request as StateRequest

import tests_dispatch_airport_view.utils as utils


DRIVERS_UPDATER = 'drivers-updater'


@pytest.mark.busy_drivers(
    busy_drivers=[
        {
            'driver_id': 'dbid_uuid1',
            'order_id': 'order_id_1',
            'taxi_status': 3,
            'final_destination': {
                'lat': 56.7454424257098,
                'lon': 60.80503137898187,
            },
        },
        {
            'driver_id': 'dbid_uuid2',
            'order_id': 'order_id_2',
            'taxi_status': 3,
            'final_destination': {
                'lat': 56.39818246923726,
                'lon': 61.92396961914058,
            },
        },
    ],
)
@pytest.mark.config(
    DISPATCH_AIRPORT_TAGS_QUEUING={
        '__default__': {
            'allow': ['airport_queue_test_allow_tag'],
            'deny': ['airport_queue_test_deny_tag'],
        },
    },
)
@pytest.mark.config(TAGS_INDEX={'enabled': True})
@pytest.mark.tags_v2_index(
    tags_list=[
        ('dbid_uuid', 'dbid_uuid5', 'airport_queue_fraud_detected'),
        ('dbid_uuid', 'dbid_uuid6', 'airport_queue_test_allow_tag'),
        ('dbid_uuid', 'dbid_uuid7', 'airport_queue_test_allow_tag'),
        ('dbid_uuid', 'dbid_uuid7', 'airport_queue_test_deny_tag'),
    ],
    topic_relations=[
        ('airport_queue', 'airport_queue_fraud_detected'),
        ('airport_queue', 'airport_queue_test_allow_tag'),
        ('airport_queue', 'airport_queue_test_deny_tag'),
    ],
)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.parametrize('demand', [0, 1])
async def test_mixed_mode(
        taxi_dispatch_airport_view,
        mockserver,
        now,
        testpoint,
        redis_store,
        mode,
        demand,
):
    number_of_drivers = 8

    @mockserver.json_handler('/dispatch-airport/v1/pins_info')
    def _pins_info(_):
        return {
            'ekb': [
                {
                    'allowed_class': 'econom',
                    'expected_wait_time': 3000,
                    'demand': demand,
                },
                {
                    'allowed_class': 'comfortplus',
                    'expected_wait_time': 1000,
                    'demand': demand,
                },
                {'allowed_class': 'business', 'demand': demand},
            ],
        }

    @mockserver.json_handler('/candidates/profiles')
    def _candidates(request):
        assert sorted(request.json['data_keys']) == [
            'classes',
            'unique_driver_id',
        ]
        return {
            'drivers': [
                {
                    'classes': ['econom', 'comfortplus', 'business'],
                    'dbid': 'dbid',
                    'position': [0, 0],
                    'uuid': 'uuid' + str(i),
                    'unique_driver_id': 'udid' + str(i),
                }
                for i in range(number_of_drivers)
            ],
        }

    @mockserver.handler('/reposition-api/v1/service/airport_queue/state')
    def _reposition_api(request):
        request = StateRequest.Request.GetRootAsRequest(request.get_data(), 0)
        assert request.AirportQueueId() == b'ekb'

        drivers = [
            {'dbid': 'dbid', 'uuid': 'uuid3'},
            {
                'dbid': 'dbid',
                'uuid': 'uuid4',
                'mode': 'Airport',
                'is_dispatch_airport_pin': True,
            },
        ]
        return mockserver.make_response(
            response=utils.generate_reposition_drivers(drivers),
            headers={'Content-Type': 'application/x-flatbuffers'},
        )

    @testpoint('position-processor-finished')
    def position_processor_finished(_):
        pass

    @testpoint('candidate_with_udid')
    def candidate_with_udid(_):
        pass

    @testpoint(DRIVERS_UPDATER + '-finished')
    def drivers_updater_finished(data):
        return data

    # dbid_uuid0 - old mode driver
    # dbid_uuid1 - has order
    # dbid_uuid2 - has order into a different airport
    # dbid_uuid3 - has repo
    # dbid_uuid4 - has old_mode repo
    # dbid_uuid5 - has forbidden tag - always not allowed
    # dbid_uuid6 - has allowed tag - always allowed
    # dbid_uuid7 - has allowed and denied tags - like old_mode driver

    await taxi_dispatch_airport_view.enable_testpoints()
    await taxi_dispatch_airport_view.invalidate_caches()

    geobus_now = now + datetime.timedelta(minutes=2)
    geobus_drivers = {
        'dbid_uuid'
        + str(i): {
            'position': utils.NEAR_EKB_AIRPORT_1,
            'timestamp': geobus_now,
        }
        for i in range(number_of_drivers)
    }
    message = utils.edge_channel_message(geobus_drivers, now)
    redis_store.publish(utils.EDGE_TRACKS_CHANNEL, message)
    await position_processor_finished.wait_call()

    await taxi_dispatch_airport_view.run_distlock_task(DRIVERS_UPDATER)
    await drivers_updater_finished.wait_call()

    assert candidate_with_udid.times_called == 8

    for i in range(number_of_drivers):
        driver_id = 'dbid_uuid' + str(i)
        response = redis_store.hgetall(utils.driver_info_key(driver_id))
        pins_answer = json.loads(response.pop(b'pins'))
        pin_state = utils.PinState.kAllowedAll
        not_allowed_reason = None
        class_wait_times = {
            'econom': 3000,
            'comfortplus': 1000,
            'business': None,
        }

        old_mode_drivers = ['dbid_uuid0', 'dbid_uuid7']
        if mode != 'old':
            if demand == 0 and driver_id in old_mode_drivers:
                if mode == 'new':
                    pin_state = utils.PinState.kNotAllowed
                    not_allowed_reason = 'full_queue_with_time'
                elif mode == 'mixed_base_old':
                    pin_state = utils.PinState.kAllowedOldMode
                    class_wait_times.pop('comfortplus')
                elif mode == 'mixed_base_new':
                    pin_state = utils.PinState.kAllowedOldMode
                    class_wait_times = {'econom': 3000}

            # for drivers on order only old_mode and target airport
            # pins are allowed
            if driver_id == 'dbid_uuid2':
                pin_state = utils.PinState.kNotAllowed
                not_allowed_reason = 'wrong_input_order'
                class_wait_times = {
                    'econom': 3000,
                    'comfortplus': 1000,
                    'business': None,
                }

            # driver on old_mode reposition has pin_state allowed_old_mode,
            # when airport_mode != old
            # but the tariffs are filtered only if the airport mode is mixed
            if driver_id == 'dbid_uuid4':
                pin_state = utils.PinState.kAllowedOldMode
                if mode == 'mixed_base_old':
                    class_wait_times.pop('comfortplus')
                elif mode == 'mixed_base_new':
                    class_wait_times = {'econom': 3000}

        pins_answer_etalon = [
            {
                'airport_id': 'ekb',
                'class_wait_times': class_wait_times,
                'pin_point': [60.80503137898187, 56.7454424257098],
                'state': int(pin_state),
            },
        ]
        if not_allowed_reason is not None:
            pins_answer_etalon[0]['not_allowed_reason'] = not_allowed_reason

        # pin for driver with forbidden tag is always not allowed
        if driver_id == 'dbid_uuid5':
            pins_answer_etalon[0]['state'] = 2
            pins_answer_etalon[0]['not_allowed_reason'] = 'anti_fraud_tag'

        assert pins_answer == pins_answer_etalon
