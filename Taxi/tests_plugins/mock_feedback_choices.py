import json

import pytest
import requests


class FeedbackChoicesContext:
    def __init__(self, choices_getter, choices_configs_getter):
        self._choices_getter = choices_getter
        self._choices_configs_getter = choices_configs_getter
        self._feedback_choices = choices_getter()
        self._feedback_choices_mask = choices_configs_getter()

        self._call_counter = 0

    def times_called(self):
        return self._call_counter

    def was_called(self):
        return bool(self._call_counter)

    def update(self):
        self._feedback_choices = self._choices_getter()
        self._feedback_choices_mask = self._choices_configs_getter()

    def get_choices_for_zone(self, zone_id=None):
        self._call_counter += 1
        default_mask = self._feedback_choices_mask['__default__']
        choices = _flatten_choices(
            self._feedback_choices_mask.get(zone_id, default_mask),
        )
        result = {}

        for val in self._feedback_choices:
            if not val['type'] in result:
                result[val['type']] = []

            if not val['name'] in choices:
                continue

            element = {
                'type': val['type'],
                'value': val['name'],
                'applicable_rating_values': [],
                'image_tag': '',
                'match': {},
            }

            if 'rating' in val:
                element['applicable_rating_values'] = val['rating']

            if 'image_tag' in val:
                element['image_tag'] = val['image_tag']

            if 'match' in val:
                element['match'] = val['match']

            result[val['type']].append(element)

        return result


@pytest.fixture
def dummy_choices(mockserver, db, mock_configs_service):
    def choices_getter():
        return list(
            db.feedback_choices.find(
                {},
                {
                    '_id': False,
                    'type': True,
                    'name': True,
                    'rating': True,
                    'image_tag': True,
                    'match': True,
                },
            ).sort('position'),
        )

    def configs_getter():
        return _fetch_config('SUPPORTED_FEEDBACK_CHOICES', mockserver.base_url)

    context = FeedbackChoicesContext(choices_getter, configs_getter)

    @mockserver.json_handler('/feedback/1.0/retrieve_choices')
    def mock_retrieve_choices(request):
        data = json.loads(request.get_data())
        zone_id = data['zone_id'] if data else None

        response = context.get_choices_for_zone(zone_id)
        return mockserver.make_response(json.dumps(response))

    return context


def _flatten_choices(choices_obj):
    result = []

    for key, values in choices_obj.items():
        result += values

    return result


def _fetch_config(config_name, base_url):
    def _request(http_method, path):
        url = '{}{}'.format(base_url, path)
        return requests.request(http_method, url)

    def post(method, json=None, data=None, params=None):
        return _request('POST', method)

    resp = post('configs-service/configs/values')
    return resp.json()['configs'][config_name]
