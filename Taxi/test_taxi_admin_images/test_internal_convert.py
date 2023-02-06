import dataclasses
import uuid

import pytest

import taxi_admin_images.repositories.images as img_repos


ADMIN_IMAGES_CONVERSION_OPTIONS_ENABLED = {
    'avif': {'enabled': True, 'quality': 60, 'minimum_savings': 0.1},
    'heif': {'enabled': True, 'quality': 60, 'minimum_savings': 0.1},
}


def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False


@pytest.mark.parametrize(
    [
        'tag',
        'file_format',
        'expected_status',
        'expected_result',
        'unchanged_images_count',
    ],
    [
        ('tag_unknown', 'avif', 400, 'result_empty.json', 0),
        ('tag1', 'avif', 200, 'result1.json', 2),
        ('tag1', 'heif', 200, 'result2.json', 2),
        ('tag2', 'avif', 200, 'result3.json', 4),
        ('tag3', 'avif', 200, 'result4.json', 1),
        ('tag4', 'avif', 200, 'result5.json', 2),
        ('tag4', 'heif', 200, 'result6.json', 2),
        ('tag5', 'heif', 200, 'result7.json', 1),
    ],
)
@pytest.mark.config(
    ADMIN_IMAGES_CONVERSION_OPTIONS=ADMIN_IMAGES_CONVERSION_OPTIONS_ENABLED,
)
@pytest.mark.filldb(images='convert')
async def test_internal_convert(
        web_app_client,
        web_app,
        tag,
        file_format,
        expected_status,
        mock_mds,
        load_json,
        expected_result,
        unchanged_images_count,
):
    img_repo = img_repos.ImagesRepository(web_app['context'].mongo)

    url = '/internal/convert-images'
    params = {}
    params['tag'] = tag
    params['file_format'] = file_format
    response = await web_app_client.post(url, params=params)
    assert response.status == expected_status

    images = await img_repo.get_images(tag)
    expected = load_json(expected_result)
    assert len(images) == len(expected)
    for i, img in enumerate(images):
        expected_img = expected[i]
        if i < unchanged_images_count:
            # verify that image_id is unchanged for existing images
            assert img.image_id == expected_img['image_id']
        else:
            assert is_valid_uuid(img.image_id)

        assert img.file_format == expected_img['file_format']
        assert img.theme == expected_img['theme']
        assert img.is_tintable == expected_img['is_tintable']
        assert img.tag == expected_img['tags'][0]
        assert [
            {hint.platform: hint.size_hint for hint in img.size_hints},
        ] == [expected_img['size_hint']]
        if expected_img.get('revision_history'):
            assert (
                img.revision_history[-1].revision
                == expected_img['revision_history'][-1]['revision']
            )


@pytest.mark.config(
    ADMIN_IMAGES_CONVERSION_OPTIONS=ADMIN_IMAGES_CONVERSION_OPTIONS_ENABLED,
)
@pytest.mark.filldb(images='convert')
async def test_internal_convert_with_conversion_error(
        web_app_client, web_app, mock_mds, patch,
):
    @patch('taxi_admin_images.logic.convert.pillow_heif.from_pillow')
    def _patch_heif_conversion():
        raise Exception

    tag = 'tag1'
    img_repo = img_repos.ImagesRepository(web_app['context'].mongo)
    images = await img_repo.get_images(tag)

    url = '/internal/convert-images'
    params = {'tag': tag, 'file_format': 'heif'}
    response = await web_app_client.post(url, params=params)
    assert response.status == 200

    images_after = await img_repo.get_images(tag)
    assert len(images) == len(images_after)

    for i, img in enumerate(images):
        img_after = images_after[i]
        assert img.image_id == img_after.image_id
        assert img.file_format == img_after.file_format
        assert img.theme == img_after.theme
        assert img.is_tintable == img_after.is_tintable
        assert img.tag == img_after.tag
        assert [dataclasses.asdict(hint) for hint in img.size_hints] == [
            dataclasses.asdict(hint) for hint in img_after.size_hints
        ]
        assert [dataclasses.asdict(rev) for rev in img.revision_history] == [
            dataclasses.asdict(rev) for rev in img_after.revision_history
        ]
