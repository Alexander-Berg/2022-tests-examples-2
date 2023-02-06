# pylint: disable=redefined-outer-name, unused-wildcard-import
# pylint: disable=protected-access
import collections
import datetime
import logging
import typing as tp

import bson
import pytest

# this import should be before libraries
import taxi_driver_metrics.generated.service.pytest_init  # noqa: F401,E501,I100 pylint: disable=C0301,C0412

from generated.clients import (  # noqa: I100
    driver_metrics_storage as dms_client,
)  # noqa: I100
from metrics_processing.events import AbstractEventsProvider  # noqa: I100
from metrics_processing.utils import action_journal  # noqa: I100
from taxi import settings  # noqa: I100

from taxi_driver_metrics.common.models import DmsEventsProvider  # noqa: I100
from taxi_driver_metrics.common.models import DriverInfo  # noqa: I100
from taxi_driver_metrics.common.models import Events  # noqa: I100
from taxi_driver_metrics.common.models import (
    ItemBasedEntityProcessor,
)  # noqa: I100
from taxi_driver_metrics.common.models import processing_items

pytest_plugins = ['taxi_driver_metrics.generated.service.pytest_plugins']


if settings.ENVIRONMENT == settings.DEVELOPMENT:
    logging.getLogger().setLevel(logging.INFO)
    logging.getLogger().addHandler(logging.StreamHandler())

BASE_TAGS_URL = '/tags/'
BASE_DRIVER_TAGS_URL = '/driver-tags/'
BASE_PASSENGER_TAGS_URL = '/passenger-tags/'

BODY = {
    'service_name': 'driver-metrics',
    'type': 'stq_callback',
    'zone': 'default',
    'actions': [
        {
            'action': [
                {
                    'queues': [
                        {
                            'data': [
                                {
                                    'expr': 'event.dbid_uuid',
                                    'name': 'park_driver_profile_id',
                                },
                            ],
                            'default_data_policy': 'replace',
                            'name': 'medic_order_event',
                        },
                    ],
                    'type': 'stq_callback',
                },
            ],
        },
    ],
    'disabled': False,
    'events': [
        {
            'name': 'complete',
            'tags': '\'event::tariff_promo\'',
            'topic': 'order',
        },
    ],
    'additional_params': {
        'events_period_sec': 3600,
        'events_to_trigger_cnt': 1,
        'tags': '\'tags::driverfix_medic_test\'',
    },
    'name': 'MedicOrderEvent',
    'tariff': '__default__',
}

PatchTags = collections.namedtuple(
    'PatchTags',
    (
        'tags_match',
        'tags_upload',
        'passenger_tags_upload',
        'driver_tags_match_profile',
        'tags_admin_tag_info',
    ),
)
ActivityItem = collections.namedtuple('ActivityItem', ('value',))


@pytest.fixture
def stq_client_patched(patch):
    @patch('taxi.stq.client.put')
    async def stq_client_put(*args, **kwargs):
        return

    return stq_client_put


@pytest.fixture
def test_rule():
    return BODY


@pytest.fixture
def create_rule():
    async def create_config_request(client, body=None, headers=None, **kwargs):
        if not body:
            body = BODY

        body.update(kwargs)

        result = await client.post(
            f'/v1/config/rule/modify', json=body, headers=headers,
        )

        json_response = await result.json()
        return result.status, json_response

    return create_config_request


@pytest.fixture()
def get_rules():
    async def get_config_request(
            client,
            type_: tp.Optional[str] = 'loyalty',
            zone: tp.Optional[str] = 'default',
            rule_name: tp.Optional[str] = 'blocking_drivers',
    ):

        query = {'service_name': 'driver-metrics'}

        if type_:
            query['type'] = type_
        if zone:
            query['zone'] = zone
        if rule_name:
            query['name'] = rule_name

        result = await client.post(
            '/v1/config/rule/values',
            json=query,
            headers={'X-Ya-Service-Ticket': 'ticket'},
        )

        body = await result.json()
        return result.status, body

    return get_config_request


@pytest.fixture
def fake_event_provider(web_context):
    class FakeEventProvider(AbstractEventsProvider):
        def __init__(
                self,
                events: tp.List[Events.OrderEvent],
                *args,
                activity: int = 100,
                **kwargs,
        ) -> None:
            self.events = events
            self.activity = activity
            super().__init__(app=web_context)

        async def events_history(
                self,
                entity_id: str,
                from_timestamp: datetime.datetime,
                limit: tp.Optional[int] = None,
        ) -> tp.List[Events.BaseEvent]:
            return sorted(
                [
                    x
                    for x in filter(
                        lambda x: x.timestamp >= from_timestamp, self.events,
                    )
                ],
                key=lambda x: x.timestamp,
                reverse=True,
            )

        async def activity_values(
                self,
                unique_driver_ids: tp.List[str],
                strict: bool = False,
                timeout_ms: int = 1000,
        ):
            client = self._app.clients.driver_metrics_storage

            response = await client.v2_activity_values_list_post(
                body=dms_client.V2ActivityValuesListPostBody(
                    unique_driver_ids=unique_driver_ids, strict=strict,
                ),
                _timeout_ms=timeout_ms,
            )

            return response.body.items

        async def complete_score_values(
                self, unique_driver_ids: tp.List[str], timeout_ms: int = 1000,
        ):
            client = self._app.clients.driver_metrics_storage

            response = await client.v1_completion_scores_list_post(
                body=dms_client.V1CompletionScoresListPostBody(
                    unique_driver_ids=unique_driver_ids,
                ),
                _timeout_ms=timeout_ms,
            )

            return response.body.contractor_scores

    return FakeEventProvider


@pytest.fixture
def simple_secdist(simple_secdist):
    simple_secdist['settings_override']['YT_CONFIG']['hahn'] = {
        'prefix': 'hahn',
        'token': 'test-token',
        'api_version': 'latest',
        'proxy': {'url': 'hahn.yt.yandex-team.ru'},
    }
    return simple_secdist


@pytest.fixture
async def predict_activity(web_context):
    async def predict(udid, event_map, value='activity'):
        dispatch_id = str(bson.ObjectId())
        prediction = {
            'dispatch_id': (
                dispatch_id if value == 'activity' else dispatch_id + '_cs'
            ),
            'udid': udid,
            'order_id': 'order_id',
            'prediction': {k: {value: v} for k, v in event_map.items()},
            'additional_params': {},
            'updated': datetime.datetime.utcnow(),
        }

        await web_context.mongo.driver_metrics_predictions.insert_one(
            prediction,
        )

        return dispatch_id

    return predict


@pytest.fixture
def tags_service_mock(mockserver):
    def patch_request(
            upload_check=None,
            match_profile_check=None,
            match_profile_return=None,
            tags=None,
            tag_info=None,
    ):
        if not tags:
            tags = ['good_driver', 'lucky']

        @mockserver.json_handler(f'{BASE_TAGS_URL}v1/match')
        async def tags_match(*_args, **kwargs):
            if match_profile_check:
                match_profile_check(*_args, **kwargs)
            if match_profile_return:
                return match_profile_return(*_args, **kwargs)
            return {'tags': tags}

        @mockserver.json_handler(f'{BASE_TAGS_URL}v1/upload')
        async def tags_upload(*_args, **kwargs):
            if upload_check:
                upload_check(*_args, **kwargs)
            return {}

        @mockserver.json_handler(f'{BASE_PASSENGER_TAGS_URL}v1/upload')
        async def passenger_tags_upload(*_args, **kwargs):
            if upload_check:
                upload_check(*_args, **kwargs)
            return {}

        @mockserver.json_handler(
            f'{BASE_DRIVER_TAGS_URL}v1/drivers/match/profile',
        )
        async def driver_tags_match_profile(*_args, **kwargs):
            if match_profile_check:
                match_profile_check(*_args, **kwargs)
            if match_profile_return:
                return match_profile_return(*_args, **kwargs)
            return {'tags': tags}

        @mockserver.json_handler(f'{BASE_TAGS_URL}v1/admin/tag/info')
        async def tags_admin_tag_info(*_args, **kwargs):
            return tag_info

        return PatchTags(
            tags_match=tags_match,
            tags_upload=tags_upload,
            passenger_tags_upload=passenger_tags_upload,
            driver_tags_match_profile=driver_tags_match_profile,
            tags_admin_tag_info=tags_admin_tag_info,
        )

    return patch_request


@pytest.fixture
def event_provider(stq3_context):
    return DmsEventsProvider(stq3_context)


@pytest.fixture
def item_entity_processor(stq3_context):
    entity_processor = ItemBasedEntityProcessor(
        stq3_context, event_provider=DmsEventsProvider(stq3_context),
    )

    async def mock_old_processor_blocking():
        await entity_processor._process_blocking_items(
            [
                entity_processor._make_item(
                    processing_items.ActivityProcessingItem,
                ),
            ],
        )

    async def prediction():
        activity = entity_processor._make_item(
            processing_items.ActivityProcessingItem,
        )
        res = await activity._predict_single_value()
        return res

    entity_processor._process_activity_blocking = mock_old_processor_blocking
    entity_processor._make_new_activity_prediction = prediction

    return entity_processor


@pytest.fixture
def entity_processor(stq3_context, item_entity_processor):
    if stq3_context.config.DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS == 100:
        return item_entity_processor
    return ItemBasedEntityProcessor(
        stq3_context, event_provider=DmsEventsProvider(stq3_context),
    )


def _extract_attributes(obj):
    return {k: v for k, v in obj.__dict__.items() if not k.startswith('_')}


@pytest.fixture
def event_equals():
    def equals(ev1, ev2):
        assert _extract_attributes(ev1) == _extract_attributes(ev2)

    return equals


@pytest.fixture(autouse=True)
async def mock_solomon(mockserver):
    @mockserver.json_handler('/solomon/')
    def push_data(*args, **kwargs):
        return {}

    return push_data


@pytest.fixture()
def patch_rules(patch, web_context):
    def add_rules(rules):
        @patch('metrics_processing.rules.manager.RulesManager.rules_by_zone')
        def get_rules(*args, **kwargs):
            return rules

        return get_rules

    return add_rules


@pytest.fixture
def cached_journals(monkeypatch):
    journals = []

    class ActionJournalSavingState(action_journal.ActionJournal):
        def __init__(self):
            journals.append(self)
            super().__init__()

    monkeypatch.setattr(
        'metrics_processing.utils.action_journal.ActionJournal',
        ActionJournalSavingState,
    )

    return journals


@pytest.fixture
def cached_drivers(monkeypatch):
    drivers = []

    class DriverInfoSavingState(DriverInfo):
        @classmethod
        # pylint: disable=arguments-differ
        async def make(cls, *args, **kwargs):
            driver = await DriverInfo.make(*args, **kwargs)
            drivers.append(driver)
            return driver

    monkeypatch.setattr(
        'taxi_driver_metrics.common.models._new_processor.DriverInfo',
        DriverInfoSavingState,
    )

    return drivers
