import datetime

import mock
import pytest

from .common import load_test_json
from atlas.api.geosubventions.data_processors import prepare_rules_new_api
import atlas.service_utils.geosubventions.service
PREPARE_INPUT = load_test_json('prepare_rules_input.json')
PREPARE_EXPECTED_OUTPUT = load_test_json('prepare_rules_outputs.json')


class FakeFinder:
    def __init__(self, param):
        self.param = param

    def find(self, *args, **kwargs):
        return PREPARE_INPUT[self.param]


class FakeMongoConnection:
    def __init__(self, *args, **kwargs):
        pass
    def __getattr__(self, item):
        return FakeFinder('fake_' + item)


@pytest.mark.parametrize(
    "filter_zones,group_rates",
    [[True, True],
     [False, False]]
)
@mock.patch('atlas.service_utils.geosubventions.service.mongo', new=FakeMongoConnection())
def test_prepare_rules_new_api(filter_zones, group_rates):
    data = {
        'draft_rules': [
            {'categories': ['econom'],
             'interval': (datetime.datetime(1900, 1, 3, 20, 0), datetime.datetime(1900, 1, 3, 21, 0)),
             'rule_sum': 135,
             'rule_type': 'guarantee',
             'geoareas': ['mscmo_pol2'],
             'geoareas_names': ['pol2']},
            {'categories': ['econom'],
             'interval': (datetime.datetime(1900, 1, 7, 20, 0), datetime.datetime(1900, 1, 7, 21, 0)),
             'rule_sum': 185,
             'rule_type': 'guarantee',
             'geoareas': ['mscmo_pol2'],
             'geoareas_names': ['pol2']},
            {'categories': ['econom'],
             'interval': (datetime.datetime(1900, 1, 3, 20, 0), datetime.datetime(1900, 1, 3, 21, 0)),
             'rule_sum': 135,
             'rule_type': 'guarantee',
             'geoareas': ['mscmo_pol5'],
             'geoareas_names': ['pol5']},
            {'categories': ['econom'],
             'interval': (datetime.datetime(1900, 1, 7, 20, 0), datetime.datetime(1900, 1, 7, 21, 0)),
             'rule_sum': 185,
             'rule_type': 'guarantee',
             'geoareas': ['mscmo_pol5'],
             'geoareas_names': ['pol5']},
            {'categories': ['econom'],
             'interval': (datetime.datetime(1900, 1, 3, 20, 0), datetime.datetime(1900, 1, 3, 21, 0)),
             'rule_sum': 135,
             'rule_type': 'guarantee',
             'geoareas': ['mscmo_pol0'],
             'geoareas_names': ['pol0']},
            {'categories': ['econom'],
             'interval': (datetime.datetime(1900, 1, 7, 20, 0), datetime.datetime(1900, 1, 7, 21, 0)),
             'rule_sum': 185,
             'rule_type': 'guarantee',
             'geoareas': ['mscmo_pol0'],
             'geoareas_names': ['pol0']},
            {'categories': ['econom'],
             'interval': (datetime.datetime(1900, 1, 7, 14, 0), datetime.datetime(1900, 1, 7, 15, 0)),
             'rule_sum': 85,
             'rule_type': 'guarantee',
             'geoareas': ['mscmo_pol3'],
             'geoareas_names': ['pol3']},
            {'categories': ['econom'],
             'interval': (datetime.datetime(1900, 1, 6, 15, 0), datetime.datetime(1900, 1, 6, 16, 0)),
             'rule_sum': 170,
             'rule_type': 'guarantee',
             'geoareas': ['mscmo_pol3'],
             'geoareas_names': ['pol3']}],
        'tariffs': ['econom'],
        'activity_points': 100500,
        'tariff_zones': ['moscow', 'dolgoprudny', 'himki'],
        'budget': [
                {'interval': (datetime.datetime(1900, 1, 3, 20, 0), datetime.datetime(1900, 1, 3, 21, 0)),
                'stats':
                    {'mscmo_pol2': {'subv_cost': 20.0},
                     'mscmo_pol0': {'subv_cost': 30.0},
                      'mscmo_pol5': {'subv_cost':20.0}
                      }
                 },
            {'interval': (datetime.datetime(1900, 1, 7, 20, 0), datetime.datetime(1900, 1, 7, 21, 0)),
            'stats':{'mscmo_pol2': {'subv_cost': 40.0},
                     'mscmo_pol5': {'subv_cost': 40.0},
                     'mscmo_pol0': {'subv_cost': 50.0}
                     }
             },
            {'interval': (datetime.datetime(1900, 1, 7, 14, 0), datetime.datetime(1900, 1, 7, 15, 0)),
             'stats': {'mscmo_pol3': {'subv_cost': 60.0}}},
            {'interval': (datetime.datetime(1900, 1, 6, 15, 0), datetime.datetime(1900, 1, 6, 16, 0)),
             'stats': {'mscmo_pol3': {'subv_cost': 70.0}}}
            ]
    }

    data['polygons'] = PREPARE_INPUT['polygons']
    expected_poly_key = 'filtered' if filter_zones else 'unfiltered'
    #tz_polygons = get_zone_activation_polygons(data['tariff_zones'], tariffs=input['fake_tariffs'],
    #                                           geoareas=input['fake_zones'])
    # assert polygons_zones == output["polygon_zones"][expected_poly_key]

    formatted_result, extra_rules_to_close, rule_stats = prepare_rules_new_api(data, PREPARE_INPUT['start'],
                                                               PREPARE_INPUT['end'], PREPARE_INPUT['current_rules'],
                                                                               group_rates=group_rates,
                                                                               filter_zones=filter_zones)
    expected_rules_key = 'grouped' if filter_zones else 'ungrouped'
    assert formatted_result == PREPARE_EXPECTED_OUTPUT['rules'][expected_rules_key]
    assert extra_rules_to_close == PREPARE_EXPECTED_OUTPUT['expected_rules_to_close'][expected_poly_key]
    assert rule_stats == PREPARE_EXPECTED_OUTPUT['stats'][expected_poly_key]
