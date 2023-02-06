# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
import collections

import pytest

import rider_metrics.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301
from rider_metrics.models import processor

pytest_plugins = ['rider_metrics.generated.service.pytest_plugins']


BASE_RMS_URL = '/rider-metrics-storage/'
UNPROCESSED_LIST_URL = f'{BASE_RMS_URL}v2/events/unprocessed/list'
EVENT_COMPLETE_URL = f'{BASE_RMS_URL}v1/event/complete'
EVENT_HISTORY_URL = f'{BASE_RMS_URL}v1/events/history'

CRM_HUB_BASE_URL = '/crm-hub/'
NEW_COMMUNICATION_URL = f'{CRM_HUB_BASE_URL}v1/communication/new'

PASSENGER_TAGS_BASE_URL = '/passenger-tags/'
TAGS_BASE_URL = '/tags/'
MATCH_URL = f'{PASSENGER_TAGS_BASE_URL}v1/match'
UPLOAD_URL = f'{PASSENGER_TAGS_BASE_URL}v1/upload'
TAGS_UPLOAD_URL = f'{TAGS_BASE_URL}v1/upload'

PATCH = collections.namedtuple(
    'Patch',
    (
        'event_complete',
        'communications',
        'event_history',
        'tags_match',
        'tags_upload',
        'driver_tags_upload',
    ),
)


@pytest.fixture
def mock_processing_service(mockserver, patch_aiohttp_session, response_mock):
    def patch(events_list, tags, events_history=None):
        events_history = events_history or []

        @mockserver.json_handler(EVENT_COMPLETE_URL)
        async def _mock_event_complete(*_args, **_kwargs):
            return

        @mockserver.json_handler(UNPROCESSED_LIST_URL)
        async def _mock_unprocessed_list(*_args, **_kwargs):
            return events_list

        @mockserver.json_handler(EVENT_HISTORY_URL)
        async def _mock_events_history(*_args, **_kwargs):
            return {'events': events_history}

        @mockserver.json_handler(NEW_COMMUNICATION_URL)
        async def _mock_new_communication(*_args, **_kwargs):
            return

        @mockserver.json_handler(MATCH_URL)
        def _mock_match(*_args, **_kwargs):
            return {'entities': [{'tags': tags}]}

        @mockserver.json_handler(UPLOAD_URL)
        def _mock_upload(*_args, **_kwargs):
            return {}

        @mockserver.json_handler(TAGS_UPLOAD_URL)
        def _mock_driver_upload(*_args, **_kwargs):
            return {}

        return PATCH(
            communications=_mock_new_communication,
            event_complete=_mock_event_complete,
            event_history=_mock_events_history,
            tags_match=_mock_match,
            tags_upload=_mock_upload,
            driver_tags_upload=_mock_driver_upload,
        )

    return patch


@pytest.fixture
def test_processor(stq3_context):
    return processor.Processor(stq3_context)


@pytest.fixture
def test_entity_processor(test_processor):
    return test_processor.make_entity_processor()
