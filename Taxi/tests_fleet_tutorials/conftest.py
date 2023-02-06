# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from fleet_tutorials_plugins import *  # noqa: F403 F401
import pytest

from tests_fleet_tutorials import utils


class FeedsContext:
    def __init__(self, load_json):
        self.feeds = load_json('feeds.json')
        self.statuses = load_json('feeds_statuses.json')
        self.create = None
        self.fetch = None
        self.fetch_by_id = None
        self.log_status = None
        self.remove = None

    def set_feeds(self, feeds):
        self.feeds = feeds

    def set_statuses(self, statuses):
        self.statuses = statuses


@pytest.fixture
def mock_feeds(mockserver, load_json):

    context = FeedsContext(load_json)

    @mockserver.json_handler(utils.FEEDS_CREATE_ENDPOINT)
    def create(request):
        return {}

    @mockserver.json_handler(utils.FEEDS_FETCH_ENDPOINT)
    def fetch(request):
        return {
            'polling_delay': 300,
            'etag': 'new-etag',
            'has_more': False,
            'feed': context.feeds,
        }

    @mockserver.json_handler(utils.FEEDS_FETCH_BY_ID_ENDPOINT)
    def fetch_by_id(request):
        feed_ids = set(request.json.get('feed_ids'))
        if not feed_ids:
            feed_ids = set(request.json.get('feed_id'))
        return {
            'feed': [
                feed for feed in context.feeds if feed['feed_id'] in feed_ids
            ],
        }

    @mockserver.json_handler(utils.FEEDS_LOG_STATUS_ENDPOINT)
    def log_status(request):
        return {'statuses': context.statuses}

    @mockserver.json_handler(utils.FEEDS_REMOVE_ENDPOINT)
    def remove(request):
        return {'statuses': context.statuses}

    context.create = create
    context.fetch = fetch
    context.fetch_by_id = fetch_by_id
    context.log_status = log_status
    context.remove = remove

    return context
