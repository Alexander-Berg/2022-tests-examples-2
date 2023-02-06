# pylint: skip-file
# flake8: noqa
from helpers.jwt_generation import generate_jwt
from helpers.tvm import generate_service_ticket
from helpers.tvm import generate_user_ticket_return_ticket_yandex_uid

HTTP_POST = 'POST'
HTTP_PUT = 'PUT'
HTTP_CODE_SUCCESS = 200

REGISTRATION_SERVICE_URL = (
    'http://signal-device-registration-api.taxi.tst.yandex.net'
)
ADMIN_SERVICE_URL = 'http://signal-device-api-admin.taxi.tst.yandex.net'
SIGNAL_SERVICE_URL = 'http://signal-device-api.taxi.tst.yandex.net'

REGISTRATION_HANDLER = '/v1/devices/registration'
ADMIN_PARTNER_HANDLER = '/v1/devices/partner'
SIGNAL_STATUS_HANDLER = '/v1/status'
SIGNAL_VIDEOS_METADATA_HANDLER = '/v1/videos/metadata'
SIGNAL_VIDEOS_UPLOAD_HANDLER = '/v1/videos/upload'
SIGNAL_PHOTOS_METADATA_HANDLER = '/v1/photos/metadata'
SIGNAL_PHOTOS_UPLOAD_HANDLER = '/v1/photos/upload'
SIGNAL_EVENT_HANDLER = '/v1/events'
WEB_DRIVER_HANDLER = '/web/v1/devices/driver'
WEB_PLATE_NUMBER_HANDLER = '/web/v1/devices/vehicle'
WEB_DEVICE_NAME_HANDLER = '/web/v1/devices'


def registration_headers():
    return {'Content-Type': 'application/json'}


def admin_partner_headers():
    return {
        'Content-Type': 'application/json',
        'X-Ya-Service-Ticket': generate_service_ticket(),
    }


def signal_status_headers(body):
    return {
        'Content-Type': 'application/json',
        'X-JWT-Signature': generate_jwt(SIGNAL_STATUS_HANDLER, {}, body),
    }


def signal_videos_metadata_headers(body):
    return {
        'Content-Type': 'application/json',
        'X-JWT-Signature': generate_jwt(
            SIGNAL_VIDEOS_METADATA_HANDLER, {}, body,
        ),
    }


def signal_videos_upload_headers(body, query_args):
    return {
        'Content-Type': 'application/octet-stream',
        'X-JWT-Signature': generate_jwt(
            SIGNAL_VIDEOS_UPLOAD_HANDLER, query_args, body, is_body_json=False,
        ),
    }


def signal_photos_metadata_headers(body):
    return {
        'Content-Type': 'application/json',
        'X-JWT-Signature': generate_jwt(
            SIGNAL_PHOTOS_METADATA_HANDLER, {}, body,
        ),
    }


def signal_photos_upload_headers(body, query_args):
    return {
        'Content-Type': 'application/octet-stream',
        'X-JWT-Signature': generate_jwt(
            SIGNAL_PHOTOS_UPLOAD_HANDLER, query_args, body, is_body_json=False,
        ),
    }


def signal_events_headers(body, query_args):
    return {
        'Content-Type': 'application/json',
        'X-JWT-Signature': generate_jwt(
            SIGNAL_EVENT_HANDLER, query_args, body,
        ),
    }


def web_headers():
    user_ticket, yandex_uid = generate_user_ticket_return_ticket_yandex_uid()
    return {
        'Content-Type': 'application/json',
        'X-Ya-Service-Ticket': generate_service_ticket(),
        'X-Ya-User-Ticket-Provider': 'yandex_team',
        'X-Yandex-UID': yandex_uid,
        'X-Ya-User-Ticket': user_ticket,
    }
