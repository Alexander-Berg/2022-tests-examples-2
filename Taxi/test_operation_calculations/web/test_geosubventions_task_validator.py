import contextlib

import pytest

from taxi.codegen import swaggen_serialization as utils

from operation_calculations.generated.service.swagger.models import (
    api as api_module,
)
from operation_calculations.geosubventions import common
from operation_calculations.geosubventions import validators


@contextlib.contextmanager
def does_not_raise():
    yield


@pytest.mark.parametrize(
    'rush_hours, polygons, draft_rules, expectation',
    (
        pytest.param(
            {
                '1': [
                    {
                        'end_time': '23:00',
                        'start_time': '23:00',
                        'end_dayofweek': 2,
                        'start_dayofweek': 2,
                    },
                    {
                        'end_time': '23:00',
                        'start_time': '23:00',
                        'end_dayofweek': 2,
                        'start_dayofweek': 2,
                    },
                    {
                        'end_time': '09:00',
                        'start_time': '20:00',
                        'end_dayofweek': 1,
                        'start_dayofweek': 1,
                    },
                ],
                '2': [],
            },
            None,
            None,
            pytest.raises(
                common.GeosubventionsInvalidTaskError,
                match='Problems in rush_hours:\nDoubled interval '
                '{"start_dayofweek": 2, "start_time": "23:00",'
                ' "end_dayofweek": 2, "end_time": "23:00"}\nIntervals'
                ' intersection {"start_dayofweek": 1, "start_time": '
                '"20:00", "end_dayofweek": 1, "end_time": "09:00"} '
                '{"start_dayofweek": 2, "start_time": "23:00", '
                '"end_dayofweek": 2, "end_time": "23:00"}\nIntervals'
                ' intersection {"start_dayofweek": 2, "start_time": '
                '"23:00", "end_dayofweek": 2, "end_time": "23:00"} '
                '{"start_dayofweek": 1, "start_time": "20:00", '
                '"end_dayofweek": 1, "end_time": "09:00"}\nNo '
                'intervals for group 2',
            ),
        ),
        pytest.param(
            {
                '1': [
                    {
                        'end_time': '11:00',
                        'start_time': '09:00',
                        'end_dayofweek': 1,
                        'start_dayofweek': 1,
                    },
                    {
                        'end_time': '23:00',
                        'start_time': '20:00',
                        'end_dayofweek': 2,
                        'start_dayofweek': 2,
                    },
                    {
                        'end_time': '09:30',
                        'start_time': '20:00',
                        'end_dayofweek': 1,
                        'start_dayofweek': 6,
                    },
                ],
            },
            None,
            None,
            pytest.raises(
                common.GeosubventionsInvalidTaskError,
                match='Problems in rush_hours:\nIntervals '
                'intersection {"start_dayofweek": 6, '
                '"start_time": "20:00", "end_dayofweek": 1, '
                '"end_time": "09:30"} {"start_dayofweek": 1, '
                '"start_time": "09:00", "end_dayofweek": 1, '
                '"end_time": "11:00"}',
            ),
        ),
        pytest.param(
            {
                '1': [
                    {
                        'end_time': '23:00',
                        'start_time': '23:00',
                        'end_dayofweek': 2,
                        'start_dayofweek': 2,
                    },
                ],
            },
            [
                {
                    'id': 'id0',
                    'type': 'Feature',
                    'properties': {'name': 'pol0'},
                    'geometry': {
                        'type': 'Polygon',
                        'coordinates': [
                            [[-400, 500], [600, 900], [0, 1], [0, 1]],
                        ],
                    },
                },
            ],
            None,
            pytest.raises(utils.ValidationError),
        ),
        pytest.param(
            {
                '1': [
                    {
                        'end_time': '23:00',
                        'start_time': '23:00',
                        'end_dayofweek': 2,
                        'start_dayofweek': 2,
                    },
                ],
            },
            [
                {
                    'id': 'id0',
                    'type': 'Feature',
                    'properties': {'name': 'pol0'},
                    'geometry': {
                        'type': 'Polygon',
                        'coordinates': [[[0, 0], [0, 1], [0, 1], [0, 1]]],
                    },
                },
                {
                    'id': 'id0',
                    'type': 'Feature',
                    'properties': {'name': 'pol2'},
                    'geometry': {
                        'type': 'Polygon',
                        'coordinates': [[[1, 0], [0, 1], [1, 1], [1, 0]]],
                    },
                },
                {
                    'id': 'id3',
                    'type': 'Feature',
                    'properties': {'name': 'pol2'},
                    'geometry': {
                        'type': 'Polygon',
                        'coordinates': [[[0, 0], [0, 1], [1, 1], [0, 0]]],
                    },
                },
                {
                    'id': 'id4',
                    'type': 'Feature',
                    'properties': {'name': 'pol4'},
                    'geometry': {
                        'type': 'Polygon',
                        'coordinates': [[[0, 0], [0, 1], [1, 1], [1, 0]]],
                    },
                },
            ],
            None,
            pytest.raises(
                common.GeosubventionsInvalidTaskError,
                match='Problems in polygons:\nLast coord != first '
                'for poly pol4\nPolygon pol0 invalid\nSeveral'
                ' polygons with id id0\nSeveral polygons '
                'with name pol2',
            ),
        ),
        pytest.param(
            {
                '1': [
                    {
                        'end_time': '23:00',
                        'start_time': '23:00',
                        'end_dayofweek': 2,
                        'start_dayofweek': 2,
                    },
                ],
            },
            [
                {
                    'id': 'id0',
                    'type': 'Feature',
                    'properties': {'name': 'pol0'},
                    'geometry': {
                        'type': 'Polygon',
                        'coordinates': [
                            [[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]],
                        ],
                    },
                },
            ],
            [
                {
                    'interval': {
                        'end_time': '23:00',
                        'start_time': '23:00',
                        'end_dayofweek': 2,
                        'start_dayofweek': 2,
                    },
                    'rule_sum': 200,
                    'rule_type': 'guarantee',
                    'geoareas': ['id0'],
                    'categories': ['econom'],
                },
                {
                    'interval': {
                        'end_time': '23:00',
                        'start_time': '23:00',
                        'end_dayofweek': 2,
                        'start_dayofweek': 2,
                    },
                    'rule_sum': 200,
                    'rule_type': 'guarantee',
                    'geoareas': ['id0', 'id2'],
                    'categories': ['econom'],
                },
                {
                    'interval': {
                        'end_time': '23:00',
                        'start_time': '23:00',
                        'end_dayofweek': 3,
                        'start_dayofweek': 2,
                    },
                    'rule_sum': 200,
                    'rule_type': 'guarantee',
                    'geoareas': ['id0'],
                    'categories': ['econom'],
                },
            ],
            pytest.raises(
                common.GeosubventionsInvalidTaskError,
                match='Problems in draft_rules:\nDoubled rules for interval '
                '{"start_dayofweek": 2, "end_dayofweek": 2, '
                '"start_time": "23:00", "end_time": "23:00"} '
                'and geo id0\nUnknown geoarea id in draft_rules: id2'
                '\nUnknown interval in draft_rules: {"start_dayofweek":'
                ' 2, "start_time": "23:00", "end_dayofweek": 3, '
                '"end_time": "23:00"}\n',
            ),
        ),
        pytest.param(
            {
                '1': [
                    {
                        'end_time': '23:00',
                        'start_time': '23:00',
                        'end_dayofweek': 2,
                        'start_dayofweek': 2,
                    },
                ],
            },
            [
                {
                    'id': 'id0',
                    'type': 'Feature',
                    'properties': {'name': 'pol0'},
                    'geometry': {
                        'type': 'Polygon',
                        'coordinates': [
                            [[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]],
                        ],
                    },
                },
            ],
            [
                {
                    'interval': {
                        'end_time': '23:00',
                        'start_time': '23:00',
                        'end_dayofweek': 2,
                        'start_dayofweek': 2,
                    },
                    'rule_sum': 200,
                    'rule_type': 'guarantee',
                    'geoareas': ['id0'],
                    'categories': ['econom'],
                },
            ],
            does_not_raise(),
        ),
    ),
)
def test_task_validators(
        load_json, draft_rules, polygons, rush_hours, expectation,
):
    with expectation:
        polygons_api = (
            [api_module.PolygonItem.deserialize(poly) for poly in polygons]
            if polygons
            else None
        )
        draft_rules_api = (
            [
                api_module.GeoSubventionDraftRule.deserialize(rule)
                for rule in draft_rules
            ]
            if draft_rules
            else None
        )
        validator = validators.TaskValidator(
            draft_rules=draft_rules_api,
            polygons=polygons_api,
            rush_hours=rush_hours,
        )
        validator.run_check()
