# pylint: disable=import-only-modules, import-error, redefined-outer-name
import copy
import datetime
import json

import pytest
import yandex.maps.proto.driving.summary_pb2 as ProtoDrivingSummary
import yandex.maps.proto.masstransit.summary_pb2 as ProtoMasstransitSummary

from tests_shuttle_control.utils import select_named

HEADERS = {
    'X-Request-Application': 'taximeter',
    'X-Request-Platform': 'android',
    'X-Request-Application-Version': '9.07',
    'X-YaTaxi-Park-Id': '111',
    'X-YaTaxi-Driver-Profile-Id': '888',
    'Accept-Language': 'ru',
}

STATIC_OFFERS = [
    {
        'offer_id': 'acfff773-398f-4913-b9e9-03bf5eda11ac',
        'shuttle_id': 1,
        'order_point_a': '(30,60)',
        'order_point_b': '(31,61)',
        'pickup_stop_id': 1,
        'pickup_lap': 1,
        'dropoff_stop_id': 2,
        'dropoff_lap': 1,
        'price': '(10.0000,RUB)',
        'created_at': datetime.datetime(2020, 1, 17, 18, 0),
        'expires_at': datetime.datetime(2020, 1, 17, 18, 18),
        'external_confirmation_code': None,
        'external_passenger_id': None,
        'passengers_count': 1,
        'yandex_uid': '012345618',
        'route_id': 1,
        'payment_type': None,
        'payment_method_id': None,
        'dropoff_timestamp': None,
        'pickup_timestamp': None,
        'suggested_route_view': None,
        'suggested_traversal_plan': None,
    },
    {
        'offer_id': 'acfff773-398f-4913-b9e9-03bf5eda12ac',
        'shuttle_id': 1,
        'order_point_a': '(30,60)',
        'order_point_b': '(31,61)',
        'pickup_stop_id': 1,
        'pickup_lap': 1,
        'dropoff_stop_id': 2,
        'dropoff_lap': 1,
        'price': '(10.0000,RUB)',
        'created_at': datetime.datetime(2020, 1, 17, 18, 0),
        'expires_at': datetime.datetime(2020, 1, 17, 18, 18),
        'external_confirmation_code': None,
        'external_passenger_id': None,
        'passengers_count': 1,
        'yandex_uid': '012345613',
        'route_id': 1,
        'payment_type': None,
        'payment_method_id': None,
        'dropoff_timestamp': None,
        'pickup_timestamp': None,
        'suggested_route_view': None,
        'suggested_traversal_plan': None,
    },
    {
        'offer_id': 'acfff773-398f-4913-b9e9-03bf5eda13ac',
        'shuttle_id': 1,
        'order_point_a': '(30,60)',
        'order_point_b': '(31,61)',
        'pickup_stop_id': 1,
        'pickup_lap': 1,
        'dropoff_stop_id': 2,
        'dropoff_lap': 1,
        'price': '(10.0000,RUB)',
        'created_at': datetime.datetime(2020, 1, 17, 18, 0),
        'expires_at': datetime.datetime(2020, 1, 17, 18, 18),
        'external_confirmation_code': None,
        'external_passenger_id': None,
        'passengers_count': 1,
        'yandex_uid': '012345612',
        'route_id': 1,
        'payment_type': None,
        'payment_method_id': None,
        'dropoff_timestamp': None,
        'pickup_timestamp': None,
        'suggested_route_view': None,
        'suggested_traversal_plan': None,
    },
    {
        'offer_id': 'acfff773-398f-4913-b9e9-03bf5eda14ac',
        'shuttle_id': 1,
        'order_point_a': '(30,60)',
        'order_point_b': '(31,61)',
        'pickup_stop_id': 1,
        'pickup_lap': 1,
        'dropoff_stop_id': 2,
        'dropoff_lap': 1,
        'price': '(10.0000,RUB)',
        'created_at': datetime.datetime(2020, 1, 17, 18, 0),
        'expires_at': datetime.datetime(2020, 1, 17, 18, 18),
        'external_confirmation_code': None,
        'external_passenger_id': None,
        'passengers_count': 1,
        'yandex_uid': '012345614',
        'route_id': 1,
        'payment_type': None,
        'payment_method_id': None,
        'dropoff_timestamp': None,
        'pickup_timestamp': None,
        'suggested_route_view': None,
        'suggested_traversal_plan': None,
    },
    {
        'offer_id': 'acfff773-398f-4913-b9e9-03bf5eda22ac',
        'shuttle_id': 1,
        'order_point_a': '(30,60)',
        'order_point_b': '(31,61)',
        'pickup_stop_id': 1,
        'pickup_lap': 1,
        'dropoff_stop_id': 2,
        'dropoff_lap': 1,
        'price': '(10.0000,RUB)',
        'created_at': datetime.datetime(2020, 1, 17, 18, 0),
        'expires_at': datetime.datetime(2020, 1, 17, 18, 18),
        'external_confirmation_code': None,
        'external_passenger_id': None,
        'passengers_count': 1,
        'yandex_uid': '012345678',
        'route_id': 1,
        'payment_type': None,
        'payment_method_id': None,
        'dropoff_timestamp': None,
        'pickup_timestamp': None,
        'suggested_route_view': None,
        'suggested_traversal_plan': None,
    },
    {
        'offer_id': 'acfff773-398f-4913-b9e9-03bf5eda26ac',
        'shuttle_id': 1,
        'order_point_a': '(30,60)',
        'order_point_b': '(31,61)',
        'pickup_stop_id': 1,
        'pickup_lap': 1,
        'dropoff_stop_id': 2,
        'dropoff_lap': 1,
        'price': '(10.0000,RUB)',
        'created_at': datetime.datetime(2020, 1, 17, 18, 0),
        'expires_at': datetime.datetime(2020, 1, 17, 18, 18),
        'external_confirmation_code': None,
        'external_passenger_id': None,
        'passengers_count': 1,
        'yandex_uid': '012345673',
        'route_id': 1,
        'payment_type': None,
        'payment_method_id': None,
        'dropoff_timestamp': None,
        'pickup_timestamp': None,
        'suggested_route_view': None,
        'suggested_traversal_plan': None,
    },
    {
        'offer_id': 'acfff773-398f-4913-b9e9-03bf5eda25ac',
        'shuttle_id': 1,
        'order_point_a': '(30,60)',
        'order_point_b': '(31,61)',
        'pickup_stop_id': 1,
        'pickup_lap': 1,
        'dropoff_stop_id': 2,
        'dropoff_lap': 1,
        'price': '(10.0000,RUB)',
        'created_at': datetime.datetime(2020, 1, 17, 18, 0),
        'expires_at': datetime.datetime(2020, 1, 17, 18, 18),
        'external_confirmation_code': None,
        'external_passenger_id': None,
        'passengers_count': 1,
        'yandex_uid': '012345670',
        'route_id': 1,
        'payment_type': None,
        'payment_method_id': None,
        'dropoff_timestamp': None,
        'pickup_timestamp': None,
        'suggested_route_view': None,
        'suggested_traversal_plan': None,
    },
    {
        'offer_id': 'acfff773-398f-4913-b9e9-03bf5eda24ac',
        'shuttle_id': 1,
        'order_point_a': '(30,60)',
        'order_point_b': '(31,61)',
        'pickup_stop_id': 1,
        'pickup_lap': 1,
        'dropoff_stop_id': 2,
        'dropoff_lap': 1,
        'price': '(10.0000,RUB)',
        'created_at': datetime.datetime(2020, 1, 17, 18, 0),
        'expires_at': datetime.datetime(2020, 1, 17, 18, 18),
        'external_confirmation_code': None,
        'external_passenger_id': None,
        'passengers_count': 1,
        'yandex_uid': '012345671',
        'route_id': 1,
        'payment_type': None,
        'payment_method_id': None,
        'dropoff_timestamp': None,
        'pickup_timestamp': None,
        'suggested_route_view': None,
        'suggested_traversal_plan': None,
    },
    {
        'offer_id': 'acfff773-398f-4913-b9e9-03bf5eda23ac',
        'shuttle_id': 1,
        'order_point_a': '(30,60)',
        'order_point_b': '(31,61)',
        'pickup_stop_id': 1,
        'pickup_lap': 1,
        'dropoff_stop_id': 2,
        'dropoff_lap': 1,
        'price': '(10.0000,RUB)',
        'created_at': datetime.datetime(2020, 1, 17, 18, 0),
        'expires_at': datetime.datetime(2020, 1, 17, 18, 18),
        'external_confirmation_code': None,
        'external_passenger_id': None,
        'passengers_count': 1,
        'yandex_uid': '012345672',
        'route_id': 1,
        'payment_type': None,
        'payment_method_id': None,
        'dropoff_timestamp': None,
        'pickup_timestamp': None,
        'suggested_route_view': None,
        'suggested_traversal_plan': None,
    },
]


def _proto_driving_summary(time, distance):
    response = ProtoDrivingSummary.Summaries()
    item = response.summaries.add()
    item.weight.time.value = time
    item.weight.time.text = ''
    item.weight.time_with_traffic.value = time
    item.weight.time_with_traffic.text = ''
    item.weight.distance.value = distance
    item.weight.distance.text = ''
    item.flags.blocked = False
    return response.SerializeToString()


def _proto_masstransit_summary(time, distance):
    response = ProtoMasstransitSummary.Summaries()
    item = response.summaries.add()
    item.weight.time.value = time
    item.weight.time.text = ''
    item.weight.walking_distance.value = distance
    item.weight.walking_distance.text = ''
    item.weight.transfers_count = 1
    return response.SerializeToString()


@pytest.mark.now('2020-01-17T18:17:38+0000')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
@pytest.mark.config(
    SHUTTLE_CONTROL_ROUTE_TANKER_KEYS_BY_USER_TYPE={
        'route1': {
            'driver': 'shuttle_control.routes.route1.name_for_driver',
            'passenger': 'shuttle_control.routes.route1.name_for_passenger',
        },
    },
)
@pytest.mark.parametrize(
    'shuttle_id,stop_id,response_code',
    [
        ('gkZxnYQ73QGqrKyz', 'shuttle-stop-gkZxnYQ73QGqrKyz', 200),
        ('Pmp80rQ23L4wZYxd', 'shuttle-stop-gkZxnYQ73QGqrKyz', 200),
        ('VlAK13MzaLx6Bmnd', 'shuttle-stop-Pmp80rQ23L4wZYxd', 200),
        ('bjoAWlMYJRG14Nnm', 'shuttle-stop-gkZxnYQ73QGqrKyz', 400),
    ],
)
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
async def test_main(
        taxi_shuttle_control,
        pgsql,
        shuttle_id,
        stop_id,
        response_code,
        mockserver,
        load_json,
        load_binary,
        driver_trackstory_v2_shorttracks,
):
    @mockserver.handler('/maps-router/v2/summary')
    def _mock_router(request):
        return mockserver.make_response(
            response=_proto_driving_summary(500, 1000),
            status=200,
            content_type='application/x-protobuf',
        )

    @mockserver.handler('/maps-router/v2/route')
    def _mock_router_route(request):
        return mockserver.make_response(
            response=load_binary('v2_route_response.pb'),
            status=200,
            content_type='application/x-protobuf',
        )

    def _mock():
        return {
            'results': [
                {
                    'position': {
                        'lon': 30.5,
                        'lat': 60.5,
                        'timestamp': 1622202780,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid0_uuid0',
                },
                {
                    'position': {
                        'lon': 30.5,
                        'lat': 60.5,
                        'timestamp': 1622202780,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid1_uuid1',
                },
                {
                    'position': {
                        'lon': 30.5,
                        'lat': 60.5,
                        'timestamp': 1622202780,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid2_uuid2',
                },
                {
                    'position': {
                        'lon': 30.5,
                        'lat': 60.5,
                        'timestamp': 1622202780,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid3_uuid3',
                },
                {
                    'position': {
                        'lon': 30.5,
                        'lat': 60.5,
                        'timestamp': 1622202780,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid4_uuid4',
                },
            ],
        }

    driver_trackstory_v2_shorttracks.set_data_from_positions(_mock())

    @mockserver.json_handler('/pricing-data-preparer/v2/prepare')
    def _mock_v2_prepare(request):
        req = json.loads(request.get_data())
        assert req['extra'] == {
            'providers': {
                'discounts': {'is_enabled': False},
                'router': {'is_fallback': True},
                'surge': {'is_enabled': False},
            },
            'shuttle_params': {'is_street_hail_booking': True},
        }

        shuttle_category = load_json('v2_prepare_response.json')
        return mockserver.make_response(
            json={'categories': {'shuttle': shuttle_category}}, status=200,
        )

    @mockserver.json_handler('/pricing-data-preparer/v2/recalc')
    def _mock_v2_recalc(request):
        return mockserver.make_response(
            json={
                'price': {
                    'driver': {'total': 45, 'meta': {}},
                    'user': {'total': 45, 'meta': {}},
                },
            },
            status=200,
        )

    headers = copy.deepcopy(HEADERS)

    if shuttle_id == 'bjoAWlMYJRG14Nnm':
        headers['X-YaTaxi-Park-Id'] = 'uuid4'
        headers['X-YaTaxi-Driver-Profile-Id'] = 'uuid4'

    response = await taxi_shuttle_control.post(
        '/driver/v1/shuttle-control/v1/street_hailing/create_offer',
        headers=headers,
        params={'shuttle_id': shuttle_id},
        json={'dropoff_stop_id': stop_id},
    )

    rows = select_named(
        """
        SELECT * FROM state.matching_offers
        ORDER BY pickup_stop_id
        """,
        pgsql['shuttle_control'],
    )
    for offer in STATIC_OFFERS:
        assert offer in rows
        rows.remove(offer)

    if shuttle_id == 'gkZxnYQ73QGqrKyz':
        assert response.status_code == 200
        assert response.json()['items'] == [
            {
                'horizontal_divider_type': 'bottom_gap',
                'primary_text_color': 'main_text',
                'right_tip': {
                    'form': 'square',
                    'icon': {'icon_type': 'cash2'},
                    'size': 'mu_4',
                },
                'secondary_text_color': 'main_text',
                'subtitle': 'Oplata nali4nimy',
                'subtitle_text_style': 'caption',
                'title': '45 руб.',
                'title_text_style': 'title',
                'type': 'detail_tip',
            },
            {
                'horizontal_divider_type': 'none',
                'reverse': True,
                'subtitle': 'stop1',
                'title': 'Ostanovka',
                'type': 'detail_tip',
            },
        ]

        assert rows == [
            {
                'offer_id': rows[0]['offer_id'],
                'yandex_uid': None,
                'shuttle_id': 1,
                'route_id': 1,
                'order_point_a': '(30.5,60.5)',
                'order_point_b': '(37.642853,55.735233)',
                'pickup_stop_id': 3,
                'pickup_lap': 4,
                'dropoff_stop_id': 1,
                'dropoff_lap': 4,
                'price': '(45.0000,RUB)',
                'passengers_count': 1,
                'created_at': datetime.datetime(2020, 1, 17, 18, 17, 38),
                'expires_at': datetime.datetime(2020, 1, 17, 18, 18, 38),
                'external_confirmation_code': None,
                'external_passenger_id': None,
                'payment_type': 'cash',
                'payment_method_id': None,
                'dropoff_timestamp': None,
                'pickup_timestamp': None,
                'suggested_route_view': None,
                'suggested_traversal_plan': None,
            },
        ]

    elif shuttle_id == 'Pmp80rQ23L4wZYxd':
        assert response.status_code == 200
        assert response.json()['items'] == [
            {
                'horizontal_divider_type': 'bottom_gap',
                'primary_text_color': 'main_text',
                'right_tip': {
                    'form': 'square',
                    'icon': {'icon_type': 'cash2'},
                    'size': 'mu_4',
                },
                'secondary_text_color': 'main_text',
                'subtitle': 'Oplata nali4nimy',
                'subtitle_text_style': 'caption',
                'title': '45 руб.',
                'title_text_style': 'title',
                'type': 'detail_tip',
            },
            {
                'horizontal_divider_type': 'none',
                'reverse': True,
                'subtitle': 'stop1',
                'title': 'Ostanovka',
                'type': 'detail_tip',
            },
        ]

        assert rows == [
            {
                'offer_id': rows[0]['offer_id'],
                'yandex_uid': None,
                'shuttle_id': 2,
                'route_id': 1,
                'order_point_a': '(30.5,60.5)',
                'order_point_b': '(37.642853,55.735233)',
                'pickup_stop_id': 4,
                'pickup_lap': 2,
                'dropoff_stop_id': 1,
                'dropoff_lap': 3,
                'price': '(45.0000,RUB)',
                'passengers_count': 1,
                'created_at': datetime.datetime(2020, 1, 17, 18, 17, 38),
                'expires_at': datetime.datetime(2020, 1, 17, 18, 18, 38),
                'external_confirmation_code': None,
                'external_passenger_id': None,
                'payment_type': 'cash',
                'payment_method_id': None,
                'dropoff_timestamp': None,
                'pickup_timestamp': None,
                'suggested_route_view': None,
                'suggested_traversal_plan': None,
            },
        ]

    elif shuttle_id == 'VlAK13MzaLx6Bmnd' or '80vm7DQm7Ml24ZdO':
        assert response.status_code == 400
        assert (
            response.json()['message'] == 'Этот вариант посадки уже недоступен'
        )

        assert rows == []

    else:
        assert 0
