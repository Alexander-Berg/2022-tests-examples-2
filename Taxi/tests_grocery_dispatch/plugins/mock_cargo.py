# pylint: disable=wildcard-import, unused-wildcard-import, import-error
# pylint: disable=redefined-outer-name
import copy
import json

import pytest

from tests_grocery_dispatch import models


@pytest.fixture(name='cargo')
def mock_cargo(mockserver):
    class Context:
        def __init__(self):
            self.request_id = None
            self.short_order_id = None
            self.items = None
            self.claim_id = 'claim_1'
            self.new_claim = 'claim_1'
            self.dispatch_id = self.claim_id
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
            self.requirement_shift_type = None
            self.requirement_meta_group = None
            self.accept_language = None
            self.taxi_class = 'express'
            self.taxi_classes = None
            self.cargo_loaders = None
            self.delivered_eta_ts = None
            self.pickuped_eta_ts = None
            self.delivery_flags = None
            self.route_points = [models.FIRST_POINT, models.CLIENT_POINT]
            self.skip_act = None
            self.check_request_flag = False
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
            self.car_number = None
            self.car_model = None
            self.car_color = None
            self.car_color_hex = None
            self.version = 1
            self.cargo_info_timeout = None
            self.features = None
            self.performers = {}

        def set_data(
                self,
                items=None,
                status=None,
                dispatch_id=None,
                short_order_id=None,
                claim_id=None,
                new_claim=None,
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
                car_number=None,
                car_model=None,
                car_color=None,
                car_color_hex=None,
                cargo_revision=None,
                version=None,
                cargo_info_timeout=None,
                features=None,
        ):
            if items is not None:
                self.items = items
            if status is not None:
                self.status = status
            if short_order_id is not None:
                self.short_order_id = short_order_id
            if dispatch_id is not None:
                self.dispatch_id = dispatch_id
            if claim_id is not None:
                self.claim_id = claim_id
            if new_claim is not None:
                self.new_claim = new_claim
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
            if car_number is not None:
                self.car_number = car_number
            if car_model is not None:
                self.car_model = car_model
            if car_color is not None:
                self.car_color = car_color
            if car_color_hex is not None:
                self.car_color_hex = car_color_hex
            if cargo_revision is not None:
                self.cargo_revision = cargo_revision
            if version is not None:
                self.version = version
            if cargo_info_timeout is not None:
                self.cargo_info_timeout = cargo_info_timeout
            if self.features is not None:
                self.features = features

        def check_authorization(self, authorization):
            self.authorization = authorization

        def check_user_contact(self, user_phone=None, user_name=None):
            if user_phone:
                self.route_points[1].phone = user_phone
            if user_name:
                self.route_points[1].name = user_name
            self.check_user_contact_flag = True

        def check_request(
                self,
                request_id=None,
                dispatch_id=None,
                short_order_id=None,
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
                requirement_shift_type=None,
                requirement_meta_group=None,
                requirement_restriction_type=None,
                accept_language=None,
                taxi_class=None,
                taxi_classes=None,
                cargo_loaders=None,
                custom_context=None,
                authorization=None,
                features=None,
        ):
            if taxi_class is not None:
                self.taxi_class = taxi_class
            if taxi_classes is not None:
                self.taxi_classes = taxi_classes
            if cargo_loaders is not None:
                self.cargo_loaders = cargo_loaders
            if request_id is not None:
                self.request_id = request_id
            if items is not None:
                self.items = items
            if route_points is not None:
                self.route_points = route_points
            if dispatch_id is not None:
                self.dispatch_id = dispatch_id
            if short_order_id is not None:
                self.short_order_id = short_order_id
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
            if requirement_shift_type is not None:
                self.requirement_shift_type = requirement_shift_type
            if requirement_meta_group is not None:
                self.requirement_meta_group = requirement_meta_group
            if accept_language is not None:
                self.accept_language = accept_language
            if custom_context is not None:
                self.custom_context = custom_context
            if authorization is not None:
                self.authorization = authorization
            if self.delivery_flags is not None:
                self.custom_context['delivery_flags'] = self.delivery_flags
            if requirement_restriction_type is not None:
                self.requirement_restriction_type = (
                    requirement_restriction_type
                )
            if features is not None:
                self.features = features

            self.check_comment_exist = check_comment_exist
            self.check_request_flag = True

        def times_create_called(self):
            return mock_create.times_called

        def times_create_accepted_called(self):
            return mock_create_accepted.times_called

        def times_accept_called(self):
            return mock_accept.times_called

        def times_info_called(self):
            return mock_info.times_called

        def times_cancel_called(self):
            return mock_cancel.times_called

        def times_return_called(self):
            return mock_return.times_called

        def times_courier_contact_called(self):
            return mock_courier_contact.times_called

        def times_courier_position_called(self):
            return mock_courier_position.times_called

        def times_external_info_called(self):
            return mock_external_performer.times_called

        def times_set_points_ready_called(self):
            return mock_set_points_ready.times_called

        def set_external_performer_status(self, status_code):
            self.external_performer_status = status_code

        def flush(self):
            mock_create.flush()

        def _convert_to_cargo_item(self, item):
            if not isinstance(item, dict):
                cargo_item = item.dict(exclude_none=True)
            else:
                cargo_item = copy.deepcopy(item)
            cargo_item['quantity'] = int(cargo_item['quantity'])
            cargo_item['pickup_point'] = 1
            cargo_item['droppof_point'] = 2
            cargo_item['cost_value'] = cargo_item['price']
            cargo_item['cost_currency'] = cargo_item['currency']
            cargo_item['extra_id'] = cargo_item['item_id']
            if 'weight' in cargo_item:
                cargo_item['weight'] = cargo_item['weight'] / 1000
            if 'width' in cargo_item:
                cargo_item['size'] = {}
                cargo_item['size']['width'] = cargo_item['width'] / 1000
                del cargo_item['width']
            if 'height' in cargo_item:
                cargo_item['size']['height'] = cargo_item['height'] / 1000
                del cargo_item['height']
            if 'depth' in cargo_item:
                cargo_item['size']['length'] = cargo_item['depth'] / 1000
                del cargo_item['depth']
            del cargo_item['price']
            del cargo_item['currency']
            del cargo_item['item_id']
            if 'item_tags' in cargo_item:
                del cargo_item['item_tags']
            return cargo_item

        def convert_items(self, items):
            return [self._convert_to_cargo_item(point) for point in items]

        def add_performer(
                self,
                *,
                name='test_courier_name',
                claim_id,
                eats_profile_id,
                driver_id,
                park_id,
                transport_type=None,
                car_number=None,
                car_model=None,
                car_color=None,
                car_color_hex=None,
        ):
            json = {}

            for key, val in zip(
                    [
                        'eats_profile_id',
                        'driver_id',
                        'park_id',
                        'name',
                        'transport_type',
                    ],
                    [
                        eats_profile_id,
                        driver_id,
                        park_id,
                        name,
                        transport_type,
                    ],
            ):
                if val is not None:
                    json[key] = val

            car_info = {}

            if car_number is not None:
                car_info['number'] = car_number
            if car_model is not None:
                car_info['model'] = car_model
            if car_color is not None:
                car_info['color'] = car_color
            if car_color_hex is not None:
                car_info['color_hex'] = car_color_hex

            if car_info:
                json['car_info'] = car_info

            self.performers[claim_id] = json

    context = Context()

    @mockserver.json_handler(
        '/b2b-taxi/b2b/cargo/integration/v2/claims/create',
    )
    def mock_create(request):
        if context.check_request_flag:
            if context.items is not None:
                assert request.json['items'] == [
                    item for item in context.items
                ]
            if context.short_order_id is not None:
                for point in request.json['route_points']:
                    assert (
                        point.get('external_order_id', context.short_order_id)
                        == context.short_order_id
                    )
            assert len(request.json['route_points']) == len(
                context.route_points,
            )
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
            if context.cargo_loaders:
                assert (
                    request.json['client_requirements']['cargo_loaders']
                    == context.cargo_loaders
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
            if context.requirement_shift_type:
                assert (
                    request.json['requirements']['soft_requirements'][0][
                        'shift_type'
                    ]
                    == context.requirement_shift_type
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
            if context.requirement_shift_type:
                assert (
                    request.json['requirements']['soft_requirements'][0][
                        'shift_type'
                    ]
                    == context.requirement_shift_type
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

        if context.features is not None:
            assert request.json['features'] == context.features

        if context.custom_context is not None:
            actual_custom_context = request.json['custom_context']
            expected_custom_context = context.custom_context
            if (
                    'dispatch_id' in expected_custom_context
                    and expected_custom_context['dispatch_id'] == 'placeholder'
            ):
                # Мы в тесте не знаем dispatch_id во время похода в карго,
                # поэтому проверяем только его наличие.
                # Сделать специальный TESTPOINT в DispatchFacade?
                assert 'dispatch_id' in actual_custom_context
                actual_custom_context.pop('dispatch_id')
                expected_custom_context.pop('dispatch_id')

            assert expected_custom_context == actual_custom_context

        if context.requirement_restriction_type is not None:
            assert (
                request.json['requirements']['soft_requirements'][0][
                    'performers_restriction_type'
                ]
                == context.requirement_restriction_type
            )

        return {
            'id': context.new_claim,
            'items': request.json['items'],
            'route_points': [
                point.as_response_object() for point in context.route_points
            ],
            'status': context.status,
            'version': context.version,
            'revision': 1,
            'created_ts': '2020-09-19T14:42:27.642389+00:00',
            'updated_ts': '2020-09-19T14:42:27.642389+00:00',
        }

    @mockserver.json_handler(
        '/b2b-taxi/b2b/cargo/integration/v2/claims/create-accepted',
    )
    def mock_create_accepted(request):
        if context.check_request_flag:
            if context.items is not None:
                assert request.json['claim']['items'] == [
                    item for item in context.items
                ]
            if context.short_order_id is not None:
                for point in request.json['claim']['route_points']:
                    assert (
                        point.get('external_order_id', context.short_order_id)
                        == context.short_order_id
                    )
            assert len(request.json['claim']['route_points']) == len(
                context.route_points,
            )
            assert request.json['claim']['route_points'] == [
                point.as_object() for point in context.route_points
            ]
            assert (
                request.json['claim']['client_requirements']['taxi_class']
                == context.taxi_class
            )
            if context.taxi_classes:
                assert (
                    request.json['claim']['client_requirements'][
                        'taxi_classes'
                    ]
                    == context.taxi_classes
                )
            if context.cargo_loaders:
                assert (
                    request.json['client_requirements']['cargo_loaders']
                    == context.cargo_loaders
                )
            assert request.json['claim']['skip_client_notify']
            if context.due_time_point:
                assert request.json['claim']['due'] == context.due_time_point
            if context.emergency_contact:
                assert (
                    request.json['claim']['emergency_contact']['name'],
                    request.json['claim']['emergency_contact']['phone'],
                ) == context.emergency_contact
            if context.claim_kind:
                assert (
                    request.json['claim']['claim_kind'] == context.claim_kind
                )
            if context.requirement_type:
                assert (
                    request.json['claim']['requirements']['soft_requirements'][
                        0
                    ]['type']
                    == context.requirement_type
                )
            if context.requirement_logistic_group:
                assert (
                    request.json['claim']['requirements']['soft_requirements'][
                        0
                    ]['logistic_group']
                    == context.requirement_logistic_group
                )
            if context.requirement_shift_type:
                assert (
                    request.json['claim']['requirements']['soft_requirements'][
                        0
                    ]['shift_type']
                    == context.requirement_shift_type
                )
            if context.requirement_meta_group:
                assert (
                    request.json['claim']['requirements']['soft_requirements'][
                        0
                    ]['meta_group']
                    == context.requirement_meta_group
                )
            if context.skip_client_notify:
                assert (
                    request.json['claim']['skip_client_notify']
                    == context.skip_client_notify
                )
            if context.skip_emergency_notify:
                assert (
                    request.json['claim']['skip_emergency_notify']
                    == context.skip_emergency_notify
                )
            if context.skip_door_to_door:
                assert (
                    request.json['claim']['skip_door_to_door']
                    == context.skip_door_to_door
                )

            if context.optional_return:
                assert (
                    request.json['claim']['optional_return']
                    == context.optional_return
                )
            if context.comment:
                assert request.json['claim']['comment'] == context.comment
            elif context.check_comment_exist:
                assert 'comment' not in request.json['claim']

        if context.check_user_contact_flag:
            assert request.json['claim']['route_points'][1]['contact'] == {
                'name': context.route_points[1].name,
                'phone': context.route_points[1].phone,
            }

        if context.number_of_user_address_parts:
            route_point = request.json['claim']['route_points'][1]
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
                    request.json['claim']['requirements']['soft_requirements'][
                        0
                    ]['type']
                    == context.requirement_type
                )
            if context.requirement_logistic_group:
                assert (
                    request.json['claim']['requirements']['soft_requirements'][
                        0
                    ]['logistic_group']
                    == context.requirement_logistic_group
                )
            if context.requirement_shift_type:
                assert (
                    request.json['claim']['requirements']['soft_requirements'][
                        0
                    ]['shift_type']
                    == context.requirement_shift_type
                )
            if context.requirement_meta_group:
                assert (
                    request.json['claim']['requirements']['soft_requirements'][
                        0
                    ]['meta_group']
                    == context.requirement_meta_group
                )
        if context.skip_act:
            assert request.json['claim']['skip_act'] == context.skip_act

        if context.custom_context is not None:
            actual_custom_context = request.json['claim']['custom_context']
            expected_custom_context = context.custom_context
            if (
                    'dispatch_id' in expected_custom_context
                    and expected_custom_context['dispatch_id'] == 'placeholder'
            ):
                # Мы в тесте не знаем dispatch_id во время похода в карго,
                # поэтому проверяем только его наличие.
                # Сделать специальный TESTPOINT в DispatchFacade?
                assert 'dispatch_id' in actual_custom_context
                actual_custom_context.pop('dispatch_id')
                expected_custom_context.pop('dispatch_id')

            assert expected_custom_context == actual_custom_context

        if context.requirement_restriction_type is not None:
            assert (
                request.json['claim']['requirements']['soft_requirements'][0][
                    'performers_restriction_type'
                ]
                == context.requirement_restriction_type
            )

        return {
            'id': context.new_claim,
            'items': request.json['claim']['items'],
            'route_points': [
                point.as_response_object() for point in context.route_points
            ],
            'status': context.status,
            'version': context.version,
            'revision': 1,
            'created_ts': '2020-09-19T14:42:27.642389+00:00',
            'updated_ts': '2020-09-19T14:42:27.642389+00:00',
        }

    @mockserver.json_handler('/b2b-taxi/b2b/cargo/integration/v2/claims/info')
    def mock_info(request):
        if context.cargo_info_timeout:
            raise mockserver.TimeoutError()
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
                    'car_number': context.car_number,
                    'car_model': context.car_model,
                    'car_color': context.car_color,
                    'car_color_hex': context.car_color_hex,
                },
            }
            if context.courier_name
            else {}
        )

        return {
            'id': context.dispatch_id,
            'items': context.items,
            'route_points': [
                point.as_response_object() for point in context.route_points
            ],
            'current_point_id': context.route_points[0].point_id,
            'status': context.status,
            'version': context.version,
            'revision': context.cargo_revision,
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
        '/b2b-taxi/b2b/cargo/integration/v1/claims/return',
    )
    def mock_return(request):
        return {}

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

    @mockserver.json_handler('/b2b-taxi/b2b/cargo/integration/v1/check-price')
    def _mock_check_price(request):
        return {'price': '100.00', 'requirements': {}}

    @mockserver.json_handler('/cargo-claims/internal/external-performer')
    def mock_external_performer(request):
        if context.cargo_performer_external_error is not None:
            return mockserver.make_response(
                json.dumps({'code': 'not_found', 'message': 'some_message'}),
                context.cargo_performer_external_error,
            )
        claim_id = request.query['sharing_key']
        json_resp = context.performers[claim_id]
        eats_profile_id = None
        if json_resp:
            eats_profile_id = json_resp['eats_profile_id']

        batch_claim_ids = []
        for batch_claim_id, performer in context.performers.items():
            if performer and performer['eats_profile_id'] == eats_profile_id:
                batch_claim_ids.append(batch_claim_id)

        if len(batch_claim_ids) > 1:
            json_resp['batch_info'] = {
                'delivery_order': [
                    {'order': idx + 1, 'claim_id': batch_claim_id}
                    for idx, batch_claim_id in enumerate(batch_claim_ids)
                ],
            }

        return mockserver.make_response(json=json_resp)

    return context
