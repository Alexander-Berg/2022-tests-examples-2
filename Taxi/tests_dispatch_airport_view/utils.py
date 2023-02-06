# pylint: disable=import-error
import datetime
import enum

import flatbuffers
import reposition_api.fbs.v1.airport_queue.state.AirportStateResponse as Response  # noqa: E501
import reposition_api.fbs.v1.airport_queue.state.Response as RepositionResponse
from reposition_api.fbs.v1.service.make_offer import OfferResponse
from reposition_api.fbs.v1.service.make_offer import (
    Request as MakeOfferRequest,
)
from reposition_api.fbs.v1.service.make_offer import (
    Response as MakeOfferResponse,
)

from geobus_tools import geobus  # noqa: F401 C5521
from tests_plugins import utils

EDGE_TRACKS_CHANNEL = 'channel:yaga:edge_positions'

# Format: (lon, lat)
OUT_EKB_RADIUS = [60.107783, 57.227150]
NEAR_EKB_AIRPORT_1 = [60.71821163, 56.77413905]
NEAR_EKB_AIRPORT_2 = [60.720161, 56.773339]
NOTIFICATION_EKB_POSITION = [60.76991035, 56.76123496]
WAITING_EKB_POSITION = [60.802226785621414, 56.752570325749566]
WAITING_BUT_NOT_AIRPORT_EKB_POSITION = [60.811625, 56.752876]
AIRPORT_EKB_POSITION = [60.80503137898187, 56.7454424257098]

BETWEEN_EKB_KAMENSKURALSK = [61.304268, 56.588581]
NEAR_KAMENSKURALSK_AIRPORT_1 = [61.752972, 56.434849]
NEAR_KAMENSKURALSK_AIRPORT_2 = [61.722691, 56.450114]
AIRPORT_KAMENSKURALSK = [61.92396961914058, 56.39818246923726]

HEADERS = {
    'X-Request-Application': 'taximeter',
    'X-Request-Platform': 'android',
    'X-Request-Application-Version': '9.07',
    'X-YaTaxi-Park-Id': '999',
    'X-YaTaxi-Driver-Profile-Id': '888',
    'Accept-Language': 'ru',
}

TAXIMETER_MESSAGES = {
    'dispatch_airport_view.alert.driver_left': {
        'ru': 'Вы уехали слишком далеко',
    },
    'dispatch_airport_view.info.offline_warning': {
        'ru': 'Выйдете на линию чтобы получить проводник в аэропорт',
    },
    'dispatch_airport.info.queue_title': {'ru': 'Заказы в аэропорт'},
    'dispatch_airport.error.orders_unavailable': {'ru': 'Очередь не доступна'},
    'ekb_airport_key': {'ru': 'Кольцово'},
    'dispatch_airport.info.enter_zone': {
        'ru': 'Заезжайте в синюю зону, чтобы встать в очередь',
    },
    'airportqueue.exact_time': {'ru': '%(minutes)s мин'},
    'airportqueue.exact_time_hours': {'ru': '%(hours)s ч'},
    'airportqueue.exact_time_hours_minutes': {
        'ru': '%(hours)s ч %(minutes)s мин',
    },
    'airportqueue.estimated_time_more_hours': {'ru': 'Более %(hours)s ч'},
    'airportqueue.estimated_time_less_minutes': {
        'ru': 'Менее %(minutes)s мин',
    },
    'dispatch_airport_view.constructor.button_reposition_title': {
        'ru': 'Проводник в аэропорт',
    },
    'dispatch_airport_view.constructor.button_reposition_subtitle': {
        'ru': 'Приоритет +1',
    },
    'dispatch_airport_view.constructor.tariff_warning': {
        'ru': 'Только по этим тарифам сейчас можно встать в очередь',
    },
    'dispatch_airport_view.constructor.time_warning': {
        'ru': 'Время ожидания указано без учета времени поездки до аэропорта',
    },
    'dispatch_airport.rules.pin_title': {'ru': 'Правила очереди'},
    'dispatch_airport.rules.paragraph.about_queue': {
        'ru': (
            'Заказы в аэропорту распределяются с помощью электронной очереди.'
        ),
    },
    'dispatch_airport.rules.paragraph.enter_geo_condition': {
        'ru': (
            'Когда вы заезжаете в синюю зону на '
            'карте, то получаете место в очереди.'
        ),
    },
    'dispatch_airport.rules.paragraph.terms_list': {
        'ru': 'Чтобы оставаться в очереди, нужно:',
    },
    'dispatch_airport.rules.bullet.stay_geo': {
        'ru': 'Не уезжать из зоны аэропорта.',
    },
    'dispatch_airport.rules.bullet.no_cancels': {
        'ru': 'Не пропускать и не отменять заказы.',
    },
    'dispatch_airport.rules.paragraph.kick_condition': {
        'ru': (
            'Если вы сделаете что-то из списка выше, '
            'то автоматически покинете очередь заказов.'
        ),
    },
    'dispatch_airport.rules.paragraph.enter_conditions': {
        'ru': 'Вы получите место в очереди, если:',
    },
    'dispatch_airport.error.driver_cancel': {
        'ru': 'Вы отменили много заказов: очередь недоступна',
    },
}
TARIFF = {
    'name.econom': {'ru': 'Эконом'},
    'name.comfortplus': {'ru': 'Комфорт+'},
    'name.vip_old': {'ru': 'Бизнес'},
}


class PinState(enum.IntEnum):
    kAllowedAll = 0
    kAllowedOldMode = 1
    kNotAllowed = 2


def get_pin_state(allowed):
    if allowed:
        return int(PinState.kAllowedAll)
    return int(PinState.kNotAllowed)


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


def _reposition_driver(builder, driver):
    session_id = builder.CreateString(
        f'session_{driver["dbid"]}_{driver["uuid"]}',
    )
    error = builder.CreateString('')
    dbid = builder.CreateString(driver['dbid'])
    uuid = builder.CreateString(driver['uuid'])
    is_dispatch_airport_pin = driver.get('is_dispatch_airport_pin', False)
    Response.AirportStateResponseStart(builder)
    Response.AirportStateResponseAddParkDbId(builder, dbid)
    Response.AirportStateResponseAddDriverProfileId(builder, uuid)
    Response.AirportStateResponseAddSessionId(builder, session_id)
    Response.AirportStateResponseAddError(builder, error)
    Response.AirportStateResponseAddIsDispatchAirportPin(
        builder, is_dispatch_airport_pin,
    )
    return Response.AirportStateResponseEnd(builder)


def generate_reposition_drivers(drivers):
    builder = flatbuffers.Builder(0)
    drivers = [_reposition_driver(builder, driver) for driver in drivers]
    RepositionResponse.ResponseStartStatesVector(builder, len(drivers))
    for driver in drivers:
        builder.PrependUOffsetTRelative(driver)
    drivers = builder.EndVector(len(drivers))

    RepositionResponse.ResponseStart(builder)
    RepositionResponse.ResponseAddStates(builder, drivers)
    obj = RepositionResponse.ResponseEnd(builder)
    builder.Finish(obj)
    return bytes(builder.Output())


def driver_info_key(dbid_uuid):
    return 'dbid_uuid:{}'.format(dbid_uuid)


def pin_point(
        airport_id, point, allowed, class_wait_times=None, last_allowed=None,
):
    info = {
        'airport_id': airport_id,
        'pin_point': point,
        'state': get_pin_state(allowed),
    }
    if class_wait_times:
        info['class_wait_times'] = class_wait_times
    if last_allowed is not None:
        info['last_allowed'] = last_allowed
    return info


def ekb_pin_point(
        allowed,
        waiting_time_sec=None,
        class_wait_times=None,
        last_allowed=None,
):
    return pin_point(
        'ekb', AIRPORT_EKB_POSITION, allowed, class_wait_times, last_allowed,
    )


def kamenskuralsky_pin_point(
        allowed, waiting_time_sec=None, class_wait_times=None,
):
    return pin_point(
        'kamenskuralsky', AIRPORT_KAMENSKURALSK, allowed, class_wait_times,
    )


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
                meta[
                    'is_dispatch_airport_pin'
                ] = meta_request.IsDispatchAirportPin()
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
