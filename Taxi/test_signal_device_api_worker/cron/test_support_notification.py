# pylint: disable=import-only-modules
import bson
import pytest

from signal_device_api_worker.components import video_identifier_class
from signal_device_api_worker.components.support_notification import (
    _notify_support,
)


TRACKER_KEY = 'TREK-228'
SUPPORT_SETTINGS = {
    'event_types': ['tired', 'road_accident'],
    'is_enabled': True,
    'park_specifications': [['signalq', 'taxi']],
    'ticket_description': (
        'Информация о машине: id = {car_id}\n'
        'Водитель: ((https://opteum.taxi.yandex-team.ru/drivers/{driver_profile_id}/parks/{park_id}/card {last_name} {first_name} {middle_name}))\n'  # noqa: E501 pylint: disable=line-too-long
        'Центр мониторинга: ((https://fleet.yandex.ru/signalq/stream/{thread_id}?park_id={park_id}))\n'  # noqa: E501 pylint: disable=line-too-long
        'ID заказа для партнёра: ((https://tariff-editor.taxi.yandex-team.ru/orders/{public_order_id} {public_order_id}))\n'  # noqa: E501 pylint: disable=line-too-long
        'Внутренний ID заказа: {internal_order_id}\n'
        'Время: {event_at}\n'
        'Уникальный ID водителя: {unique_driver_id}\n'
        'Ссылка для поднятия тревоги: ((https://fleet.yandex-team.ru/api/fleet/signal-device-message-api/v1/event?jwt_signature={jwt_signature}))\n'  # noqa: E501 pylint: disable=line-too-long
    ),
    'anonymous_driver_ticket_description': (
        'Водитель не определен\n'
        'Информация о машине: id : {car_id}, номер : {car_number}\n'
        'Возможные водители:\n'
        '{possible_drivers}\n'
        'Центр мониторинга: ((https://fleet.yandex.ru/signalq/stream/{thread_id}?park_id={park_id}))\n'  # noqa: E501 pylint: disable=line-too-long
        'Время: {event_at}\n'
        'Ссылка для поднятия тревоги: ((https://fleet.yandex-team.ru/api/fleet/signal-device-message-api/v1/event?jwt_signature={jwt_signature}))\n'  # noqa: E501 pylint: disable=line-too-long
    ),
    'ticket_queue': 'SUPPARTNERS',
    'possible_driver_info': (
        '{last_name} {first_name} {middle_name} https://opteum.taxi.yandex-team.ru/drivers/{driver_profile_id}/parks/{park_id}/card \n'  # noqa: E501 pylint: disable=line-too-long
        'Текущий статус: {status}\n'
        'Уникальный Id водителя: {unique_driver_id}\n\n'
    ),
    'ticket_summary': {
        'road_accident': (
            'Зафиксировано ДТП {last_name} {first_name} {middle_name}'
        ),
        'tired': (
            'Обнаружена сонливость {last_name} {first_name} {middle_name}'
        ),
    },
    'ticket_tags': {
        '__default__': ['signalq_video'],
        'road_accident': ['signalq_proactive_accident'],
    },
}


@pytest.mark.now('2019-09-16T12:00:00.0+0000')
@pytest.mark.config(
    SIGNAL_DEVICE_API_WORKER_SUPPORT_SETTINGS_V4=SUPPORT_SETTINGS,
)
@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['test_notify_support_anon.sql'],
)
async def test_notify_support_anon(pgsql, stq3_context, mockserver, load_json):
    tracker_uniques = []
    attachment_names = []

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def __fleet_parks_response(request):
        return load_json('fleet_parks_response.json')

    @mockserver.json_handler('/parks/driver-profiles/list')
    def __parks_response(request):
        return load_json('parks_response.json')

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    def __unique_drivers_response(request):
        return {
            'uniques': [
                {
                    'data': {'unique_driver_id': 'unique_driver_id_1'},
                    'park_driver_profile_id': (
                        'p2_3b0af7c6544f1d7c8e74fbabe4ec0f45'
                    ),
                },
                {
                    'data': {'unique_driver_id': 'unique_driver_id_2'},
                    'park_driver_profile_id': (
                        'p2_68adad2a1769c43a7ffc8ba8bcdc1c34'
                    ),
                },
            ],
        }

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def __driver_profiles(request):
        return {'profiles': [{'park_driver_profile_id': '123123'}]}

    @mockserver.json_handler('/api-tracker/v2/issues')
    def __api_tracker_response(request):
        unique = request.json['unique']
        if unique in tracker_uniques:
            return mockserver.make_response(
                headers=({'X-Ticket-Key': TRACKER_KEY}),
                json=(
                    {'errorMessages': ['already exists'], 'statusCode': 409}
                ),
                status=409,
            )
        tracker_uniques.append(unique)
        assert request.json == load_json('notify_support_anon_result.json')
        return mockserver.make_response(
            json=({'key': TRACKER_KEY, 'id': '593cd211ef7e8a332414f2a7'}),
            status=201,
        )

    @mockserver.json_handler(
        f'/api-tracker/v2/issues/{TRACKER_KEY}/attachments',
    )
    def __api_tracker_response2(request):
        if request.method == 'POST':
            attachment_names.append(request.query['filename'])
            return mockserver.make_response(
                json=({'id': '593cd211ef7e8a332414f2a2'}), status=201,
            )
        attachments_info = []
        for name in attachment_names:
            attachments_info.append({'name': name})
        return mockserver.make_response(json=attachments_info, status=200)

    video_identifier = video_identifier_class.VideoIdentifier(
        1, 'e58e753c44e548ce9edaec0e0ef9c8c1', 'file1',
    )
    await _notify_support(stq3_context, video_identifier, bytearray())
    video_identifier = video_identifier_class.VideoIdentifier(
        1, 'e58e753c44e548ce9edaec0e0ef9c8c1', 'file2',
    )
    await _notify_support(stq3_context, video_identifier, bytearray())
    assert sorted(attachment_names) == [
        'external_video.mp4',
        'internal_video.mp4',
    ]


@pytest.mark.now('2019-09-16T12:00:00.0+0000')
@pytest.mark.config(
    SIGNAL_DEVICE_API_WORKER_SUPPORT_SETTINGS_V4=SUPPORT_SETTINGS,
)
@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['test_notify_support.sql'],
)
async def test_notify_support(pgsql, stq3_context, mockserver, load_json):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def __fleet_parks_response(request):
        return load_json('fleet_parks_response.json')

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    def __unique_drivers_response(request):
        return {
            'uniques': [
                {
                    'data': {'unique_driver_id': 'unique_driver_id_1'},
                    'park_driver_profile_id': 'p2_driverid2',
                },
            ],
        }

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def __driver_profiles_response(request):
        return {
            'profiles': [
                {
                    'park_driver_profile_id': 'p2_driverid2',
                    'data': {
                        'full_name': {
                            'first_name': 'Serega',
                            'middle_name': 'Seregovich',
                            'last_name': 'Seregin',
                        },
                    },
                },
            ],
        }

    @mockserver.json_handler('/driver-status/v2/statuses')
    def __driver_status_response(request):
        return {
            'statuses': [
                {
                    'park_id': 'p2',
                    'driver_id': 'driverid2',
                    'status': 'online',
                    'orders': [{'id': 'publicorderid1', 'status': 'driving'}],
                },
            ],
        }

    @mockserver.handler(
        '/order-core/internal/processing/v1/order-proc/get-fields',
    )
    def _mock_order_get_fields(request):
        response_fields = {
            'document': {
                '_id': 'internalorderid1',
                'created': '2020-02-25T23:57:00+00',
                'performer': {'candidate_index': None},
                'order': {'nz': 'msk'},
                'candidates': [],
            },
            'revision': {'processing.version': 1, 'order.version': 1},
        }

        return mockserver.make_response(
            status=200,
            content_type='application/bson',
            response=bson.BSON.encode(response_fields),
        )

    tracker_uniques = []
    attachment_names = []

    @mockserver.json_handler('/api-tracker/v2/issues')
    def __api_tracker_response(request):
        unique = request.json['unique']
        if unique in tracker_uniques:
            return mockserver.make_response(
                headers=({'X-Ticket-Key': TRACKER_KEY}),
                json=(
                    {'errorMessages': ['already exists'], 'statusCode': 409}
                ),
                status=409,
            )
        tracker_uniques.append(unique)
        assert request.json == load_json('notify_support_detected_result.json')
        return mockserver.make_response(
            json=({'key': TRACKER_KEY, 'id': '593cd211ef7e8a332414f2a7'}),
            status=201,
        )

    @mockserver.json_handler(
        f'/api-tracker/v2/issues/{TRACKER_KEY}/attachments',
    )
    def __api_tracker_response2(request):
        if request.method == 'POST':
            attachment_names.append(request.query['filename'])
            return mockserver.make_response(
                json=({'id': '593cd211ef7e8a332414f2a2'}), status=201,
            )
        attachments_info = []
        for name in attachment_names:
            attachments_info.append({'name': name})
        return mockserver.make_response(json=attachments_info, status=200)

    video_identifier = video_identifier_class.VideoIdentifier(
        1, 'e58e753c44e548ce9edaec0e0ef9c8c1', 'file1',
    )
    await _notify_support(stq3_context, video_identifier, bytearray())
    video_identifier = video_identifier_class.VideoIdentifier(
        1, 'e58e753c44e548ce9edaec0e0ef9c8c1', 'file2',
    )
    await _notify_support(stq3_context, video_identifier, bytearray())
    assert sorted(attachment_names) == [
        'external_video.mp4',
        'internal_video.mp4',
    ]
