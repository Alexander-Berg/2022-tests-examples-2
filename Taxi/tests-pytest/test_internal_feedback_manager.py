import pytest

from taxi.internal import dbh
from taxi.internal import feedback_manager


OLD_STYLE_FEEDBACK = {
    'app_comment': False,
    'rating': 2,
    'msg': 'message',
    'choices': {
        'low_rating_reason': ['rudedriver', 'test'],
        'rating_reason': ['bad_driving'],
    },
    'c': True,
    'iac': True,
}


@pytest.mark.parametrize('input_obj,new_style', [
    (
        OLD_STYLE_FEEDBACK, False,
    ),
    (
        dbh.order_proc.Doc(
            {'order': {'feedback': OLD_STYLE_FEEDBACK}}
        ).order.feedback, False,
    ),
    (
        {  # new style
            'app_comment': False,
            'rating': 2,
            'msg': 'message',
            'choices': [
                {'type': 'low_rating_reason', 'value': 'test'},
                {'type': 'low_rating_reason', 'value': 'rudedriver'},
                {'type': 'rating_reason', 'value': 'bad_driving'},
            ],
            'call_me': True,
            'is_after_complete': True,
        }, True,
    )
])
def test_feedback_storage(input_obj, new_style):
    feedback = feedback_manager.FeedbackStorage(input_obj, new_style=new_style)

    assert feedback.choices == OLD_STYLE_FEEDBACK['choices']
    assert feedback.call_requested == OLD_STYLE_FEEDBACK['c']
    assert feedback.rating == OLD_STYLE_FEEDBACK['rating']
    assert feedback.comment == OLD_STYLE_FEEDBACK['msg']
    assert feedback.app_comment == OLD_STYLE_FEEDBACK['app_comment']
    assert feedback.is_after_complete == OLD_STYLE_FEEDBACK['iac']

    feedback = {
        dbh.orders.Doc.feedback.comment.key: feedback.comment or '',
        dbh.orders.Doc.feedback.choices.key: feedback.choices or {},
        dbh.orders.Doc.feedback.call_requested.key: feedback.call_requested or False,
        dbh.orders.Doc.feedback.rating.key: feedback.rating or '',
    }
    assert feedback == {
        'rating': OLD_STYLE_FEEDBACK['rating'],
        'msg': OLD_STYLE_FEEDBACK['msg'],
        'choices': OLD_STYLE_FEEDBACK['choices'],
        'c': OLD_STYLE_FEEDBACK['c'],
    }


@pytest.mark.parametrize('data,expected_result,new_style', [
    (
        OLD_STYLE_FEEDBACK,
        {
            'app_comment': False,
            'rating': 2,
            'msg': 'message',
            'choices': {
                'low_rating_reason': ['rudedriver', 'test'],
                'rating_reason': ['bad_driving'],
            },
            'call_me': True,
            'is_after_complete': True,
        },
        False,
    ),
    (
        {  # new style
            'rating': 2,
            'msg': 'message',
            'choices': [
                {'type': 'low_rating_reason', 'value': 'rudedriver'},
                {'type': 'low_rating_reason', 'value': 'test'},
                {'type': 'rating_reason', 'value': 'bad_driving'},
            ],
            'call_me': True,
            'is_after_complete': True,
        },
        {
            'rating': 2,
            'msg': 'message',
            'choices': {
                'low_rating_reason': ['rudedriver', 'test'],
                'rating_reason': ['bad_driving'],
            },
            'call_me': True,
            'is_after_complete': True,
        },
        True,
    ),
    (
        None, {}, True,
    ),
    (
        None, {}, False,
    ),
])
def test_map_feedback_data(data, expected_result, new_style):
    assert feedback_manager._map_feedback_data(
        data, input_style=(feedback_manager.NEW_STYLE if new_style
                           else feedback_manager.OLD_STYLE)
    ) == expected_result
