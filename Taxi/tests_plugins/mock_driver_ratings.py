import json

import pytest


@pytest.fixture(autouse=True)
def driver_ratings(mockserver, db):
    @mockserver.json_handler('/driver_ratings/v1/driver/ratings/updates')
    def mock_countries_taxi(request):
        last_known_revision = request.args.get('last_known_revision')
        if not last_known_revision:
            # First query - fetch all data
            #   Fetch from mongo
            ratings = []
            revision = None
            for ud in db.unique_drivers.find():
                revision = str(ud['updated_ts'])
                rating = {
                    'revision': revision,
                    'unique_driver_id': str(ud['_id']),
                }
                new_score = ud.get('new_score')
                if new_score:
                    unified = new_score.get('unified')
                    if unified:
                        data = {}
                        if 'rating' in unified:
                            data['rating'] = unified['rating']
                        if 'rating_count' in unified:
                            data['rating_count'] = unified['rating_count']
                        if 'total' in unified:
                            data['total'] = unified['total']
                        rating['data'] = data
                ratings.append(rating)
            #  Build body
            body = {
                'last_modified': '2019-12-08T11:09:11.123Z',
                'last_revision': revision,
                'cache_lag': 1,
                'ratings': ratings,
            }
        else:
            # Second query - no more data
            body = {
                'last_modified': '2019-12-08T11:09:11.123Z',
                'last_revision': last_known_revision,
                'cache_lag': 0,
                'ratings': [],
            }
        # Response
        response = mockserver.make_response(json.dumps(body), 200)
        response.headers['X-Polling-Delay-Ms'] = 10
        return response
