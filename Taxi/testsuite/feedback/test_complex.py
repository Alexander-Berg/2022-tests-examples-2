import json

import pytest


def call(taxi_feedback, path, request):
    return taxi_feedback.post(
        '/1.0/{}'.format(path),
        request,
        headers={'YaTaxi-Api-Key': 'feedback_apikey'},
    )


@pytest.mark.now('2018-08-10T21:01:30+0300')
@pytest.mark.config(
    FEEDBACK_SAVE_MODE='feedbacks',
    FEEDBACK_RETRIEVE_FROM_DBFEEDBACK=True,
    EXCLUDED_DRIVERS_PERSONAL_DATA_WRITE_MODE={
        '__default__': 'old_way',
        'feedback_save': 'both_fallback',
    },
)
def test_one(taxi_feedback, mockserver):
    @mockserver.json_handler('/personal/v1/driver_licenses/store')
    def mock_personal_store(request):
        request_json = json.loads(request.get_data())
        assert 'value' in request_json
        return {
            'id': request_json['value'] + 'ID',
            'value': request_json['value'],
        }

    retrieve_request = {'order_id': 'order_id', 'from_archive': False}
    response = call(taxi_feedback, 'retrieve', retrieve_request)
    assert response.status_code == 404

    save_request = {
        'id': 'user_id',
        'phone_id': '123456789012345678901234',
        'order_id': 'order_id',
        'rating': 3,
        'msg': 'message',
        'call_me': True,
        'app_comment': False,
        'created_time': '2018-08-10T21:01:30+0300',
        'choices': [{'type': 'low_rating_reason', 'value': 'rudedriver'}],
        'badges': [],
        'allow_overwrite': True,
        'order_city': 'Москва',
        'order_created_time': '2018-08-10T21:01:30+0300',
        'order_cancelled': False,
        'order_completed': False,
        'order_finished_for_client': True,
        'driver_license': 'AB0254',
    }
    response = call(taxi_feedback, 'save', save_request)
    assert response.status_code == 200
    assert response.json() == {}

    response = call(taxi_feedback, 'retrieve', retrieve_request)
    assert response.status_code == 200
    data = response.json()
    assert data == {
        'rating': 3,
        'msg': 'message',
        'call_me': True,
        'choices': [{'type': 'low_rating_reason', 'value': 'rudedriver'}],
        'is_after_complete': False,
        'app_comment': False,
    }

    wanted_push_request = {
        'id': 'user_id',
        'phone_id': '123456789012345678901234',
        'order_id': 'order_id',
        'order_created': '2018-08-09T16:31:13+0000',
        'order_due': '2018-08-09T16:31:14+0000',
        'order_completed': '2018-08-10T16:31:15+0000',
        'park_id': 'park_id',
    }
    response = call(taxi_feedback, 'wanted/push', wanted_push_request)
    assert response.status_code == 409

    wanted_push_request['switched_to_card'] = True
    response = call(taxi_feedback, 'wanted/push', wanted_push_request)
    assert response.status_code == 200
    assert response.json() == {}
