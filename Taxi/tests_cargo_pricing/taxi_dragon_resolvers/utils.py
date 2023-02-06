from tests_cargo_pricing import utils as global_utils
from tests_cargo_pricing.taxi_dragon_resolvers import models


def extract_calc_id(v1_or_v2_response):
    if not isinstance(v1_or_v2_response, dict):
        v1_or_v2_response = v1_or_v2_response.json()
    return v1_or_v2_response['calc_id']


def extract_previous_calc_id(v1_or_v2_response):
    if not isinstance(v1_or_v2_response, dict):
        v1_or_v2_response = v1_or_v2_response.json()
    if 'diagnostics' in v1_or_v2_response:
        return v1_or_v2_response['diagnostics']['calc_request'][
            'previous_calc_id'
        ]
    return v1_or_v2_response['request']['previous_calc_id']


def extract_events_kinds(events):
    kinds = set()
    for event in events:
        kinds.add(event['payload']['kind'])
    return kinds


def make_segment_points(segment: models.Segment):
    boilerplate = global_utils.get_default_calc_request()['waypoints']
    for waypoint in boilerplate:
        waypoint['claim_id'] = segment.id
    return boilerplate
