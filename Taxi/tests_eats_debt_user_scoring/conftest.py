# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest

from eats_debt_user_scoring_plugins import *  # noqa: F403 F401


@pytest.fixture(name='eats_core_eater')
def eats_core_eater(mockserver):
    @mockserver.json_handler('/eats-core-eater/find-by-passport-uid')
    def _mock_eats_core(json_request):
        uid = json_request.json['passport_uid']
        return {
            'eater': {
                'id': f'eater-{uid}',
                'uuid': 'eater-uuid',
                'passport_uid': uid,
                'created_at': '2019-12-31T10:59:59+03:00',
                'updated_at': '2019-12-31T10:59:59+03:00',
            },
        }


@pytest.fixture(name='eats_order_stats')
def eats_order_stats(mockserver):
    def fixture(counters=None, status_code: int = 200):
        @mockserver.json_handler(
            '/eats-order-stats/internal/eats-order-stats/v1/orders',
        )
        def _mock_eats_order_stats(json_request):
            eater_id = json_request.json['identities'][0]['value']
            stats = counters or []
            return mockserver.make_response(
                status=status_code,
                json={
                    'data': [
                        {
                            'identity': {
                                'type': 'eater_id',
                                'value': eater_id,
                            },
                            'counters': stats,
                        },
                    ],
                },
            )

    return fixture


@pytest.fixture(name='mock_saturn')
def _mock_saturn(mockserver):
    def _inner(status: str, status_code: int = 200):
        # pylint: disable=invalid-name
        @mockserver.json_handler('/saturn/api/v1/eda/search')
        def eda_search_handler(request):
            return mockserver.make_response(
                status=status_code,
                json={
                    'reqid': 'identity',
                    'puid': 98765,
                    'score': 45.78,
                    'score_percentile': 90,
                    'formula_id': 'formula_123',
                    'status': status,
                },
            )

        return eda_search_handler

    return _inner


@pytest.fixture(name='mock_debt_collector')
def _mock_debt_collector(mockserver):
    def _inner(status_code: int = 200, debts=None):
        if debts is None:
            debts = []

        # pylint: disable=invalid-name
        @mockserver.json_handler('/debt-collector/v1/debts/list')
        def debts_list_handler(request):
            return mockserver.make_response(
                status=status_code, json={'debts': debts},
            )

        return debts_list_handler

    return _inner
