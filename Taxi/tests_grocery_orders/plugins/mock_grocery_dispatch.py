import datetime
import json

import pytest
import pytz

from tests_grocery_orders import consts


@pytest.fixture(name='grocery_dispatch', autouse=True)
def mock_grocery_dispatch(mockserver, mocked_time):
    class Context:
        def __init__(self):
            self.order_id = None
            self.short_order_id = None
            self.items = None
            self.dispatch_id = consts.DEFAULT_DISPATCH_ID
            self.depot_id = None
            self.status = None
            self.performer_name = None
            self.performer_first_name = None
            self.cargo_revision = 1
            self.due_time_point = None
            self.performer_contact_phone = None
            self.performer_contact_ext = None
            self.accept_language = None
            self.performer_status = 200
            self.transport_type = None
            self.eats_profile_id = None
            self.performer_id = None
            self.taxi_alias_id = None
            self.driver_id = None
            self.create_error_code = None
            self.cancel_error_code = None
            self.info_error_code = None
            self.accept_error_code = None
            self.performer_contact_error_code = None
            self.performer_position_error = None
            self.performer_info_error = None
            self.check_request_flag = False
            self.location = None
            self.zone_type = None
            self.created_at = None
            self.max_eta = None
            self.exact_eta = None
            self.min_eta = None
            self.personal_phone_id = None
            self.additional_phone_code = None
            self.delivery_common_comment = None
            self.yandex_uid = None
            self.user_name = None
            self.country = None
            self.city = None
            self.street = None
            self.building = None
            self.floor = None
            self.flat = None
            self.porch = None
            self.door_code = None
            self.door_code_extra = None
            self.doorbell_name = None
            self.building_name = None
            self.postal_code = None
            self.leave_under_door = None
            self.meet_outside = None
            self.no_door_call = None
            self.market_slot = None
            self.comment = None
            self.map_uri = None
            self.eta = 10
            self.eta_timestamp = (
                (mocked_time.now() + datetime.timedelta(seconds=self.eta))
                .astimezone(pytz.UTC)
                .isoformat()
            )
            self.status_meta = None
            self.failure_reason_type = None
            self.car_number = None
            self.car_model = None
            self.car_color = None
            self.car_color_hex = None
            self.order_ready_status = 200
            self.wave = 1
            self.edit_error_code = None

        def set_data(
                self,
                order_id=None,
                short_order_id=None,
                depot_id=None,
                location=None,
                zone_type=None,
                created_at=None,
                due_time_point=None,
                max_eta=None,
                exact_eta=None,
                min_eta=None,
                items=None,
                accept_language=None,
                status=None,
                dispatch_id=None,
                performer_name=None,
                performer_first_name=None,
                create_error_code=None,
                cancel_error_code=None,
                info_error_code=None,
                accept_error_code=None,
                performer_contact_phone=None,
                performer_contact_ext=None,
                performer_contact_error_code=None,
                performer_position_error=None,
                performer_info_error=None,
                additional_phone_code=None,
                delivery_common_comment=None,
                transport_type=None,
                performer_id=None,
                eats_profile_id=None,
                taxi_alias_id=None,
                driver_id=None,
                cargo_revision=None,
                eta=None,
                eta_timestamp=None,
                status_meta=None,
                failure_reason_type=None,
                door_code_extra=None,
                doorbell_name=None,
                postal_code=None,
                building_name=None,
                leave_under_door=None,
                meet_outside=None,
                no_door_call=None,
                market_slot=None,
                car_number=None,
                car_model=None,
                car_color=None,
                car_color_hex=None,
                order_ready_status=200,
                wave=None,
                edit_error_code=None,
                street=None,
                building=None,
                flat=None,
                door_code=None,
                porch=None,
                floor=None,
                comment=None,
                map_uri=None,
        ):
            if items is not None:
                self.items = items
            if status is not None:
                self.status = status
            if dispatch_id is not None:
                self.dispatch_id = dispatch_id
            if depot_id is not None:
                self.depot_id = depot_id
            if order_id is not None:
                self.order_id = order_id
            if short_order_id is not None:
                self.short_order_id = short_order_id
            if performer_name is not None:
                self.performer_name = performer_name
            if performer_first_name is not None:
                self.performer_first_name = performer_first_name
            if additional_phone_code is not None:
                self.additional_phone_code = additional_phone_code
            if delivery_common_comment is not None:
                self.delivery_common_comment = delivery_common_comment
            if info_error_code is not None:
                self.info_error_code = info_error_code
            if performer_info_error is not None:
                self.performer_info_error = performer_info_error
            if accept_error_code is not None:
                self.accept_error_code = accept_error_code
            if performer_contact_error_code is not None:
                self.performer_contact_error_code = (
                    performer_contact_error_code
                )
            if create_error_code is not None:
                self.create_error_code = create_error_code
            if cancel_error_code is not None:
                self.cancel_error_code = cancel_error_code
            if performer_position_error is not None:
                self.performer_position_error = performer_position_error
            if transport_type is not None:
                self.transport_type = transport_type
            if eats_profile_id is not None:
                self.eats_profile_id = eats_profile_id
            if performer_id is not None:
                self.performer_id = performer_id
            if taxi_alias_id is not None:
                self.taxi_alias_id = taxi_alias_id
            if driver_id is not None:
                self.driver_id = driver_id
            if cargo_revision is not None:
                self.cargo_revision = cargo_revision
            if performer_contact_phone is not None:
                self.performer_contact_phone = performer_contact_phone
            if performer_contact_ext is not None:
                self.performer_contact_ext = performer_contact_ext
            if location is not None:
                self.location = location
            if zone_type is not None:
                self.zone_type = zone_type
            if created_at is not None:
                self.created_at = created_at
            if max_eta is not None:
                self.max_eta = max_eta
            if exact_eta is not None:
                self.exact_eta = exact_eta
            if min_eta is not None:
                self.min_eta = min_eta
            if accept_language is not None:
                self.accept_language = accept_language
            if due_time_point is not None:
                self.due_time_point = due_time_point
            if eta is not None:
                self.eta = eta
            if eta_timestamp is not None:
                self.eta_timestamp = eta_timestamp
            if status_meta is not None:
                self.status_meta = status_meta
            if failure_reason_type is not None:
                self.failure_reason_type = failure_reason_type
            if door_code_extra is not None:
                self.door_code_extra = door_code_extra
            if doorbell_name is not None:
                self.doorbell_name = doorbell_name
            if postal_code is not None:
                self.postal_code = postal_code
            if building_name is not None:
                self.building_name = building_name
            if leave_under_door is not None:
                self.leave_under_door = leave_under_door
            if meet_outside is not None:
                self.meet_outside = meet_outside
            if no_door_call is not None:
                self.no_door_call = no_door_call
            if market_slot is not None:
                self.market_slot = market_slot
            if car_number is not None:
                self.car_number = car_number
            if car_model is not None:
                self.car_model = car_model
            if car_color is not None:
                self.car_color = car_color
            if car_color_hex is not None:
                self.car_color_hex = car_color_hex
            if order_ready_status is not None:
                self.order_ready_status = order_ready_status
            if wave is not None:
                self.wave = wave
            if edit_error_code is not None:
                self.edit_error_code = edit_error_code
            if street is not None:
                self.street = street
            if building is not None:
                self.building = building
            if flat is not None:
                self.flat = flat
            if door_code is not None:
                self.door_code = door_code
            if porch is not None:
                self.porch = porch
            if comment is not None:
                self.comment = comment
            if map_uri is not None:
                self.map_uri = map_uri

        def reset_performer(self):
            self.performer_id = None
            self.performer_name = None
            self.performer_first_name = None
            self.driver_id = None
            self.eats_profile_id = None
            self.performer_contact_phone = None
            self.performer_contact_ext = None
            self.car_number = None
            self.car_model = None
            self.car_color = None
            self.car_color_hex = None

        def set_performer_status(self, status_code):
            self.performer_status = status_code

        def set_cargo_dispatch_info(
                self,
                dispatch_in_batch=None,
                batch_order_num=None,
                dispatch_delivery_type=None,
        ):
            if self.status_meta is None:
                self.status_meta = dict()
            elif 'cargo_dispatch' in self.status_meta.keys():
                del self.status_meta['cargo_dispatch']

            if (
                    dispatch_in_batch is not None
                    or batch_order_num is not None
                    or dispatch_delivery_type is not None
            ):
                self.status_meta.update({'cargo_dispatch': dict()})
                if dispatch_in_batch is not None:
                    self.status_meta['cargo_dispatch'].update(
                        {'dispatch_in_batch': dispatch_in_batch},
                    )
                if batch_order_num is not None:
                    self.status_meta['cargo_dispatch'].update(
                        {'batch_order_num': batch_order_num},
                    )
                if dispatch_delivery_type is not None:
                    self.status_meta['cargo_dispatch'].update(
                        {'dispatch_delivery_type': dispatch_delivery_type},
                    )

        def times_create_called(self):
            return mock_create.times_called

        def times_accept_called(self):
            return mock_accept.times_called

        def times_info_called(self):
            return mock_info.times_called

        def times_cancel_called(self):
            return mock_cancel.times_called

        def times_performer_contact_called(self):
            return mock_performer_contact.times_called

        def times_performer_position_called(self):
            return mock_performer_position.times_called

        def times_performer_info_called(self):
            return mock_performer_info.times_called

        def times_order_ready_called(self):
            return mock_order_ready.times_called

        def times_edit_called(self):
            return mock_edit.times_called

        def check_create_request(self, request_data):
            if self.depot_id is not None:
                assert self.depot_id == request_data['depot_id']
            if self.order_id is not None:
                assert self.order_id == request_data['order_id']
            if self.short_order_id is not None:
                assert self.short_order_id == request_data['short_order_id']
            if self.additional_phone_code is not None:
                assert (
                    self.additional_phone_code
                    == request_data['additional_phone_code']
                )
            if self.delivery_common_comment is not None:
                assert (
                    self.delivery_common_comment
                    == request_data['delivery_common_comment']
                )
            if self.zone_type is not None:
                assert self.zone_type == request_data['zone_type']
            if self.max_eta is not None:
                assert self.max_eta * 60 == request_data['max_eta']
            if self.exact_eta is not None:
                assert self.exact_eta * 60 == request_data['exact_eta']
            if self.min_eta is not None:
                assert self.min_eta * 60 == request_data['min_eta']
            if self.accept_language is not None:
                assert self.accept_language == request_data['user_locale']
            if self.items is not None:
                request_weights = [
                    it['weight'] for it in request_data['items']
                ]
                self_weights = [it['gross_weight'] for it in self.items]
                assert self_weights == request_weights
            if self.door_code_extra is not None:
                assert self.door_code_extra == request_data['door_code_extra']
            if self.doorbell_name is not None:
                assert self.doorbell_name == request_data['doorbell_name']
            if self.postal_code is not None:
                assert self.postal_code == request_data['postal_code']
            if self.building_name is not None:
                assert self.building_name == request_data['building_name']
            if self.leave_under_door is not None:
                assert (
                    self.leave_under_door == request_data['leave_under_door']
                )
            if self.meet_outside is not None:
                assert self.meet_outside == request_data['meet_outside']
            if self.no_door_call is not None:
                assert self.no_door_call == request_data['no_door_call']
            if self.market_slot:
                assert self.market_slot == request_data['market_slot']

        def check_edit_request(self, request_data):
            new_data = request_data['new_data']
            if self.street is not None:
                assert self.street == new_data['street']
            if self.building is not None:
                assert self.building == new_data['building']
            if self.flat is not None:
                assert self.flat == new_data['flat']
            if self.door_code is not None:
                assert self.door_code == new_data['door_code']
            if self.porch is not None:
                assert self.porch == new_data['porch']
            if self.floor is not None:
                assert self.floor == new_data['floor']
            if self.comment is not None:
                assert self.comment == new_data['comment']
            if self.location is not None:
                assert self.location == new_data['location']

    context = Context()

    def _check_request_dispatch_id(request_data):
        if context.dispatch_id:
            assert context.dispatch_id == request_data['dispatch_id']

    def get_performer_info():
        return {
            'performer_id': context.performer_id,
            'eats_profile_id': context.eats_profile_id,
            'performer_name': context.performer_name,
            'first_name': context.performer_first_name,
            'legal_name': 'ООО Ромашка',
            'transport_type': context.transport_type,
            'driver_id': context.driver_id,
            'park_id': '123',
            'taxi_alias_id': context.taxi_alias_id,
        }

    def get_dispatch_info():
        performer_info = (
            {'performer': get_performer_info()}
            if context.performer_name
            else {}
        )

        cargo_dispatch_info = (
            {'status_meta': context.status_meta}
            if context.status_meta is not None
            else {}
        )

        return {
            'dispatch_id': context.dispatch_id,
            'order_id': context.order_id,
            'version': context.cargo_revision,
            'status': context.status,
            'eta': context.eta,
            'eta_timestamp': context.eta_timestamp,
            'dispatch_type': 'pedestrian',
            **performer_info,
            **cargo_dispatch_info,
            'failure_reason_type': context.failure_reason_type,
            'wave': context.wave,
        }

    @mockserver.json_handler('/grocery-dispatch/internal/dispatch/v1/create')
    def mock_create(request):
        if context.create_error_code:
            return mockserver.make_response(
                json.dumps({'code': 'not_found', 'message': 'some_message'}),
                context.create_error_code,
            )

        context.check_create_request(request.json)
        return get_dispatch_info()

    @mockserver.json_handler('/grocery-dispatch/internal/dispatch/v1/status')
    def mock_info(request):
        if context.info_error_code:
            return mockserver.make_response('', context.info_error_code)
        _check_request_dispatch_id(request.json)
        return get_dispatch_info()

    @mockserver.json_handler('/grocery-dispatch/internal/dispatch/v1/accept')
    def mock_accept(request):
        if context.accept_error_code:
            return mockserver.make_response('', context.accept_error_code)
        _check_request_dispatch_id(request.json)
        return mockserver.make_response('', 200)

    @mockserver.json_handler('/grocery-dispatch/internal/dispatch/v1/cancel')
    def mock_cancel(request):
        if context.cancel_error_code:
            return mockserver.make_response(
                json.dumps({'code': 'not_found', 'message': 'some_message'}),
                context.cancel_error_code,
            )

        _check_request_dispatch_id(request.json)
        return mockserver.make_response('', 200)

    @mockserver.json_handler(
        '/grocery-dispatch/internal/dispatch/v1/order_ready',
    )
    def mock_order_ready(request):
        _check_request_dispatch_id(request.json)
        if context.order_ready_status != 200:
            return mockserver.make_response('', context.order_ready_status)
        return get_dispatch_info()

    @mockserver.json_handler(
        '/grocery-dispatch/internal/dispatch/v1/performer_position',
    )
    def mock_performer_position(request):
        if context.performer_position_error:
            return mockserver.make_response(
                json.dumps({'code': 'not_found', 'message': 'some_message'}),
                context.performer_position_error,
            )
        _check_request_dispatch_id(request.json)
        return {
            'performer_id': '101',
            'timestamp': '2020-05-25T17:43:45+00:00',
            'location': {'lat': 35, 'lon': 55},
            'speed': 3,
            'direction': 25,
        }

    @mockserver.json_handler(
        '/grocery-dispatch/internal/dispatch/v1/performer_contact',
    )
    def mock_performer_contact(request):
        if context.performer_contact_error_code == 404:
            return mockserver.make_response(
                json.dumps({'code': 'not_found', 'message': 'some_message'}),
                context.performer_contact_error_code,
            )
        if context.performer_contact_error_code:
            return mockserver.make_response(
                status=context.performer_contact_error_code,
            )

        _check_request_dispatch_id(request.json)

        if context.performer_contact_phone is not None:
            response_phone = {'phone': context.performer_contact_phone}
        else:
            response_phone = {}

        if context.performer_contact_ext is not None:
            response_ext = {'ext': context.performer_contact_ext}
        else:
            response_ext = {}

        if context.performer_id is not None:
            response_id = {'performer_id': context.performer_id}
        else:
            response_id = {}

        return mockserver.make_response(
            json={
                **response_id,
                **response_phone,
                **response_ext,
                'ttl_seconds': 2088,
            },
            status=200,
        )

    @mockserver.json_handler(
        '/grocery-dispatch/internal/dispatch/v1/performer_info',
    )
    def mock_performer_info(request):
        _check_request_dispatch_id(request.json)
        if context.performer_info_error is not None:
            return mockserver.make_response(
                json.dumps(
                    {'code': 'claim_not_ready', 'message': 'some_error'},
                ),
                context.performer_info_error,
            )

        return get_performer_info()

    @mockserver.json_handler('/grocery-dispatch/internal/dispatch/v1/edit')
    def mock_edit(request):
        if context.edit_error_code:
            return mockserver.make_response(
                json.dumps({'code': 'not_found', 'message': 'some_message'}),
                context.edit_error_code,
            )

        _check_request_dispatch_id(request.json)
        context.check_edit_request(request.json)
        return mockserver.make_response('', 200)

    return context
