import json
from functools import partial

import datetime

# TODO delete
time_sensors = {
    'walker_stage_finalize_external': 'walker_stage.finalize_external_time_milliseconds',
    'walker_stage_finalize_internal': 'walker_stage.finalize_internal_time_milliseconds',
    'walker_stage_finish_heavy_scenarios': 'walker_stage.finish_heavy_scenarios_time_milliseconds',
    'walker_stage_make_scenario_wrappers': 'walker_stage.make_scenario_wrappers_time_milliseconds',
    'walker_stage_per_query_sources': 'walker_stage.per_query_sources_time_milliseconds',
    'walker_stage_postclassification': 'walker_stage.postclassification_time_milliseconds',
    'walker_stage_preclassification': 'walker_stage.preclassification_time_milliseconds',
    'walker_stage_run_fast_scenarios': 'walker_stage.run_fast_scenarios_time_milliseconds',
    'walker_stage_start_heavy_scenarios': 'walker_stage.start_heavy_scenarios_time_milliseconds',
    'http_request_time': 'http_request.time_milliseconds',
    'http_request_wait_in_queue': 'http_request.wait_in_queue_time_milliseconds'
}


#


def parse_date_mm(date):
    return datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ')


def parse_date_vins(date):
    return datetime.datetime.fromtimestamp(date)


def sensor_filter_mm(sensor):
    # TODO delete
    if 'histogram' in sensor['labels'] and sensor['labels']['histogram'] in time_sensors:
        return True
    if sensor['labels']['name'] in time_sensors:
        return True
    #
    return 'name' in sensor['labels'] and (sensor['labels']['name'].endswith('_time_milliseconds') or
                                           sensor['labels']['name'].endswith('_time_microseconds'))


def sensor_filter_vins(sensor):
    return sensor['name'].endswith('_time')


class LabelsJoiner:
    def __init__(self, label1_name, label2_name, label2_value):
        self._label1_name = label1_name
        self._label2_name = label2_name
        self._label2_value = label2_value

    def join(self, labels):
        return labels[self._label1_name] + '__' + self._label2_value

    def joinable(self, labels):
        return self._label1_name in labels and self._label2_name in labels and labels[
            self._label2_name] == self._label2_value


megamind_joiners = [
    LabelsJoiner('scenario_name', 'name', 'scenario.response_time_milliseconds'),
    LabelsJoiner('scenario_name', 'name', 'scenario.retry_response_time_milliseconds'),
    LabelsJoiner('source', 'name', 'response_time_milliseconds')
]


def extract_name_mm(sensor, labels_joiners):
    for labels_joiner in labels_joiners:
        if labels_joiner.joinable(sensor['labels']):
            return labels_joiner.join(sensor['labels'])
    # TODO delete
    if 'histogram' in sensor['labels']:
        return time_sensors[sensor['labels']['histogram']]
    if sensor['labels']['name'] in time_sensors:
        return time_sensors[sensor['labels']['name']]
    #
    return sensor['labels']['name']


extract_name_mm = partial(extract_name_mm, labels_joiners=megamind_joiners)


def extract_name_vins(sensor):
    return sensor['name']


def load_data(filepath, date_parser, sensor_filter, name_extractor, filter_warm_up=False):
    dt_start = None
    d = dict()
    with open(filepath, 'r') as f:
        for line in f:
            j = json.loads(line.strip())
            dt = date_parser(j['time'])
            if not dt_start:
                dt_start = dt + datetime.timedelta(minutes=3)
            if filter_warm_up and dt <= dt_start:
                continue
            if not sensor_filter(j):
                continue
            name = name_extractor(j)

            if name not in d:
                d[name] = {
                    'value': [],
                    'time': []
                }
            d[name]['value'].append(j['value'])
            d[name]['time'].append(dt)

    for k, v in d.items():
        v['time'], v['value'] = zip(*sorted(zip(v['time'], v['value'])))
    return d


def unite_sensors_keys(old_data, new_data):
    keys = set(old_data.keys() + new_data.keys())
    for k in keys:
        if k not in old_data:
            old_data[k] = {'value': [], 'time': []}
        if k not in new_data:
            new_data[k] = {'value': [], 'time': []}
