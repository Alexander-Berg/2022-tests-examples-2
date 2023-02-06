# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from fleet_notifications_plugins import *  # noqa: F403 F401
import pytest

from tests_fleet_notifications import utils


class FeedsContext:
    def __init__(self, load_json):
        self.feeds = load_json('feeds.json')
        self.statuses = load_json('feeds_statuses.json')
        self.summary_response = load_json('feeds_summary.json')
        self.create = None
        self.fetch = None
        self.log_status = None
        self.summary = None

    def set_feeds(self, feeds):
        self.feeds = feeds

    def set_statuses(self, statuses):
        self.statuses = statuses

    def set_summary(self, summary):
        self.summary_response = summary


@pytest.fixture
def mock_feeds(mockserver, load_json):

    context = FeedsContext(load_json)

    @mockserver.json_handler(utils.FEEDS_CREATE_ENDPOINT)
    def create(request):
        return {
            'service': 'fleet-notifications',
            'filtered': [],
            'feed_ids': {},
        }

    @mockserver.json_handler(utils.FEEDS_FETCH_ENDPOINT)
    def fetch(request):
        return {
            'polling_delay': 300,
            'etag': 'new-etag',
            'has_more': False,
            'feed': context.feeds,
        }

    @mockserver.json_handler(utils.FEEDS_LOG_STATUS_ENDPOINT)
    def log_status(request):
        return {'statuses': context.statuses}

    @mockserver.json_handler(utils.FEEDS_SUMMARY_ENDPOINT)
    def summary(request):
        return context.summary_response

    context.create = create
    context.fetch = fetch
    context.log_status = log_status
    context.summary = summary

    return context
