import datetime
from typing import Callable

import pytest

from support_info import app
from support_info.internal import autoreply_source


@pytest.mark.config(
    SUPPORT_INFO_GET_DMS_META=True,
    DRIVER_METRICS_STORAGE_CLIENT_SETTINGS={
        '__default__': {
            '__default__': {
                'num_retries': 0,
                'retry_delay_ms': [50],
                'request_timeout_ms': 250,
            },
        },
    },
    SUPPORT_INFO_ACTION_META_FIELDS={'enabled': True, 'hours_limit': 6},
)
@pytest.mark.parametrize(
    ('data', 'mock_data', 'expected_result'),
    (
        (
            {
                'unique_driver_id': 'unique_driver_id',
                'order_id': 'order_id',
                'created': '2018-11-01T01:00:00.000Z',
            },
            {
                'events': [
                    {
                        'event': {
                            'udid': 'unique_driver_id',
                            'type': 'order',
                            'order_id': 'order_id',
                            'datetime': (
                                datetime.datetime.utcnow()
                                - datetime.timedelta(hours=2)
                            ).strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                            'event_id': 'event_id',
                        },
                        'activity_change': -10,
                        'loyalty_change': 0,
                    },
                    {
                        'event': {
                            'udid': 'unique_driver_id',
                            'type': 'dm_service_manual',
                            'order_id': '',
                            'datetime': (
                                datetime.datetime.utcnow()
                                - datetime.timedelta(hours=1)
                            ).strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                            'event_id': 'event_id',
                            'extra': {'reason': 'order_id'},
                            'descriptor': {'type': 'set_activity_value'},
                        },
                        'activity_change': 5,
                        'loyalty_change': 0,
                    },
                ],
            },
            {
                'return_activity': True,
                'activity_decrease': 10,
                'driver_activity_return_count': 1,
                'complete_score_decrease': 0,
                'driver_complete_score_return_count': 0,
                'return_complete_score': False,
            },
        ),
        (
            {
                'unique_driver_id': 'unique_driver_id',
                'order_id': 'order_id',
                'created': '2018-11-01T01:00:00.000Z',
            },
            {
                'events': [
                    {
                        'event': {
                            'udid': 'unique_driver_id',
                            'type': 'order',
                            'order_id': 'order_id',
                            'datetime': (
                                datetime.datetime.utcnow()
                                - datetime.timedelta(hours=2)
                            ).strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                            'event_id': 'event_id',
                        },
                        'activity_change': 5,
                        'loyalty_change': 0,
                    },
                    {
                        'event': {
                            'udid': 'unique_driver_id',
                            'type': 'dm_service_manual',
                            'order_id': '',
                            'datetime': (
                                datetime.datetime.utcnow()
                                - datetime.timedelta(hours=1)
                            ).strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                            'event_id': 'event_id',
                            'extra': {'reason': 'order_id2'},
                            'descriptor': {'type': 'set_activity_value'},
                        },
                        'activity_change': 7,
                        'loyalty_change': 0,
                    },
                    {
                        'event': {
                            'udid': 'unique_driver_id',
                            'type': 'dm_service_manual',
                            'order_id': '',
                            'datetime': (
                                datetime.datetime.utcnow()
                                - datetime.timedelta(hours=7)
                            ).strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                            'event_id': 'event_id',
                            'extra': {'reason': 'order_id2'},
                            'descriptor': {'type': 'set_activity_value'},
                        },
                        'activity_change': 7,
                        'loyalty_change': 0,
                    },
                ],
            },
            {
                'return_activity': False,
                'activity_decrease': 0,
                'driver_activity_return_count': 1,
                'complete_score_decrease': 0,
                'driver_complete_score_return_count': 0,
                'return_complete_score': False,
            },
        ),
        (
            {
                'unique_driver_id': 'unique_driver_id',
                'order_id': 'order_id',
                'created': '2018-11-01T01:00:00.000Z',
            },
            {'events': []},
            {
                'return_activity': False,
                'activity_decrease': 0,
                'driver_activity_return_count': 0,
                'complete_score_decrease': 0,
                'driver_complete_score_return_count': 0,
                'return_complete_score': False,
            },
        ),
        (
            {
                'unique_driver_id': 'unique_driver_id',
                'order_id': 'order_id',
                'created': '2018-11-01T01:00:00.000Z',
            },
            {
                'events': [
                    {
                        'event': {
                            'udid': 'unique_driver_id',
                            'type': 'order',
                            'order_id': 'order_id',
                            'datetime': (
                                datetime.datetime.utcnow()
                                - datetime.timedelta(hours=2)
                            ).strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                            'event_id': 'event_id',
                        },
                        'complete_score_change': -10,
                        'loyalty_change': 0,
                    },
                    {
                        'event': {
                            'udid': 'unique_driver_id',
                            'type': 'dm_service_manual',
                            'order_id': '',
                            'datetime': (
                                datetime.datetime.utcnow()
                                - datetime.timedelta(hours=1)
                            ).strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                            'event_id': 'event_id',
                            'extra': {'reason': 'order_id'},
                            'descriptor': {
                                'type': 'set_complete_scores_value',
                            },
                        },
                        'complete_score_change': 5,
                        'loyalty_change': 0,
                    },
                ],
            },
            {
                'return_activity': False,
                'activity_decrease': 0,
                'driver_activity_return_count': 0,
                'complete_score_decrease': 10,
                'driver_complete_score_return_count': 1,
                'return_complete_score': True,
            },
        ),
        (
            {
                'unique_driver_id': 'unique_driver_id',
                'order_id': 'order_id',
                'created': '2018-11-01T01:00:00.000Z',
            },
            {
                'events': [
                    {
                        'event': {
                            'udid': 'unique_driver_id',
                            'type': 'order',
                            'order_id': 'order_id',
                            'datetime': (
                                datetime.datetime.utcnow()
                                - datetime.timedelta(hours=2)
                            ).strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                            'event_id': 'event_id',
                        },
                        'complete_score_change': 5,
                        'loyalty_change': 0,
                    },
                    {
                        'event': {
                            'udid': 'unique_driver_id',
                            'type': 'dm_service_manual',
                            'order_id': '',
                            'datetime': (
                                datetime.datetime.utcnow()
                                - datetime.timedelta(hours=1)
                            ).strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                            'event_id': 'event_id',
                            'extra': {'reason': 'order_id2'},
                            'descriptor': {
                                'type': 'set_complete_scores_value',
                            },
                        },
                        'complete_score_change': 7,
                        'loyalty_change': 0,
                    },
                    {
                        'event': {
                            'udid': 'unique_driver_id',
                            'type': 'dm_service_manual',
                            'order_id': '',
                            'datetime': (
                                datetime.datetime.utcnow()
                                - datetime.timedelta(hours=7)
                            ).strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                            'event_id': 'event_id',
                            'extra': {'reason': 'order_id2'},
                            'descriptor': {
                                'type': 'set_complete_scores_value',
                            },
                        },
                        'complete_score_change': 7,
                        'loyalty_change': 0,
                    },
                ],
            },
            {
                'return_activity': False,
                'activity_decrease': 0,
                'driver_activity_return_count': 0,
                'complete_score_decrease': 0,
                'driver_complete_score_return_count': 1,
                'return_complete_score': False,
            },
        ),
    ),
)
async def test_dms_data_source(
        support_info_app: app.SupportInfoApplication,
        patch_aiohttp_session,
        response_mock,
        patch_get_dms: Callable,
        data: dict,
        mock_data: list,
        expected_result: dict,
):
    patch_get_dms(mock_data)

    dms_source = autoreply_source.DriverMetricsStorageDataSource(
        dms_client=support_info_app.driver_metrics_storage_client,
        config=support_info_app.config,
    )

    result = await dms_source.get_data(data)

    assert result == expected_result
