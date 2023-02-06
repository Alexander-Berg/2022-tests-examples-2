# pylint: disable=protected-access
import datetime
import json

import pytest

from replication.api import map_data


@pytest.mark.parametrize(
    'data, expected',
    [
        (
            {
                'items': [
                    {
                        'id': 'foo',
                        'target_name': 'test_sharded_rule_sharded_struct',
                        'data': map_data._dump_json(
                            {
                                '_id': 'foo',
                                'value_1': 'value_1',
                                'value_2': datetime.datetime(2019, 6, 24, 10),
                                'value_3': 3,
                            },
                        ),
                    },
                    {
                        'id': 'bar',
                        'target_name': 'test_map_data_columns',
                        'data': map_data._dump_json(
                            {
                                '_id': 'bar',
                                'value_2': datetime.datetime(2019, 6, 24, 10),
                                'value_3': 3,
                            },
                        ),
                    },
                ],
            },
            {
                'items': [
                    {
                        'id': 'foo',
                        'target_name': 'test_sharded_rule_sharded_struct',
                        'mapped_data': [
                            map_data._dump_json(
                                {
                                    'id': 'foo',
                                    'value_1': 'value_1',
                                    'value_2': datetime.datetime(
                                        2019, 6, 24, 10,
                                    ),
                                },
                            ),
                        ],
                    },
                    {
                        'id': 'bar',
                        'target_name': 'test_map_data_columns',
                        'mapped_data': [
                            map_data._dump_json(
                                {
                                    'id': 'bar',
                                    'value_1': None,
                                    'value_2': 1561370400,
                                },
                            ),
                        ],
                    },
                ],
            },
        ),
        (
            {
                'items': [
                    {
                        'id': 'foo',
                        'target_name': 'test_map_data_premap',
                        'data': map_data._dump_json(
                            {'id': 'foo', 'doc': 'premapper_skipped'},
                        ),
                    },
                ],
            },
            {
                'items': [
                    {
                        'id': 'foo',
                        'target_name': 'test_map_data_premap',
                        'mapped_data': [
                            map_data._dump_json(
                                {'id': 'foo', 'doc': 'premapper_not_skipped'},
                            ),
                        ],
                    },
                ],
            },
        ),
        pytest.param(
            {
                'items': [
                    {
                        'id': 'foo',
                        'target_name': 'test_map_data_premap',
                        'data': map_data._dump_json(
                            {'id': 'foo', 'doc': 'premapper_skipped'},
                        ),
                    },
                ],
            },
            {
                'items': [
                    {
                        'id': 'foo',
                        'target_name': 'test_map_data_premap',
                        'mapped_data': [
                            map_data._dump_json(
                                {'id': 'foo', 'doc': 'premapper_skipped'},
                            ),
                        ],
                    },
                ],
            },
            marks=pytest.mark.config(
                REPLICATION_WEB_CTL={
                    'runtime': {
                        'skip_premappers_target_names': [
                            'test_map_data_premap',
                        ],
                    },
                },
            ),
            id='map_data_skip_premapper_by_config',
        ),
    ],
)
async def test_map_data(replication_client, data, expected):
    response = await replication_client.post(
        '/map_data', data=json.dumps(data),
    )
    if response.status != 200:
        print(await response.text())
    assert response.status == 200
    assert await response.json() == expected
