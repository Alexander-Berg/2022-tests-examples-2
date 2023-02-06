import bson
import pytest

from taxi.internal import client_urls
from taxi.internal import image_manager


@pytest.mark.parametrize('image_tag,user_application,size_hint,result,exc', [
    # Happy path, real size_hint is 240
    (
        'test_image',
        'android',
        140,
        'https://tc-tst.mobile.yandex.net/static/test-images/image1.png',
        None
    ),

    # Exact match on size_hint
    (
        'test_image',
        'android',
        240,
        'https://tc-tst.mobile.yandex.net/static/test-images/image1.png',
        None
    ),

    # Happy path: just another image
    (
        'test_image',
        'android',
        360,
        'https://tc-tst.mobile.yandex.net/static/test-images/image2.png',
        None
    ),

    # Another size_hint scale
    (
        'test_image',
        'iphone',
        1,
        'https://tc-tst.mobile.yandex.net/static/test-images/image1.png',
        None
    ),

    (
        'test_image',
        'iphone',
        3,
        'https://tc-tst.mobile.yandex.net/static/test-images/image2.png',
        None
    ),

    # Web clients probably won't support size_hint at all
    (
        'test_image',
        'web',
        0,
        'https://tc-tst.mobile.yandex.net/static/test-images/image1.png',
        None
    ),

    # Win works like web
    (
        'test_image',
        'win',
        0,
        'https://tc-tst.mobile.yandex.net/static/test-images/image1.png',
        None
    ),

    # size_hint too high, the largest one will be returned
    (
        'test_image',
        'android',
        1400,
        'https://tc-tst.mobile.yandex.net/static/test-images/highest.png',
        None,
    ),

    (
        'test_image',
        'iphone',
        11,
        'https://tc-tst.mobile.yandex.net/static/test-images/highest.png',
        None,
    ),

    # Error: image not found
    (
        'unknown',
        'android',
        0,
        None,
        image_manager.ImageNotFoundError
    ),

    # Error: invalid user application
    (
        'test_image',
        'sailfish',
        140,
        None,
        ValueError
    ),
])
@pytest.mark.config(
    IMAGES_URL_TEMPLATE='https://tc-tst.mobile.yandex.net'
                        '/static/test-images/{}')
@pytest.inline_callbacks
def test_find_best_image(image_tag, user_application, size_hint,
                         result, exc):
    if exc is None:
        image = yield image_manager.find_best_image(
            image_tag, user_application, size_hint
        )

        assert image is not None
        assert image.url == result
    else:
        with pytest.raises(exc):
            yield image_manager.find_best_image(
                image_tag, user_application, size_hint
            )


@pytest.mark.filldb(images='small')
@pytest.inline_callbacks
def test_get_images_by_tag_name():
    images = yield image_manager.get_images_by_tag_name('test_image')

    expected_images = [
        image_manager.Image(**kwargs) for kwargs in [
            {
                'url': (yield client_urls.build_image_url('image1.png')),
                'url_parts': client_urls.build_image_url_parts('image1.png'),
                'user_application': 'android',
                'size_hint': 240,
                'id': bson.objectid.ObjectId('000000000000000000000004')
            },

            {
                'url': (yield client_urls.build_image_url('image1.png')),
                'url_parts': client_urls.build_image_url_parts('image1.png'),
                'user_application': 'iphone',
                'size_hint': 480,
                'id': bson.objectid.ObjectId('000000000000000000000004')
            },

            {
                'url': (yield client_urls.build_image_url('image2.png')),
                'url_parts': client_urls.build_image_url_parts('image2.png'),
                'user_application': 'android',
                'size_hint': 480,
                'id': bson.objectid.ObjectId('000000000000000000000005')
            },

            {
                'url': (yield client_urls.build_image_url('image2.png')),
                'url_parts': client_urls.build_image_url_parts('image2.png'),
                'user_application': 'iphone',
                'size_hint': 667,
                'id': bson.objectid.ObjectId('000000000000000000000005')
            }
        ]
    ]

    assert len(images) == 4
    # Order-insensitive comparison
    assert images == expected_images


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize(
    'image_data,image_tag,user_application,size_hint', [
        # Case 1: create new document
        ('data1', 'completely_new', 'android', 640),
        # Case 2: update existing document with new data
        ('data2', 'completely_new', 'android', 640),
        # Case 3: another image for existing tag
        ('data3', 'completely_new', 'iphone', 768),
    ]
)
@pytest.inline_callbacks
def test_set_image(image_data, image_tag, user_application, size_hint,
                   patch):
    @patch('taxi.internal.image_manager._image_removal_task.call')
    def call(*args, **kwargs):
        pass

    @patch('taxi.external.mds.upload')
    def _upload(img, log_extra=None):
        # Use data provided as an id so we can easily say the picture
        return img

    yield image_manager.set_image(
        image_data, image_tag, user_application, size_hint
    )
    image = yield image_manager.find_best_image(
        image_tag, user_application, size_hint
    )
    assert image is not None
    assert image.url == (yield client_urls.build_image_url(image_data))
    assert image.url_parts == client_urls.build_image_url_parts(image_data)
    assert image.size_hint == size_hint
    assert image.user_application == user_application
