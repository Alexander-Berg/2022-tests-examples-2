import json

import pytest


@pytest.fixture(scope='function', autouse=True)
def feedback_service(mockserver):
    @mockserver.json_handler('/feedback/1.0/retrieve')
    def mock_blackbox(request):
        assert request.headers['YaTaxi-Api-Key'] == 'feedback_apikey'
        data = json.loads(request.get_data())
        assert 'order_id' in data
        assert 'from_archive' in data
        assert 'order_due' in data
        return {
            'app_comment': False,
            'call_me': True,
            'is_after_complete': False,
            'choices': [
                {'type': 'badge', 'value': 'pleasantmusic'},
                {'type': 'low_rating_reason', 'value': 'rudedriver'},
            ],
            'msg': 'message',
            'rating': 3,
        }


@pytest.fixture(name='driver_ratings_v2', autouse=True)
def driver_ratings_v2(mockserver):
    @mockserver.json_handler('/driver-ratings/v2/driver/rating')
    def _get_rating_v2(_request):
        return {'unique_driver_id': 'id', 'rating': '4.6'}


@pytest.fixture(name='mock_personal', autouse=True)
def mock_personal(mockserver):
    class PersonalDataContext:
        def __init__(self):
            self.retrieve_use_count = 0

    context = PersonalDataContext()

    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def _phones_retrieve(request):
        context.retrieve_use_count += 1
        pd_id = request.json['id']
        if 'id_' in pd_id:
            return {'id': pd_id, 'value': pd_id.replace('id_', '')}
        else:
            return {}

    return context
