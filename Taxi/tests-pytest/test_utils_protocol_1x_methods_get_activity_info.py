# -*- coding: utf-8 -*-
from utils.protocol_1x.methods import get_activity_info

import json
import mocks
import pytest


@pytest.mark.filldb(_fill=False)
@pytest.mark.config(DRIVER_POINTS_ACTION_COSTS={
    '__default__': {
        'a': [1, 1, 1]
    },
    u'Москва': {
        'c': [1, 2, 3],
        'n': [4, 5, 6]
    }
})
@pytest.mark.parametrize(
    'city, expected', [
        (
            u'Москва',
            {
                'assigned_canceled': [0, 0, 0],
                'canceled_manual': [4, 5, 6],
                'complete': [1, 2, 3]
            }
        ),
        (
            u'НесуществующийГород',
            {
                'assigned_canceled': [1, 1, 1],
                'canceled_manual': [0, 0, 0],
                'complete': [0, 0, 0]
            }
        )
    ]
)
@pytest.inline_callbacks
def test_get_activity_info_fetch(city, expected):
    m = get_activity_info.Method()
    activity_info = yield m.get_activity_info({}, city)
    assert activity_info == expected


@pytest.mark.filldb(_fill=False)
@pytest.mark.config(DRIVER_POINTS_ACTION_COSTS={
    '__default__': {
        'a': [1, 1, 1]
    },
    u'Москва': {
        'c': [1, 2, 3],
        'n': [4, 5, 6]
    }
})
@pytest.mark.parametrize(
    'args,expected_status,expected_response', [
        (
            {},
            400,
            {
                'status': 'error',
                'message': 'city parameter not found'
            }
        ),
        (
            {'city': ['НесуществующийГород']},
            200,
            {
                'assigned_canceled': [1, 1, 1],
                'canceled_manual': [0, 0, 0],
                'complete': [0, 0, 0]
            }
        ),
        (
            {'city': ['Москва']},
            200,
            {
                'assigned_canceled': [0, 0, 0],
                'canceled_manual': [4, 5, 6],
                'complete': [1, 2, 3]
            }
        )
    ]
)
@pytest.inline_callbacks
def test_get_activity_info_http(args, expected_status, expected_response):
    m = get_activity_info.Method()
    request = mocks.FakeRequest()
    request.args = args
    response = yield m.render_GET(request)
    assert request.response_code == expected_status
    assert response == json.dumps(expected_response)
