# pylint: disable=import-only-modules, import-error
import datetime

import pytest
import yandex.maps.proto.driving.summary_pb2 as ProtoDrivingSummary

from tests_shuttle_control.utils import select_named


MOCK_NOW = '2020-09-14T14:15:16+0000'
MOCK_NOW_DT = datetime.datetime(2020, 9, 14, 14, 15, 16)


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


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize(
    'booking_id', ['2fef68c9-25d0-4174-9dd0-bdd1b3730776'],
)
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
@pytest.mark.experiments3(filename='shuttle_booking_information_settings.json')
async def test_main(taxi_shuttle_control, mockserver, booking_id, pgsql):
    @mockserver.handler('/maps-router/v2/summary')
    def _mock_router(request):
        return mockserver.make_response(
            response=_proto_driving_summary(100, 10500),
            status=200,
            content_type='application/x-protobuf',
        )

    @mockserver.json_handler('/driver-trackstory/position')
    def _mock(request):
        return {
            'position': {'lon': 30.008, 'lat': 60.008, 'timestamp': 3},
            'type': 'adjusted',
        }

    @mockserver.json_handler('/fleet-parks/v1/parks')
    def _mock_park(request):
        return {
            'id': '',
            'login': '',
            'name': '',
            'is_active': True,
            'city_id': '',
            'locale': '',
            'is_billing_enabled': True,
            'is_franchising_enabled': True,
            'country_id': 'russian_id',
            'demo_mode': True,
            'geodata': {'lat': 0, 'lon': 1, 'zoom': 2},
        }

    for _ in range(2):
        response = await taxi_shuttle_control.post(
            '/4.0/shuttle-control/v1/booking/cancel?booking_id=' + booking_id,
            headers={'X-Yandex-UID': '0123456789'},
        )

        rows = select_named(
            """
            SELECT booking_id, yandex_uid, shuttle_id, stop_id,
            dropoff_stop_id, status, finished_at, ticket, cancel_reason
            FROM state.passengers
            WHERE booking_id = '2fef68c9-25d0-4174-9dd0-bdd1b3730776'
            ORDER BY yandex_uid, shuttle_id, stop_id
            """,
            pgsql['shuttle_control'],
        )
        assert rows == [
            {
                'booking_id': booking_id,
                'yandex_uid': '0123456789',
                'shuttle_id': 2,
                'stop_id': 1,
                'dropoff_stop_id': 5,
                'status': 'cancelled',
                'ticket': '123',
                'finished_at': MOCK_NOW_DT,
                'cancel_reason': 'by_user',
            },
        ]

        assert response.status_code == 200
        assert response.json() == {
            'tariff_info': {'class_name': 'Шаттл'},
            'booking_id': booking_id,
            'status': 'cancelled',
            'available_actions': ['cancel', 'contact_support'],
            'typed_experiments': {'items': [], 'version': -1},
            'route': {
                'dropoff_stop': {
                    'position': [30.0, 60.0],
                    'stop_id': 'stop__5',
                },
                'id': 'gkZxnYQ73QGqrKyz',
                'pickup_stop': {
                    'position': [30.0, 60.0],
                    'stop_id': 'stop__123',
                },
            },
            'cost': {'total': '10 $SIGN$$CURRENCY$'},
            'currency_rules': {
                'code': 'RUB',
                'sign': '₽',
                'template': '$VALUE$ $SIGN$$CURRENCY$',
                'text': 'руб.',
            },
            'destination_point': {
                'full_text': '',
                'position': [30.0, 60.0],
                'short_text': '',
            },
            'source_point': {
                'full_text': '',
                'position': [30.0, 60.0],
                'short_text': '',
            },
            'payment': {'type': 'cash'},
            'ticket': {'code': '123'},
            'ui': {
                'main_panel': {
                    'title': 'Бронирование отменено',
                    'subtitle': 'Пока не ясно почему',
                    'footer': {
                        'payment_text': 'Оплата наличными',
                        'text': 'Билет 123',
                    },
                },
                'cancellation_dialog': {
                    'back_button_text': 'Назад',
                    'confirm_button_text': 'Да, отменить поездку',
                    'subtitle': 'Подзаголовок',
                    'title': 'Точно решили не ехать?',
                },
                'support_dialog': {
                    'back_button_text': 'Назад',
                    'items': [],
                    'title_text': 'Заголовок',
                },
                'card_details': {
                    'button_text': 'Ясно',
                    'image_tag': 'class_shuttle_car_detailed_card',
                    'popup_config': {
                        'max_popups_count': 5,
                        'seconds_before_count_reset': 600,
                    },
                    'text': 'Стоимость 10 $SIGN$$CURRENCY$',
                    'title': 'Билет 123',
                },
            },
        }
