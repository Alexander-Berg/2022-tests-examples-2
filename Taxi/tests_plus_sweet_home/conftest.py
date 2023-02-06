import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from plus_sweet_home_plugins import *  # noqa: F403 F401

from tests_plus_sweet_home import constants


@pytest.fixture(autouse=True)
def mock_fast_prices(mockserver):
    @mockserver.json_handler('/fast-prices-notify/billing/user/state')
    def _mock_user_state(request):
        return {
            'activeIntervals': [
                {
                    'featureBundle': 'new-plus',
                    'end': '2021-01-07T18:21:26Z',
                    'orderType': 'native-auto-subscription',
                },
            ],
            'uid': constants.DEFAULT_UID,
        }

    @mockserver.json_handler('/fast-prices/billing/transitions')
    def _mock_transitions(request):
        return {
            'transitions': [
                {
                    'available': True,
                    'product': {
                        'id': constants.DEFAULT_PRODUCT_ID,
                        'vendor': 'YANDEX',
                    },
                    'transitionType': 'SUBMIT',
                },
            ],
        }
