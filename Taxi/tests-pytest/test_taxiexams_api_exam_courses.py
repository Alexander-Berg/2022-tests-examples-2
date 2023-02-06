from __future__ import unicode_literals

import json
import pytest

from django.test import RequestFactory
from taxi import config

from taxiexams.api import exam


@pytest.inline_callbacks
@pytest.mark.asyncenv('blocking')
def test_post_method():
    request = RequestFactory().post('')
    response = yield exam.get_courses(request)
    assert response.status_code == 405
    assert json.loads(response.content) == {
        'status': 'error',
        'message': 'Request must be GET',
        'code': 'general'
    }


@pytest.inline_callbacks
@pytest.mark.asyncenv('blocking')
def test_get_method():
    request = RequestFactory().get('')
    response = yield exam.get_courses(request)
    assert response.status_code == 200
    mapper = yield config.EXTRA_EXAMS_INFO.get()
    expected_content = {
        'courses': [
            {
                'course': key,
                'description': val['description']
            }
            for key, val in mapper.iteritems()
        ]
    }
    assert json.loads(response.content) == expected_content
