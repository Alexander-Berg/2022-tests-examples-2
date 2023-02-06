import json

import pytest


class GeofenceContext:
    def __init__(self):
        self.areas = {}
        self._add_area('default')
        self.calls = 0
        self.state_calls = 0
        self.geozones = []
        self.timestamp = 1

    def _add_area(self, name):
        self.areas[name] = {'calls': 0, 'last_event_id': '-1', 'events': []}

    def add_event(self, area, event_id, event_type, driver_clid, driver_uuid):
        if area not in self.areas:
            self._add_area(area)
        area_context = self.areas[area]
        area_context['events'].append(
            {
                'event_id': event_id,
                'event_type': event_type,
                'clid': driver_clid,
                'uuid': driver_uuid,
                'arrival_time': 1,
                'event_time': self.timestamp,
                'last_update_time': self.timestamp,
            },
        )
        self.timestamp += 1
        area_context['last_event_id'] = event_id


@pytest.fixture
def geofence(mockserver):
    geofence_context = GeofenceContext()

    def mock_events_history(request, context):
        data = json.loads(request.get_data())
        if 'newer_than' in data['range']:
            min_id = data['range']['newer_than']
            if (
                    len(context['events']) > 0
                    and min_id < context['events'][0]['event_id']
            ):
                return mockserver.make_response(
                    '{"error": {"text": "Event too old"}}', 400,
                )
        return {
            'events': context['events'],
            'last_event_id': context['last_event_id'],
            'unread': 0,
        }

    def mock_state(request, context):
        events = [
            ev for ev in context['events'] if ev['event_type'] == 'entered'
        ]
        return {
            'events': events,
            'last_event_id': events[-1]['event_id'] if events else '-1',
        }

    @mockserver.json_handler('/geofence/monitoring-areas/', prefix=True)
    def _mock_monitoring_areas(request):
        if request.method == 'PUT':
            geofence_context.geozones.append(json.loads(request.data))
        else:
            for area in geofence_context.areas:
                path = '/geofence/monitoring-areas/' + area + '/'
                if not request.path.startswith(path):
                    continue
                context = geofence_context.areas[area]
                context['calls'] += 1
                geofence_context.calls += 1
                # TODO: process limit
                if request.path == path + 'events-history':
                    return mock_events_history(request, context)
                if request.path == path + 'state':
                    geofence_context.state_calls += 1
                    return mock_state(request, context)
            context = geofence_context.areas['default']
            context['calls'] += 1
            if request.path.endswith('events-history'):
                return mock_events_history(request, context)
            geofence_context.state_calls += 1
            return mock_state(request, context)

    return geofence_context
