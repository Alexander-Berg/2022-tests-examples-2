import base64
from unittest import mock

import pytest

from taxi_antifraud.qc import protector


@pytest.mark.parametrize(
    'photo_filename,driver_id,expected_signature',
    [
        (
            'normal_photo.txt',
            '7c173b491074630fa936bb0073561ff0',
            {
                'lady_signature': '7a92a66ec918620bc53697edfd3dcfa3',
                'protector_signature': '7a92a66ec918620bc53697edfd3dcfa3',
                'protector_timestamp': 1622823234565,
            },
        ),
        ('not_jpeg.txt', '', None),
        ('without_exif.txt', '', None),
        ('without_makernotes.txt', '', None),
        ('wrong_proto.txt', '', None),
        ('bad_makernotes_type.txt', '', None),
    ],
)
async def test_photo_signature(
        load, photo_filename, driver_id, expected_signature,
):
    config = mock.Mock(
        AFS_CRON_RESOLVE_QC_PASSES_PROTECTOR_SIGNATURE_ENABLED=True,
    )
    picture_bytes = base64.b64decode(load(photo_filename))

    signature = protector.get_photo_signature(picture_bytes, driver_id, config)

    assert signature == expected_signature
