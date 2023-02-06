# pylint: disable=import-error
import datetime

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


from geobus_tools import geobus
from tests_plugins import utils

POS_PROCESSOR_NAME = 'driver-pos-processor'
EDGE_TRACKS_CHANNEL = 'channel:yaga:edge_positions'
RAW_POSITIONS_CHANNEL = 'channel:yagr:position'


def unix_time(timestamp):
    return int(utils.timestamp(timestamp))


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


async def read_from_parking_drivers_db(pgsql):
    cursor = pgsql['dispatch_airport_partner_protocol'].cursor()
    cursor.execute(
        'SELECT '
        'driver_id, '
        'parking_id, '
        'on_parking_lot, '
        'created_ts, '
        'updated_ts, '
        'heartbeated, '
        'car_id, '
        'unique_driver_id, '
        'enabled_classes, '
        'car_number, '
        'car_number_normalized, '
        'year, '
        'mark, '
        'model, '
        'color, '
        'order_id, '
        'taxi_status, '
        'has_suitable_order, '
        'latitude, '
        'longitude, '
        'driver_diagnostics_updated_ts, '
        'driver_diagnostics_reasons, '
        'driver_status, '
        'dispatch_airport_filter_reason, '
        'dispatch_airport_times_queued, '
        'dispatch_airport_partner_parking_id, '
        'tags_block_reason, '
        'has_allowed_provider, '
        'has_reposition, '
        'reposition_api_updated_ts '
        'FROM dispatch_airport_partner_protocol.parking_drivers',
    )
    result = []
    for row in cursor:
        cur_row = {
            'driver_id': row[0],
            'parking_id': row[1],
            'on_parking_lot': row[2],
            'created_ts': row[3].astimezone(pytz.utc).isoformat(),
            'updated_ts': row[4].astimezone(pytz.utc).isoformat(),
            'heartbeated': row[5].astimezone(pytz.utc).isoformat(),
            'car_id': row[6],
            'unique_driver_id': row[7],
            'enabled_classes': row[8],
            'car_number': row[9],
            'car_number_normalized': row[10],
            'year': row[11],
            'mark': row[12],
            'model': row[13],
            'color': row[14],
            'order_id': row[15],
            'taxi_status': row[16],
            'has_suitable_order': row[17],
            'latitude': row[18],
            'longitude': row[19],
            'driver_diagnostics_updated_ts': (
                row[20].astimezone(pytz.utc).isoformat() if row[20] else None
            ),
            'driver_diagnostics_reasons': row[21],
            'driver_status': row[22],
            'dispatch_airport_filter_reason': row[23],
            'dispatch_airport_times_queued': row[24],
            'dispatch_airport_partner_parking_id': row[25],
            'tags_block_reason': row[26],
            'has_allowed_provider': row[27],
            'has_reposition': row[28],
            'reposition_api_updated_ts': (
                row[29].astimezone(pytz.utc).isoformat() if row[29] else None
            ),
        }
        result.append(cur_row)
    return result


async def get_sorted_db_drivers(pgsql):
    return sorted(
        (await read_from_parking_drivers_db(pgsql)),
        key=lambda e: (e['driver_id'], e['parking_id']),
    )


def assert_result_fields(expected_fields, actual_fields, fields_name):
    for one_expected, one_actual in zip(expected_fields, actual_fields):
        actual_selected_fields = {}
        expected_selected_fields = {}
        for name in fields_name:
            actual_selected_fields[name] = one_actual[name]
            if isinstance(actual_selected_fields[name], list):
                actual_selected_fields[name].sort()
            expected_selected_fields[name] = one_expected[name]
        assert (
            actual_selected_fields == expected_selected_fields
        ), f'{actual_selected_fields} {expected_selected_fields}'


async def compare_db_with_expected(pgsql, expected, fields_names):
    actual = await get_sorted_db_drivers(pgsql)
    assert len(actual) == len(expected), f'{len(actual)}, {len(expected)}'
    assert_result_fields(expected, actual, fields_names)


def form_driver_profile_response(request, all_driver_profiles_data):
    ids = request.json['id_in_set']
    result = {
        'profiles': [
            x
            for x in all_driver_profiles_data['profiles']
            if x['park_driver_profile_id'] in ids
        ],
    }
    return result


def form_fleet_vehicles_response(request, all_data):
    ids = request.json['id_in_set']
    result = {
        'vehicles': [
            x for x in all_data['vehicles'] if x['park_id_car_id'] in ids
        ],
    }
    return result


def form_unique_drivers_response(request, all_data):
    ids = request.json['profile_id_in_set']
    result = {
        'uniques': [
            x
            for x in all_data['uniques']
            if x['park_driver_profile_id'] in ids
        ],
    }
    return result


def form_partner_drivers_response(request, all_data):
    ids = [x['dbid_uuid'] for x in request.json['driver_ids']]
    result = {
        'queued_drivers': [
            x for x in all_data['queued_drivers'] if x['dbid_uuid'] in ids
        ],
        'filtered_drivers': [
            x for x in all_data['filtered_drivers'] if x['dbid_uuid'] in ids
        ],
    }
    return result


def form_list_cars_response(request, all_data):
    parking_id = request.json['parking_id']
    if parking_id in all_data.keys():
        return all_data[parking_id]
    return {}


def _reposition_api_driver(builder, driver):
    session_id = builder.CreateString(
        f'session_{driver["dbid"]}_{driver["uuid"]}',
    )
    error = builder.CreateString('')
    dbid = builder.CreateString(driver['dbid'])
    uuid = builder.CreateString(driver['uuid'])
    airport_id = builder.CreateString('')
    mode = builder.CreateString('')
    is_dispatch_airport_pin = False
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


def form_reposition_api_response(drivers):
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
                        offer.StartUntil(),
                    ),
                    'finish_until': datetime.datetime.fromtimestamp(
                        offer.FinishUntil(),
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


async def check_handles_metrics(
        service, monitor, mocked_time, check_issue_rfid=False,
):
    mocked_time.sleep(15)
    await service.tests_control(invalidate_caches=False)

    metrics = await monitor.get_metric(
        'dispatch_airport_partner_protocol_metrics',
    )
    is_allowed_metrics = metrics['driver_is_allowed']['parking_lot1']
    reason_metrics = metrics['driver_block_reason']['parking_lot1']

    assert is_allowed_metrics['allowed'] == 1
    assert is_allowed_metrics['not_allowed'] == 2
    assert reason_metrics['not_updated'] == 1
    assert reason_metrics['tag'] == 1
    assert reason_metrics['diagnostics'] == 1
    if check_issue_rfid:
        assert 'dispatch_airport' not in reason_metrics.keys()
        assert 'status' not in reason_metrics.keys()
    else:
        assert reason_metrics['status'] == 1
        assert reason_metrics['dispatch_airport'] == 1
