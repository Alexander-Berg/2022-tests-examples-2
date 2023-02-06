# pylint: disable=import-error
import copy
import datetime
import enum

import flatbuffers
import pytz
import reposition_api.fbs.v1.airport_queue.state.AirportStateResponse as RepositionApiAirportState  # noqa: E501
import reposition_api.fbs.v1.airport_queue.state.Response as RepositionApiResponse  # noqa: E501
from reposition_api.fbs.v1.service.make_offer import OfferResponse
from reposition_api.fbs.v1.service.make_offer import (
    Request as MakeOfferRequest,
)
from reposition_api.fbs.v1.service.make_offer import (
    Response as MakeOfferResponse,
)

from geobus_tools import geobus  # noqa: F401 C5521
from tests_plugins import utils

AIRPORT_QUEUE_TAG = 'airport_queue_driver'
AIRPORT_ENTERED_TAG = 'airport_entered_driver'
POS_PROCESSOR_NAME = 'driver-pos-processor'
QUEUE_UPDATER_NAME = 'queue-update'
EDGE_TRACKS_CHANNEL = 'channel:yaga:edge_positions'
RAW_POSITIONS_CHANNEL = 'channel:yagr:position'

# Format: (lon, lat)
OUT_POSITION = [14, 9]
NOTIFICATION_POSITION = [16, 6]
WAITING_POSITION = [21, 11]
AIRPORT_POSITION = [26, 16]

SVO_WAITING_POSITION = [61, 11]
SVO_NOTIFICATION_POSITION = [56, 6]
SVO_AIRPORT_POSITION = [70, 20]
SVO_OUT_POSITION = [89, 89]


class State(enum.IntEnum):
    kEntered = 0
    kQueued = 1
    kFiltered = 2


class Reason:
    kOnAction = 'on_action'
    kOnActionTooLate = 'on_action_too_late'
    kOnReposition = 'on_reposition'
    kOnRepositionOldMode = 'on_reposition_old_mode'
    kOnTag = 'on_tag'
    kOnRepeatQueue = 'on_repeat_queue'
    kUnknownReposition = 'unknown_reposition'
    kOldMode = 'old_mode'
    kHolded = 'holded'
    kFullQueue = 'full_queue'
    kLeftZone = 'left_zone'
    kFilterQueuedLeftZone = 'filter_queued_left_zone'
    kChangeTariff = 'changed_tariff'
    kGps = 'gps'
    kQueuedGps = 'queued_gps'
    kMaxQueueTimeExceed = 'max_queue_time'
    kBlacklist = 'blacklist'
    kAntiFraudTag = 'anti_fraud_tag'
    kUserCancel = 'user_cancel'
    kDriverCancel = 'driver_cancel'
    kOffline = 'offline'
    kQueuedOffline = 'queued_offline'
    kNoClasses = 'no_classes'
    kWrongClient = 'wrong_client'
    kWrongProvider = 'wrong_provider'
    kInputOrderWithoutDestination = 'input_order_without_destination'
    kNotAirportInputOrder = 'not_airport_input_order'
    kNotAllowedAreaInputOrder = 'not_allowed_area_input_order'
    kWrongGroupInputOrder = 'wrong_group_input_order'
    kLowOrderPrice = 'low_order_price'
    kWrongOutputOrder = 'wrong_output_order'
    kForbiddenByPartner = 'forbidden_by_partner'
    kFreezeExpired = 'freeze_expired'
    kNonAirportReposition = 'non_airport_reposition'
    kWithoutActiveRfidLabel = 'without_active_rfid_label'


def get_state(state):
    if isinstance(state, str):
        if state == 'entered':
            return State.kEntered
        if state == 'queued':
            return State.kQueued
        return State.kFiltered
    if isinstance(state, int):
        return State(state)
    return state


def get_old_mode_enabled(mode):
    return mode in ['old', 'mixed_base_old']


def set_mode_in_config(
        taxi_config, mode, zone='ekb', enabled_driver_config_filter=False,
):
    zones_config = taxi_config.get('DISPATCH_AIRPORT_ZONES')
    zones_config[zone]['old_mode_enabled'] = mode in ['old', 'mixed_base_old']
    if mode in ['mixed_base_old', 'mixed_base_new']:
        zones_config[zone]['mixed_mode_enabled'] = True
    if mode == 'mixed_base_old':
        zones_config[zone]['whitelist_classes']['comfortplus'][
            'old_mode_tariff'
        ] = False
    elif mode == 'mixed_base_new':
        zones_config[zone]['whitelist_classes']['econom'][
            'old_mode_tariff'
        ] = True
    taxi_config.set_values({'DISPATCH_AIRPORT_ZONES': zones_config})
    if enabled_driver_config_filter:
        taxi_config.set_values(
            {
                'DISPATCH_AIRPORT_MIXED_MODE_ALLOWED_DRIVERS': {
                    'enabled': True,
                    'allowed_drivers': [],
                },
            },
        )


def get_drivers_queue(db):
    cursor = db.cursor()
    cursor.execute('SELECT driver_id FROM dispatch_airport.drivers_queue;')
    return sorted([r[0] for r in cursor])


def _get_areas(areas):
    return sorted([area.strip('{} ') for area in areas.split(',')])


def _get_field(name, field):
    if name == 'areas':
        return _get_areas(field)
    return field


def get_drivers_queue_full(db):
    cursor = db.cursor()
    cursor.execute(
        'SELECT driver_id,'
        'state,'
        'reason,'
        'entered,'
        'heartbeated,'
        'updated,'
        'queued,'
        'airport,'
        'areas,'
        'classes,'
        'taximeter_tariffs,'
        'input_order_id,'
        'reposition_session_id,'
        'details,'
        'airport_tag_deadline,'
        'last_freeze_started_tp,'
        'class_queued,'
        'left_queue_started_tp,'
        'car_number,'
        'offline_started_tp,'
        'offline_total,'
        'input_order_finished_tp,'
        'old_mode_enabled,'
        'no_classes_started_tp,'
        'car_id,'
        'change_tariff_started_tp,'
        'freeze_total,'
        'forbidden_by_partner_started_tp,'
        'driver_mode,'
        'filtered_tp'
        ' FROM dispatch_airport.drivers_queue;',
    )
    names = (
        'driver_id',
        'state',
        'reason',
        'entered',
        'heartbeated',
        'updated',
        'queued',
        'airport',
        'areas',
        'classes',
        'taximeter_tariffs',
        'input_order_id',
        'reposition_session_id',
        'details',
        'airport_tag_deadline',
        'last_freeze_started_tp',
        'class_queued',
        'left_queue_started_tp',
        'car_number',
        'offline_started_tp',
        'offline_total',
        'input_order_finished_tp',
        'old_mode_enabled',
        'no_classes_started_tp',
        'car_id',
        'change_tariff_started_tp',
        'freeze_total',
        'forbidden_by_partner_started_tp',
        'driver_mode',
        'filtered_tp',
    )
    queue = [
        {names[i]: _get_field(names[i], r[i]) for i in range(len(names))}
        for r in cursor
    ]
    return sorted(queue, key=lambda x: x['driver_id'])


def get_driver_events(db, udid=None, no_event_id=False):
    cursor = db.cursor()
    if udid:
        cursor.execute(
            f"""
            SELECT udid, event_id, event_type, driver_id, airport_id, details
            FROM dispatch_airport.driver_events
            WHERE udid = '{udid}';
        """,
        )
    else:
        cursor.execute(
            """
              SELECT udid, event_id, event_type, driver_id, airport_id, details
              FROM dispatch_airport.driver_events
              ORDER BY udid, event_id, event_type, airport_id;
          """,
        )
    result = {}
    for (
            result_udid,
            event_id,
            event_type,
            driver_id,
            airport_id,
            details,
    ) in cursor:
        key = (
            (result_udid, event_type)
            if no_event_id
            else (result_udid, event_id, event_type)
        )
        result[key] = {'airport_id': airport_id, 'driver_id': driver_id}
        if details is not None:
            taximeter_tariffs = details.get('relocation_info', {}).get(
                'taximeter_tariffs',
            )
            if taximeter_tariffs is not None:
                taximeter_tariffs.sort()
            result[key]['details'] = details
    return result


def get_driver_session_id(db, dbid_uuid):
    cursor = db.cursor()
    cursor.execute(
        f"""
      SELECT details->'session_id'
      FROM dispatch_airport.drivers_queue
      WHERE driver_id = '{dbid_uuid}';""",
    )
    return [r[0] for r in cursor][0]


def is_driver_exists(db, dbid_uuid, airport):
    cursor = db.cursor()
    cursor.execute(
        f"""
    SELECT EXISTS(
      SELECT *
      FROM dispatch_airport.drivers_queue
      WHERE driver_id='{dbid_uuid}' AND airport='{airport}'
    );""",
    )
    return list(cursor)[0][0]


def unix_time(timestamp):
    return int(utils.timestamp(timestamp))


def generate_candidates_response(driver_ids, classes):
    driver_numbers = [driver_id[9:] for driver_id in driver_ids]
    return {
        'drivers': [
            {
                'classes': classes,
                'dbid': 'dbid',
                'position': [0, 0],
                'unique_driver_id': 'udid' + str(i),
                'uuid': 'uuid' + str(i),
                'car_id': 'car_id_' + str(i),
            }
            for i in driver_numbers
        ],
    }


def generate_categories_response(driver_ids, classes):
    driver_numbers = [driver_id[4:] for driver_id in driver_ids]
    return {
        'drivers': [
            {
                'car_id': 'car_id_' + str(i),
                'categories': classes,
                'driver_id': 'uuid' + str(i),
                'park_id': 'dbid',
            }
            for i in driver_numbers
        ],
    }


def edge_channel_message(drivers, now):
    drivers = [
        {
            'driver_id': driver_id,
            'position': info['position'],
            'timestamp': unix_time(info['timestamp']) * 1000,  # milliseconds
        }
        for driver_id, info in drivers.items()
    ]
    return geobus.serialize_edge_positions_v2(drivers, now)


def raw_positions_channel_message(drivers, now):
    drivers = [
        {
            'driver_id': driver_id,
            'position': info['position'],
            'direction': 45,
            'timestamp': unix_time(info['timestamp']),
            'speed': 10,
            'accuracy': 1,
        }
        for driver_id, info in drivers.items()
    ]
    return geobus.serialize_positions_v2(drivers, now)


def publish_positions(redis_store, drivers, now, edge=True):
    if edge:
        message = edge_channel_message(drivers, now)
        redis_store.publish(EDGE_TRACKS_CHANNEL, message)
    else:
        message = raw_positions_channel_message(drivers, now)
        redis_store.publish(RAW_POSITIONS_CHANNEL, message)


def get_numbered_areas(areas):
    if not areas or isinstance(areas[0], int):
        return areas
    numbered_areas = []
    if 'notification' in areas:
        numbered_areas.append(2)
    if 'waiting' in areas:
        numbered_areas.append(1)
    if 'main' in areas:
        numbered_areas.append(0)
    return sorted(numbered_areas)


def update_etalons_by_simulation_old_queue_filter_processing(
        updated_etalons, mode, delayed_processing=(),
):  # pylint: disable=C0103
    for driver_id, driver in updated_etalons.items():
        if driver_id in delayed_processing:
            continue

        if driver['reason'] in [
                '',
                Reason.kOldMode,
                Reason.kOnRepositionOldMode,
        ]:
            if mode == 'new' and driver['reason'] == '':
                driver['reason'] = Reason.kFullQueue
                driver['state'] = State.kFiltered
            else:
                if driver['reason'] != Reason.kOnRepositionOldMode:
                    driver['reason'] = Reason.kOldMode
                if mode in ['mixed_base_old', 'mixed_base_new']:
                    driver['classes'].remove('comfortplus')


def check_drivers(driver, etalon):
    # print('driver = ', driver)
    # print('etalon = ', etalon)
    assert driver['driver_id'] == etalon['driver_id']
    assert get_state(driver['state']) == get_state(etalon['state'])
    assert driver['reason'] == etalon['reason']

    if get_state(driver['state']) == State.kFiltered:
        assert driver['filtered_tp'] is not None
    else:
        assert driver['filtered_tp'] is None

    if 'filtered_tp' in etalon:
        local = pytz.timezone('UTC')
        assert driver['filtered_tp'] == local.localize(etalon['filtered_tp'])

    if 'updated' in etalon:
        local = pytz.timezone('UTC')
        assert driver['updated'] == local.localize(etalon['updated'])

    assert driver['airport'] == etalon['airport']
    assert driver['old_mode_enabled'] == etalon.get('old_mode_enabled', True)
    assert get_numbered_areas(driver['areas']) == get_numbered_areas(
        etalon['areas'],
    )
    assert sorted(driver['classes']) == sorted(etalon['classes'])
    assert driver['reposition_session_id'] == etalon.get(
        'reposition_session_id', None,
    )
    assert driver['input_order_id'] == etalon.get('input_order_id', None)
    if 'taximeter_tariffs' in etalon:
        assert (
            sorted(driver['taximeter_tariffs']) == etalon['taximeter_tariffs']
        )
    details = driver['details']
    if 'taximeter_status' in etalon:
        assert details['taximeter_status'] == etalon['taximeter_status']
    if 'driver_very_busy_status' in etalon:
        assert (
            details['driver_very_busy_status']
            == etalon['driver_very_busy_status']
        )
    if 'reposition_session_mode' in etalon:
        assert (
            details['reposition_session_mode']
            == etalon['reposition_session_mode']
        )
    if driver['state'] == State.kQueued:
        assert driver['queued']
    if 'details' in etalon:
        assert driver['details'] == etalon['details']
    if 'in_terminal_area' in etalon:
        assert (
            driver['details']['in_terminal_area'] == etalon['in_terminal_area']
        )
    if 'force_polling_order' in etalon:
        assert details['force_polling_order'] == etalon['force_polling_order']

    if 'class_queued' in etalon:
        if etalon['class_queued'] is None:
            assert driver['class_queued'] is None
        else:
            assert len(etalon['class_queued']) == len(driver['class_queued'])
            for tariff in etalon['class_queued']:
                assert tariff in driver['class_queued']
    if 'driver_mode' in etalon:
        assert etalon['driver_mode'] == driver['driver_mode']
    if 'parking_relocation_session' in etalon:
        assert (
            details.get('parking_relocation_session')
            == etalon['parking_relocation_session']
        )
    if 'ever_available_classes' in etalon:
        assert sorted(details.get('ever_available_classes')) == sorted(
            etalon['ever_available_classes'],
        ), details.get('ever_available_classes')

    if 'last_time_driver_had_order_from_airport' in etalon:
        assert (
            details.get('last_time_driver_had_order_from_airport')
            == etalon['last_time_driver_had_order_from_airport']
        ), details.get('last_time_driver_had_order_from_airport')

    for timeout_tp in (
            'last_freeze_started_tp',
            'input_order_finished_tp',
            'left_queue_started_tp',
            'offline_started_tp',
            'forbidden_by_partner_started_tp',
            'no_classes_started_tp',
    ):
        if timeout_tp in etalon:
            assert bool(driver[timeout_tp]) == etalon[timeout_tp]


def check_drivers_pos(driver_pos, etalon):
    # print('driver = ', driver)
    # print('etalon = ', etalon)
    assert driver_pos['driver_id'] == etalon['driver_id']
    assert (
        driver_pos['is_stored_driver_update']
        == etalon['is_stored_driver_update']
    )
    assert driver_pos['airport_id'] == etalon['airport_id']
    assert get_numbered_areas(driver_pos['areas']) == get_numbered_areas(
        etalon['areas'],
    )

    if 'in_terminal_area' in etalon:
        assert driver_pos['in_terminal_area'] == etalon['in_terminal_area']
    if 'lat' in etalon:
        assert driver_pos['lat'] == etalon['lat']
    if 'lon' in etalon:
        assert driver_pos['lon'] == etalon['lon']


def check_drivers_queue(db, etalons):
    drivers_queue = get_drivers_queue_full(db)
    assert len(drivers_queue) == len(etalons)
    for (driver, etalon) in zip(
            drivers_queue, sorted(etalons, key=lambda x: x['driver_id']),
    ):
        check_drivers(driver, etalon)


def check_filter_result(filter_result, etalon):
    assert len(filter_result) == len(etalon)
    for driver in filter_result:
        driver_etalon = etalon[driver['driver_id']]
        check_drivers(driver, driver_etalon)


async def wait_certain_testpoint(task_id, updated_testpoint):
    task_airport = None
    while task_airport != task_id:
        data = await updated_testpoint.wait_call()
        task_airport = data['_']


def _reposition_api_driver(builder, driver):
    session_id = builder.CreateString(
        driver.get('session_id')
        or f'session_{driver["dbid"]}_{driver["uuid"]}',
    )
    error = builder.CreateString('')
    dbid = builder.CreateString(driver['dbid'])
    uuid = builder.CreateString(driver['uuid'])
    airport_id = builder.CreateString(driver['airport_id'])
    mode = builder.CreateString(driver.get('mode', 'Airport'))
    is_dispatch_airport_pin = driver.get('is_dispatch_airport_pin', False)
    res = RepositionApiAirportState
    res.AirportStateResponseStart(builder)
    res.AirportStateResponseAddParkDbId(builder, dbid)
    res.AirportStateResponseAddDriverProfileId(builder, uuid)
    res.AirportStateResponseAddAirportQueueId(builder, airport_id)
    res.AirportStateResponseAddSessionId(builder, session_id)
    res.AirportStateResponseAddMode(builder, mode)
    res.AirportStateResponseAddError(builder, error)
    res.AirportStateResponseAddIsDispatchAirportPin(
        builder, is_dispatch_airport_pin,
    )
    return res.AirportStateResponseEnd(builder)


def generate_reposition_api_drivers(drivers):
    builder = flatbuffers.Builder(0)
    drivers = [_reposition_api_driver(builder, driver) for driver in drivers]

    res = RepositionApiResponse
    res.ResponseStartStatesVector(builder, len(drivers))
    for driver in drivers:
        builder.PrependUOffsetTRelative(driver)
    drivers = builder.EndVector(len(drivers))

    res.ResponseStart(builder)
    res.ResponseAddStates(builder, drivers)
    obj = res.ResponseEnd(builder)
    builder.Finish(obj)
    return bytes(builder.Output())


def custom_config(old_mode_enabled):
    return {
        'DISPATCH_AIRPORT_ZONES': {
            'ekb': {
                'use_queue': False,
                'enabled': True,
                'log_tariffs_classes': True,
                'main_area': 'ekb_airport',
                'notification_area': 'ekb_airport_notification',
                'waiting_area': 'ekb_airport_waiting',
                'update_interval_sec': 2,
                'old_mode_enabled': old_mode_enabled,
                'tariff_home_zone': 'ekb_home_zone',
                'airport_title_key': 'ekb_airport_key',
                'whitelist_classes': {
                    'comfortplus': {
                        'reposition_enabled': True,
                        'nearest_mins': 30,
                    },
                    'econom': {'reposition_enabled': True, 'nearest_mins': 30},
                    'vip': {'reposition_enabled': True, 'nearest_mins': 30},
                },
            },
        },
    }


class MakeOfferFbHelper:
    def read_str(self, fbs_output):
        if not fbs_output:
            return ''
        return fbs_output.decode('utf-8')

    def parse_request(self, data):
        offers = []
        request = MakeOfferRequest.Request.GetRootAsRequest(data, 0)
        for i in range(0, request.OffersLength()):
            offer = request.Offers(i)
            tags = []
            completed_tags = []
            for tag in range(0, offer.TagsLength()):
                tags.append(self.read_str(offer.Tags(tag)))
            for tag in range(0, offer.CompletedTagsLength()):
                completed_tags.append(self.read_str(offer.CompletedTags(tag)))
            meta_request = offer.Metadata()
            meta = dict()
            if meta_request:
                queue_id = self.read_str(meta_request.AirportQueueId())
                if queue_id:
                    meta['airport_queue_id'] = queue_id
                classes = []
                for airport_cl in range(0, meta_request.ClassesLength()):
                    classes.append(
                        self.read_str(meta_request.Classes(airport_cl)),
                    )
                if classes:
                    meta['classes'] = classes
            restrictions = []
            for restriction_request_ind in range(
                    0, offer.RestrictionsLength(),
            ):
                restriction_request = offer.Restrictions(
                    restriction_request_ind,
                )
                restriction = dict()
                if restriction_request:
                    restriction['image_id'] = self.read_str(
                        restriction_request.ImageId(),
                    )
                    short_text = self.read_str(restriction_request.ShortText())
                    if short_text:
                        restriction['short_text'] = short_text
                    text = self.read_str(restriction_request.Text())
                    if text:
                        restriction['text'] = text
                    title = self.read_str(restriction_request.Title())
                    if title:
                        restriction['title'] = title
                    if restriction:
                        restrictions.append(restriction)
            offers.append(
                {
                    'park_db_id': self.read_str(offer.ParkDbId()),
                    'driver_id': self.read_str(offer.DriverId()),
                    'mode_name': self.read_str(offer.ModeName()),
                    'address': self.read_str(offer.Address()),
                    'city': self.read_str(offer.City()),
                    'start_until': datetime.datetime.fromtimestamp(
                        offer.StartUntil(), tz=datetime.timezone.utc,
                    ),
                    'finish_until': datetime.datetime.fromtimestamp(
                        offer.FinishUntil(), tz=datetime.timezone.utc,
                    ),
                    'image_id': self.read_str(offer.ImageId()),
                    'name': self.read_str(offer.Name()),
                    'description': self.read_str(offer.Description()),
                    'tags': tags,
                    'completed_tags': completed_tags,
                    'tariff_class': self.read_str(offer.TariffClass()),
                    'origin': offer.Origin(),
                    'auto_accept': offer.AutoAccept(),
                    'metadata': meta,
                    'restrictions': restrictions,
                    'draft_id': self.read_str(offer.DraftId()),
                },
            )
        return offers

    def build_response(self, data):
        builder = flatbuffers.Builder(0)
        responses = []
        for result in data:
            dbid_fbs = builder.CreateString(result['park_db_id'])
            uuid_fbs = builder.CreateString(result['driver_id'])
            point_id_fbs = builder.CreateString(result['point_id'])
            error_fbs = None
            if 'error' in result:
                error_fbs = builder.CreateString(result['error'])
            OfferResponse.OfferResponseStart(builder)
            OfferResponse.OfferResponseAddDriverId(builder, uuid_fbs)
            OfferResponse.OfferResponseAddParkDbId(builder, dbid_fbs)
            OfferResponse.OfferResponseAddPointId(builder, point_id_fbs)
            if error_fbs:
                OfferResponse.OfferResponseAddError(builder, error_fbs)
            res = OfferResponse.OfferResponseEnd(builder)
            responses.append(res)
        MakeOfferResponse.ResponseStartResultsVector(builder, len(responses))
        for response in responses:
            builder.PrependUOffsetTRelative(response)
        responses_vec = builder.EndVector(len(responses))

        MakeOfferResponse.ResponseStart(builder)
        MakeOfferResponse.ResponseAddResults(builder, responses_vec)
        response = MakeOfferResponse.ResponseEnd(builder)
        builder.Finish(response)
        return builder.Output()


def get_calls_sorted(func, number_of_calls, field, key):
    assert func.times_called == number_of_calls
    return sorted(
        [func.next_call()[field] for _ in range(number_of_calls)],
        key=lambda x: x if not key else x[key],
    )


def get_calls_sorted_two_keys(func, number_of_calls, field, key1, key2):
    assert func.times_called == number_of_calls
    values = [func.next_call()[field] for _ in range(number_of_calls)]
    return sorted(values, key=lambda x: (x[key1], x[key2]))


def check_airport_tags(tags_request, expected_queued, expected_entered=()):
    assert tags_request['entity_type'] == 'dbid_uuid'
    tags = tags_request['tags']
    queud_tags = [tag for tag in tags if tag['name'] == AIRPORT_QUEUE_TAG]
    entered_tags = [tag for tag in tags if tag['name'] == AIRPORT_ENTERED_TAG]
    assert len(queud_tags) + len(entered_tags) == len(tags), (
        queud_tags,
        entered_tags,
    )
    assert len(queud_tags) == len(expected_queued), queud_tags
    for tag in queud_tags:
        assert tag['entity'] in expected_queued
    assert len(entered_tags) == len(expected_entered), entered_tags
    for tag in entered_tags:
        assert tag['entity'] in expected_entered, tag['entity']


def get_event_session_ids(events):
    result = []
    for key in events:
        result.append(key[1])
    return sorted(result)


def transform_restrictions_to_eng(restrictions):
    results = copy.deepcopy(restrictions)
    for result in results:
        result['short_text'] = 'en: ' + result['short_text']
        result['text'] = 'en: ' + result['text']
        result['title'] = 'en: ' + result['title']
    return results
