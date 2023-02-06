import copy
import dataclasses
import datetime
import re
import typing

import dateutil
import pytest

ENDPOINT = '/drivematics/signalq-drivematics-api/v1/events/media-presigned-urls/generate'  # noqa: E501


EventObjectType = typing.List[
    typing.Dict[typing.Optional[str], typing.Optional[str]]
]

S3_VIDEOS_BUCKET = 'sda-videos'
S3_PHOTOS_BUCKET = 'sda-photos'
S3_SIGNATURE = 'Signature'
S3_AWS_ACCESS_KEY_ID = 'AWSAccessKeyId'
S3_EXPIRES = 'Expires'


@dataclasses.dataclass(frozen=True)
class ResponseFieldInfo:
    field: str
    bucket: str


COMMON_REQUEST_FIELD_TO_RESPONSE_FIELD_INFO = {
    's3_video_path': ResponseFieldInfo(
        field='s3_video_presigned_url', bucket=S3_VIDEOS_BUCKET,
    ),
    's3_external_video_path': ResponseFieldInfo(
        field='s3_external_video_presigned_url', bucket=S3_VIDEOS_BUCKET,
    ),
    's3_photo_path': ResponseFieldInfo(
        field='s3_photo_presigned_url', bucket=S3_PHOTOS_BUCKET,
    ),
    's3_external_photo_path': ResponseFieldInfo(
        field='s3_external_photo_presigned_url', bucket=S3_PHOTOS_BUCKET,
    ),
}


UPLOADED_VIDEO = 'v1/video/v1'
NOT_UPLOADED_VIDEO = 'v1/video/nonexisting_v1'
UPLOADED_EXTERNAL_VIDEO = 'v1/external_video/v1'
NOT_UPLOADED_EXTERNAL_VIDEO = 'v1/external_video/nonexisting_v1'

UPLOADED_PHOTO = 'v1/photo/p1'
NOT_UPLOADED_PHOTO = 'v1/photo/nonexisting_p1'
UPLOADED_EXTERNAL_PHOTO = 'v1/external_photo/p1'
NOT_UPLOADED_EXTERNAL_PHOTO = 'v1/external_photo/nonexisting_p1'

S3_PATH_TO_IS_UPLOADED = {
    UPLOADED_VIDEO: True,
    NOT_UPLOADED_VIDEO: False,
    UPLOADED_EXTERNAL_VIDEO: True,
    NOT_UPLOADED_EXTERNAL_VIDEO: False,
    UPLOADED_PHOTO: True,
    NOT_UPLOADED_PHOTO: False,
    UPLOADED_EXTERNAL_PHOTO: True,
    NOT_UPLOADED_EXTERNAL_PHOTO: False,
}


def _check_presigned_url(bucket, presigned_url, path, expires_at):
    matched = re.match(
        rf'https://{bucket}\.localhost:[0-9]*/private/{path}', presigned_url,
    )
    assert matched is not None
    assert matched.pos == 0

    assert S3_AWS_ACCESS_KEY_ID + '=key' in presigned_url
    assert S3_SIGNATURE in presigned_url
    assert S3_EXPIRES + '=' + str(int(expires_at.timestamp())) in presigned_url


def _check_response(
        request_events: EventObjectType,
        result_events: EventObjectType,
        expires_at: datetime.datetime,
        only_uploaded: bool,
) -> None:
    assert len(request_events) == len(result_events)
    request_events.sort(key=lambda x: x['serial_number_event_id'])
    result_events.sort(key=lambda x: x['serial_number_event_id'])

    for request_event, result_event in zip(request_events, result_events):
        assert request_event.pop('serial_number_event_id') == result_event.pop(
            'serial_number_event_id',
        )
        for (
                request_field,
                response_field_info,
        ) in COMMON_REQUEST_FIELD_TO_RESPONSE_FIELD_INFO.items():
            request_s3_path = request_event.get(request_field)
            presigned_url = result_event.get(response_field_info.field)

            if request_s3_path is None:
                assert presigned_url is None
                continue

            if only_uploaded and not S3_PATH_TO_IS_UPLOADED[request_s3_path]:
                assert presigned_url is None
                continue

            _check_presigned_url(
                bucket=response_field_info.bucket,
                presigned_url=presigned_url,
                path=request_s3_path,
                expires_at=expires_at,
            )


REQUEST_EVENTS1 = [
    {
        'serial_number_event_id': 'some_id',
        's3_video_path': UPLOADED_VIDEO,
        's3_external_video_path': UPLOADED_EXTERNAL_VIDEO,
        's3_photo_path': UPLOADED_PHOTO,
        's3_external_photo_path': UPLOADED_EXTERNAL_PHOTO,
    },
    {
        'serial_number_event_id': 'some_id2',
        's3_external_video_path': UPLOADED_EXTERNAL_VIDEO,
        's3_photo_path': UPLOADED_PHOTO,
        's3_external_photo_path': UPLOADED_EXTERNAL_PHOTO,
    },
    {
        'serial_number_event_id': 'some_id3',
        's3_video_path': NOT_UPLOADED_VIDEO,
        's3_external_video_path': NOT_UPLOADED_EXTERNAL_VIDEO,
        's3_photo_path': NOT_UPLOADED_PHOTO,
        's3_external_photo_path': NOT_UPLOADED_EXTERNAL_PHOTO,
    },
    {'serial_number_event_id': 'some_id4'},
    {
        'serial_number_event_id': 'some_id5',
        's3_video_path': UPLOADED_VIDEO,
        's3_external_video_path': UPLOADED_EXTERNAL_VIDEO,
    },
    {
        'serial_number_event_id': 'some_id6',
        's3_video_path': NOT_UPLOADED_VIDEO,
        's3_external_video_path': NOT_UPLOADED_EXTERNAL_VIDEO,
        's3_external_photo_path': UPLOADED_EXTERNAL_PHOTO,
    },
]

REQUEST_EVENTS2 = [
    {'serial_number_event_id': 'some_id2122', 's3_video_path': UPLOADED_VIDEO},
]


@pytest.mark.parametrize(
    'events, links_expires_at, only_uploaded',
    [
        (REQUEST_EVENTS1, '2022-03-12T00:00:00+03:00', None),
        (REQUEST_EVENTS1, '2022-03-12T00:00:00+03:00', True),
        (REQUEST_EVENTS1, '2022-03-12T00:00:00+03:00', False),
        (REQUEST_EVENTS2, '2022-04-14T00:00:00+03:00', None),
        (REQUEST_EVENTS2, '2022-04-14T00:00:00+03:00', False),
        (REQUEST_EVENTS2, '2022-04-14T00:00:00+03:00', True),
    ],
)
async def test_drivematics_v1_presigned_urls_generate(
        taxi_signalq_drivematics_api, events, links_expires_at, only_uploaded,
):
    body = {'events': events, 'links_expires_at': links_expires_at}
    if only_uploaded is not None:
        body['only_uploaded'] = only_uploaded

    response = await taxi_signalq_drivematics_api.post(ENDPOINT, json=body)
    assert response.status_code == 200, response.text
    _check_response(
        request_events=copy.deepcopy(events),
        result_events=response.json()['events'],
        expires_at=dateutil.parser.parse(links_expires_at),
        only_uploaded=False if only_uploaded is None else only_uploaded,
    )
