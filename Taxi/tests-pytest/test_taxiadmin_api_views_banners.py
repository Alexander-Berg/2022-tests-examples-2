from __future__ import unicode_literals

import json

import bson
from django import test as django_test
from django.core.files import uploadedfile
import pytest

from taxi.core import async
from taxi.core import db


@pytest.mark.asyncenv('blocking')
@pytest.mark.config(
    IMAGES_URL_TEMPLATE='https://tc-tst.mobile.yandex.net'
                        '/static/test-images/{}')
def test_banner_get(load):
    response = django_test.Client().get(
        '/api/banners/get_banner/',
        {'banner_id': '55acb3046c090a201fac1811'}
    )

    assert response.status_code == 200
    assert json.loads(response.content) == json.loads(load('expected.json'))


@pytest.mark.asyncenv('blocking')
def test_banner_set_and_get(load):
    response = django_test.Client().post(
        '/api/banners/set_banner/',
        data=load('create_request.json'),
        content_type='application/json'
    )
    assert response.status_code == 200
    banner_id = json.loads(response.content)['banner_id']

    response = django_test.Client().get(
        '/api/banners/get_banner/',
        {'banner_id': banner_id}
    )
    assert response.status_code == 200
    deeplink = json.loads(response.content)['action_button']
    assert deeplink['deeplink_custom'] == {
        'android': "('yandextaxi://',)",
        'iphone': "('yandextaxi://',)",
        'yango_iphone': "('yangotaxi://',)",
        'yango_android': ''
    }
    assert deeplink['deeplink_target'] == {
        'android': '6786899',
        'iphone': '87686',
        'yango_iphone': '123455',
        'yango_android': ''
    }


@pytest.mark.parametrize(
    'experiment_version,expected_code',
    [
        (2, 400),
        (3, 200),
        (None, 400),
        (1, 400),
        (0, 400),
        (4, 400),
    ],
)
@pytest.mark.asyncenv('blocking')
def test_banner_set_and_deploy(experiment_version, expected_code, load, patch):
    @patch('taxi.external.exp.get_experiment')
    @async.inline_callbacks
    def get_experiment3(name, log_extra=None):
        yield
        async.return_value({})

    @patch('taxiadmin.audit.check_ticket')
    @async.inline_callbacks
    def check_ticket(ticket_key, login, **kwargs):
        yield

    response = django_test.Client().post(
        '/api/banners/set_banner/',
        data=load('create_request.json'),
        content_type='application/json'
    )
    assert response.status_code == 200
    banner_id = json.loads(response.content)['banner_id']

    response = django_test.Client().post(
        '/api/banners/deploy_banner/',
        {
            'banner_id': banner_id,
            'global': True,
            'experiment': 'experiment_name',
            'experiment_version': experiment_version,
            'ticket': 'ticket',
        },
    )
    assert response.status_code == expected_code

    if expected_code != 200:
        return

    response = django_test.Client().get(
        '/api/banners/get_banner/',
        {'banner_id': banner_id}
    )
    assert response.status_code == 200
    data = json.loads(response.content)
    assert data['experiment'] == 'experiment_name'
    assert data['experiment_version'] == experiment_version


@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_create_banner_with_images(load):
    response = django_test.Client().post(
        '/api/banners/set_banner/',
        data=load('create_request.json'),
        content_type='application/json'
    )

    assert response.status_code == 200

    data = json.loads(response.content)
    banner_id = data['banner_id']

    for locale in ('ru', 'en'):
        tag = 'banner_%s_%s_image' % (banner_id, locale)

        images = yield db.images.find({'tags': tag}).run()

        assert len(images) == 9

        for image in images:
            assert image['tags'] == [tag]


@pytest.mark.parametrize('images,code', [
    (
        [{
            'id': '123',
            'locale': 'ru',
            'property': 'android_hdpi'
        }],
        'image_invalid_id'
    ),
    (
        [{
            'id': '000000000000000000000001',
            'locale': 'ru',
            'property': 'android_hdpi'
        }],
        'image_not_exists'
    ),
    (
        [{
            'id': '55acb304d2773bdb84dc823a',
            'locale': 'ru',
            'property': 'invalid_property'
        }],
        'image_invalid_property'
    ),
    (
        [{
            'id': '55acb304d2773bdb84dc823a',
            'locale': 'ru',
            'property': 'android_mdpi'
        }],
        'image_property_mismatch'
    ),
    (
        [
            {
                'id': '55acb304d2773bdb84dc823a',
                'locale': 'ru',
                'property': 'android_hdpi'
            },
            {
                'id': '55acb305d2773bdb84dc8243',
                'locale': 'ru',
                'property': 'android_hdpi'
            }
        ],
        'image_property_duplicate'
    )

])
@pytest.mark.asyncenv('blocking')
def test_validate_images(load, images, code):
    data = json.loads(load('create_request.json'))
    data['images'] = images

    response = django_test.Client().post(
        '/api/banners/set_banner/',
        data=json.dumps(data),
        content_type='application/json'
    )
    assert response.status_code == 400
    error = json.loads(response.content)
    assert error['code'] == code
    assert error['status'] == 'error'


@pytest.mark.asyncenv('blocking')
@pytest.mark.config(
    IMAGES_URL_TEMPLATE='https://tc-tst.mobile.yandex.net'
                        '/static/test-images/{}')
@pytest.inline_callbacks
def test_set_banner_image(patch):
    @patch('taxi.external.mds.upload')
    @async.inline_callbacks
    def upload_patched(content, log_extra):
        yield
        async.return_value('image_id')

    @patch('taxi.internal.image_manager._image_removal_task.call')
    @async.inline_callbacks
    def image_removal_task(*args, **kwargs):
        yield

    image = uploadedfile.SimpleUploadedFile(
        'image.jpg',
        'content',
        'image/jpeg'
    )

    data = {
        'property': 'iphone_6',
        'banner_id': '55acb3046c090a201fac1811',
        'image': image,
        'locale': 'ru'
    }

    response = django_test.Client().post('/api/banners/set_banner_image/', data)
    assert json.loads(response.content) == {
        "url": 'https://tc-tst.mobile.yandex.net/static/test-images/image_id'
    }

    changed_image = yield db.images.find_one(
        {'_id': bson.objectid.ObjectId('55acb304d2773bdb84dc823e')}
    )

    assert changed_image['image_id'] == 'image_id'
    assert image_removal_task.calls[0] == {
        'args': ('1138/adf999a0-a30c-450f-ae23-1ab057a3c9e7',),
        'kwargs': {'log_extra': None}
    }

    # update image with image_id existing in other image
    data['property'] = 'android_mdpi'

    response = django_test.Client().post('/api/banners/set_banner_image/', data)
    assert json.loads(response.content) == {
        "url": 'https://tc-tst.mobile.yandex.net/static/test-images/image_id'
    }

    changed_image = yield db.images.find_one(
        {'_id': bson.objectid.ObjectId('55acb304d2773bdb84dc823d')}
    )
    assert changed_image['image_id'] == 'image_id'
    # image_id exists in other image => no remove task call
    assert image_removal_task.calls == []
