# pylint: disable=redefined-outer-name, import-only-modules
# flake8: noqa F401
import datetime
import json

import pytest

from tests_passenger_feedback.plugins.mock_order_core import mock_order_core
from tests_passenger_feedback.plugins.mock_order_core import order_core


def default_request() -> dict:
    return {
        'id': 'user_id',
        'phone_id': '123456789012345678901234',
        'personal_phone_id': 'p_123456789012345678901234',
        'order_id': 'bfda5489e2215d599abc840fd8f56a76',
        'reorder_id': 'reorder_id',
        'rating': 3,
        'msg': 'message',
        'call_me': True,
        'app_comment': False,
        'created_time': '2018-08-10T21:01:30+0300',
        'choices': [{'type': 'low_rating_reason', 'value': 'rudedriver'}],
        'badges': [],
        'order_city': 'Москва',
        'order_created_time': '2018-08-10T21:01:30+0300',
        'order_cancelled': False,
        'order_completed': False,
        'order_finished_for_client': True,
        'driver_license_pd_id': 'license_pd_id',
    }


@pytest.mark.now('2018-08-10T21:01:30+0300')
@pytest.mark.parametrize(
    'save_to_order',
    [
        pytest.param(
            True,
            marks=pytest.mark.config(PASSENGER_FEEDBACK_SAVE_TO_ORDER=True),
        ),
        pytest.param(
            False,
            marks=pytest.mark.config(PASSENGER_FEEDBACK_SAVE_TO_ORDER=False),
        ),
    ],
)
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
)
async def test_save(mongodb, feedback_save, save_to_order, order_core_api):
    request = default_request()
    request['order_id'] = '9b0ef3c5398b3e07b59f03110563479d'
    request['badges'] = [{'type': 'rating_reason', 'value': 'pleasantmusic'}]
    result = await feedback_save.call(request)
    if save_to_order:
        assert order_core_api.times_called == 1

    assert result.excluded_drivers_called

    expected_survey = (
        [{'question_id': 'q_1'}]
        if feedback_save.version == 'v1'
        else [{'answer_id': 'a_1', 'question_id': 'q_1'}]
    )

    assert result.feedback == {
        'created': datetime.datetime(2018, 8, 10, 18, 1, 30),
        'data_created': datetime.datetime(2018, 8, 10, 18, 1, 30),
        'order_created': datetime.datetime(2018, 8, 10, 18, 1, 30),
        '_id': '9b0ef3c5398b3e07b59f03110563479d',
        'reorder_id': 'reorder_id',
        'data': {
            'rating': 3,
            'call_me': True,
            'choices': [
                {'type': 'rating_reason', 'value': 'pleasantmusic'},
                {'type': 'low_rating_reason', 'value': 'rudedriver'},
            ],
            'app_comment': False,
            'is_after_complete': False,
            'msg': 'message',
        },
        'survey': expected_survey,
        'user_id': 'user_id',
        'user_phone_id': '123456789012345678901234',
        'wanted': False,
        'udid': 'udid00',
    }

    if save_to_order:
        assert result.order == {
            'feedback': {
                'app_comment': False,
                'rating': 3,
                'c': True,
                'iac': False,
                'ct': datetime.datetime(2018, 8, 10, 18, 1, 30),
                'msg': 'message',
                'choices': {
                    'low_rating_reason': ['rudedriver'],
                    'rating_reason': ['pleasantmusic'],
                },
            },
        }
    else:
        assert not result.order

    assert result.zendesk_ticket == {
        'msg': 'message',
        'rating': 3,
        'c': True,
        'app_comment': False,
        'choices': {
            'low_rating_reason': ['rudedriver'],
            'rating_reason': ['pleasantmusic'],
        },
    }


@pytest.mark.now('2018-08-10T21:01:30+0300')
@pytest.mark.config(PASSENGER_FEEDBACK_SAVE_TO_ORDER=True)
async def test_setting_order_data_with_order_core(
        feedback_save, order_core_api,
):
    request = default_request()
    request['order_id'] = '222ef3c5398b3e07b59f03110563479d'

    # mock get fields returns verison 1 in revision
    # (though in document itself it will be the same)
    # since we are using revision update with different versions should fail
    await feedback_save.call(request, expected_code=409)
    assert order_core_api.times_called == 1


@pytest.mark.parametrize(
    ['rating', 'excluded'],
    [(1, True), (2, True), (3, True), (4, False), (5, False)],
)
async def test_exclude_driver(feedback_save, rating, excluded, order_core_api):
    request = default_request()
    request['rating'] = rating
    result = await feedback_save.call(request)
    assert order_core_api.times_called == 1
    assert result.excluded_drivers_called == excluded


async def test_driver_missing_license_id(feedback_save, order_core_api):
    request = default_request()
    request.pop('driver_license_pd_id')
    result = await feedback_save.call(request)
    assert order_core_api.times_called == 1
    assert not result.excluded_drivers_called


async def test_feedback_idempotency(feedback_save, order_core_api):
    request = default_request()
    await feedback_save.call(request, expected_code=200)
    await feedback_save.call(request, expected_code=200)


async def test_feedback_no_tips(feedback_save, order_core_api):
    """
    We shouldn't change 'tips' in 'creditcard' field in dbs
    order & order_proc
    'order' already contains "creditcard.tips_perc_default" = 5
    """
    request = default_request()
    result = await feedback_save.call(request)
    assert order_core_api.times_called == 1

    assert result.order['creditcard'].get('tips') is None
    assert result.order['creditcard']['tips_perc_default'] == 5


async def test_feedback_cancel_reason_on_non_cancelled_order(feedback_save):
    request = default_request()
    request['choices'] = [{'type': 'cancelled_reason', 'value': 'longwait'}]
    await feedback_save.call(request, expected_code=400)


async def test_feedback_archive_order_proc(feedback_save, order_core_api):
    request = default_request()
    request['order_id'] = 'archive_order'
    await feedback_save.call(request, 409)


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
)
async def test_feedback_with_badges(feedback_save, order_core_api):

    request = default_request()
    request['rating'] = 4
    request['badges'] = [
        {'type': 'rating_reason', 'value': 'other'},
        {'type': 'rating_reason', 'value': 'pong'},
    ]
    result = await feedback_save.call(request)
    assert order_core_api.times_called == 1

    feedback = result.order.get('feedback')
    assert feedback is not None
    assert feedback['c']
    assert feedback['rating'] == 4
    assert feedback['choices']['low_rating_reason'] == ['rudedriver']
    assert set(feedback['choices']['rating_reason']) == {'other', 'pong'}
    assert not feedback['iac']
    assert feedback['msg'] == 'message'


@pytest.mark.now('2018-08-10T21:01:30+0300')
@pytest.mark.config(PASSENGER_FEEDBACK_SAVE_TO_ORDER=False)
async def test_save_wanted(feedback_save):
    request = default_request()
    request['order_id'] = 'wanted_order'
    request.pop('reorder_id')
    result = await feedback_save.call(request)

    expected_survey = (
        [{'question_id': 'q_1'}]
        if feedback_save.version == 'v1'
        else [{'answer_id': 'a_1', 'question_id': 'q_1'}]
    )

    assert result.feedback == {
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
        'survey': expected_survey,
        'order_due': datetime.datetime(2017, 1, 1, 0, 0),
        'user_phone_id': '123456789012345678901234',
        'park_id': 'park_id',
        'order_completed': datetime.datetime(2017, 1, 1, 0, 0),
        '_id': 'wanted_order',
        'data_created': datetime.datetime(2018, 8, 10, 18, 1, 30),
        'wanted': False,
    }


@pytest.mark.now('2018-08-10T21:01:30+0300')
async def test_save_null_choices(feedback_save, order_core_api):
    request = default_request()
    request['choices'] = []
    await feedback_save.call(request)
    assert order_core_api.times_called == 1


def make_update_rating_exp_mark(enabled=False):
    value = {'enabled': enabled}

    return {
        'match': {'predicate': {'type': 'true'}, 'enabled': True},
        'name': 'update_selected_class_after_upgrade',
        'consumers': ['passenger-feedback/v1/feedback'],
        'clauses': [
            {'title': '', 'value': value, 'predicate': {'type': 'true'}},
        ],
    }


@pytest.mark.now('2018-08-10T21:01:30+0300')
@pytest.mark.parametrize(
    'is_exp_enabled',
    [
        pytest.param(False, id='No exp'),
        pytest.param(
            False,
            marks=pytest.mark.experiments3(
                **make_update_rating_exp_mark(enabled=False),
            ),
            id='Exp disabled',
        ),
        pytest.param(
            True,
            marks=pytest.mark.experiments3(
                **make_update_rating_exp_mark(enabled=True),
            ),
            id='Exp enabled',
        ),
    ],
)
@pytest.mark.parametrize(
    'is_order_finished_for_client',
    [
        pytest.param(False, id='Order not finished'),
        pytest.param(True, id='Order finished'),
    ],
)
@pytest.mark.parametrize(
    'rating',
    [
        pytest.param(None, id='No rating'),
        pytest.param(1, id='Low rating'),
        pytest.param(5, id='High rating'),
    ],
)
async def test_user_state_update_rating(
        feedback_save,
        mockserver,
        is_exp_enabled: bool,
        is_order_finished_for_client: bool,
        rating: int,
        order_core_api,
):
    request = default_request()
    request['order_finished_for_client'] = is_order_finished_for_client
    request['rating'] = rating
    request['order_zone'] = 'moscow'

    @mockserver.json_handler(
        '/user-state/internal/user-state/v1/update-order-rating',
    )
    def mock_user_state_update_rating(inner_request):
        request_json = json.loads(inner_request.get_data())
        assert request_json == {
            'order_id': request['order_id'],
            'rating': request['rating'],
            'is_order_completed': request['order_finished_for_client'],
        }
        return {}

    await feedback_save.call(request)
    assert order_core_api.times_called == 1

    assert mock_user_state_update_rating.times_called == (
        1 if is_exp_enabled and rating is not None else 0
    )


@pytest.mark.now('2018-08-10T21:01:30+0300')
@pytest.mark.experiments3(**make_update_rating_exp_mark(enabled=True))
async def test_user_state_update_rating_error(
        feedback_save, mockserver, order_core_api,
):
    request = default_request()
    request['order_finished_for_client'] = True
    request['order_zone'] = 'moscow'

    @mockserver.json_handler(
        '/user-state/internal/user-state/v1/update-order-rating',
    )
    def mock_user_state_update_rating(inner_request):
        return mockserver.make_response('fail', status=500)

    # 200 asserted inside call()
    await feedback_save.call(request, 200)
    assert order_core_api.times_called == 1

    assert mock_user_state_update_rating.times_called == 1


def get_current_questions_db(pgsql):
    cursor = pgsql['passenger_feedback'].cursor()
    cursor.execute(
        (
            f'SELECT udid, current_question_id, answer_ids, answer_values'
            f' FROM passenger_feedback.current_questions'
        ),
    )
    return list(cursor)


@pytest.mark.parametrize('feedback_save', ['v2'], indirect=True)
@pytest.mark.pgsql('passenger_feedback', files=['pg_save_feedback.sql'])
@pytest.mark.now('2018-08-10T21:01:30+0300')
@pytest.mark.config(
    PASSENGER_FEEDBACK_SURVEY_ANSWER_DESCRIPTIONS={
        'a_1': 1,
        'a_2': 0,
        'a_3': 1,
        'a_4': 0,
    },
)
@pytest.mark.parametrize(
    ['order_id', 'expected_cur_questions_db'],
    [
        (
            '000ef3c5398b3e07b59f03110563479d',
            [('udid00', 'q_1', ['negative', 'a_2'], [0, 0])],
        ),
        (
            '111ef3c5398b3e07b59f03110563479d',
            [
                ('udid00', 'q_1', ['negative'], [0]),
                ('udid01', 'q_1', ['a_2'], [0]),
            ],
        ),
    ],
    ids=['simple', 'new_question'],
)
async def test_smart_question_picker_save_answers(
        feedback_save,
        pgsql,
        order_id,
        expected_cur_questions_db,
        order_core_api,
):
    expected_initial_db = [('udid00', 'q_1', ['negative'], [0])]
    assert expected_initial_db == get_current_questions_db(pgsql)

    request = default_request()
    request['order_id'] = order_id
    request['survey'] = [{'question_id': 'q_1', 'answer_id': 'a_2'}]
    await feedback_save.call(
        request, expected_code=200, has_survey_result=False,
    )
    assert order_core_api.times_called == 1

    assert expected_cur_questions_db == get_current_questions_db(pgsql)
