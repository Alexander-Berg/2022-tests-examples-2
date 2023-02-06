import datetime
import json
import time

import pytest


class SolomonContext:
    def __init__(self):
        self.excepted_sensors = []
        self.weak_excepted_sensors = []
        self.ordered_flag = True

    def reset(self):
        self.excepted_sensors = []
        self.ordered_flag = True

    def set_ordered(self, flag):
        self.ordered_flag = flag

    def add(self, sensors):
        self.excepted_sensors.extend(sensors)

    def add_weak(self, sensors):
        weak_sensors = [(e['kind'], e['labels']) for e in sensors]
        self.weak_excepted_sensors.extend(weak_sensors)

    def try_exclude(self, sensors):
        for sensor in sensors:
            if self.excepted_sensors:
                if self.ordered_flag:
                    if self.excepted_sensors[0] == sensor:
                        del self.excepted_sensors[0]
                else:
                    if sensor in self.excepted_sensors:
                        self.excepted_sensors.remove(sensor)
            if self.weak_excepted_sensors:
                weak_sensor = (sensor['kind'], sensor['labels'])

                if self.ordered_flag:
                    if self.excepted_sensors[0] == weak_sensor:
                        del self.excepted_sensors[0]
                else:
                    if weak_sensor in self.excepted_sensors:
                        self.excepted_sensors.remove(weak_sensor)

    def wait_for(self, timeout=10, sleep=0.5):
        end = datetime.datetime.now() + datetime.timedelta(seconds=timeout)
        while datetime.datetime.now() < end:
            if not self.excepted_sensors:
                return
            time.sleep(sleep)
        if self.excepted_sensors:
            raise TimeoutError(self.excepted_sensors)
        if self.weak_excepted_sensors:
            raise TimeoutError(self.weak_excepted_sensors)


@pytest.fixture(autouse=True)
def mock_solomon(mockserver):
    solomon_context = SolomonContext()

    @mockserver.json_handler('/solomon/')
    def handler(request):
        data = json.loads(request.get_data())
        solomon_context.try_exclude(data['sensors'])

    return solomon_context
