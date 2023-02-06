# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from driver_ratings_plugins import *  # noqa: F403 F401
import pytest


class DriverRatingsStorageContext:
    def __init__(self):
        self.events = []

    def set_events(self, events):
        self.events = events


@pytest.fixture(name='driver_ratings_storage', autouse=True)
def _driver_ratings_request(mockserver):
    context = DriverRatingsStorageContext()

    @mockserver.json_handler(
        '/driver-ratings-storage/internal/v1/ratings/process/'
        'uniques-events/bulk',
    )
    def _mock_process_uiques_events(request):
        events = request.json['uniques_events']
        assert context.events == events
        return {}

    @mockserver.json_handler(
        '/driver-ratings-storage/driver-ratings-storage/v1/ratings/updates',
    )
    def _mock_updates(request):
        assert request.json['limit'] > 0
        if 'cursor' in request.json:
            assert request.json['cursor'] in {'cursor1', 'cursor2'}
            if request.json['cursor'] == 'cursor2':
                # Send same cursor if no elements after cursor
                return {'cursor': 'cursor2', 'ratings': []}
            return {
                'cursor': 'cursor2',
                'ratings': [
                    {
                        'unique_driver_id': 'unique_driver_id_round1',
                        'rating': 4.44444444,
                        'calc_at': '2020-01-01T10:01:01+00:00',
                        'used_scores_num': 144,
                    },
                    {
                        'unique_driver_id': 'unique_driver_id_round2',
                        'rating': 4.99999999,
                        'calc_at': '2020-01-01T10:01:02+00:00',
                        'used_scores_num': 156,
                    },
                    {
                        'unique_driver_id': 'unique_driver_id_round3',
                        'rating': 4,
                        'calc_at': '2020-01-01T10:01:02+00:00',
                        'used_scores_num': 0,
                    },
                    {
                        'unique_driver_id': 'unique_driver_id48',
                        'rating': 5,
                        'calc_at': '2020-01-01T10:01:30+00:00',
                        'used_scores_num': 175,
                    },
                ],
            }
        return {
            'cursor': 'cursor1',
            'ratings': [
                {
                    'unique_driver_id': 'unique_driver_id1',
                    'rating': 5,
                    'previous_rating': 4.983412,
                    'calc_at': '2019-01-01T10:00:00+00:00',
                    'used_scores_num': 175,
                    'details': '[{"ts": 1599047171.123, "order": "oreder_id_1", "rating": 5, "weight": 1}, {"count": 11, "rating": 5, "source": "padding", "artificial": true}, {"ts": 1599047871.321, "order": "oreder_id_2", "rating": 4, "weight": 2}]',  # noqa: E501
                },
                {
                    'unique_driver_id': 'unique_driver_id4',
                    'rating': 4,
                    'calc_at': '2020-01-01T10:00:00+00:00',
                    'used_scores_num': 175,
                },
            ],
        }

    return context
