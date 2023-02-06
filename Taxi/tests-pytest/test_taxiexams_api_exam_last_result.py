from __future__ import unicode_literals

import json

from django.test import RequestFactory
import pytest

from taxiexams.api import exam


@pytest.mark.config(EXAMS_LAST_RESULT_RETURN_NULL=True)
@pytest.mark.parametrize(
    'data,expected_code,expected_response',
    [
        ({'bad_license': 'test_license_1'}, 200, {'result': None}),
        ({'driver_license': 123123}, 200, {'result': None}),
        ({'driver_license': 'test_license_123'}, 200, {'result': None}),
        ({'driver_license': 'test_license_3'}, 200, {'result': None}),
        ({'driver_license': 'test_license_1'}, 200, {'result': None}),
    ],
)
@pytest.inline_callbacks
@pytest.mark.asyncenv('blocking')
def test_upload_result_null(data, expected_code, expected_response):
    request = RequestFactory().post(
        '', data=json.dumps(data), content_type='application/json',
    )
    response = yield exam.get_last_result(request)
    assert response.status_code == expected_code
    assert json.loads(response.content) == expected_response


@pytest.mark.parametrize(
    'data,expected_code,expected_response',
    [
        (
            {'bad_license': 'test_license_1'},
            400,
            {
                'status': 'error',
                'message': '"driver_license": no field given',
                'code': 'invalid-input',
            },
        ),
        (
            {'driver_license': 123123},
            400,
            {
                'status': 'error',
                'message': '"driver_license": wrong type of field',
                'code': 'invalid-input',
            },
        ),
        (
            {'driver_license': 'test_license_123'},
            404,
            {
                'status': 'error',
                'message': 'There is no driver with this license number',
                'code': 'not-found',
            },
        ),
        ({'driver_license': 'test_license_3'}, 200, {'result': None}),
        ({'driver_license': 'test_license_1'}, 200, {'result': 4}),
    ],
)
@pytest.inline_callbacks
@pytest.mark.asyncenv('blocking')
def test_upload_result(data, expected_code, expected_response):
    request = RequestFactory().post(
        '', data=json.dumps(data), content_type='application/json',
    )
    response = yield exam.get_last_result(request)
    assert response.status_code == expected_code
    assert json.loads(response.content) == expected_response
