# flake8: noqa I202
# pylint: disable=E0401
import flatbuffers
import datetime
import pytz

from reposition_api.fbs.v1.airport_queue.state import (
    Driver as AirportQueueStateDriver,
)
from reposition_api.fbs.v1.airport_queue.state import (
    Request as AirportQueueStateRequest,
)
from reposition_api.fbs.v1.airport_queue.state import (
    Response as AirportQueueStateResponse,
)
from reposition_api.fbs.v1.service.offers import (
    Response as ServiceOffersResponse,
)

from reposition_api.fbs.v1.service.make_offer import (
    GeoPoint as MakeOfferGeoPoint,
)
from reposition_api.fbs.v1.service.make_offer import (
    OfferMetadata as MakeOfferOfferMetadata,
)
from reposition_api.fbs.v1.service.make_offer import (
    OfferRequest as MakeOfferOfferRequest,
)
from reposition_api.fbs.v1.service.make_offer import (
    OfferRestriction as MakeOfferOfferRestriction,
)
from reposition_api.fbs.v1.service.make_offer import (
    Request as MakeOfferRequest,
)
from reposition_api.fbs.v1.service.make_offer import (
    Response as MakeOfferResponse,
)
from reposition_api.fbs.v1.service.make_offer.Origin import (
    Origin as MakeOfferOrigin,
)

from reposition.fbs.v1.service.bulk_state import (
    DriverRequest as BulkStateDriverRequest,
)
from reposition.fbs.v1.service.bulk_state import (
    RouterInfo as BulkStateRouterInfo,
)
from reposition.fbs.v1.service.bulk_state import Request as BulkStateRequest
from reposition.fbs.v1.service.bulk_state import Response as BulkStateResponse

from reposition.fbs.v1.service.sessions import (
    Response as ServiceSessionsResponse,
)

from reposition.fbs.v2.drivers.index import Response as DriversIndexResponse


class AirportQueueStateFbs:
    def build_request(self, data):
        builder = flatbuffers.Builder(0)
        queries = []

        airport_queue_id = None

        if 'airport_queue_id' in data:
            airport_queue_id = builder.CreateString(data['airport_queue_id'])

        for query in data['queries'][::-1]:
            driver_id = builder.CreateString(query['driver_profile_id'])
            park_db_id = builder.CreateString(query['park_db_id'])

            AirportQueueStateDriver.DriverStart(builder)
            AirportQueueStateDriver.DriverAddDriverProfileId(
                builder, driver_id,
            )
            AirportQueueStateDriver.DriverAddParkDbId(builder, park_db_id)

            queries.append(AirportQueueStateDriver.DriverEnd(builder))

        AirportQueueStateRequest.RequestStartDriversVector(
            builder, len(queries),
        )
        for query in queries:
            builder.PrependUOffsetTRelative(query)
        drivers = builder.EndVector(len(queries))

        AirportQueueStateRequest.RequestStart(builder)
        if airport_queue_id:
            AirportQueueStateRequest.RequestAddAirportQueueId(
                builder, airport_queue_id,
            )
        AirportQueueStateRequest.RequestAddDrivers(builder, drivers)
        request = AirportQueueStateRequest.RequestEnd(builder)
        builder.Finish(request)
        return builder.Output()

    def parse_response(self, data):
        response = AirportQueueStateResponse.Response.GetRootAsResponse(
            data, 0,
        )
        states = []
        for i in range(0, response.StatesLength()):
            airport_queue_id = response.States(i).AirportQueueId()
            driver_id = response.States(i).DriverProfileId()
            park_db_id = response.States(i).ParkDbId()
            session_id = response.States(i).SessionId()
            mode = response.States(i).Mode()
            is_dispatch_airport_pin = response.States(i).IsDispatchAirportPin()
            error = response.States(i).Error()

            data = {
                'driver_profile_id': driver_id.decode('utf-8'),
                'park_db_id': park_db_id.decode('utf-8'),
            }

            if airport_queue_id:
                data['airport_queue_id'] = airport_queue_id.decode('utf-8')

            if session_id:
                data['session_id'] = session_id.decode('utf-8')

            if mode:
                data['mode'] = mode.decode('utf-8')

            data['is_dispatch_airport_pin'] = is_dispatch_airport_pin

            if error:
                data['error'] = error.decode('utf-8')

            states.append(data)
        return {'states': states}


class ServiceBulkStateFbs:
    def build_request(self, data):
        builder = flatbuffers.Builder(0)
        drivers = []
        for driver in data['drivers'][::-1]:
            driver_id = builder.CreateString(driver['driver_profile_id'])
            park_db_id = builder.CreateString(driver['park_db_id'])

            BulkStateDriverRequest.DriverRequestStart(builder)
            BulkStateDriverRequest.DriverRequestAddDriverProfileId(
                builder, driver_id,
            )
            BulkStateDriverRequest.DriverRequestAddParkDbId(
                builder, park_db_id,
            )
            drivers.append(BulkStateDriverRequest.DriverRequestEnd(builder))

        BulkStateRequest.RequestStartDriversVector(builder, len(drivers))
        for driver in drivers:
            builder.PrependUOffsetTRelative(driver)
        drivers = builder.EndVector(len(drivers))

        BulkStateRequest.RequestStart(builder)
        BulkStateRequest.RequestAddDrivers(builder, drivers)
        request = BulkStateRequest.RequestEnd(builder)
        builder.Finish(request)
        return builder.Output()

    def parse_response(self, data):
        response = BulkStateResponse.Response.GetRootAsResponse(data, 0)
        states = []
        for i in range(0, response.StatesLength()):
            state = response.States(i)
            has_session = state.HasSession()
            mode = state.Mode()
            submode = state.Submode()
            active = state.Active()
            bonus = state.Bonus()
            session_id = state.SessionId()
            area_radius = state.AreaRadius()
            start_timestamp = state.StartTimestamp()
            start_router_info = state.StartRouterInfo()
            # skip point check
            data = {'has_session': has_session}
            if mode:
                data['mode'] = mode.decode('utf-8')
            if submode:
                data['submode'] = submode.decode('utf-8')
            if active:
                data['active'] = active
            if bonus:
                data['bonus'] = {'until': bonus.Until()}
            if session_id:
                data['session_id'] = session_id
            if area_radius:
                data['area_radius'] = area_radius
            if start_timestamp:
                data['start_timestamp'] = start_timestamp
            if start_router_info:
                data['start_router_info'] = {
                    'time': start_router_info.Time(),
                    'dist': start_router_info.Dist(),
                }

            states.append(data)

        return {'states': states}


class ServiceSessionsFbs:
    def parse_response(self, data):
        response = ServiceSessionsResponse.Response.GetRootAsResponse(data, 0)
        sessions = []
        for i in range(0, response.SessionsLength()):
            session = response.Sessions(i)
            sessions.append(
                {
                    'driver_id': session.DriverId().decode('utf-8'),
                    'park_db_id': session.ParkDbId().decode('utf-8'),
                    'mode': session.Mode().decode('utf-8'),
                    'submode': (
                        session.Submode().decode('utf-8')
                        if session.Submode()
                        else ''
                    ),
                    'start': session.Start(),
                    'end': session.End() if session.End() else None,
                },
            )
        return {'sessions': sessions}


class DriversIndexFbs:
    def parse_response(self, data):
        response = DriversIndexResponse.Response.GetRootAsResponse(data, 0)
        drivers = []
        for i in range(0, response.DriversLength()):
            driver = response.Drivers(i)
            drivers.append(
                {
                    'driver_id': driver.DriverId().decode('utf-8'),
                    'park_db_id': driver.ParkDbId().decode('utf-8'),
                    'can_take_orders': driver.CanTakeOrders(),
                    'can_take_orders_when_busy': (
                        driver.CanTakeOrdersWhenBusy()
                    ),
                    'reposition_check_required': (
                        driver.RepositionCheckRequired()
                    ),
                    'mode_name': driver.ModeName().decode('utf-8'),
                    'bonus_until': (
                        datetime.datetime.fromtimestamp(
                            int(driver.BonusUntil()), pytz.timezone('UTC'),
                        )
                        if driver.BonusUntil()
                        else None
                    ),
                    'destination_point': [
                        driver.DestinationPoint().Longitude(),
                        driver.DestinationPoint().Latitude(),
                    ],
                },
            )
        return {
            'drivers': drivers,
            'revision': response.Revision(),
            'has_more': response.HasMore(),
        }


class ServiceOffersFbs:
    def parse_response(self, data):
        response = ServiceOffersResponse.Response.GetRootAsResponse(data, 0)

        offers = []

        for i in range(0, response.OffersLength()):
            offer = response.Offers(i)

            offers.append(
                {
                    'park_id': offer.ParkId().decode('utf-8'),
                    'driver_profile_id': offer.DriverProfileId().decode(
                        'utf-8',
                    ),
                    'mode_name': offer.ModeName().decode('utf-8'),
                    'used': offer.Used(),
                    'point': [
                        offer.Point().Longitude(),
                        offer.Point().Latitude(),
                    ],
                    'valid_until': datetime.datetime.fromtimestamp(
                        int(offer.ValidUntil()), pytz.timezone('UTC'),
                    ),
                    'created': datetime.datetime.fromtimestamp(
                        int(offer.Created()), pytz.timezone('UTC'),
                    ),
                },
            )

        return {'offers': sorted(offers, key=lambda x: x['driver_profile_id'])}


class MakeOfferFbs:
    def datestr_to_timestamp(self, date):
        if not date:
            return 0

        date_time = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S%z')

        return int(datetime.datetime.timestamp(date_time))

    def to_fbs_str_list(self, builder, str_list):
        out_list = []

        for str_item in str_list[::-1]:
            out_list.append(builder.CreateString(str_item))

        return out_list

    def to_fbs_restriction_list(self, builder, rest_list):
        res_list = []

        for rest_item in rest_list[::-1]:
            image_id = builder.CreateString(rest_item['image_id'])
            short_text = builder.CreateString(rest_item['short_text'])
            text = builder.CreateString(rest_item['text'])
            title = builder.CreateString(rest_item['title'])

            MakeOfferOfferRestriction.OfferRestrictionStart(builder)
            MakeOfferOfferRestriction.OfferRestrictionAddImageId(
                builder, image_id,
            )
            MakeOfferOfferRestriction.OfferRestrictionAddShortText(
                builder, short_text,
            )
            MakeOfferOfferRestriction.OfferRestrictionAddText(builder, text)
            MakeOfferOfferRestriction.OfferRestrictionAddTitle(builder, title)

            res_list.append(
                MakeOfferOfferRestriction.OfferRestrictionEnd(builder),
            )

        return res_list

    def to_fbs_metadata(self, builder, metadata_dict):
        airport_queue_id = None
        if 'airport_queue_id' in metadata_dict:
            airport_queue_id = builder.CreateString(
                metadata_dict['airport_queue_id'],
            )

        classes = None
        if 'classes' in metadata_dict:
            fbs_classes = self.to_fbs_str_list(
                builder, metadata_dict['classes'],
            )

            MakeOfferOfferMetadata.OfferMetadataStartClassesVector(
                builder, len(metadata_dict['classes']),
            )

            for fbs_class in fbs_classes:
                builder.PrependUOffsetTRelative(fbs_class)

            classes = builder.EndVector(len(metadata_dict['classes']))

        is_dispatch_airport_pin = None
        if 'is_dispatch_airport_pin' in metadata_dict:
            is_dispatch_airport_pin = metadata_dict['is_dispatch_airport_pin']

        is_surge_pin = None
        if 'is_surge_pin' in metadata_dict:
            is_surge_pin = metadata_dict['is_surge_pin']

        surge_pin_value = None
        if 'surge_pin_value' in metadata_dict:
            surge_pin_value = metadata_dict['surge_pin_value']

        MakeOfferOfferMetadata.OfferMetadataStart(builder)

        if airport_queue_id is not None:
            MakeOfferOfferMetadata.OfferMetadataAddAirportQueueId(
                builder, airport_queue_id,
            )

        if classes is not None:
            MakeOfferOfferMetadata.OfferMetadataAddClasses(builder, classes)

        if is_dispatch_airport_pin is not None:
            MakeOfferOfferMetadata.OfferMetadataAddIsDispatchAirportPin(
                builder, is_dispatch_airport_pin,
            )

        if is_surge_pin is not None:
            MakeOfferOfferMetadata.OfferMetadataAddIsSurgePin(
                builder, is_surge_pin,
            )

        if surge_pin_value is not None:
            MakeOfferOfferMetadata.OfferMetadataAddSurgePinValue(
                builder, surge_pin_value,
            )

        return MakeOfferOfferMetadata.OfferMetadataEnd(builder)

    def build_request(self, data):
        builder = flatbuffers.Builder(0)
        offers = []
        for offer in data['offers'][::-1]:
            driver_id = builder.CreateString(offer['driver_id'])
            park_db_id = builder.CreateString(offer['park_db_id'])
            mode = builder.CreateString(offer['mode'])
            address = builder.CreateString(offer['address'])
            city = builder.CreateString(offer['city'])
            image_id = builder.CreateString(offer['image_id'])
            name = builder.CreateString(offer['name'])
            description = builder.CreateString(offer['description'])

            tariff_class = None
            if 'tariff_class' in offer:
                tariff_class = builder.CreateString(offer['tariff_class'])

            origin = offer['origin']

            auto_accept = None
            if 'auto_accept' in offer:
                auto_accept = offer['auto_accept']

            fbs_tags = self.to_fbs_str_list(builder, offer['tags'])

            MakeOfferOfferRequest.OfferRequestStartTagsVector(
                builder, len(offer['tags']),
            )
            for tag in fbs_tags:
                builder.PrependUOffsetTRelative(tag)
            tags = builder.EndVector(len(offer['tags']))

            completed_tags = None
            if 'completed_tags' in offer:
                fbs_completed_tags = self.to_fbs_str_list(
                    builder, offer['completed_tags'],
                )
                MakeOfferOfferRequest.OfferRequestStartCompletedTagsVector(
                    builder, len(offer['completed_tags']),
                )
                for tag in fbs_completed_tags:
                    builder.PrependUOffsetTRelative(tag)
                completed_tags = builder.EndVector(
                    len(offer['completed_tags']),
                )

            restrictions = None
            if 'restrictions' in offer:
                fbs_restrictions = self.to_fbs_restriction_list(
                    builder, offer['restrictions'],
                )
                MakeOfferOfferRequest.OfferRequestStartRestrictionsVector(
                    builder, len(offer['restrictions']),
                )
                for restriction in fbs_restrictions:
                    builder.PrependUOffsetTRelative(restriction)
                restrictions = builder.EndVector(len(offer['restrictions']))

            draft_id = None
            if 'draft_id' in offer:
                draft_id = builder.CreateString(offer['draft_id'])

            metadata = None
            if 'metadata' in offer:
                metadata = self.to_fbs_metadata(builder, offer['metadata'])

            MakeOfferOfferRequest.OfferRequestStart(builder)
            MakeOfferOfferRequest.OfferRequestAddDriverId(builder, driver_id)
            MakeOfferOfferRequest.OfferRequestAddParkDbId(builder, park_db_id)
            MakeOfferOfferRequest.OfferRequestAddModeName(builder, mode)
            if 'destination' in offer:
                MakeOfferOfferRequest.OfferRequestAddDestination(
                    builder,
                    MakeOfferGeoPoint.CreateGeoPoint(
                        builder,
                        offer['destination'][1],
                        offer['destination'][0],
                    ),
                )
            MakeOfferOfferRequest.OfferRequestAddAddress(builder, address)
            MakeOfferOfferRequest.OfferRequestAddCity(builder, city)
            MakeOfferOfferRequest.OfferRequestAddStartUntil(
                builder, self.datestr_to_timestamp(offer['start_until']),
            )
            if 'finish_until' in offer:
                MakeOfferOfferRequest.OfferRequestAddFinishUntil(
                    builder, self.datestr_to_timestamp(offer['finish_until']),
                )
            MakeOfferOfferRequest.OfferRequestAddImageId(builder, image_id)
            MakeOfferOfferRequest.OfferRequestAddName(builder, name)
            MakeOfferOfferRequest.OfferRequestAddDescription(
                builder, description,
            )
            MakeOfferOfferRequest.OfferRequestAddTags(builder, tags)
            if completed_tags:
                MakeOfferOfferRequest.OfferRequestAddCompletedTags(
                    builder, completed_tags,
                )
            if tariff_class:
                MakeOfferOfferRequest.OfferRequestAddTariffClass(
                    builder, tariff_class,
                )
            MakeOfferOfferRequest.OfferRequestAddOrigin(builder, origin)
            if auto_accept is not None:
                MakeOfferOfferRequest.OfferRequestAddAutoAccept(
                    builder, auto_accept,
                )
            if restrictions:
                MakeOfferOfferRequest.OfferRequestAddRestrictions(
                    builder, restrictions,
                )
            if draft_id is not None:
                MakeOfferOfferRequest.OfferRequestAddDraftId(builder, draft_id)
            if metadata:
                MakeOfferOfferRequest.OfferRequestAddMetadata(
                    builder, metadata,
                )

            offers.append(MakeOfferOfferRequest.OfferRequestEnd(builder))

        MakeOfferRequest.RequestStartOffersVector(builder, len(offers))
        for offer in offers:
            builder.PrependUOffsetTRelative(offer)
        offers = builder.EndVector(len(offers))

        MakeOfferRequest.RequestStart(builder)
        MakeOfferRequest.RequestAddOffers(builder, offers)
        request = MakeOfferRequest.RequestEnd(builder)
        builder.Finish(request)

        return builder.Output()

    def parse_response(self, data):
        response = MakeOfferResponse.Response.GetRootAsResponse(data, 0)
        results = []
        for i in range(0, response.ResultsLength()):
            result = response.Results(i)
            point_id = result.PointId()
            error = result.Error()
            data = {
                'driver_id': result.DriverId().decode('utf-8'),
                'park_db_id': result.ParkDbId().decode('utf-8'),
            }
            if point_id:
                data['point_id'] = point_id.decode('utf-8')
            if error:
                data['error'] = error.decode('utf-8')
            results.append(data)
        return {'results': results}
