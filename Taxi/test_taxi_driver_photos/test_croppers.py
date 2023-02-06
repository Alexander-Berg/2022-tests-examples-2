import pytest

from taxi.models.image_typing import ImageFragment
from taxi.models.image_typing import ImageSize

from taxi_driver_photos.models.croppers import AvatarCropper
from taxi_driver_photos.models.croppers import PortraitCropper


@pytest.mark.parametrize(
    ['cropper', 'image_size', 'face_rect', 'expected_crop'],
    [
        # Ava normal
        (
            AvatarCropper,
            ImageSize(2000, 2000),
            ImageFragment(500, 500, 200, 150, 0),
            ImageFragment(380, 368, 200 + 240, 150 + 240, 0),
        ),
        # Ava too small
        (
            AvatarCropper,
            ImageSize(600, 600),
            ImageFragment(50, 50, 200, 150, 0),
            ImageFragment(25, 0, 250, 250, 0),
        ),
        # Portrait normal
        (
            PortraitCropper,
            ImageSize(2000, 2000),
            ImageFragment(500, 500, 200, 150, 0),
            ImageFragment(260, 395, 720, 360, 0),
        ),
        # Portrait too small
        (
            PortraitCropper,
            ImageSize(600, 600),
            ImageFragment(50, 50, 200, 150, 0),
            ImageFragment(0, 0, 600, 600, 0),
        ),
    ],
)
def test_calculate_crop(cropper, image_size, face_rect, expected_crop, stub):
    photo = stub(size=image_size)
    # pylint: disable=protected-access
    crop = cropper._get_crop_fragment(photo, face_rect)
    assert crop == expected_crop
