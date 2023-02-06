import json

import pytest

from tests_grocery_orders import consts
from tests_grocery_orders import models


@pytest.fixture(name='cargo')
def mock_cargo(mockserver):
    class Context:
        def __init__(self):
            self.request_id = None
            self.items = None
            self.dispatch_id = consts.DEFAULT_DISPATCH_ID
            self.status = 'new'
            self.claim_kind = None
            self.cargo_create_error_code = None
            self.cargo_info_error_code = None
            self.cargo_accept_error_code = None
            self.cargo_courier_phone_error_code = None
            self.cargo_courier_position_error = None
            self.cargo_performer_external_error = None
            self.courier_name = None
            self.cargo_revision = 0
            self.due_time_point = None
            self.emergency_contact = None
            self.courier_contact_phone = '+79995556677'
            self.courier_contact_ext = '109'
            self.authorization = None
            self.skip_door_to_door = None
            self.skip_client_notify = None
            self.skip_emergency_notify = None
            self.optional_return = None
            self.comment = None
            self.requirement_type = None
            self.requirement_logistic_group = None
            self.requirement_meta_group = None
            self.accept_language = None
            self.taxi_class = 'express'
            self.taxi_classes = None
            self.delivered_eta_ts = None
            self.pickuped_eta_ts = None
            self.delivery_flags = None
            self.route_points = [
                models.CargoRoutePoint(
                    point_id=1,
                    visit_order=1,
                    type='source',
                    coordinates=[37.655688, 55.738495],
                    country='Россия',
                    city='city',
                    street='street',
                    building='building',
                    floor='floor',
                    flat='flat',
                    door_code='doorcode',
                    door_code_extra='doorcode_extra',
                    building_name='building_name',
                    doorbell_name='doorbell_name',
                    leave_under_door=False,
                    phone='phone',
                    name='Лавка',
                    comment='comment',
                    short_order_id='1a1a1a',
                    place_id='some_place_id_1',
                    time_intervals=None,
                ),
                models.CargoRoutePoint(
                    point_id=2,
                    visit_order=2,
                    type='destination',
                    coordinates=[50.0, 30.0],
                    country='Россия',
                    city='order_city',
                    street='order_street',
                    building='order_building',
                    floor='order_floor',
                    flat='order_flat',
                    door_code='doorcode',
                    door_code_extra='doorcode_extra',
                    building_name='building_name',
                    doorbell_name='doorbell_name',
                    leave_under_door=False,
                    phone='phone',
                    name='Иван Иванович',
                    comment='comment',
                    short_order_id='1a1a1a',
                    place_id='some_place_id_2',
                    time_intervals=[],
                    entrance='entrance',
                ),
            ]
            self.skip_act = None
            self.check_request_flag = False
            self.check_fields_flag = False
            self.check_user_contact_flag = False
            self.check_requirements_flag = False
            self.number_of_user_address_parts = None
            self.custom_context = None
            self.requirement_restriction_type = None
            self.external_performer_status = 200
            self.transport_type = None
            self.check_comment_exist = False
            self.eats_profile_id = None
            self.courier_id = None
            self.taxi_alias_id = None
            self.driver_id = None

        def set_data(
                self,
                items=None,
                status=None,
                dispatch_id=None,
                courier_name=None,
                delivered_eta_ts=None,
                pickuped_eta_ts=None,
                cargo_create_error_code=None,
                cargo_info_error_code=None,
                cargo_accept_error_code=None,
                cargo_courier_phone_error_code=None,
                cargo_courier_position_error=None,
                cargo_performer_external_error=None,
                skip_act=None,
                number_of_user_address_parts=None,
                route_points=None,
                transport_type=None,
                courier_id=None,
                eats_profile_id=None,
                multidispatch_forbidden=None,
                taxi_alias_id=None,
                driver_id=None,
                cargo_revision=None,
        ):
            if items is not None:
                self.items = items
            if status is not None:
                self.status = status
            if dispatch_id is not None:
                self.dispatch_id = dispatch_id
            if courier_name is not None:
                self.courier_name = courier_name
            if route_points is not None:
                self.route_points = route_points
            if delivered_eta_ts is not None:
                self.route_points[1].visited_at_expected_ts = delivered_eta_ts
            if pickuped_eta_ts is not None:
                self.route_points[0].visited_at_expected_ts = pickuped_eta_ts
            if cargo_info_error_code is not None:
                self.cargo_info_error_code = cargo_info_error_code
            if cargo_performer_external_error is not None:
                self.cargo_performer_external_error = (
                    cargo_performer_external_error
                )
            if cargo_accept_error_code is not None:
                self.cargo_accept_error_code = cargo_accept_error_code
            if cargo_courier_phone_error_code is not None:
                self.cargo_courier_phone_error_code = (
                    cargo_courier_phone_error_code
                )
            if cargo_create_error_code is not None:
                self.cargo_create_error_code = cargo_create_error_code
            if cargo_courier_position_error is not None:
                self.cargo_courier_position_error = (
                    cargo_courier_position_error
                )
            if skip_act is not None:
                self.skip_act = skip_act
            if number_of_user_address_parts is not None:
                self.number_of_user_address_parts = (
                    number_of_user_address_parts
                )
            if transport_type is not None:
                self.transport_type = transport_type
            if eats_profile_id is not None:
                self.eats_profile_id = eats_profile_id
            if courier_id is not None:
                self.courier_id = courier_id
            if multidispatch_forbidden is not None:
                self.delivery_flags = {
                    'is_forbidden_to_be_in_batch': multidispatch_forbidden,
                }
            if taxi_alias_id is not None:
                self.taxi_alias_id = taxi_alias_id
            if driver_id is not None:
                self.driver_id = driver_id
            if cargo_revision is not None:
                self.cargo_revision = cargo_revision

        def check_authorization(self, authorization):
            self.authorization = authorization

        def check_user_contact(self, user_phone=None, user_name=None):
            if user_phone:
                self.route_points[1].phone = user_phone
            if user_name:
                self.route_points[1].name = user_name
            self.check_user_contact_flag = True

        def check_fields(self, claim_kind=None):
            if claim_kind is not None:
                self.claim_kind = claim_kind
            self.check_fields_flag = True

        def check_request(
                self,
                request_id=None,
                dispatch_id=None,
                items=None,
                route_points=None,
                status=None,
                due_time_point=None,
                emergency_contact=None,
                courier_contact_phone=None,
                courier_contact_ext=None,
                claim_kind=None,
                skip_door_to_door=None,
                skip_client_notify=None,
                skip_emergency_notify=None,
                optional_return=None,
                comment=None,
                check_comment_exist=False,
                requirement_type=None,
                requirement_logistic_group=None,
                requirement_meta_group=None,
                requirement_restriction_type=None,
                accept_language=None,
                taxi_class=None,
                taxi_classes=None,
                custom_context=None,
        ):
            if taxi_class is not None:
                self.taxi_class = taxi_class
            if taxi_classes is not None:
                self.taxi_classes = taxi_classes
            if request_id is not None:
                self.request_id = request_id
            if items is not None:
                self.items = items
            if route_points is not None:
                self.route_points = route_points
            if dispatch_id is not None:
                self.dispatch_id = dispatch_id
            if status is not None:
                self.status = status
            if due_time_point is not None:
                self.due_time_point = due_time_point
            if emergency_contact is not None:
                self.emergency_contact = emergency_contact
            if courier_contact_phone is not None:
                self.courier_contact_phone = courier_contact_phone
            if courier_contact_ext is not None:
                self.courier_contact_ext = courier_contact_ext
            if claim_kind is not None:
                self.claim_kind = claim_kind
            if skip_door_to_door is not None:
                self.skip_door_to_door = skip_door_to_door
            if skip_client_notify is not None:
                self.skip_client_notify = skip_client_notify
            if skip_emergency_notify is not None:
                self.skip_emergency_notify = skip_emergency_notify
            if optional_return is not None:
                self.optional_return = optional_return
            if comment is not None:
                self.comment = comment
            if requirement_type is not None:
                self.requirement_type = requirement_type
            if requirement_logistic_group is not None:
                self.requirement_logistic_group = requirement_logistic_group
            if requirement_meta_group is not None:
                self.requirement_meta_group = requirement_meta_group
            if accept_language is not None:
                self.accept_language = accept_language
            if custom_context is not None:
                self.custom_context = custom_context
            if self.delivery_flags is not None:
                self.custom_context['delivery_flags'] = self.delivery_flags
            if requirement_restriction_type is not None:
                self.requirement_restriction_type = (
                    requirement_restriction_type
                )

            self.check_comment_exist = check_comment_exist
            self.check_request_flag = True

        def times_create_called(self):
            return mock_create.times_called

        def times_accept_called(self):
            return mock_accept.times_called

        def times_info_called(self):
            return mock_info.times_called

        def times_cancel_called(self):
            return mock_cancel.times_called

        def times_courier_contact_called(self):
            return mock_courier_contact.times_called

        def times_courier_position_called(self):
            return mock_courier_position.times_called

        def times_set_points_ready_called(self):
            return mock_set_points_ready.times_called

        def external_performer_times_called(self):
            return mock_external_performer.times_called

        def set_external_performer_status(self, status_code):
            self.external_performer_status = status_code

        def flush(self):
            mock_create.flush()

    context = Context()

    @mockserver.json_handler(
        '/b2b-taxi/b2b/cargo/integration/v2/claims/create',
    )
    def mock_create(request):
        if context.check_fields_flag:
            if context.claim_kind:
                assert request.json['claim_kind'] == context.claim_kind

        if context.check_request_flag:
            if context.items is not None:
                assert request.json['items'] == [
                    item.as_cargo_object() for item in context.items
                ]
            # поле comment не проверяется
            for i in range(len(context.route_points)):
                point = request.json['route_points'][i]
                if 'comment' in point['address']:
                    context.route_points[i].comment = point['address'][
                        'comment'
                    ]
            assert request.json['route_points'] == [
                point.as_object() for point in context.route_points
            ]
            assert (
                request.json['client_requirements']['taxi_class']
                == context.taxi_class
            )
            if context.taxi_classes:
                assert (
                    request.json['client_requirements']['taxi_classes']
                    == context.taxi_classes
                )
            assert request.json['skip_client_notify']
            if context.due_time_point:
                assert request.json['due'] == context.due_time_point
            if context.emergency_contact:
                assert (
                    request.json['emergency_contact']['name'],
                    request.json['emergency_contact']['phone'],
                ) == context.emergency_contact
            if context.claim_kind:
                assert request.json['claim_kind'] == context.claim_kind
            if context.requirement_type:
                assert (
                    request.json['requirements']['soft_requirements'][0][
                        'type'
                    ]
                    == context.requirement_type
                )
            if context.requirement_logistic_group:
                assert (
                    request.json['requirements']['soft_requirements'][0][
                        'logistic_group'
                    ]
                    == context.requirement_logistic_group
                )
            if context.requirement_meta_group:
                assert (
                    request.json['requirements']['soft_requirements'][0][
                        'meta_group'
                    ]
                    == context.requirement_meta_group
                )
            if context.skip_client_notify:
                assert (
                    request.json['skip_client_notify']
                    == context.skip_client_notify
                )
            if context.skip_emergency_notify:
                assert (
                    request.json['skip_emergency_notify']
                    == context.skip_emergency_notify
                )
            if context.skip_door_to_door:
                assert (
                    request.json['skip_door_to_door']
                    == context.skip_door_to_door
                )

            if context.optional_return:
                assert (
                    request.json['optional_return'] == context.optional_return
                )
            if context.comment:
                assert request.json['comment'] == context.comment
            elif context.check_comment_exist:
                assert 'comment' not in request.json

        if context.check_user_contact_flag:
            assert request.json['route_points'][1]['contact'] == {
                'name': context.route_points[1].name,
                'phone': context.route_points[1].phone,
            }

        if context.number_of_user_address_parts:
            route_point = request.json['route_points'][1]
            fullname = route_point['address']['fullname']
            address_parts = fullname.split(', ')
            assert len(address_parts) == context.number_of_user_address_parts

        if context.authorization:
            assert request.headers['Authorization'] == context.authorization

        if context.cargo_create_error_code:
            return mockserver.make_response(
                json.dumps({'code': 'not_found', 'message': 'some_message'}),
                context.cargo_create_error_code,
            )

        if context.check_requirements_flag:
            if context.requirement_type:
                assert (
                    request.json['requirements']['soft_requirements'][0][
                        'type'
                    ]
                    == context.requirement_type
                )
            if context.requirement_logistic_group:
                assert (
                    request.json['requirements']['soft_requirements'][0][
                        'logistic_group'
                    ]
                    == context.requirement_logistic_group
                )
            if context.requirement_meta_group:
                assert (
                    request.json['requirements']['soft_requirements'][0][
                        'meta_group'
                    ]
                    == context.requirement_meta_group
                )
        if context.skip_act:
            assert request.json['skip_act'] == context.skip_act

        if context.custom_context is not None:
            assert request.json['custom_context'] == context.custom_context

        if context.requirement_restriction_type is not None:
            assert (
                request.json['requirements']['soft_requirements'][0][
                    'performers_restriction_type'
                ]
                == context.requirement_restriction_type
            )

        return {
            'id': context.dispatch_id,
            'items': request.json['items'],
            'route_points': [
                point.as_response_object() for point in context.route_points
            ],
            'status': context.status,
            'version': 1,
            'revision': 1,
            'emergency_contact': request.json['emergency_contact'],
            'created_ts': '2020-09-19T14:42:27.642389+00:00',
            'updated_ts': '2020-09-19T14:42:27.642389+00:00',
        }

    @mockserver.json_handler('/b2b-taxi/b2b/cargo/integration/v2/claims/info')
    def mock_info(request):
        if context.cargo_info_error_code:
            return mockserver.make_response('', context.cargo_info_error_code)

        performer_info = (
            {
                'performer_info': {
                    'courier_name': context.courier_name,
                    'legal_name': 'ООО Ромашка',
                    'transport_type': context.transport_type,
                    'courier_id': context.courier_id,
                    'driver_id': context.driver_id,
                },
            }
            if context.courier_name
            else {}
        )

        return {
            'id': context.dispatch_id,
            'items': [item.as_cargo_object() for item in context.items],
            'route_points': [
                point.as_response_object() for point in context.route_points
            ],
            'status': context.status,
            'version': 1,
            'revision': context.cargo_revision,
            'emergency_contact': {'name': 'name_emergency', 'phone': '+7123'},
            'created_ts': '2020-09-19T14:42:27.642389+00:00',
            'updated_ts': '2020-09-19T14:42:27.642389+00:00',
            **performer_info,
        }

    @mockserver.json_handler(
        '/b2b-taxi/b2b/cargo/integration/v1/claims/accept',
    )
    def mock_accept(request):
        if context.cargo_accept_error_code:
            return mockserver.make_response(
                '', context.cargo_accept_error_code,
            )
        return {'id': context.dispatch_id, 'status': 'accepted', 'version': 2}

    @mockserver.json_handler(
        '/b2b-taxi/b2b/cargo/integration/v1/claims/set-points-ready',
    )
    def mock_set_points_ready(request):
        return {}

    @mockserver.json_handler(
        '/b2b-taxi/b2b/cargo/integration/v1/claims/cancel',
    )
    def mock_cancel(request):
        return {'id': context.dispatch_id, 'status': 'cancelled', 'version': 2}

    @mockserver.json_handler(
        '/b2b-taxi/b2b/cargo/integration/v1/driver-voiceforwarding',
    )
    def mock_courier_contact(request):
        if context.cargo_courier_phone_error_code:
            return mockserver.make_response(
                json.dumps({'code': 'not_found', 'message': 'some_message'}),
                context.cargo_courier_phone_error_code,
            )
        if context.check_request_flag:
            assert request.json['claim_id'] == context.dispatch_id
        return {
            'phone': context.courier_contact_phone,
            'ext': context.courier_contact_ext,
            'ttl_seconds': 2088,
        }

    @mockserver.json_handler(
        '/b2b-taxi/b2b/cargo/integration/v1/claims/performer-position',
    )
    def mock_courier_position(request):
        if context.cargo_courier_position_error:
            return mockserver.make_response(
                json.dumps({'code': 'not_found', 'message': 'some_message'}),
                context.cargo_courier_position_error,
            )
        return {
            'position': {
                'accuracy': 0,
                'direction': 25,
                'lat': 35,
                'lon': 55,
                'speed': 3,
                'timestamp': 120314,
            },
        }

    @mockserver.json_handler('/cargo-claims/internal/external-performer')
    def mock_external_performer(request):
        if context.dispatch_id is not None:
            assert context.dispatch_id == request.query['sharing_key']

        if context.cargo_performer_external_error is not None:
            return mockserver.make_response(
                json.dumps(
                    {'code': 'claim_not_ready', 'message': 'some_error'},
                ),
                context.cargo_performer_external_error,
            )

        return mockserver.make_response(
            json.dumps(
                {
                    'eats_profile_id': context.eats_profile_id,
                    'taxi_alias_id': context.taxi_alias_id,
                    'driver_id': context.driver_id,
                    'name': context.courier_name,
                    'transport_type': context.transport_type,
                },
            ),
            context.external_performer_status,
        )

    return context
