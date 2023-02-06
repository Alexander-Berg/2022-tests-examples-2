# pylint: disable=protected-access
import pytest

from taxi_admin_images.logic import upload
from taxi_admin_images.models import image_size_hint
from taxi_admin_images.view import structure


@pytest.mark.parametrize(
    'size_hint_doc, result',
    [
        (
            {'web': 0, 'android': 720, 'iphone': 206, 'mobileweb': 9999},
            'mobileweb_9999',
        ),
        ({'web': 0, 'iphone': 480}, 'iphone_480'),
        ({'web': 9999, 'android': 0, 'iphone': 0}, 'web_9999'),
        ({'android': 720}, 'android_720'),
    ],
)
async def test_parse_size_hint_to_str(size_hint_doc, result):
    size_hints = image_size_hint.size_hint_from_doc(size_hint_doc)
    size_hint_str = image_size_hint.size_hint_to_str(size_hints)
    assert size_hint_str == result


@pytest.mark.parametrize(
    'tag, expected_struct',
    [
        (
            'class_business_icon_5_yango_auris',
            structure.ImageStructure('class', 'icon', 'business'),
        ),
        (
            'class_business_icon_5',
            structure.ImageStructure('class', 'icon', 'business'),
        ),
        (
            'class_business_icon',
            structure.ImageStructure('class', 'icon', 'business'),
        ),
        ('class_vip_car_5', structure.ImageStructure('class', 'car', 'vip')),
        (
            'class_business_child_poi_5_yango_auris',
            structure.ImageStructure('class', 'poi', 'business_child'),
        ),
        ('class_mkk_car', structure.ImageStructure('class', 'car', 'mkk')),
        (
            'branding_pool_image_2',
            structure.ImageStructure('class', 'branding', 'pool'),
        ),
        (
            'branding_child_tariff_video_preview',
            structure.ImageStructure('class', 'branding', 'child_tariff'),
        ),
        (
            'branding_child_tariff_logo',
            structure.ImageStructure('class', 'branding', 'child_tariff'),
        ),
        (
            'branding_image_default',
            structure.ImageStructure('class', 'branding', ''),
        ),
        ('image_sdc_eula', structure.ImageStructure('common', '', '')),
        ('app_icon_disk', structure.ImageStructure('common', '', '')),
        (
            'achievements_inactive_initial',
            structure.ImageStructure('driver', '', ''),
        ),
        ('uber_color_344559', structure.ImageStructure('uber', '', '')),
        (
            'forced_class_combo_from_econom',
            structure.ImageStructure('other', '', ''),
        ),
        ('other_tag', structure.ImageStructure('other', '', '')),
    ],
)
async def test_parse_structure(web_app, tag, expected_struct):
    res = structure.parse_structure(web_app['context'].config, tag)
    assert res == expected_struct


@pytest.mark.config(
    ADMIN_IMAGE_HACK_IPHONE_NOT_POI=[
        'iphone_206',
        'iphone_240',
        'iphone_300',
        'iphone_390',
        'iphone_9999',
    ],
    ADMIN_IMAGE_HACK_IPHONE_POI=['iphone_128', 'iphone_192'],
)
@pytest.mark.parametrize(
    'tag, size_hint, expected',
    [
        ('class_business_icon', 'iphone_206', False),
        ('class_business_icon', 'iphone_300', False),
        ('class_business_icon', 'iphone_192', True),
        ('class_business_icon', 'iphone_128', True),
        ('class_business_poi', 'iphone_206', True),
        ('class_business_poi', 'iphone_300', True),
        ('class_business_poi_5', 'iphone_300', True),
        ('class_business_poi', 'iphone_192', False),
        ('class_business_poi', 'iphone_128', False),
        ('class_business_poi', 'iphone_9999', True),
        ('class_business_pointer', 'iphone_128', True),
        ('class_business_pointer', 'iphone_300', False),
        ('class_business_poi', 'android_480', False),
        ('class_business_icon', 'android_160', False),
    ],
)
async def test_hack_poi(web_app, tag, size_hint, expected):
    res = upload._is_hack_for_iphone_poi(
        web_app['context'].config, tag, size_hint,
    )
    assert res == expected
