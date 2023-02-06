import datetime
import json

import pytest

from taxi_tests import utils


class TrackerContext:
    def __init__(self):
        self.airport_queue = {
            'calls': [],  # types
            'event_log': [],
            'events': 0,
        }
        self.positions = {}
        self.drivers = {}

    def set_position(
            self, driver_id, timestamp, lat, lon, speed=0, direction=0,
    ):
        if isinstance(timestamp, datetime.datetime):
            timestamp = utils.timestamp(timestamp)
        self.positions[driver_id] = {
            'lat': lat,
            'lon': lon,
            'timestamp': timestamp,
            'speed': speed,
            'direction': direction,
        }

    def set_driver(
            self,
            driver_id,
            timestamp,
            lat,
            lon,
            speed=0,
            direction=0,
            free=False,
    ):
        if isinstance(timestamp, datetime.datetime):
            timestamp = utils.timestamp(timestamp)
        self.drivers[driver_id] = {
            'id': driver_id,
            'point': {
                'direction': direction,
                'lat': lat,
                'lon': lon,
                'speed': speed,
                'timestamp': timestamp,
            },
            'free': free,
        }


@pytest.fixture
def tracker(mockserver):
    tracker_context = TrackerContext()

    @mockserver.json_handler('/tracker/1.0/airport-queue')
    def mock_airport_queue(request):
        body = json.loads(list(request.form.items())[0][0])
        assert 'type' in body
        if 'events' in body:
            for event in body['events']:
                assert 'action' in event
                assert 'timestamp' in event
                assert 'driver_id' in event
                tracker_context.airport_queue['events'] += 1
                tracker_context.airport_queue['event_log'].append(event)
        tracker_context.airport_queue['calls'].append(body['type'])
        return {}

    @mockserver.json_handler('/tracker/position')
    def mock_driver_position(request):
        driver_id = request.args['id']
        if driver_id != '':
            return tracker_context.positions[driver_id]
        else:
            return mockserver.make_response('', 404)

    @mockserver.json_handler('/tracker/drivers')
    def mock_driver_drivers(request):
        body = json.loads(list(request.form.items())[0][0])
        driver_ids = body['driver_ids']
        result = []
        for k, v in tracker_context.drivers.items():
            if k in driver_ids:
                result.append(v)
        return {'drivers': result}

    @mockserver.json_handler('/tracker/smooth-routing')
    def mock_smooth_routing(request):
        return {
            'duration': 226,
            'smooth_duration': 227,
            'distance': 1010,
            'driver_position': [37.51, 55.61],
            'path': [
                [37.511, 55.611],
                [37.514, 55.614],
                [37.518, 55.618],
                [40.454257, 56.152082],
            ],
        }

    @mockserver.json_handler('/tracker/service/drivers-classes-bulk')
    def mock_drivers_classes_bulk(request):
        body = json.loads(list(request.form.items())[0][0])
        subrequests = body['drivers']
        result = []
        for req in subrequests:
            data = req
            data['driver_classes'] = ['econom', 'business']
            data['payment_type_restrictions'] = 'none'
            result.append(data)
        return {'results': result}

    return tracker_context
