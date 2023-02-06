import typing as tp

import pytest


@pytest.fixture(name='driver_metrics_storage')
def driver_metrics_storage(mockserver):
    class Context:
        USE_ACTIVITY = 0
        USE_PRIORITY = 1

        def __init__(self):
            self.calls = 0
            self.events_processed_response = {}
            self.activity_history_response = {}

        def set_metric_event(
                self, metric_type, order_id: str, value_change, distance: str,
        ):
            if metric_type == self.USE_ACTIVITY:
                return self._set_activity(order_id, value_change, distance)
            if metric_type == self.USE_PRIORITY:
                return self._set_priority(order_id, value_change, distance)
            raise Exception(
                'Unknown metrics_type, use one of USE_ACTIVITY, USE_PRIORITY',
            )

        def _make_response(
                self,
                order_id: str,
                distance: str,
                additional_info: tp.Dict,
                extra_data_fields: tp.Dict,
        ):
            extra_data = {
                'driver_id': '643753730233_c1b3df5adad3491fa9186a9d82387b12',
                'db_id': '7f74df331eb04ad78bc2ff25ff88a8f2',
            }
            if extra_data_fields:
                extra_data.update(extra_data_fields)
            event = {
                'event': {
                    'datetime': '2019-11-28T13:03:39.396000Z',
                    'event_id': '1',
                    'extra_data': '{"this-filed-is-deprecated":true}',
                    'extra': extra_data,
                    'descriptor': {
                        'type': 'complete',
                        'tags': ['tariff_econom', 'dispatch_' + distance],
                    },
                    'order_alias': order_id,
                    'order_id': 'unused-order-id',
                    'park_driver_profile_id': '_'.join(
                        [
                            '7f74df331eb04ad78bc2ff25ff88a8f2',
                            'c1b3df5adad3491fa9186a9d82387b12',
                        ],
                    ),
                    'tariff_zone': 'moscow',
                    'type': 'order',
                },
            }
            event.update(additional_info)
            return {'events': [event]}

        def _set_activity(self, order_id, value_change: int, distance: str):
            self.events_processed_response = self._make_response(
                order_id, distance, {'activity_change': value_change}, {},
            )

        def _set_priority(
                self, order_id, value_change: tp.Dict, distance: str,
        ):
            assert (
                'priority_change' in value_change
                and 'priority_absolute' in value_change
                and 'completion_scores_change' in value_change
            )
            self.events_processed_response = self._make_response(
                order_id,
                distance,
                {
                    'priority_change': value_change['priority_change'],
                    'priority_absolute': value_change['priority_absolute'],
                    'complete_score_change': value_change[
                        'completion_scores_change'
                    ],
                },
                extra_data_fields={'replace_activity_with_priority': True},
            )

    context = Context()

    @mockserver.json_handler('/driver-metrics-storage/v3/events/processed')
    async def _events_processed(request):
        context.calls += 1
        return context.events_processed_response

    return context
