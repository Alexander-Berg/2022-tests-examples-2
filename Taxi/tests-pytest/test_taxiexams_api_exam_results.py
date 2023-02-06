# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import uuid

import pytest
import json

from django.test import RequestFactory

from taxi.core import db
from taxiexams.api import exam


driver_photos_called = False


@pytest.mark.translations([
    ('client_messages', 'driverphotos.service_not_available', 'ru', u'ERROR MESSAGE'),
])
@pytest.mark.config(
    EXTRA_EXAMS_INFO={
        'business': {
            'description': 'Допуск к классу Бизнес',
            'requires': [{'course': 'base', 'min_result': 3}],
            'permission': ['vip']
        },
        'kids': {
            'description': 'Допуск к классу Детский',
            'requires': [{'course': 'base', 'min_result': 3}],
            'permission': ['kids']
        }
    },
)
@pytest.mark.parametrize('data,expected_code,expected_response', [
    (
        {
            'course': 'business',
        },
        400,
        {
            'status': 'error',
            'message': '"city": no field given',
            'code': 'invalid-input'
        },
    ),
    (
        {
            'course': 'business',
            'exam_date': '2017-10-29T12:18:00+0000',
            'license': '123124',
            'result': 'asd',
            'center': 'test_center_1',
            'city': 'Москва',
        },
        400,
        {
            'status': 'error',
            'message': '"result": wrong type of field',
            'code': 'invalid-input'
        },
    ),
    (
        {
            'course': 'business',
            'exam_date': '2017-10-29T12:18:00+0000',
            'license': '123124',
            'result': 20,
            'center': 'test_center_2',
            'city': 'Москва',
        },
        406,
        {
            'status': 'error',
            'message': '"20": wrong field value',
            'code': 'not-acceptable'
        },
    ),
    (
        {
            'course': 'business',
            'exam_date': '20400asd',
            'license': '123124',
            'result': 5,
            'center': 'test_center_3',
            'city': 'Москва',
        },
        400,
        {
            'status': 'error',
            'message': '"exam_date": wrong type of field',
            'code': 'invalid-input'
        },
    ),
    (
        {
            'course': 'business',
            'exam_date': '2017-09-29T12:18:00+0000',
            'license': '123124',
            'result': 5,
            'center': 'test_center_4',
            'city': 'Москва',
        },
        409,
        {
            'status': 'error',
            'message': 'The result with a newer date of the'
                       ' exam already exists',
            'code': 'wrong-value'
        },
    ),
    (
        {
            'course': 'business',
            'exam_date': '2017-11-29T12:18:00+0000',
            'license': '123124',
            'result': 5,
            'center': 'test_center_5',
            'city': 'Москва',
        },
        200,
        {
            'status': 'error',
            'message': None,
            'code': 'invalid-input'
        },
    ),
    # driver_photos returns 200
    (
        {
            'course': 'business',
            'exam_date': '2017-11-29T12:18:00+0000',
            'license': '123124',
            'profile-photo': '1138/bc4be874-757b-44bc-a10d-17bb7420f2b7',
            'result': 5,
            'center': 'test_center_5',
            'city': 'Москва',
        },
        200,
        None,
    ),
    # driver_photos returns 500
    (
        {
            'course': 'business',
            'exam_date': '2017-11-29T12:18:00+0000',
            'license': '123124',
            'profile-photo': 'return_warning',
            'result': 5,
            'center': 'test_center_5',
            'city': 'Москва',
        },
        200,
        None,
    ),
])
@pytest.inline_callbacks
@pytest.mark.asyncenv('blocking')
def test_upload_result(patch, mock, data, expected_code, expected_response, areq_request):

    @patch('taxi.util.helpers.clean_driver_license')
    def exists(value):
        return value

    @patch('taxi.internal.personal.find')
    def license_find(data_type, value, log_extra=None):
        return {'id': value + '_pd_id', 'license': value}

    global driver_photos_called
    driver_photos_called = False

    @areq_request
    def aresponse(method, url, **kwargs):
        assert 'driver-photos.taxi.yandex.net/photos/new' in url
        assert method == 'POST'
        global driver_photos_called
        driver_photos_called = True
        if kwargs['data']['source'] == 'return_warning':
            code = 500
        else:
            code = 200
        return (code, '{}', {})

    request = RequestFactory().post(
        '',
        data=json.dumps(data),
        content_type='application/json'
    )
    response = yield exam.upload_result(request)
    assert response.status_code == expected_code
    if expected_code != 200:
        assert json.loads(response.content) == expected_response
    else:
        assert not (yield db.exam_results.find_one({
            'license': data['license'],
            'updated_by': {'$exists': True}
        }))
        if 'profile-photo' in data:
            if data['profile-photo'] == 'return_warning':
                # Service should have returned 500
                resp = json.loads(response.content)
                assert resp['warning'] == {
                    'message': u'ERROR MESSAGE',
                    'code': 'driver_photo_service_fail'
                }
                assert 'id' in resp
            else:
                # Service should have returned 200
                assert driver_photos_called


@pytest.mark.translations([
    ('client_messages', 'driverphotos.service_not_available', 'ru', u'ERROR MESSAGE'),
])
@pytest.mark.config(
    EXTRA_EXAMS_INFO={
        'business': {
            'description': 'Допуск к классу Бизнес',
            'requires': [{'course': 'base', 'min_result': 3}],
            'permission': ['vip']
        },
        'kids': {
            'description': 'Допуск к классу Детский',
            'requires': [{'course': 'base', 'min_result': 3}],
            'permission': ['kids']
        }
    },
    TAXI_EXAMS_SAVE_REQUEST_ID=True,
)
@pytest.mark.parametrize('send_request_id', [False, True])
@pytest.mark.parametrize('data,expected_code,expected_response', [
    (
        {
            'course': 'business',
        },
        400,
        {
            'status': 'error',
            'message': '"city": no field given',
            'code': 'invalid-input'
        },
    ),
    (
        {
            'course': 'business',
            'exam_date': '2017-10-29T12:18:00+0000',
            'license': '123124',
            'result': 'asd',
            'center': 'test_center_1',
            'city': 'Москва',
        },
        400,
        {
            'status': 'error',
            'message': '"result": wrong type of field',
            'code': 'invalid-input'
        },
    ),
    (
        {
            'course': 'business',
            'exam_date': '2017-10-29T12:18:00+0000',
            'license': '123124',
            'result': 20,
            'center': 'test_center_2',
            'city': 'Москва',
        },
        406,
        {
            'status': 'error',
            'message': '"20": wrong field value',
            'code': 'not-acceptable'
        },
    ),
    (
        {
            'course': 'business',
            'exam_date': '20400asd',
            'license': '123124',
            'result': 5,
            'center': 'test_center_3',
            'city': 'Москва',
        },
        400,
        {
            'status': 'error',
            'message': '"exam_date": wrong type of field',
            'code': 'invalid-input'
        },
    ),
    (
        {
            'course': 'business',
            'exam_date': '2017-09-29T12:18:00+0000',
            'license': '123124',
            'result': 5,
            'center': 'test_center_4',
            'city': 'Москва',
        },
        409,
        {
            'status': 'error',
            'message': 'The result with a newer date of the'
                       ' exam already exists',
            'code': 'wrong-value'
        },
    ),
    (
        {
            'course': 'business',
            'exam_date': '2017-11-29T12:18:00+0000',
            'license': '123124',
            'result': 5,
            'center': 'test_center_5',
            'city': 'Москва',
        },
        200,
        {
            'status': 'error',
            'message': None,
            'code': 'invalid-input'
        },
    ),
    # driver_photos returns 200
    (
        {
            'course': 'business',
            'exam_date': '2017-11-29T12:18:00+0000',
            'license': '123124',
            'profile-photo': '1138/bc4be874-757b-44bc-a10d-17bb7420f2b7',
            'result': 5,
            'center': 'test_center_5',
            'city': 'Москва',
        },
        200,
        None,
    ),
    # driver_photos returns 500
    (
        {
            'course': 'business',
            'exam_date': '2017-11-29T12:18:00+0000',
            'license': '123124',
            'profile-photo': 'return_warning',
            'result': 5,
            'center': 'test_center_5',
            'city': 'Москва',
        },
        200,
        None,
    ),
])
@pytest.inline_callbacks
@pytest.mark.asyncenv('blocking')
def test_upload_result_with_request_id(
        patch,
        mock,
        areq_request,
        send_request_id,
        data,
        expected_code,
        expected_response,
):

    @patch('taxi.util.helpers.clean_driver_license')
    def exists(value):
        return value

    @patch('taxi.internal.personal.find')
    def license_find(data_type, value, log_extra=None):
        return {'id': value + '_pd_id', 'license': value}

    global driver_photos_called
    driver_photos_called = False

    @areq_request
    def aresponse(method, url, **kwargs):
        assert 'driver-photos.taxi.yandex.net/photos/new' in url
        assert method == 'POST'
        global driver_photos_called
        driver_photos_called = True
        if kwargs['data']['source'] == 'return_warning':
            code = 500
        else:
            code = 200
        return (code, '{}', {})

    request = RequestFactory().post(
        '',
        data=json.dumps(data),
        content_type='application/json',
    )
    if send_request_id:
        header = {'X-Ya-Request-Id': uuid.uuid4().hex}
        request = RequestFactory().post(
            '',
            data=json.dumps(data),
            content_type='application/json',
            **header
        )
    response = yield exam.upload_result(request)
    assert response.status_code == expected_code
    if expected_code != 200:
        assert json.loads(response.content) == expected_response
    else:
        mongo_doc = yield db.exam_results.find_one({
            'license': data['license'],
        })
        if send_request_id:
            assert mongo_doc['request_id']
        assert not (yield db.exam_results.find_one({
            'license': data['license'],
            'updated_by': {'$exists': True}
        }))
        if 'profile-photo' in data:
            if data['profile-photo'] == 'return_warning':
                # Service should have returned 500
                resp = json.loads(response.content)
                assert resp['warning'] == {
                    'message': u'ERROR MESSAGE',
                    'code': 'driver_photo_service_fail'
                }
                assert 'id' in resp
            else:
                # Service should have returned 200
                assert driver_photos_called
