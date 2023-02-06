# pylint: disable=unused-variable,invalid-name,protected-access
import collections

import pytest

from generated import models as client_models

from crm_hub.generated.service.swagger import models
from crm_hub.logic.schedule import bulk_logger
from crm_hub.logic.schedule import bulk_logger as t


@pytest.mark.parametrize(
    'entity,sending_id,pg_table',
    [
        ('driver', '00000000000000000000000000000001', 'batch_11_22'),
        ('driver', '00000000000000000000000000000002', 'batch_33_44'),
        ('driver', '00000000000000000000000000000003', 'batch_55_66'),
        ('driver', '00000000000000000000000000000004', 'batch_66_77'),
        ('driver', '00000000000000000000000000000005', 'batch_12_21'),
        ('driver', '00000000000000000000000000000006', 'batch_55_66'),
        ('driver', '00000000000000000000000000000007', 'batch_33_44'),
    ],
)
@pytest.mark.pgsql('crm_hub', files=['drivers.sql'])
async def test_task(
        stq3_context, patch, entity, sending_id, pg_table, load_json,
):
    @patch('crm_hub.generated.stq3.yt_wrapper.plugin.AsyncYTClient.exists')
    async def exists(*args, **kwargs):
        return False

    @patch('crm_hub.generated.stq3.yt_wrapper.plugin.AsyncYTClient.create')
    async def create(*args, **kwargs):
        assert kwargs.get('recursive') and kwargs.get('ignore_existing')

    @patch(
        'crm_hub.generated.stq3.yt_wrapper.plugin.AsyncYTClient.write_table',
    )
    async def write_table(path, rows):
        pass

    @patch(
        'crm_hub.logic.experiments_logger'
        '.ExperimentsLogger._collect_report_extra',
    )
    async def _collect_report_extra():
        pass

    report_extra_full = load_json('report_extra.json')[sending_id]
    task_properties = [
        client_models.crm_scheduler.TaskProperty(
            scope_start=1, scope_end=1000, size=1000, offset=0,
        ),
    ]
    await bulk_logger.start_bulk_logger(
        stq3_context,
        sending_id,
        report_extra_full,
        task_properties,
        action_result=collections.defaultdict(int),
        task_ids_to_log=None,
    )

    expected = load_json('expected_records.json')[sending_id]
    actual = write_table.call['rows']

    assert actual == expected


@pytest.mark.parametrize(
    'subfilters, result',
    [
        (None, bulk_logger.EfficiencyPart.direct.value),
        ([], bulk_logger.EfficiencyPart.direct.value),
        (
            [models.api.FilterObject(column='efficiency_flag', value='1')],
            bulk_logger.EfficiencyPart.efficiency.value,
        ),
        (
            [models.api.FilterObject(column='efficiency_flag', value='0')],
            bulk_logger.EfficiencyPart.main.value,
        ),
    ],
)
async def test_efficiency_logging(subfilters, result):
    # pylint: disable=protected-access
    assert bulk_logger._get_efficiency_value(subfilters) == result


@pytest.mark.parametrize(
    'dtype, expected',
    [
        (t.StringType(), ['DataType', 'String']),
        (
            t.OptionalType(t.StringType()),
            ['OptionalType', ['DataType', 'String']],
        ),
        (t.ListType(t.StringType()), ['ListType', ['DataType', 'String']]),
        (
            t.DictType(t.StringType(), t.StringType()),
            ['DictType', ['DataType', 'String'], ['DataType', 'String']],
        ),
        (
            t.FieldType('name', t.StringType()),
            ['name', ['DataType', 'String']],
        ),
        (
            t.StructType(t.FieldType('name', t.StringType())),
            ['StructType', [['name', ['DataType', 'String']]]],
        ),
        (
            t.Schema(t.StructType(t.FieldType('name', t.StringType()))),
            {
                'StrictSchema': True,
                'Type': ['StructType', [['name', ['DataType', 'String']]]],
            },
        ),
    ],
)
def test_types_serialization(dtype, expected):
    assert dtype.serialize() == expected


@pytest.mark.parametrize(
    'dtype, expected',
    [
        (t.StringType(), {'type': 'string'}),
        (
            t.OptionalType(t.StringType()),
            {'type': 'string', 'required': False},
        ),
        (t.ListType(t.StringType()), {'type': 'any'}),
        (t.DictType(t.StringType(), t.StringType()), {'type': 'any'}),
        (
            t.FieldType('name', t.StringType()),
            {'name': 'name', 'type': 'string', 'required': True},
        ),
        (
            t.FieldType('name', t.OptionalType(t.StringType())),
            {'name': 'name', 'type': 'string', 'required': False},
        ),
        (
            t.StructType(t.FieldType('name', t.StringType())),
            [{'name': 'name', 'type': 'string', 'required': True}],
        ),
        (
            t.Schema(t.StructType(t.FieldType('name', t.StringType()))),
            [{'name': 'name', 'type': 'string', 'required': True}],
        ),
    ],
)
def test_types_serialization_v1(dtype, expected):
    assert dtype.serialize_v1() == expected


@pytest.mark.parametrize('entity_type', ('user', 'lavkauser'))
def test_user_and_lavkauser_schemas(entity_type):
    expected_yql_row_spec = {
        'StrictSchema': True,
        'Type': [
            'StructType',
            [
                ['experiment_name', ['DataType', 'String']],
                ['experiment_id', ['DataType', 'String']],
                ['channel', ['DataType', 'String']],
                ['creation_time', ['OptionalType', ['DataType', 'String']]],
                ['creation_day', ['OptionalType', ['DataType', 'String']]],
                ['unic_obj_id', ['OptionalType', ['DataType', 'String']]],
                ['comm_obj_id', ['DataType', 'String']],
                [
                    'comm_ids',
                    [
                        'OptionalType',
                        ['ListType', ['OptionalType', ['DataType', 'String']]],
                    ],
                ],
                ['group_id', ['DataType', 'String']],
                [
                    'properties',
                    [
                        'OptionalType',
                        [
                            'DictType',
                            ['DataType', 'String'],
                            ['DataType', 'String'],
                        ],
                    ],
                ],
                [
                    'comm_names',
                    [
                        'OptionalType',
                        ['ListType', ['OptionalType', ['DataType', 'String']]],
                    ],
                ],
                ['city', ['OptionalType', ['DataType', 'String']]],
                ['group_name', ['DataType', 'String']],
            ],
        ],
    }

    expected_v1_schema = [
        {'name': 'experiment_name', 'required': True, 'type': 'string'},
        {'name': 'experiment_id', 'required': True, 'type': 'string'},
        {'name': 'channel', 'required': True, 'type': 'string'},
        {'name': 'creation_time', 'required': False, 'type': 'string'},
        {'name': 'creation_day', 'required': False, 'type': 'string'},
        {'name': 'unic_obj_id', 'required': False, 'type': 'string'},
        {'name': 'comm_obj_id', 'required': True, 'type': 'string'},
        {'name': 'comm_ids', 'required': False, 'type': 'any'},
        {'name': 'group_id', 'required': True, 'type': 'string'},
        {'name': 'properties', 'required': False, 'type': 'any'},
        {'name': 'comm_names', 'required': False, 'type': 'any'},
        {'name': 'city', 'required': False, 'type': 'string'},
        {'name': 'group_name', 'required': True, 'type': 'string'},
    ]

    expected_columns = [row['name'] for row in expected_v1_schema]

    v1_schema, columns, yql_row_spec = t._get_schema(entity_type)
    assert v1_schema == expected_v1_schema
    assert columns == expected_columns

    if entity_type == 'user':
        assert yql_row_spec == expected_yql_row_spec
    else:
        assert yql_row_spec is None


def test_zuser_schemas():
    expected_yql_row_spec = {
        'StrictSchema': True,
        'Type': [
            'StructType',
            [
                ['zuser_id', ['DataType', 'String']],
                ['experiment_id', ['DataType', 'String']],
                ['experiment_name', ['DataType', 'String']],
                ['group_id', ['DataType', 'String']],
                ['group_name', ['DataType', 'String']],
                ['channel', ['DataType', 'String']],
                ['city', ['OptionalType', ['DataType', 'String']]],
                [
                    'comm_ids',
                    [
                        'OptionalType',
                        ['ListType', ['OptionalType', ['DataType', 'String']]],
                    ],
                ],
                [
                    'comm_names',
                    [
                        'OptionalType',
                        ['ListType', ['OptionalType', ['DataType', 'String']]],
                    ],
                ],
                ['creation_day', ['OptionalType', ['DataType', 'String']]],
                ['creation_time', ['OptionalType', ['DataType', 'String']]],
                [
                    'properties',
                    [
                        'OptionalType',
                        [
                            'DictType',
                            ['DataType', 'String'],
                            ['DataType', 'String'],
                        ],
                    ],
                ],
            ],
        ],
    }

    expected_v1_schema = [
        {'name': 'zuser_id', 'required': True, 'type': 'string'},
        {'name': 'experiment_id', 'required': True, 'type': 'string'},
        {'name': 'experiment_name', 'required': True, 'type': 'string'},
        {'name': 'group_id', 'required': True, 'type': 'string'},
        {'name': 'group_name', 'required': True, 'type': 'string'},
        {'name': 'channel', 'required': True, 'type': 'string'},
        {'name': 'city', 'required': False, 'type': 'string'},
        {'name': 'comm_ids', 'required': False, 'type': 'any'},
        {'name': 'comm_names', 'required': False, 'type': 'any'},
        {'name': 'creation_day', 'required': False, 'type': 'string'},
        {'name': 'creation_time', 'required': False, 'type': 'string'},
        {'name': 'properties', 'required': False, 'type': 'any'},
    ]

    expected_columns = [row['name'] for row in expected_v1_schema]

    v1_schema, columns, yql_row_spec = t._get_schema('zuser')
    assert v1_schema == expected_v1_schema
    assert columns == expected_columns
    assert yql_row_spec == expected_yql_row_spec


def test_driver_schemas():
    expected_yql_row_spec = None

    expected_v1_schema = [
        {'name': 'experiment_name', 'required': True, 'type': 'string'},
        {'name': 'channel', 'required': True, 'type': 'string'},
        {'name': 'experiment_type', 'required': True, 'type': 'string'},
        {'name': 'creation_time', 'required': True, 'type': 'string'},
        {'name': 'uniq_obj_id', 'required': False, 'type': 'string'},
        {'name': 'comm_obj_id', 'required': False, 'type': 'string'},
        {'name': 'comm_ids', 'required': False, 'type': 'string'},
        {'name': 'group_id', 'required': True, 'type': 'string'},
        {'name': 'creation_day', 'required': True, 'type': 'string'},
        {'name': 'experiment_id', 'required': True, 'type': 'string'},
        {'name': 'properties', 'required': False, 'type': 'any'},
        {'name': 'text', 'required': False, 'type': 'string'},
    ]

    expected_columns = [row['name'] for row in expected_v1_schema]

    v1_schema, columns, yql_row_spec = t._get_schema('driver')
    assert v1_schema == expected_v1_schema
    assert columns == expected_columns
    assert yql_row_spec == expected_yql_row_spec


def test_eatsuser_schemas():
    expected_yql_row_spec = {
        'StrictSchema': True,
        'Type': [
            'StructType',
            [
                ['comm_id', ['DataType', 'String']],
                ['eda_client_id', ['DataType', 'String']],
                ['phone_pd_id', ['DataType', 'String']],
                ['campaign_id', ['DataType', 'String']],
                ['issue_id', ['DataType', 'String']],
                ['campaign_step_id', ['DataType', 'String']],
                ['group_id', ['DataType', 'String']],
                ['channel', ['DataType', 'String']],
                ['global_control_flg', ['DataType', 'Bool']],
                ['local_control_flg', ['DataType', 'Bool']],
                ['utc_created_dttm', ['DataType', 'String']],
                [
                    'properties',
                    [
                        'OptionalType',
                        [
                            'DictType',
                            ['DataType', 'String'],
                            ['DataType', 'String'],
                        ],
                    ],
                ],
            ],
        ],
    }

    expected_v1_schema = [
        {'name': 'comm_id', 'required': True, 'type': 'string'},
        {'name': 'eda_client_id', 'required': True, 'type': 'string'},
        {'name': 'phone_pd_id', 'required': True, 'type': 'string'},
        {'name': 'campaign_id', 'required': True, 'type': 'string'},
        {'name': 'issue_id', 'required': True, 'type': 'string'},
        {'name': 'campaign_step_id', 'required': True, 'type': 'string'},
        {'name': 'group_id', 'required': True, 'type': 'string'},
        {'name': 'channel', 'required': True, 'type': 'string'},
        {'name': 'global_control_flg', 'required': True, 'type': 'boolean'},
        {'name': 'local_control_flg', 'required': True, 'type': 'boolean'},
        {'name': 'utc_created_dttm', 'required': True, 'type': 'string'},
        {'name': 'properties', 'required': False, 'type': 'any'},
    ]

    expected_columns = [row['name'] for row in expected_v1_schema]

    v1_schema, columns, yql_row_spec = t._get_schema('eatsuser')
    assert v1_schema == expected_v1_schema
    assert columns == expected_columns
    assert yql_row_spec == expected_yql_row_spec
