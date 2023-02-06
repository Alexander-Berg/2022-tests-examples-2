# pylint: skip-file
# flake8: noqa
import json

import requests

from helpers.config import read_dynamic_config
from helpers.data_generation import *
from helpers.media import *
from helpers.web import *


def register_device_return_id():
    response = requests.request(
        HTTP_POST,
        REGISTRATION_SERVICE_URL + REGISTRATION_HANDLER,
        headers=registration_headers(),
        json=generate_registration_payload(),
    )
    if response.status_code != HTTP_CODE_SUCCESS:
        raise RuntimeError(
            f'status code {response.status_code} '
            f'for registration: {response.text}',
        )
    device_id = json.loads(response.text)['device_id']
    print(f'created device, device_id={device_id}')
    return device_id


def assign_device_to_partner(device_id, partner_passport_uid):
    response = requests.request(
        HTTP_PUT,
        ADMIN_SERVICE_URL + ADMIN_PARTNER_HANDLER,
        params={'device_id': device_id},
        headers=admin_partner_headers(),
        json=generate_admin_partner_payload(partner_passport_uid),
    )
    if response.status_code != HTTP_CODE_SUCCESS:
        raise RuntimeError(
            f'status code {response.status_code} '
            f'for partner assignment: {response.text}',
        )
    print(f'assigned device to partner {partner_passport_uid}')


def set_driver_name(device_id):
    response = requests.request(
        HTTP_PUT,
        ADMIN_SERVICE_URL + WEB_DRIVER_HANDLER,
        params={'device_id': device_id},
        headers=web_headers(),
        json=generate_web_driver_payload(),
    )
    if response.status_code != HTTP_CODE_SUCCESS:
        raise RuntimeError(
            f'status code {response.status_code} '
            f'for driver assignment: {response.text}',
        )
    print(f'assigned device to driver')


def set_plate_number(device_id):
    response = requests.request(
        HTTP_PUT,
        ADMIN_SERVICE_URL + WEB_PLATE_NUMBER_HANDLER,
        params={'device_id': device_id},
        headers=web_headers(),
        json=generate_web_plate_number_payload(),
    )
    if response.status_code != HTTP_CODE_SUCCESS:
        raise RuntimeError(
            f'status code {response.status_code} '
            f'for plate number assignment: {response.text}',
        )
    print(f'assigned device to plate number')


def set_device_name(device_id):
    response = requests.request(
        HTTP_PUT,
        ADMIN_SERVICE_URL + WEB_DEVICE_NAME_HANDLER,
        params={'device_id': device_id},
        headers=web_headers(),
        json=generate_device_name_payload(),
    )
    if response.status_code != HTTP_CODE_SUCCESS:
        raise RuntimeError(
            f'status code {response.status_code} '
            f'for device name assignment: {response.text}',
        )
    print(f'assigned device_id to device name')


def send_status(device_id):
    body = generate_status_payload(device_id)
    headers = signal_status_headers(body)
    response = requests.request(
        HTTP_POST,
        SIGNAL_SERVICE_URL + SIGNAL_STATUS_HANDLER,
        headers=headers,
        json=body,
    )
    if response.status_code != HTTP_CODE_SUCCESS:
        raise RuntimeError(
            f'status code {response.status_code} for sending status: {response.text}',
        )
    print('sent status')


def send_videos_metadata_return_payload(device_id, video_bin):
    payload = generate_videos_metadata_payload(device_id, video_bin)
    response = requests.request(
        HTTP_POST,
        SIGNAL_SERVICE_URL + SIGNAL_VIDEOS_METADATA_HANDLER,
        headers=signal_videos_metadata_headers(payload),
        json=payload,
    )
    if response.status_code != HTTP_CODE_SUCCESS:
        raise RuntimeError(
            f'status code {response.status_code} for sending video metadata: {response.text}',
        )
    print('sent video metadata')
    return payload


def send_videos_upload(metadata_payload, video_bin):
    query_args = {
        'device_id': metadata_payload['device_id'],
        'timestamp': metadata_payload['timestamp'],
        'size_bytes': metadata_payload['size_bytes'],
        'file_id': metadata_payload['file_id'],
        'offset_bytes': 0,
    }
    url = SIGNAL_SERVICE_URL + SIGNAL_VIDEOS_UPLOAD_HANDLER
    headers = signal_videos_upload_headers(video_bin, query_args)
    response = requests.request(
        HTTP_PUT, url, params=query_args, headers=headers, data=video_bin,
    )
    if response.status_code != HTTP_CODE_SUCCESS:
        raise RuntimeError(
            f'status code {response.status_code} for sending video upload: {response.text}',
        )
    print('sent video')


def send_photos_metadata_return_payload(device_id, photo_bin):
    payload = generate_photos_metadata_payload(device_id, photo_bin)
    response = requests.request(
        HTTP_POST,
        SIGNAL_SERVICE_URL + SIGNAL_PHOTOS_METADATA_HANDLER,
        headers=signal_photos_metadata_headers(payload),
        json=payload,
    )
    if response.status_code != HTTP_CODE_SUCCESS:
        raise RuntimeError(
            f'status code {response.status_code} for sending photo metadata: {response.text}',
        )
    print('sent photo metadata')
    return payload


def send_photos_upload(metadata_payload, photo_bin):
    query_args = {
        'device_id': metadata_payload['device_id'],
        'timestamp': metadata_payload['timestamp'],
        'size_bytes': metadata_payload['size_bytes'],
        'file_id': metadata_payload['file_id'],
    }
    url = SIGNAL_SERVICE_URL + SIGNAL_PHOTOS_UPLOAD_HANDLER
    headers = signal_photos_upload_headers(photo_bin, query_args)
    response = requests.request(
        HTTP_PUT, url, params=query_args, headers=headers, data=photo_bin,
    )
    if response.status_code != HTTP_CODE_SUCCESS:
        raise RuntimeError(
            f'status code {response.status_code} for sending photo upload: {response.text}',
        )
    print('sent photo')


def send_event(device_id, photo_file_id, video_file_id):
    query_args = {
        'device_id': device_id,
        'timestamp': generate_timestamp_now(),
    }
    url = SIGNAL_SERVICE_URL + SIGNAL_EVENT_HANDLER
    payload = generate_event_payload(photo_file_id, video_file_id)
    headers = signal_events_headers(payload, query_args)
    response = requests.request(
        HTTP_POST, url, params=query_args, headers=headers, json=payload,
    )
    if response.status_code != HTTP_CODE_SUCCESS:
        raise RuntimeError(
            f'status code {response.status_code} for sending event: {response.text}',
        )
    print('sent event')


def main():
    config = read_dynamic_config()
    devices_quantity = config['devices_quantity']
    events_per_device = config['events_per_device']
    for i in range(1, devices_quantity + 1):
        try:
            device_id = register_device_return_id()
            send_status(device_id)
            assign_device_to_partner(device_id, config['partner_passport_uid'])
            set_driver_name(device_id)
            set_plate_number(device_id)
            set_device_name(device_id)
            for j in range(events_per_device):
                video_bin = read_random_video()
                videos_metadata_payload = send_videos_metadata_return_payload(
                    device_id, video_bin,
                )
                send_videos_upload(videos_metadata_payload, video_bin)
                photo_bin = read_random_photo()
                photos_metadata_payload = send_photos_metadata_return_payload(
                    device_id, photo_bin,
                )
                send_photos_upload(photos_metadata_payload, photo_bin)
                send_event(
                    device_id,
                    photos_metadata_payload['file_id'],
                    videos_metadata_payload['file_id'],
                )
            print(f'finished device {i} out of {devices_quantity}')
        except Exception as ex:
            print(f'Failed to finish device {i}, skipping: {ex}')


if __name__ == '__main__':
    main()
