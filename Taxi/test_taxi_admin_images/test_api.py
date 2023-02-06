# pylint: disable=too-many-lines
import io
import typing

import aiohttp
import deepdiff
import PIL.Image as PilImage
import pytest

import taxi_admin_images.const as const
import taxi_admin_images.logic.upload as upload_logic
import taxi_admin_images.models.image_size_hint as size_hint_module
import taxi_admin_images.repositories.images as img_repos
import test_taxi_admin_images.helpers as helpers

RealImage = helpers.RealImage
JPEG_FORMAT = const.JPEG_FORMAT
PNG_FORMAT = const.PNG_FORMAT
AVIF, HEIF = 'avif', 'heif'

ADMIN_IMAGES_GROUP_SUBGROUP = [
    {
        'key': 'test1',
        'name': 'Тест 1',
        'subgroups': [{'key': 'sub_test', 'name': 'Подгруппа'}],
    },
    {'key': 'test2', 'name': 'Тест 2', 'subgroups': []},
]

ADMIN_IMAGES_SIZE_HINTS = [
    {'key': 'iphone_206', 'name': 'iPhone @2x'},
    {'key': 'android_320', 'name': 'Android - XHDPI'},
    {'key': 'web_9999', 'name': 'Web'},
]

ADMIN_IMAGES_THEMES = ['light', 'dark']

ADMIN_IMAGES_SIZE_POSTFIX = [
    {
        'postfix': '@2x',
        'size_hints': ['iphone_128', 'iphone_206', 'iphone_240'],
    },
    {'postfix': '_ldpi', 'size_hints': ['android_120']},
    {
        'postfix': '_xxxhdpi',
        'size_hints': ['android_640', 'android_720', 'web_9999'],
    },
]
ADMIN_IMAGE_HACK_IPHONE_POI = ['iphone_128', 'iphone_192']
ADMIN_IMAGES_UPLOAD_SIZE_HINTS = {
    'android_480': ['android_480', 'iphone_206', 'iphone_240'],
    'iphone_300': ['iphone_192', 'iphone_300', 'iphone_390', 'iphone_9999'],
}

ADMIN_IMAGES_GROUPS_PROPERTIES = {
    'class': {'max_image_size_kb': 10},
    'childchair': {'max_image_size_kb': 10},
    '__default__': {
        'max_image_size_kb': 300,
        'max_resolution': {'width': 2000, 'height': 3000},
    },
}
ADMIN_IMAGES_CONVERSION_OPTIONS_ENABLED = {
    'avif': {'enabled': True, 'quality': 60, 'minimum_savings': 0.1},
    'heif': {'enabled': True, 'quality': 60, 'minimum_savings': 0.1},
}


@pytest.mark.config(ADMIN_IMAGES_GROUP_SUBGROUP=ADMIN_IMAGES_GROUP_SUBGROUP)
async def test_groups(web_app_client, web_app):
    response = await web_app_client.get('/groups')
    assert response.status == 200

    groups = (await response.json())['groups']
    assert groups == ADMIN_IMAGES_GROUP_SUBGROUP


@pytest.mark.config(ADMIN_IMAGES_SIZE_HINTS=ADMIN_IMAGES_SIZE_HINTS)
async def test_size_hint(web_app_client, web_app):
    response = await web_app_client.get('/size_hints')
    assert response.status == 200

    size_hints = (await response.json())['size_hints']
    assert size_hints == ADMIN_IMAGES_SIZE_HINTS


@pytest.mark.config(ADMIN_IMAGES_THEMES=ADMIN_IMAGES_THEMES)
async def test_themes(web_app_client, web_app):
    response = await web_app_client.get('/themes')
    assert response.status == 200

    themes = (await response.json())['themes']
    assert themes == ADMIN_IMAGES_THEMES


@pytest.mark.config(ADMIN_IMAGES_SIZE_POSTFIX=ADMIN_IMAGES_SIZE_POSTFIX)
async def test_size_matching(web_app_client, web_app):
    response = await web_app_client.get('/size_matching')
    assert response.status == 200

    size_matching = (await response.json())['size_matching']
    assert size_matching == ADMIN_IMAGES_SIZE_POSTFIX


@pytest.mark.config(
    ADMIN_IMAGES_PREFIX_TO_GROUP_MAP={'tag1': 'test1', 'tag2': 'test2'},
)
async def test_groups_and_prefixes(web_app_client, web_app):
    response = await web_app_client.get('/groups_and_prefixes')
    assert response.status == 200

    groups_and_prefixes = (await response.json())['groups_and_prefixes']
    assert groups_and_prefixes == [
        {'group': 'test1', 'prefixes': ['tag1']},
        {'group': 'test2', 'prefixes': ['tag2']},
    ]


@pytest.mark.config(ADMIN_IMAGES_SIZE_HINT_PREVIEW='android_480')
async def test_list(web_app_client):
    response = await web_app_client.get('/list')
    assert response.status == 200

    expected_tags = [
        'class_business_icon_2',
        'class_minivan_car',
        'class_minivan_icon_2',
        'class_minivan_icon_3',
        'class_minivan_icon',
        'class_econom_car',
        'class_econom_icon',
        'class_vip_icon',
        'class_vip_icon_2',
        'class_business_car',
        'class_econom_car_2',
        'class_business_icon',
        'class_vip_car',
        'class_econom_icon_2',
        'class_business_car_7',
        'class_business_car_7_vip_moscow',
        'class_business_car_7_some_branding',
        'class_comfort_car_7',
        'class_comfort_car_7_spb',
        'class_business_car_7_moscow',
        'childchair_for_child_tariff.infant.image',
        'banner_5627df642ce99940c3a2dfbb_ru_image',
        'branding_image_default',
        'branding_some_branding_image_1',
    ]

    result = await response.json()
    for img in result['images']:
        assert sorted(img.keys()) == sorted(
            ['tag', 'url', 'group', 'subgroup', 'tariff'],
        )
        assert img['tag'] in expected_tags

    # For a tag with multiple file formats preview is built from
    # file_format = None record.
    images = [
        img for img in result['images'] if img['tag'] == 'class_minivan_icon_3'
    ]
    assert len(images) == 1
    assert images[0]['url'].endswith(
        '10005/4e5086d0-d3e1-40d4-a5e0-372aab886e81',
    )


@pytest.mark.config(ADMIN_IMAGES_SIZE_HINT_PREVIEW='android_480')
@pytest.mark.parametrize(
    'group, subgroup, tariff',
    [
        ('class', '', ''),
        ('class', 'car', ''),
        ('class', '', 'minivan'),
        ('class', 'car', 'minivan'),
        ('banner', '', ''),
    ],
)
async def test_list_filtered(web_app_client, group, subgroup, tariff):
    response = await web_app_client.get(
        '/list',
        params={'group': group, 'subgroup': subgroup, 'tariff': tariff},
    )
    assert response.status == 200

    for img in (await response.json())['images']:
        assert sorted(img.keys()) == sorted(
            ['tag', 'url', 'group', 'subgroup', 'tariff'],
        )
        assert img['group'] == group
        assert not subgroup or img['subgroup'] == subgroup
        assert not tariff or img['tariff'] == tariff


@pytest.mark.config(
    ADMIN_IMAGES_UPLOAD_SIZE_HINTS={'iphone_300': ['iphone_300']},
)
@pytest.mark.parametrize('tag', ['class_econom_icon_2', 'class_business_car'])
async def test_detail_no_file_format(web_app_client, tag):
    response = await web_app_client.get(f'/detail/{tag}')
    assert response.status == 200

    images = (await response.json())['images']
    assert images

    for img in images:
        assert sorted(img.keys()) == sorted(['url', 'size_hint'])
        assert img['url']
        assert img['size_hint']


@pytest.mark.config(
    ADMIN_IMAGES_UPLOAD_SIZE_HINTS={'android_480': ['android_480']},
)
@pytest.mark.parametrize('tag', ['class_minivan_icon_3'])
async def test_detail_with_file_format(web_app_client, tag):
    response = await web_app_client.get(f'/detail/{tag}')
    assert response.status == 200

    images = (await response.json())['images']
    assert len(images) == 3
    images_by_url = {img['url']: img for img in images}
    for url, img in images_by_url.items():
        assert img['size_hint']
        if url.endswith('10005/4e5086d0-d3e1-40d4-a5e0-372aab886e81'):
            assert set(img.keys()) == {'url', 'size_hint'}
        elif url.endswith('10005/4e5086d0-d3e1-40d4-a5e0-372aab886e82'):
            assert set(img.keys()) == {'file_format', 'url', 'size_hint'}
            assert img['file_format'] == 'avif'
        elif url.endswith('10005/4e5086d0-d3e1-40d4-a5e0-372aab886e83'):
            assert set(img.keys()) == {'file_format', 'url', 'size_hint'}
            assert img['file_format'] == 'heif'
        else:
            raise ValueError


@pytest.mark.parametrize('tag', ['tag_not_found'])
async def test_detail_tag_not_exist(web_app_client, tag):
    response = await web_app_client.get(f'/detail/{tag}')
    assert response.status == 404

    res = await response.json()
    assert res['code'] == 'TAG_NOT_FOUND'


@pytest.mark.parametrize(
    'tag',
    ['class_minivan_icon_2', 'class_minivan_icon_3', 'class_business_car'],
)
async def test_remove(web_app_client, mock_mds, tag):
    response = await web_app_client.post(f'/delete/{tag}')
    assert response.status == 200

    response = await web_app_client.get(f'/detail/{tag}')
    assert response.status == 404


@pytest.mark.parametrize(
    'tag, file_format, expected_delete_status, images_count, expected_result',
    [
        (
            'class_minivan_icon_2',
            'avif',
            200,
            2,
            'expected_remove_file_format_response1.json',
        ),
        (
            'class_minivan_icon_3',
            'heif',
            200,
            2,
            'expected_remove_file_format_response2.json',
        ),
        (
            'class_minivan_icon_3',
            'default',
            404,
            3,
            'expected_remove_file_format_response3.json',
        ),
    ],
)
@pytest.mark.config(
    ADMIN_IMAGES_UPLOAD_SIZE_HINTS={'iphone_300': ['iphone_300']},
)
async def test_remove_with_file_format(
        web_app_client,
        web_app,
        mock_mds,
        tag,
        file_format,
        expected_delete_status,
        expected_result,
        images_count,
        load_json,
):
    response = await web_app_client.post(
        f'/delete/{tag}?file_format={file_format}',
    )
    assert response.status == expected_delete_status

    img_repo = img_repos.ImagesRepository(web_app['context'].mongo)
    images = await img_repo.get_images(tag)
    assert len(images) == images_count

    response = await web_app_client.get(f'/detail/{tag}')
    assert response.status == 200
    assert load_json(expected_result) == await response.json()


@pytest.mark.parametrize('tag', ['tag_not_found'])
async def test_remove_tag_not_found(web_app_client, tag):
    response = await web_app_client.post(f'/delete/{tag}')
    assert response.status == 404

    res = await response.json()
    assert res['code'] == 'TAG_NOT_FOUND'


@pytest.mark.parametrize(
    'tag, size_hint',
    [
        ('class_minivan_icon_2_new', 'android_666'),
        ('class_business_car', 'incorrect_100'),
    ],
)
async def test_upload_incorrect_size(
        get_image, web_app_client, tag, size_hint, mock_mds,
):
    filename = 'app.png'
    form_data = aiohttp.FormData()
    form_data.add_field(
        'file',
        get_image(RealImage(PNG_FORMAT)).getbuffer(),
        filename=filename,
        content_type='image/png',
    )
    response = await web_app_client.post(
        f'/upload/{tag}/{size_hint}', data=form_data,
    )

    assert response.status == 404

    res = await response.json()
    assert res['code'] == 'SIZE_NOT_FOUND'


@pytest.mark.config(ADMIN_IMAGES_PREFIX_TO_GROUP_MAP={'class': 'class'})
@pytest.mark.parametrize(
    'tag, expected_status, expected_code',
    [
        ('class', 400, 'INCORRECT_TAG'),
        ('class_', 400, 'INCORRECT_TAG'),
        ('_class_vip_car', 400, 'INCORRECT_TAG'),
        ('business_car', 404, 'GROUP_NOT_FOUND'),
        ('error_group_vip', 404, 'GROUP_NOT_FOUND'),
        ('class_vip_car_5', 400, 'REQUEST_VALIDATION_ERROR'),
    ],
)
async def test_upload_error(
        get_image,
        web_app_client,
        tag,
        expected_status,
        expected_code,
        mock_mds,
):
    form_data = None
    if expected_code != 'REQUEST_VALIDATION_ERROR':
        filename = 'app.png'
        form_data = aiohttp.FormData()
        form_data.add_field(
            'file',
            get_image(RealImage(PNG_FORMAT)).getbuffer(),
            filename=filename,
            content_type='image/png',
        )
    response = await web_app_client.post(
        f'/upload/{tag}/web_9999', data=form_data,
    )

    assert response.status == expected_status

    res = await response.json()
    assert res['code'] == expected_code


@pytest.mark.config(
    ADMIN_IMAGE_HACK_IPHONE_POI=ADMIN_IMAGE_HACK_IPHONE_POI,
    ADMIN_IMAGES_UPLOAD_SIZE_HINTS=ADMIN_IMAGES_UPLOAD_SIZE_HINTS,
)
async def test_cannot_upload_not_an_image(
        get_image, web_app_client, web_app, mock_mds, load_binary,
):
    tag = 'class_minivan_icon_2_new'
    size_hint = 'android_480'
    filename = 'app.png'
    form_data = aiohttp.FormData()
    form_data.add_field(
        'file',
        io.BytesIO(load_binary('db_images_theme_duples.json')).getbuffer(),
        filename=filename,
        content_type='image/png',
    )

    response = await web_app_client.post(
        f'/upload/{tag}/{size_hint}', data=form_data,
    )
    assert response.status == 400

    response = await web_app_client.get(f'/detail/{tag}')
    assert response.status == 404

    img_repo = img_repos.ImagesRepository(web_app['context'].mongo)
    images = await img_repo.get_images(tag)
    assert not images


@pytest.mark.config(
    ADMIN_IMAGES_UPLOAD_SIZE_HINTS=ADMIN_IMAGES_UPLOAD_SIZE_HINTS,
    ADMIN_IMAGES_THEMES=['light'],
)
@pytest.mark.parametrize('theme, status', [('light', 200), ('dark', 404)])
async def test_create_theme(
        get_image, web_app_client, web_app, mock_mds, theme, status,
):
    filename = 'app.png'
    form_data = aiohttp.FormData()
    form_data.add_field(
        'file',
        get_image(RealImage(PNG_FORMAT)).getbuffer(),
        filename=filename,
        content_type='image/png',
    )

    response = await web_app_client.post(
        f'/upload/class_business_poi_new/iphone_192?theme={theme}',
        data=form_data,
    )
    assert response.status == status

    if status == 200:
        response = await web_app_client.get(f'/detail/class_business_poi_new')
        assert response.status == 200
        response_json = await response.json()
        assert response_json['images'][0]['theme'] == theme

        img_repo = img_repos.ImagesRepository(web_app['context'].mongo)
        images = await img_repo.get_images('class_business_poi_new')
        assert images[0].theme == theme


@pytest.mark.config(
    ADMIN_IMAGE_HACK_IPHONE_POI=ADMIN_IMAGE_HACK_IPHONE_POI,
    ADMIN_IMAGES_UPLOAD_SIZE_HINTS=ADMIN_IMAGES_UPLOAD_SIZE_HINTS,
)
@pytest.mark.parametrize(
    'tag, size_hint, is_poi',
    [
        ('class_minivan_icon_2_new', 'android_480', False),
        ('class_business_car_new', 'web_9999', False),
        ('class_business_poi_new', 'iphone_192', True),
    ],
)
async def test_create_new(
        get_image, web_app_client, web_app, mock_mds, tag, size_hint, is_poi,
):
    filename = 'app.png'
    form_data = aiohttp.FormData()
    form_data.add_field(
        'file',
        get_image(RealImage(PNG_FORMAT)).getbuffer(),
        filename=filename,
        content_type='image/png',
    )

    response = await web_app_client.post(
        f'/upload/{tag}/{size_hint}', data=form_data,
    )
    assert response.status == 200

    response = await web_app_client.get(f'/detail/{tag}')
    assert response.status == 200

    img_repo = img_repos.ImagesRepository(web_app['context'].mongo)
    images = await img_repo.get_images(tag)

    database_sh = {
        size_hint_module.size_hint_to_str(img.size_hints) for img in images
    }

    img_sh = (await response.json())['images'][0]['size_hint']
    if is_poi:
        hack_poi_sh = ADMIN_IMAGE_HACK_IPHONE_POI
        assert img_sh in hack_poi_sh
        assert len(database_sh) == 1
        assert database_sh.pop() in hack_poi_sh

    else:
        assert img_sh == size_hint

        upload_size_hints = ADMIN_IMAGES_UPLOAD_SIZE_HINTS
        expected_sh = set(upload_size_hints.get(size_hint, [size_hint]))
        assert database_sh == expected_sh

    for image in images:
        assert image.file_format is None
        assert len(image.revision_history) == 1
        assert image.revision_history[0].image_id == image.image_id


@pytest.mark.config(
    ADMIN_IMAGES_CONVERSION_OPTIONS=ADMIN_IMAGES_CONVERSION_OPTIONS_ENABLED,
    ADMIN_IMAGE_HACK_IPHONE_POI=ADMIN_IMAGE_HACK_IPHONE_POI,
    ADMIN_IMAGES_UPLOAD_SIZE_HINTS=ADMIN_IMAGES_UPLOAD_SIZE_HINTS,
)
async def test_create_new_with_conversion(
        get_image, web_app_client, web_app, mock_mds,
):
    tag = 'class_minivan_icon_2_new'
    size_hint, filename = 'android_480', 'app.png'
    form_data = aiohttp.FormData()
    form_data.add_field(
        'file',
        get_image(RealImage(PNG_FORMAT)).getbuffer(),
        filename=filename,
        content_type='image/png',
    )

    response = await web_app_client.post(
        f'/upload/{tag}/{size_hint}', data=form_data,
    )
    assert response.status == 200

    response = await web_app_client.get(f'/detail/{tag}')
    assert response.status == 200

    img_repo = img_repos.ImagesRepository(web_app['context'].mongo)
    images = await img_repo.get_images(tag)
    assert len(images) == 9
    # All images have same revision
    revisions = set()
    for img in images:
        assert len(img.revision_history) == 1
        revisions.add(img.revision_history[-1].revision)
    assert len(revisions) == 1

    img_default = [img for img in images if img.file_format is None]
    img_avif = [img for img in images if img.file_format == AVIF]
    img_heif = [img for img in images if img.file_format == HEIF]
    assert len(img_default) == len(img_avif) == len(img_heif) == 3
    assert (
        len({img.image_id for img in img_default})
        == len({img.image_id for img in img_avif})
        == len({img.image_id for img in img_heif})
        == 1
    )
    assert len({img.image_id for img in images}) == 3

    img = await img_repo.find_image(tag)
    assert img.file_format is None

    img = await img_repo.find_image(tag, file_format=AVIF)
    assert img.file_format == AVIF

    img = await img_repo.find_image(tag, file_format=HEIF)
    assert img.file_format == HEIF

    async def _check_images_by_format(_tag, _format):
        _images = await img_repo.get_images_by_format(
            _tag, file_format=_format,
        )
        assert len(_images) == 3
        for img in _images:
            assert img.file_format == _format

    await _check_images_by_format(tag, AVIF)
    await _check_images_by_format(tag, HEIF)
    await _check_images_by_format(tag, None)


@pytest.mark.config(
    ADMIN_IMAGES_CONVERSION_OPTIONS=ADMIN_IMAGES_CONVERSION_OPTIONS_ENABLED,
)
async def test_update_with_conversion(
        get_image, web_app_client, web_app, mock_mds, patch,
):
    tag, size_hint, filename = 'class_minivan_icon_2', 'iphone_300', 'app.png'
    new_revision = 'rev3'

    @patch('taxi_admin_images.logic.upload._generate_new_revision_id')
    def _patch_generate_new_revision_id():
        return new_revision

    img_repo = img_repos.ImagesRepository(web_app['context'].mongo)
    images = await img_repo.get_images(tag)
    assert len(images) == 3
    assert {img.file_format for img in images} == {None, AVIF, HEIF}

    form_data = aiohttp.FormData()
    form_data.add_field(
        'file',
        get_image(RealImage(PNG_FORMAT)).getbuffer(),
        filename=filename,
        content_type='image/png',
    )

    response = await web_app_client.post(
        f'/upload/{tag}/{size_hint}', data=form_data,
    )
    assert response.status == 200
    response = await web_app_client.get(f'/detail/{tag}')
    assert response.status == 200

    images = await img_repo.get_images(tag)
    assert len(images) == 3
    assert {img.file_format for img in images} == {None, AVIF, HEIF}
    assert set(img.revision_history[-1].revision for img in images) == {
        new_revision,
    }
    default_image = [img for img in images if img.file_format is None][0]
    avif_image = [img for img in images if img.file_format == AVIF][0]
    heif_image = [img for img in images if img.file_format == HEIF][0]
    assert default_image.image_id != avif_image.image_id != heif_image.image_id
    assert default_image.image_id != 'image_default_rev2'
    assert avif_image.image_id != 'image_avif_rev2'
    assert heif_image.image_id != 'image_heif_rev1'


def _check_update_with_conversion_fail(
        images, failed_format, old_revisions_by_format, old_ids_by_format,
):
    assert len(images) == 3
    image_by_format = {img.file_format: img for img in images}
    assert set(image_by_format.keys()) == {None, AVIF, HEIF}

    # If image was converted then revision and image_id changed, else unchanged
    ok_format = AVIF if failed_format == HEIF else HEIF
    assert (
        image_by_format[ok_format].revision_history[-1].revision
        != old_revisions_by_format[ok_format]
    )
    assert (
        image_by_format[failed_format].revision_history[-1].revision
        == old_revisions_by_format[failed_format]
    )

    assert (
        image_by_format[ok_format].revision_history[-1].image_id
        != old_ids_by_format[ok_format]
    )
    assert (
        image_by_format[failed_format].revision_history[-1].image_id
        == old_ids_by_format[failed_format]
    )


@pytest.mark.config(
    ADMIN_IMAGES_CONVERSION_OPTIONS=ADMIN_IMAGES_CONVERSION_OPTIONS_ENABLED,
)
@pytest.mark.parametrize(
    'fail_type, failed_format',
    [
        ('disabled', AVIF),
        ('disabled', HEIF),
        ('not_enough_savings', AVIF),
        ('not_enough_savings', HEIF),
    ],
)
async def test_update_with_conversion_fail(
        get_image,
        web_app_client,
        web_app,
        patch,
        fail_type,
        failed_format,
        taxi_config,
        taxi_admin_images,
        mockserver,
):
    tag, size_hint, filename = 'class_minivan_icon_2', 'iphone_300', 'app.png'
    img_repo = img_repos.ImagesRepository(web_app['context'].mongo)
    old_images = await img_repo.get_images(tag)
    old_revisions_by_format = {
        img.file_format: img.revision_history[-1].revision
        for img in old_images
    }
    old_ids_by_format = {
        img.file_format: img.revision_history[-1].image_id
        for img in old_images
    }

    if fail_type == 'disabled':
        config = taxi_config.get('ADMIN_IMAGES_CONVERSION_OPTIONS')
        config[failed_format]['enabled'] = False
        taxi_config.set_values({'ADMIN_IMAGES_CONVERSION_OPTIONS': config})
    elif fail_type == 'not_enough_savings':
        config = taxi_config.get('ADMIN_IMAGES_CONVERSION_OPTIONS')
        config[failed_format]['minimum_savings'] = 0.95
        taxi_config.set_values({'ADMIN_IMAGES_CONVERSION_OPTIONS': config})

    @mockserver.json_handler('/mds/upload-taxi', prefix=True)
    def handler(request):  # pylint: disable=W0612
        return mockserver.make_response(f'<post><key>new_rev</key></post>')

    await taxi_admin_images.invalidate_caches()
    form_data = aiohttp.FormData()
    form_data.add_field(
        'file',
        get_image(RealImage(PNG_FORMAT)).getbuffer(),
        filename=filename,
        content_type='image/png',
    )

    response = await taxi_admin_images.post(
        f'/upload/{tag}/{size_hint}', data=form_data,
    )
    assert response.status == 200

    images = await img_repo.get_images(tag)
    _check_update_with_conversion_fail(
        images, failed_format, old_revisions_by_format, old_ids_by_format,
    )


@pytest.mark.config(
    ADMIN_IMAGES_CONVERSION_OPTIONS=ADMIN_IMAGES_CONVERSION_OPTIONS_ENABLED,
)
@pytest.mark.parametrize('failed_format', [AVIF, HEIF])
async def test_update_with_conversion_fail2(
        get_image,
        web_app_client,
        web_app,
        patch,
        failed_format,
        taxi_config,
        mockserver,
        mock_mds,
):
    tag, size_hint, filename = 'class_minivan_icon_2', 'iphone_300', 'app.png'
    img_repo = img_repos.ImagesRepository(web_app['context'].mongo)
    old_images = await img_repo.get_images(tag)
    old_revisions_by_format = {
        img.file_format: img.revision_history[-1].revision
        for img in old_images
    }
    old_ids_by_format = {
        img.file_format: img.revision_history[-1].image_id
        for img in old_images
    }
    image_buffer = get_image(RealImage(PNG_FORMAT)).getbuffer()

    if failed_format == HEIF:

        @patch('taxi_admin_images.logic.convert.pillow_heif.from_pillow')
        def _patch_heif_conversion():
            raise Exception

    elif failed_format == AVIF:
        # Couldn't find a better patching place to break avif conversion
        # but keep Image.save working
        @patch('PIL.Image.Image.save')
        def _patch_avif_conversion():
            raise Exception

    form_data = aiohttp.FormData()
    form_data.add_field(
        'file', image_buffer, filename=filename, content_type='image/png',
    )

    response = await web_app_client.post(
        f'/upload/{tag}/{size_hint}', data=form_data,
    )
    assert response.status == 200

    images = await img_repo.get_images(tag)
    _check_update_with_conversion_fail(
        images, failed_format, old_revisions_by_format, old_ids_by_format,
    )


@pytest.mark.config(
    ADMIN_IMAGES_SIZE_HINTS=[
        {'key': 'iphone_667', 'name': 'iPhone @2x'},
        {'key': 'android_240', 'name': 'Android - XHDPI'},
        {'key': 'android_480', 'name': 'Android - XHDPI'},
    ],
)
@pytest.mark.parametrize(
    'tag, size_hint, old_id',
    [
        (
            'class_business_car',
            'android_240',
            '10593/d9029fab-2ca4-4664-97b2-072789856420',
        ),
        (
            'childchair_for_child_tariff.infant.image',
            'iphone_667',
            '10504/8db9fc17-95cb-404b-a041-f35fa47212b8',
        ),
        (
            'class_minivan_car',
            'android_480',
            '10504/8db9fc17-95cb-404b-a041-f35fa47212b8',
        ),
    ],
)
async def test_update(
        get_image, web_app_client, web_app, tag, size_hint, old_id, mock_mds,
):
    response = await web_app_client.get(f'/detail/{tag}')
    assert response.status == 200

    old_imgs = (await response.json())['images']
    old_url = {i['url'] for i in old_imgs if i['size_hint'] == size_hint}

    filename = 'app.png'
    form_data = aiohttp.FormData()
    form_data.add_field(
        'file',
        get_image(RealImage(PNG_FORMAT)).getbuffer(),
        filename=filename,
        content_type='image/png',
    )

    response = await web_app_client.post(
        f'/upload/{tag}/{size_hint}', data=form_data,
    )

    assert response.status == 200

    response = await web_app_client.get(f'/detail/{tag}')
    assert response.status == 200

    new_imgs = (await response.json())['images']
    new_url = {i['url'] for i in new_imgs if i['size_hint'] == size_hint}

    assert len(old_imgs) == len(new_imgs)
    assert old_url != new_url

    img_repo = img_repos.ImagesRepository(web_app['context'].mongo)
    images = await img_repo.get_images(tag)
    revisions = set()
    for image in images:
        assert image.file_format is None
        for entry in image.revision_history:
            revisions.add(entry.revision)
    # all images by tag have the same revision
    assert len(revisions) == 1


async def _upload(web_app_client, patch, data):
    sent_files: typing.List[bytes] = []

    @patch('client_mds.components.MDSClient.upload')
    async def upload_patch(file_obj):  # pylint: disable=unused-variable
        sent_files.append(file_obj)

    form_data = aiohttp.FormData()
    form_data.add_field('file', data)
    tag = 'test1_sometag'
    size_hint = 'android_480'
    response = await web_app_client.post(
        f'/upload/{tag}/{size_hint}', data=form_data,
    )
    return response, sent_files


async def intercept_upload(web_app_client, patch, data: memoryview):
    response, sent_files = await _upload(web_app_client, patch, data)
    assert response.status == 200
    assert sent_files
    return sent_files


def _check_compression_response_content(raw_image, content, is_compressed):
    if is_compressed:
        assert len(content) < len(raw_image)
    else:
        assert raw_image == content


@pytest.mark.parametrize(
    'image_stream, is_compressed, compression_broken',
    [
        pytest.param(
            io.BytesIO(b'123'),
            False,
            False,
            id='file is not an image. do not compress',
        ),
        pytest.param(
            RealImage(JPEG_FORMAT), True, False, id='valid jpeg, compress',
        ),
        pytest.param(
            RealImage(JPEG_FORMAT),
            False,
            True,
            id='valid jpeg, compression broken',
        ),
    ],
)
async def test_compression_jpeg(
        web_app_client,
        patch,
        image_stream,
        is_compressed,
        compression_broken,
        get_image,
):
    raw_image = get_image(image_stream).getbuffer()

    if compression_broken:

        @patch('PIL.Image.Image.save')
        def _save(*args, **kwargs):
            raise Exception('Compression broken')

    form_data = aiohttp.FormData()
    form_data.add_field('file', raw_image)

    response = await web_app_client.post(
        '/internal/compress-jpeg', data=form_data, params={'quality': 90},
    )
    assert response.status == 200
    assert response.content_type == 'application/octet-stream'

    content = await response.read()
    _check_compression_response_content(raw_image, content, is_compressed)


@pytest.mark.parametrize(
    'image_stream, is_compressed, liq_is_supported',
    [
        pytest.param(
            io.BytesIO(b'123'),
            False,
            False,
            id='file is not an image. do not compress',
        ),
        pytest.param(
            RealImage(PNG_FORMAT),
            True,
            True,
            id='valid png, libimagequant is supported, compress',
        ),
        pytest.param(
            RealImage(PNG_FORMAT),
            False,
            False,
            id='valid png, libimagequant is not supported, do not compress',
        ),
    ],
)
async def test_compression_png(
        web_app_client,
        patch,
        image_stream,
        is_compressed,
        liq_is_supported,
        get_image,
):
    raw_image = get_image(image_stream).getbuffer()

    # required for png quantization
    @patch('PIL.features.check_feature')
    def _check_feature(feature):
        assert feature == 'libimagequant'
        return liq_is_supported

    if liq_is_supported:
        # required for png quantization
        @patch('PIL.Image.Image.quantize')
        def _quantize(method):
            assert method == PilImage.LIBIMAGEQUANT
            # looks like it's impossible to quantize png image on macos
            # just return image of a smaller dimension
            return PilImage.open(get_image(RealImage(PNG_FORMAT, (100, 100))))

    form_data = aiohttp.FormData()
    form_data.add_field('file', raw_image)

    response = await web_app_client.post(
        '/internal/compress-png', data=form_data,
    )
    assert response.status == 200
    assert response.content_type == 'application/octet-stream'

    content = await response.read()
    _check_compression_response_content(raw_image, content, is_compressed)


@pytest.mark.config(
    ADMIN_IMAGES_PREFIX_TO_GROUP_MAP={'test1': 'test1'},
    ADMIN_IMAGES_GROUPS_PROPERTIES_V2=ADMIN_IMAGES_GROUPS_PROPERTIES,
)
@pytest.mark.parametrize(
    'image_params, expected_status, expected_code',
    [
        pytest.param(RealImage(JPEG_FORMAT), 200, None, id='ok'),
        pytest.param(
            RealImage(JPEG_FORMAT),
            413,
            'RESOLUTION_TOO_HIGH',
            id='high resolution',
            marks=[
                pytest.mark.config(
                    ADMIN_IMAGES_GROUPS_PROPERTIES_V2={
                        'test1': {
                            'max_resolution': {'width': 100, 'height': 100},
                        },
                    },
                ),
            ],
        ),
        pytest.param(
            RealImage(JPEG_FORMAT),
            413,
            'BYTES_PER_PIXEL_RATIO_TOO_HIGH',
            id='high bytes per pixels ratio',
            marks=[
                pytest.mark.config(
                    ADMIN_IMAGES_GROUPS_PROPERTIES_V2={
                        'test1': {'max_bytes_per_pixel_ratio': 0.001},
                    },
                ),
            ],
        ),
        pytest.param(
            RealImage(JPEG_FORMAT),
            413,
            'FILE_TOO_LARGE',
            id='file is too large (group restriction)',
            marks=[
                pytest.mark.config(
                    ADMIN_IMAGES_GROUPS_PROPERTIES_V2={
                        'test1': {'max_image_size_kb': 5},
                    },
                ),
            ],
        ),
    ],
)
async def test_upload_heavy_image(
        web_app_client,
        patch,
        image_params,
        expected_status,
        expected_code,
        get_image,
):
    image = get_image(image_params)
    response, _ = await _upload(web_app_client, patch, image.getbuffer())
    assert response.status == expected_status
    if response.status != 200:
        data = await response.json()
        assert data['code'] == expected_code


@pytest.mark.config(ADMIN_IMAGES_PREFIX_TO_GROUP_MAP={'test1': 'test1'})
@pytest.mark.parametrize(
    'is_compressed',
    [
        pytest.param(
            True,
            id='saving above threshold, compress',
            marks=[
                pytest.mark.config(
                    ADMIN_IMAGES_GROUPS_PROPERTIES_V2={
                        '__default__': {
                            'jpeg_quality': 85,
                            'minimum_compression_savings': 0.1,
                        },
                    },
                ),
            ],
        ),
        pytest.param(
            False,
            id='savings under threshold, do not compress',
            marks=[
                pytest.mark.config(
                    ADMIN_IMAGES_GROUPS_PROPERTIES_V2={
                        '__default__': {
                            'jpeg_quality': 85,
                            'minimum_compression_savings': 0.8,
                        },
                    },
                ),
            ],
        ),
        pytest.param(
            False,
            id='no property minimum_compression_savings in config',
            marks=[
                pytest.mark.config(
                    ADMIN_IMAGES_GROUPS_PROPERTIES_V2={
                        'test1': {'jpeg_quality': 85},
                    },
                ),
            ],
        ),
        pytest.param(
            False,
            id='no property jpeg_quality in config',
            marks=[
                pytest.mark.config(
                    ADMIN_IMAGES_GROUPS_PROPERTIES_V2={
                        'test1': {'minimum_compression_savings': 0.1},
                    },
                ),
            ],
        ),
    ],
)
async def test_compress_upload_jpeg(
        get_image, web_app_client, patch, is_compressed,
):
    image_stream = get_image(RealImage(JPEG_FORMAT))
    sent_files = await intercept_upload(
        web_app_client, patch, image_stream.getbuffer(),
    )
    assert len(sent_files) == 1
    if is_compressed:
        assert len(sent_files[0]) < len(image_stream.getbuffer())
    else:
        assert len(sent_files[0]) == len(image_stream.getbuffer())


@pytest.mark.config(
    ADMIN_IMAGES_PREFIX_TO_GROUP_MAP={'test1': 'test1'},
    ADMIN_IMAGES_GROUPS_PROPERTIES_V2={
        '__default__': {
            'jpeg_quality': 10,
            'minimum_compression_savings': 0.1,
        },
        'test1': {'minimum_compression_savings': 0.2},
    },
)
async def test_group_parameters(web_context):
    get_group_properties = (
        upload_logic._get_group_properties  # pylint: disable=W0212
    )
    assert get_group_properties('test1', web_context.config) == {
        'jpeg_quality': 10,
        'minimum_compression_savings': 0.2,
    }


@pytest.mark.config(
    ADMIN_IMAGES_DEFAULT_SKIN_VERSION=7,
    BRANDING_ITEMS_COUNT={'some_branding': 2},
    ZONES_TARIFFS_SETTINGS={
        'moscow': {'business': {'subtitle': 'card.subtitle.business_moscow'}},
        'spb': {'comfort': {'subtitle': 'card.subtitle.comfort_spb'}},
    },
)
@pytest.mark.translations(
    client_messages={
        'mainscreen.description_business_moscow': {
            'en': 'Mercedes-Benz E-class, BMW 5, Audi A6',
            'ru': 'Mercedes-Benz E-class, BMW 5, Audi A6',
        },
        'branding.some_branding.text_items_1': {
            'en': 'Drivers have the highest passenger feedback',
            'ru': 'Водители с лучшими оценками от пассажиров',
        },
        'branding.some_branding.text_items_2': {
            'en': 'Drivers interviewed individually and trained in quality standards',  # noqa
            'ru': 'Водители прошли собеседование: хорошо знают стандарты качества',  # noqa
        },
        'branding.moscow.text_items_1': {
            'en': 'Fixed price of €25 and maximum 20 minutes in the sauna',
        },
        'branding.moscow.text_items_2': {'en': 'A smooth, quiet ride'},
        'branding.spb.text_items_1': {'en': 'Fast pickup'},
    },
    tariff={
        'card.subtitle.business_moscow': {
            'en': 'Relaxed rides with experienced drivers',
            'ru': 'Спокойная поездка с опытным водителем',
        },
        'card.subtitle.comfort_spb': {
            'en': 'Comfort ride to the office or meetings',
        },
    },
)
@pytest.mark.parametrize(
    'zone, branding, tariff, lang, expected_response_file',
    [
        (
            'moscow',
            'some_branding',
            'business',
            'en',
            'expected_moscow_business_branding_response_en.json',
        ),
        (
            'moscow',
            'some_branding',
            'business',
            'ru',
            'expected_moscow_business_branding_response_ru.json',
        ),
        (
            'moscow',
            '',
            'business',
            'en',
            'expected_moscow_business_no_branding_response.json',
        ),
        ('spb', '', 'comfort', 'en', 'expected_spb_comfort_response.json'),
    ],
)
async def test_zone_info(
        web_app_client,
        load_json,
        zone,
        branding,
        tariff,
        lang,
        expected_response_file,
):
    request_url = f'/v1/info/{zone}/{tariff}?branding={branding}'
    response = await web_app_client.get(
        request_url, headers={'Accept-Language': lang},
    )
    assert response.status == 200
    expected_response = load_json(expected_response_file)
    content = await response.json()
    diff = deepdiff.DeepDiff(content, expected_response, ignore_order=True)
    assert diff == {}


async def test_repo_find_image_with_file_formats(web_app_client, web_app):
    img_repo = img_repos.ImagesRepository(web_app['context'].mongo)
    image = await img_repo.find_image('class_minivan_icon_3')
    assert image
    assert image.file_format is None

    image = await img_repo.find_image(
        'class_minivan_icon_3', file_format='avif',
    )
    assert image
    assert image.file_format == 'avif'


@pytest.mark.parametrize(
    'tint,tag',
    [
        (True, 'class_minivan_car'),
        (False, 'class_minivan_car'),
        (True, 'class_minivan_icon_3'),
        (False, 'class_minivan_icon_3'),
    ],
)
async def test_set_tint(web_app_client, web_app, tint, tag):
    tint_query = '?tint=true' if tint else '?tint=false'
    response = await web_app_client.post(f'/set_tint/{tag}{tint_query}')
    assert response.status == 200

    img_repo = img_repos.ImagesRepository(web_app['context'].mongo)
    images = await img_repo.get_images(tag)
    if tag == 'class_minivan_icon_3':
        assert len(images) == 3
    for image in images:
        assert image.is_tintable == (tint if tint else None)

    response = await web_app_client.get(f'/detail/{tag}')
    assert response.status == 200

    response = await response.json()
    assert response.get('is_tintable', False) == tint


@pytest.mark.filldb('theme_duples')
async def test_detail_duples(web_app_client):
    response = await web_app_client.get(f'/detail/class_business_car_7')
    assert response.status == 200

    images = (await response.json())['images']
    assert len(images) == 1
