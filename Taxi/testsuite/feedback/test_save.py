import datetime
import json

import bson
import pytest


def call_save(taxi_feedback, request):
    return taxi_feedback.post(
        '/1.0/save', request, headers={'YaTaxi-Api-Key': 'feedback_apikey'},
    )


@pytest.mark.now('2018-08-10T21:01:30+0300')
@pytest.mark.config(
    FEEDBACK_BADGES_MAPPING={
        'feedback_badges': [
            {
                'name': 'pleasantmusic',
                'label': 'feedback_badges.pleasantmusic',
                'filters': {'tariffs': ['default']},
            },
        ],
        'feedback_rating_mapping': [
            {
                'rating': 3,
                'choice_title': 'feedback_badges.rating_title_5',
                'badges': ['pleasantmusic'],
            },
        ],
    },
    EXCLUDED_DRIVERS_PERSONAL_DATA_WRITE_MODE={'__default__': 'old_way'},
)
@pytest.mark.parametrize('user_id', ['user_id', 'crossdevice_user_id'])
def test_save(taxi_feedback, db, mock_stq_agent, user_id, mockserver):
    @mockserver.json_handler('/personal/v1/driver_licenses/store')
    def mock_personal_store(request):
        request_json = json.loads(request.get_data())
        assert 'value' in request_json
        return {
            'id': request_json['value'] + 'ID',
            'value': request_json['value'],
        }

    request = {
        'id': user_id,
        'phone_id': '123456789012345678901234',
        'order_id': 'order_id',
        'rating': 3,
        'msg': 'message',
        'call_me': True,
        'app_comment': False,
        'created_time': '2018-08-10T21:01:30+0300',
        'choices': [{'type': 'low_rating_reason', 'value': 'rudedriver'}],
        'badges': [{'type': 'badge', 'value': 'pleasantmusic'}],
        'allow_overwrite': True,
        'order_city': 'Москва',
        'order_created_time': '2018-08-10T21:01:30+0300',
        'order_cancelled': False,
        'order_completed': False,
        'order_finished_for_client': True,
        'driver_license': 'AB0254',
    }
    response = call_save(taxi_feedback, request)
    assert response.status_code == 200
    data = response.json()
    assert data == {}

    order = db.orders.find_one('order_id')
    order.pop('updated')
    assert order == {
        '_id': 'order_id',
        '_shard_id': 0,
        'feedback': {
            'app_comment': False,
            'rating': 3,
            'c': True,
            'iac': False,
            'ct': datetime.datetime(2018, 8, 10, 18, 1, 30),
            'msg': 'message',
            'choices': {
                'low_rating_reason': ['rudedriver'],
                'badge': ['pleasantmusic'],
            },
        },
    }
    proc = db.order_proc.find_one('order_id')
    proc.pop('updated')
    assert proc == {
        '_id': 'order_id',
        '_shard_id': 0,
        'order': {
            'feedback': {
                'app_comment': False,
                'rating': 3,
                'c': True,
                'iac': False,
                'ct': datetime.datetime(2018, 8, 10, 18, 1, 30),
                'msg': 'message',
                'choices': {
                    'low_rating_reason': ['rudedriver'],
                    'badge': ['pleasantmusic'],
                },
            },
        },
    }

    bad_order = db.excluded_drivers.find_one({'o': 'order_id'})
    bad_order.pop('_id')
    assert bad_order == {
        'd': 'AB0254',
        'i': bson.ObjectId('123456789012345678901234'),
        'o': 'order_id',
        'r': 'bad_feedback',
        't': datetime.datetime(2018, 9, 9, 18, 1, 30),
    }

    stq_tasks = mock_stq_agent.get_tasks('zendesk_ticket')
    assert len(stq_tasks) == 1

    report_stq_task = stq_tasks[0]

    assert report_stq_task.args[:-1] == [
        'order_id',
        {
            'msg': 'message',
            'rating': 3,
            'c': True,
            'app_comment': False,
            'choices': {
                'low_rating_reason': ['rudedriver'],
                'badge': ['pleasantmusic'],
            },
        },
    ]

    assert len(report_stq_task.kwargs) == 1
    assert 'log_extra' in report_stq_task.kwargs

    assert report_stq_task.is_urgent


# Modified tests from protocol test_feedback below


def test_naive(taxi_feedback, db):
    request = {
        'order_finished_for_client': False,
        'rating': 4,
        'call_me': True,
        'order_id': 'order_id',
        'order_created_time': '2018-08-10T21:01:30+0300',
        'order_cancelled': False,
        'phone_id': '5714f45e98956f06baaae3d4',
        'choices': [{'type': 'low_rating_reason', 'value': 'rudedriver'}],
        'created_time': '2018-08-17T10:09:22+0000',
        'driver_license': 'AB0254',
        'app_comment': False,
        'order_completed': False,
        'allow_overwrite': True,
        'order_zone': 'moscow',
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'badges': [],
        'msg': 'hello world',
    }
    response = call_save(taxi_feedback, request)
    assert response.status_code == 200
    data = response.json()
    assert data == {}

    proc = db.order_proc.find_one({'_id': 'order_id'})
    feedback = proc.get('order').get('feedback')
    assert feedback is not None
    assert feedback['c']
    assert feedback['rating'] == 4
    assert feedback['choices']['low_rating_reason'] == ['rudedriver']
    assert not feedback['iac']
    assert feedback['msg'] == 'hello world'
    order = db.orders.find_one({'_id': 'order_id'})
    assert order.get('feedback') == feedback

    # once more, without overwrite flag
    request['allow_overwrite'] = False
    response = call_save(taxi_feedback, request)
    assert response.status_code == 409


def test_feedback_no_tips(taxi_feedback, db):
    """
    We shouldn't change 'tips' in 'creditcard' field in dbs
    order & order_proc
    'order' already contains "creditcard.tips_perc_default" = 5
    """
    request = {
        'order_finished_for_client': False,
        'rating': 4,
        'call_me': False,
        'order_id': '8c83b49edb274ce0992f337061047375',
        'order_created_time': '2018-08-10T21:01:30+0300',
        'order_cancelled': False,
        'phone_id': '5714f45e98956f06baaae3d4',
        'choices': [{'type': 'low_rating_reason', 'value': 'rudedriver'}],
        'created_time': '2018-08-17T10:33:49+0000',
        'driver_license': 'AB0254',
        'app_comment': False,
        'order_completed': False,
        'allow_overwrite': True,
        'order_zone': 'moscow',
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'badges': [],
        'msg': 'hello world',
    }
    response = call_save(taxi_feedback, request)
    assert response.status_code == 200
    data = response.json()
    assert data == {}

    proc = db.order_proc.find_one({'_id': '8c83b49edb274ce0992f337061047375'})
    feedback = proc.get('order').get('feedback')
    assert proc.get('creditcard') is None
    order = db.orders.find_one({'_id': '8c83b49edb274ce0992f337061047375'})
    assert order.get('feedback') == feedback
    assert order['creditcard'].get('tips') is None
    assert order['creditcard']['tips_perc_default'] == 5


@pytest.mark.config(
    SUPPORTED_FEEDBACK_CHOICES={
        '__default__': {'type': ['value']},
        'moscow': {'type': []},
    },
)
def test_feedback_nochoice_city_nodefault(taxi_feedback):
    request = {
        'order_finished_for_client': False,
        'rating': 4,
        'call_me': False,
        'order_id': '8c83b49edb274ce0992f337061047375',
        'order_created_time': '2018-08-10T21:01:30+0300',
        'order_cancelled': False,
        'phone_id': '5714f45e98956f06baaae3d4',
        'choices': [{'type': 'type', 'value': 'value'}],
        'created_time': '2018-08-17T10:43:38+0000',
        'driver_license': 'AB0254',
        'app_comment': False,
        'order_completed': False,
        'allow_overwrite': True,
        'order_zone': 'moscow',
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'badges': [],
        'msg': 'hello world',
    }
    response = call_save(taxi_feedback, request)
    assert response.status_code == 404

    request['order_zone'] = 'notmoscow'
    response = call_save(taxi_feedback, request)
    assert response.status_code == 200


def test_feedback_cancel_reason_on_non_cancelled_order(taxi_feedback):
    request = {
        'order_finished_for_client': False,
        'rating': 4,
        'call_me': False,
        'order_id': '8c83b49edb274ce0992f337061047375',
        'order_created_time': '2018-08-10T21:01:30+0300',
        'order_cancelled': False,
        'phone_id': '5714f45e98956f06baaae3d4',
        'choices': [{'type': 'cancelled_reason', 'value': 'longwait'}],
        'created_time': '2018-08-17T10:48:20+0000',
        'driver_license': 'AB0254',
        'app_comment': False,
        'order_completed': False,
        'allow_overwrite': True,
        'order_zone': 'moscow',
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'badges': [],
        'msg': 'hello world',
    }
    response = call_save(taxi_feedback, request)
    assert response.status_code == 400


@pytest.mark.filldb(orders='archive', order_proc='archive')
def test_feedback_archive_order_proc(taxi_feedback):
    request = {
        'order_finished_for_client': False,
        'rating': 4,
        'call_me': False,
        'order_id': '8c83b49edb274ce0992f337061047375',
        'order_created_time': '2018-08-10T21:01:30+0300',
        'order_cancelled': False,
        'phone_id': '5714f45e98956f06baaae3d4',
        'choices': [{'type': 'low_rating_reason', 'value': 'rudedriver'}],
        'created_time': '2018-08-17T10:33:49+0000',
        'driver_license': 'AB0254',
        'app_comment': False,
        'order_completed': False,
        'allow_overwrite': True,
        'order_zone': 'moscow',
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'badges': [],
        'msg': 'hello world',
    }
    response = call_save(taxi_feedback, request)
    assert response.status_code == 409


@pytest.mark.user_experiments('five_stars')
@pytest.mark.config(
    FEEDBACK_BADGES_MAPPING={
        'feedback_badges': [
            {
                'name': 'pleasantmusic',
                'label': 'feedback_badges.pleasantmusic',
                'filters': {'tariffs': ['default']},
            },
            {
                'name': 'pong',
                'label': 'feedback_badges.pong',
                'filters': {'tariffs': ['default']},
            },
            {
                'name': 'other',
                'label': 'feedback_badges.other',
                'image': {
                    'active_image_tag': 'tag.other',
                    'inactive_image_tag': 'tag.inother',
                },
                'filters': {'tariffs': ['default']},
            },
        ],
        'feedback_rating_mapping': [
            {'rating': 1, 'badges': []},
            {'rating': 2, 'badges': []},
            {'rating': 3, 'badges': []},
            {
                'rating': 4,
                'choice_title': 'feedback_badges.rating_title_4',
                'badges': ['pong', 'other'],
            },
            {
                'rating': 5,
                'choice_title': 'feedback_badges.rating_title_5',
                'badges': ['pleasantmusic', 'other'],
            },
        ],
    },
    EXCLUDED_DRIVERS_PERSONAL_DATA_WRITE_MODE={'__default__': 'old_way'},
)
def test_feedback_with_badges(taxi_feedback, db):
    request = {
        'order_finished_for_client': False,
        'rating': 4,
        'call_me': True,
        'order_id': '8c83b49edb274ce0992f337061047375',
        'order_created_time': '2018-08-10T21:01:30+0300',
        'order_cancelled': False,
        'phone_id': '5714f45e98956f06baaae3d4',
        'choices': [{'type': 'low_rating_reason', 'value': 'rudedriver'}],
        'created_time': '2018-08-17T11:32:43+0000',
        'driver_license': 'AB0254',
        'app_comment': False,
        'order_completed': False,
        'allow_overwrite': True,
        'order_zone': 'moscow',
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'badges': [
            {'type': 'rating_reason', 'value': 'other'},
            {'type': 'rating_reason', 'value': 'pong'},
        ],
        'msg': 'hello world',
    }

    response = call_save(taxi_feedback, request)
    assert response.status_code == 200
    data = response.json()
    assert data == {}

    proc = db.order_proc.find_one({'_id': '8c83b49edb274ce0992f337061047375'})
    feedback = proc.get('order').get('feedback')
    assert feedback is not None
    assert feedback['c']
    assert feedback['rating'] == 4
    assert feedback['choices']['low_rating_reason'] == ['rudedriver']
    assert feedback['choices']['rating_reason'] == ['other', 'pong']
    assert not feedback['iac']
    assert feedback['msg'] == 'hello world'
    order = db.orders.find_one({'_id': '8c83b49edb274ce0992f337061047375'})
    assert order.get('feedback') == feedback


@pytest.mark.now('2018-08-10T21:01:30+0300')
@pytest.mark.config(
    FEEDBACK_SAVE_MODE='order_proc_feedbacks',
    EXCLUDED_DRIVERS_PERSONAL_DATA_WRITE_MODE={'__default__': 'both_fallback'},
)
def test_save_to_dbfeedback(taxi_feedback, db, mock_stq_agent, mockserver):
    @mockserver.json_handler('/personal/v1/driver_licenses/store')
    def mock_personal_store(request):
        request_json = json.loads(request.get_data())
        assert 'value' in request_json
        return {
            'id': request_json['value'] + 'ID',
            'value': request_json['value'],
        }

    request = {
        'id': 'user_id',
        'phone_id': '123456789012345678901234',
        'order_id': 'order_id',
        'reorder_id': 'reorder_id',
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
    response = call_save(taxi_feedback, request)
    assert response.status_code == 200
    data = response.json()
    assert data == {}

    order = db.orders.find_one('order_id')
    order.pop('updated')
    assert order == {
        '_id': 'order_id',
        '_shard_id': 0,
        'feedback': {
            'app_comment': False,
            'rating': 3,
            'c': True,
            'iac': False,
            'ct': datetime.datetime(2018, 8, 10, 18, 1, 30),
            'msg': 'message',
            'choices': {'low_rating_reason': ['rudedriver']},
        },
    }
    proc = db.order_proc.find_one('order_id')
    proc.pop('updated')
    assert proc == {
        '_id': 'order_id',
        '_shard_id': 0,
        'order': {
            'feedback': {
                'app_comment': False,
                'rating': 3,
                'c': True,
                'iac': False,
                'ct': datetime.datetime(2018, 8, 10, 18, 1, 30),
                'msg': 'message',
                'choices': {'low_rating_reason': ['rudedriver']},
            },
        },
    }
    feedback = db.feedbacks.find_one('order_id')
    feedback.pop('updated')
    feedback.pop('data_updated')
    assert feedback == {
        'created': datetime.datetime(2018, 8, 10, 18, 1, 30),
        'data_created': datetime.datetime(2018, 8, 10, 18, 1, 30),
        'order_created': datetime.datetime(2018, 8, 10, 18, 1, 30),
        '_id': 'order_id',
        'reorder_id': 'reorder_id',
        'data': {
            'rating': 3,
            'call_me': True,
            'choices': [{'type': 'low_rating_reason', 'value': 'rudedriver'}],
            'app_comment': False,
            'is_after_complete': False,
            'msg': 'message',
        },
        'user_id': 'user_id',
        'user_phone_id': '123456789012345678901234',
        'wanted': False,
    }

    bad_order = db.excluded_drivers.find_one({'o': 'order_id'})
    bad_order.pop('_id')
    assert bad_order == {
        'd': 'AB0254',
        'p_id': 'AB0254ID',
        'i': bson.ObjectId('123456789012345678901234'),
        'o': 'order_id',
        'r': 'bad_feedback',
        't': datetime.datetime(2018, 9, 9, 18, 1, 30),
    }

    report_stq_task = mock_stq_agent.get_tasks('zendesk_ticket')[0]

    assert len(report_stq_task.kwargs) == 1
    assert 'log_extra' in report_stq_task.kwargs

    assert report_stq_task.args[:-1] == [
        'order_id',
        {
            'msg': 'message',
            'rating': 3,
            'c': True,
            'app_comment': False,
            'choices': {'low_rating_reason': ['rudedriver']},
        },
    ]

    assert report_stq_task.is_urgent


@pytest.mark.now('2018-08-10T21:01:30+0300')
@pytest.mark.config(
    FEEDBACK_SAVE_MODE='feedbacks',
    EXCLUDED_DRIVERS_PERSONAL_DATA_WRITE_MODE={
        '__default__': 'old_way',
        'feedback_save': 'both_fallback',
    },
)
def test_save_to_dbfeedback_overwrites(mockserver, taxi_feedback, db):
    @mockserver.json_handler('/personal/v1/driver_licenses/store')
    def mock_personal_store(request):
        request_json = json.loads(request.get_data())
        assert 'value' in request_json
        return {
            'id': request_json['value'] + 'ID',
            'value': request_json['value'],
        }

    request = {
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
    response = call_save(taxi_feedback, request)
    assert response.status_code == 200
    data = response.json()
    assert data == {}

    # owerwrite with newer version
    request['created_time'] = '2018-09-10T21:01:30+0300'
    request['rating'] = 1
    response = call_save(taxi_feedback, request)
    assert response.status_code == 200
    feedback = db.feedbacks.find_one('order_id')
    assert feedback['data']['rating'] == 1
    assert feedback['data_created'] == datetime.datetime(
        2018, 9, 10, 18, 1, 30,
    )

    # do not overwrite with older version
    request['created_time'] = '2018-07-10T21:01:30+0300'
    request['rating'] = 5
    response = call_save(taxi_feedback, request)
    assert response.status_code == 409
    assert db.feedbacks.find_one('order_id') == feedback

    # do not overwrite as per parameter
    request['allow_overwrite'] = False
    request['created_time'] = '2018-10-10T21:01:30+0300'
    request['rating'] = 5
    response = call_save(taxi_feedback, request)
    assert response.status_code == 409
    assert db.feedbacks.find_one('order_id') == feedback


@pytest.mark.now('2018-08-10T21:01:30+0300')
@pytest.mark.config(
    FEEDBACK_SAVE_MODE='order_proc',
    EXCLUDED_DRIVERS_PERSONAL_DATA_WRITE_MODE={
        '__default__': 'old_way',
        'feedback_save': 'both_no_fallback',
    },
)
def test_save_to_proc_overwrites(mockserver, taxi_feedback, db):
    @mockserver.json_handler('/personal/v1/driver_licenses/store')
    def mock_personal_store(request):
        request_json = json.loads(request.get_data())
        assert 'value' in request_json
        return {
            'id': request_json['value'] + 'ID',
            'value': request_json['value'],
        }

    request = {
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
    response = call_save(taxi_feedback, request)
    assert response.status_code == 200
    data = response.json()
    assert data == {}

    # owerwrite with newer version
    request['created_time'] = '2018-09-10T21:01:30+0300'
    request['rating'] = 1
    response = call_save(taxi_feedback, request)
    assert response.status_code == 200
    feedback = db.order_proc.find_one('order_id')['order']['feedback']
    assert feedback['rating'] == 1
    assert feedback['ct'] == datetime.datetime(2018, 9, 10, 18, 1, 30)
    assert db.orders.find_one('order_id')['feedback'] == feedback

    # do not overwrite with older version
    request['created_time'] = '2018-07-10T21:01:30+0300'
    request['rating'] = 5
    response = call_save(taxi_feedback, request)
    assert response.status_code == 409
    assert db.order_proc.find_one('order_id')['order']['feedback'] == feedback

    # do not overwrite as per parameter
    request['allow_overwrite'] = False
    request['created_time'] = '2018-10-10T21:01:30+0300'
    request['rating'] = 5
    response = call_save(taxi_feedback, request)
    assert response.status_code == 409
    assert db.order_proc.find_one('order_id')['order']['feedback'] == feedback


@pytest.mark.now('2018-08-10T21:01:30+0300')
@pytest.mark.config(
    FEEDBACK_SAVE_MODE='feedbacks',
    EXCLUDED_DRIVERS_PERSONAL_DATA_WRITE_MODE={
        '__default__': 'old_way',
        'feedback_save': 'both_fallback',
    },
)
def test_save_wanted(mockserver, taxi_feedback, db):
    @mockserver.json_handler('/personal/v1/driver_licenses/store')
    def mock_personal_store(request):
        request_json = json.loads(request.get_data())
        assert 'value' in request_json
        return {
            'id': request_json['value'] + 'ID',
            'value': request_json['value'],
        }

    request = {
        'id': 'user_id',
        'phone_id': '123456789012345678901234',
        'order_id': 'wanted_order',
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
    response = call_save(taxi_feedback, request)
    assert response.status_code == 200
    data = response.json()
    assert data == {}

    feedback = db.feedbacks.find_one('wanted_order')
    feedback.pop('updated')
    feedback.pop('data_updated')
    assert feedback == {
        'user_id': 'user_id',
        'created': datetime.datetime(2017, 1, 1, 0, 0),
        'order_created': datetime.datetime(2018, 8, 10, 18, 1, 30),
        'data': {
            'rating': 3,
            'call_me': True,
            'choices': [{'type': 'low_rating_reason', 'value': 'rudedriver'}],
            'app_comment': False,
            'is_after_complete': False,
            'msg': 'message',
        },
        'order_due': datetime.datetime(2017, 1, 1, 0, 0),
        'user_phone_id': '123456789012345678901234',
        'park_id': 'park_id',
        'order_completed': datetime.datetime(2017, 1, 1, 0, 0),
        '_id': 'wanted_order',
        'data_created': datetime.datetime(2018, 8, 10, 18, 1, 30),
        'wanted': False,
    }


@pytest.mark.now('2018-08-10T21:01:30+0300')
@pytest.mark.config(
    FEEDBACK_SAVE_MODE='order_proc_feedbacks',
    EXCLUDED_DRIVERS_PERSONAL_DATA_WRITE_MODE={
        '__default__': 'both_no_fallback',
    },
)
def test_save_personal_error(taxi_feedback, db, mock_stq_agent, mockserver):
    @mockserver.json_handler('/personal/v1/driver_licenses/store')
    def mock_personal_store(request):
        request_json = json.loads(request.get_data())
        assert 'value' in request_json
        return mockserver.make_response('', 500)

    request = {
        'id': 'user_id',
        'phone_id': '123456789012345678901234',
        'order_id': 'order_id',
        'reorder_id': 'reorder_id',
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
    response = call_save(taxi_feedback, request)
    assert response.status_code == 500
