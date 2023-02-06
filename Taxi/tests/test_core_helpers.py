from context import settings
from context.settings import init_settings


def test_get_queue_for_user():
    settings._settings = None
    extra_test_settings = {
        'SQS': {
            'ACCESS_KEY': 'mock',
            'SESSION_TOKEN': 'mock',
            'ENDPOINT': 'mock',
        }
    }
    init_settings(extra_test_settings)

    from core.helpers import get_queue_for_user

    assert 'etl' == get_queue_for_user('robot-taxi-stat')
    assert 'analysts' == get_queue_for_user('other-robot')
