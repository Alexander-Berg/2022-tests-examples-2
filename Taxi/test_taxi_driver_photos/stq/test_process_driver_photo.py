import io
import re
from typing import Callable
from typing import Dict
from typing import List
from typing import Tuple

import aiohttp
import aiohttp.web
from PIL import Image
import pytest

from taxi.models.image_typing import ImagePriority
from taxi.models.image_typing import ImageRejectedReason
from taxi.models.image_typing import ImageStatus
from taxi.models.image_typing import ImageType

from taxi_driver_photos.api import exceptions
from taxi_driver_photos.controllers.process_photo import ProcessPhotoController
from taxi_driver_photos.generated.stq3 import stq_context
from taxi_driver_photos.models.dto import ProcessPhotoRequest
from test_taxi_driver_photos import stubs


FaceRectangles = List[Tuple[int, int, int, int]]
FaceRectanglesFunc = Callable[[], FaceRectangles]


@pytest.mark.config(DRIVER_PHOTOS_STQ_MAX_RETRIES_LIMIT=2)
@pytest.mark.parametrize(
    ['photo_size', 'detect_faces_response', 'fails', 'avatars_500'],
    (
        pytest.param(
            (6000, 4000),
            stubs.several_faces,
            False,
            False,
            id='Normal execution',
        ),
        pytest.param(
            (100, 100), stubs.several_faces, True, False, id='Too small pic',
        ),
        pytest.param(
            (6000, 4000), stubs.no_faces, True, False, id='Pic with no face',
        ),
        pytest.param(
            (6000, 4000),
            stubs.face_on_the_edge,
            False,
            False,
            id='Unable to crop portrait correctly-don\'t crop',
        ),
        pytest.param(
            (6000, 4000),
            stubs.face_on_the_edge,
            False,
            True,
            id='Test request timeout',
        ),
    ),
)
async def test_process_driver_photo(
        stq3_context: stq_context.Context,
        mockserver,
        patch,
        pgsql,
        photo_size: Tuple[int, int],
        detect_faces_response: FaceRectanglesFunc,
        fails: bool,
        avatars_500: bool,
):
    unique_driver_id = '54256bf766d93ee2c902dcbd'
    idempotency_key = 'idempotency'
    group_id = 603

    # Mock TVM

    # Mock MDS
    @patch('taxi.clients.mds.MDSClient.download')
    async def _patched_download(path):
        test_image = Image.new('RGB', photo_size)
        fp = io.BytesIO()
        test_image.save(fp, 'JPEG')
        fp.seek(0)
        return fp.read()

    # Mock face detection
    @patch('face_recognition.face_locations')
    def _patched_face_locations(*args) -> FaceRectangles:
        return detect_faces_response()

    # Mock avatars-mds
    uploaded_photos: Dict[str, str] = dict()

    @mockserver.handler('/mds_avatars/put-driver-photos', prefix=True)
    async def _patched_request(request, **kwargs):
        if avatars_500:
            return aiohttp.web.Response(status=500)
        image_id = re.match(r'.*/(.*)$', request.url).group(1)
        uploaded_photos[image_id] = 'image'
        return aiohttp.web.json_response(
            data=stubs.avatars_mds_upload_response(),
        )

    controller = ProcessPhotoController(stq3_context)
    photo_request = ProcessPhotoRequest(
        idempotency_key=idempotency_key,
        unique_driver_id=unique_driver_id,
        source_type='MDS',
        source='some_file_in_mds',
        priority=ImagePriority.TAXIMETER,
        status=ImageStatus.NEED_MODERATION,
        park_id='park_id',
        driver_profile_id='driver_profile_id',
    )

    if avatars_500:
        retry_limit_exceeded = False
        try:
            for _ in range(3):
                try:
                    await controller.process_photo(photo_request)
                except exceptions.SavePhotoError:
                    pass
        except exceptions.RetryLimitExceededError:
            retry_limit_exceeded = True
        assert retry_limit_exceeded
        return

    cursor = pgsql['driver_photos'].cursor()

    if fails:
        # Ensure that failed photos are rejected with correct reason
        if detect_faces_response is stubs.several_faces:
            with pytest.raises(exceptions.ImageTooSmallError):
                await controller.process_photo(photo_request)
            cursor.execute(
                'SELECT * FROM driver_photos WHERE '
                'driver_id =%s '
                'AND photo_status=%s '
                'AND reason=%s',
                (
                    unique_driver_id,
                    ImageStatus.REJECTED.value,
                    ImageRejectedReason.TOO_SMALL.value,
                ),
            )
            photo_errors = list(row for row in cursor)
            assert len(photo_errors) == 1
        elif detect_faces_response is stubs.no_faces:
            with pytest.raises(exceptions.NoFaceFoundError):
                await controller.process_photo(photo_request)
            cursor.execute(
                'SELECT * FROM driver_photos WHERE '
                'driver_id =%s '
                'AND photo_status=%s '
                'AND reason=%s',
                (
                    unique_driver_id,
                    ImageStatus.REJECTED.value,
                    ImageRejectedReason.NO_FACE_FOUND.value,
                ),
            )
            photo_errors = list(row for row in cursor)
            assert len(photo_errors) == 1
    else:
        await controller.process_photo(photo_request)

    # Check that two images are in the driver_photos collection
    cursor.execute(
        'SELECT id, group_id, photo_type, photo_status, reason, park_id, '
        'driver_profile_id, priority FROM driver_photos WHERE driver_id = %s',
        (unique_driver_id,),
    )
    photos_types = set()
    photos = list(row for row in cursor)
    if not photos:
        pytest.fail('No driver photos found at all')
    for photo in photos:
        (
            photo_id,
            photo_group_id,
            photo_type,
            photo_status,
            reason,
            park_id,
            driver_profile_id,
            priority,
        ) = photo

        assert park_id == 'park_id'
        assert driver_profile_id == 'driver_profile_id'

        assert priority == 'taximeter'

        photos_types.add(photo_type)
        if not fails:
            if photo_id not in uploaded_photos:
                pytest.fail('Photo not uploaded to Avatars MDS')
            # Check group id
            assert photo_group_id == group_id

            # Check the size of the resulting photos
            if photo_type in {
                    ImageType.ORIGINAL.value,
                    ImageType.PORTRAIT.value,
                    ImageType.AVA.value,
            }:
                pass
            else:
                pytest.fail('Unknown photo type')
            assert photo_status == ImageStatus.NEED_MODERATION.value
            assert reason is None
        else:
            assert photo_status == ImageStatus.REJECTED.value
            assert reason is not None

    # Check all the image types are present
    if not fails:
        assert ImageType.PORTRAIT.value in photos_types
        assert ImageType.AVA.value in photos_types
    else:
        assert ImageType.ORIGINAL.value in photos_types
        assert ImageType.PORTRAIT.value not in photos_types
        assert ImageType.AVA.value not in photos_types
