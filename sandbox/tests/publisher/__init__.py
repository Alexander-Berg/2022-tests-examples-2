import uuid
from datetime import datetime
from typing import List
from unittest.mock import MagicMock

from google.protobuf.json_format import ParseDict
from ott.drm.library.python.cms.clients import VhAdminClient, OttContentApiClient
from ott.drm.library.python.cms.models import (
    InputStream,
    InputStreamStatus,
    OutputStream,
    ContentVersionUpdateParams,
    ContentGroup,
    ContentVersion,
    FaasAnswer,
    FaasAnswerFormat
)
from yweb.video.faas.proto.common.outputs_pb2 import TOutput

from sandbox.projects.ott.packager_management_system.lib.publisher import Publisher

TASK_ID = uuid.uuid4()
CONTENT_GROUP_UUID = 'uuid'
INPUT_STREAM_ID = '11'
CONTENT_VERSION_ID = 1

T_STREAM = {
    'Url': 'https://strm.yandex.ru/vh-ottenc-converted/dash-cenc/sdr_hd_avc_aac.mpd',
    'Type': 'EST_DASH',
    'DrmType': 'EDT_PLAYREADY',
    'Meta': '{"prop": "value"}',
    'DynamicRange': 'EDR_SDR',
    'VideoCodec': 'EVC_AVC',
    'AudioCodec': 'EAC_AAC',
    'VideoQuality': 'EVQ_HD'
}

T_INPUT_VIDEO = {
    'Url': 'https://s3.mds.yandex.net/elty/elysium_trailer_4k_30sec.mp4',
    'Size': 74961128,
    'Width': 4096,
    'Height': 1716
}

INPUT_STREAM = InputStream(
    input_stream_id=INPUT_STREAM_ID,
    content_version_id=CONTENT_VERSION_ID,
    status=InputStreamStatus.FAAS_SENT,
    faas_custom_parameters={'key': 'value'},
    faas_answer=FaasAnswer(ott_packager_task_id=TASK_ID)
)

OUTPUT_STREAM = OutputStream(
    data='https://strm.yandex.ru/vh-ottenc-converted/dash-cenc/sdr_hd_avc_aac.mpd',
    drm_type='playready',
    meta={'prop': 'value'},
    stream_type='DASH',
    video_descriptor_id=2,
    playlist_generation='from-data'
)

FAAS_ANSWER = FaasAnswer(
    ott_packager_task_id=TASK_ID,
    width=4096,
    height=1716,
    format=FaasAnswerFormat(filename='https://s3.mds.yandex.net/elty/elysium_trailer_4k_30sec.mp4', size=74961128)
)


def test_publish_new_output_stream():
    mocked_vh_admin_client, publisher = _init()

    publisher.publish_packager_output(TASK_ID, CONTENT_GROUP_UUID, CONTENT_VERSION_ID, _build_t_output())

    mocked_vh_admin_client.update_content_version.assert_called_once_with(
        CONTENT_VERSION_ID,
        ContentVersionUpdateParams([OUTPUT_STREAM])
    )


def test_publish_rounded_duration():
    mocked_vh_admin_client, publisher = _init()

    publisher.publish_packager_output(TASK_ID, CONTENT_GROUP_UUID, CONTENT_VERSION_ID, _build_t_output(duration=4.99))

    mocked_vh_admin_client.update_content_group.assert_called_once_with(
        CONTENT_GROUP_UUID,
        ContentGroup(duration=5, video_screenshots=[])
    )


def test_publish_thumbnails():
    mocked_vh_admin_client, publisher = _init()

    output = _build_t_output([], ['thumb1', 'thumb2'], 5.0)
    publisher.publish_packager_output(TASK_ID, CONTENT_GROUP_UUID, CONTENT_VERSION_ID, output)

    mocked_vh_admin_client.update_content_group.assert_called_once_with(
        CONTENT_GROUP_UUID,
        ContentGroup(duration=5, video_screenshots=['thumb1', 'thumb2'])
    )


def test_not_duplicate_stream():
    mocked_vh_admin_client, publisher = _init(init_output_streams=[OUTPUT_STREAM])

    publisher.publish_packager_output(TASK_ID, CONTENT_GROUP_UUID, CONTENT_VERSION_ID, _build_t_output())

    mocked_vh_admin_client.update_content_version.assert_called_once_with(
        CONTENT_VERSION_ID,
        ContentVersionUpdateParams([OUTPUT_STREAM])
    )


def test_publish_faas_answer():
    mocked_vh_admin_client, publisher = _init(init_input_streams=[INPUT_STREAM])

    publisher.publish_packager_output(TASK_ID, CONTENT_GROUP_UUID, CONTENT_VERSION_ID,
                                      _build_t_output(input_video=T_INPUT_VIDEO))

    mocked_vh_admin_client.update_input_stream.assert_called_once_with(
        INPUT_STREAM_ID,
        InputStream(input_stream_id=INPUT_STREAM_ID, faas_answer=FAAS_ANSWER)
    )


def test_not_publish_faas_answer_wihout_input_stream():
    mocked_vh_admin_client, publisher = _init(init_input_streams=[InputStream(input_stream_id='555')])

    publisher.publish_packager_output(TASK_ID, CONTENT_GROUP_UUID, CONTENT_VERSION_ID,
                                      _build_t_output(input_video=T_INPUT_VIDEO))

    mocked_vh_admin_client.update_input_stream.assert_not_called()


def _init(init_input_streams: List[InputStream] = None, init_output_streams: List[OutputStream] = None):
    mocked_vh_admin_client = VhAdminClient('vh_admin_url', 10)
    mocked_ott_content_api_client = OttContentApiClient('ott_content_api_url', 10)
    publisher = Publisher('tasks_api_url', mocked_vh_admin_client, mocked_ott_content_api_client, max_workers=1)

    content_version = ContentVersion(1, False, 'ORIGINAL_SDR', init_input_streams or [], init_output_streams or [],
                                     datetime.now())
    mocked_vh_admin_client.get_content_version= MagicMock(return_value=content_version)

    mocked_vh_admin_client.update_content_version = MagicMock()
    mocked_vh_admin_client.update_content_group = MagicMock()
    mocked_vh_admin_client.update_input_stream = MagicMock()

    return mocked_vh_admin_client, publisher


def _build_t_output(streams: list = None, thumbnails: list = None, duration: float = 5.0,
                    input_video: dict = None) -> TOutput():
    output_dict = {
        'Streams': streams or [T_STREAM],
        'Thumbnails': thumbnails or [],
        'Duration': duration,
        'InputVideo': input_video or {}
    }

    return ParseDict(output_dict, TOutput())
