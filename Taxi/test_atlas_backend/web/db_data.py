import copy
import typing as tp


# see test_atlas_backend/web/static/default/pg_dimension.sql
DIMENSIONS = [
    {
        'dimension_id': 1,
        'dimension_name': 'city',
        'description': 'Город',
        'dimension_type': 'STR',
    },
    {
        'dimension_id': 2,
        'dimension_name': 'time',
        'description': 'Время',
        'dimension_type': 'DATETIME',
    },
    {
        'dimension_id': 3,
        'dimension_name': 'tariff',
        'description': 'Тариф',
        'dimension_type': 'STR',
    },
    {
        'dimension_id': 4,
        'dimension_name': 'tags',
        'description': 'Тэги',
        'dimension_type': 'ARRAY_OF_STR',
    },
    {
        'dimension_id': 5,
        'dimension_name': 'one_more_time',
        'description': 'Еще одно время',
        'dimension_type': 'DATETIME',
    },
    {
        'dimension_id': 6,
        'dimension_name': 'id',
        'description': 'Некий идентификатор',
        'dimension_type': 'INT',
    },
]

# see test_atlas_backend/web/static/default/pg_source.sql
SOURCES: tp.List[tp.Dict[str, tp.Any]] = [
    {
        'source_id': 1,
        'source_cluster': 'hahn',
        'source_type': 'chyt',
        'source_path': '//home/some/path',
        'source_name': 'first_test_source',
        'description': 'first test source',
        'is_partitioned': False,
        'partition_key': '',
        'partition_template': '',
        'author': '@source_author',
        'created_at': 1355314332,
        'changed_by': '@source_author',
        'changed_at': 1638483742,
        'data_updated_at': 946684800,
    },
    {
        'source_id': 2,
        'source_cluster': 'arnold',
        'source_type': 'chyt',
        'source_path': '//home/other/path',
        'source_name': 'second_test_source',
        'description': 'second test source',
        'is_partitioned': True,
        'partition_key': 'timestamp',
        'partition_template': '%Y-%m',
        'author': '@other_source_author',
        'created_at': 1293840000,
        'changed_by': '@source_changer',
        'changed_at': 1325376000,
        'data_updated_at': 1262304000,
    },
    {
        'source_id': 3,
        'source_cluster': 'atlastest_mdb',
        'source_type': 'clickhouse',
        'source_path': 'some_database.some_table',
        'source_name': 'third_test_source',
        'description': 'third test source',
        'is_partitioned': False,
        'partition_key': '',
        'partition_template': '',
        'author': '@source_author',
        'created_at': 1293840001,
        'changed_by': '@other_source_changer',
        'changed_at': 1325376001,
        'data_updated_at': 1262304001,
    },
    {
        'source_id': 4,
        'source_cluster': 'atlas_mdb',
        'source_type': 'clickhouse',
        'source_path': 'other_database.other_table',
        'source_name': 'fourth_test_source',
        'description': 'fourth test source',
        'is_partitioned': False,
        'partition_key': '',
        'partition_template': '',
        'author': '@another_source_author',
        'created_at': 1293840002,
        'changed_by': '@another_source_changer',
        'changed_at': 1325376002,
        'data_updated_at': 1262304002,
    },
]

# see test_atlas_backend/web/static/default/pg_column.sql
COLUMNS: tp.List[tp.Dict[str, tp.Any]] = [
    {
        'source_id': SOURCES[2]['source_id'],  # source_id == 3
        'column_name': 'record_id',
        'description': 'Идентификатор записи',
        'db_type': 'UInt32',
        'native_type': 'INT',
        'expression': '',
        'metadata': [
            {
                'key': 'Комментарий',
                'value': '"Здесь будет шутка"',
                'set_by': 'someuser',
            },
        ],
        'is_valid': True,
    },
    {
        'source_id': SOURCES[2]['source_id'],  # source_id == 3
        'column_name': 'city',
        'description': 'Город',
        'db_type': 'String',
        'native_type': 'STR',
        'expression': '',
        'metadata': [],
        'is_valid': True,
    },
    {
        'source_id': SOURCES[2]['source_id'],  # source_id == 3
        'column_name': 'dttm',
        'description': 'Время',
        'db_type': 'DateTime',
        'native_type': 'DATETIME',
        'expression': '',
        'metadata': [
            {'key': 'utc_offset', 'value': '3', 'set_by': 'otheruser'},
        ],
        'is_valid': True,
    },
    {
        'source_id': SOURCES[2]['source_id'],  # source_id == 3
        'column_name': 'dttm_utc',
        'description': 'Время UTC',
        'db_type': 'DateTime',
        'native_type': 'DATETIME',
        'expression': '{dttm} - 60 * 60 * 3',
        'metadata': [
            {'key': 'used_columns', 'value': '["dttm"]', 'set_by': ''},
            {'key': 'utc_offset', 'value': '0', 'set_by': 'otheruser'},
        ],
        'is_valid': True,
    },
    {
        'source_id': SOURCES[2]['source_id'],  # source_id == 3
        'column_name': 'quadkey',
        'description': 'Идентификатор тайтла',
        'db_type': 'String',
        'native_type': 'STR',
        'expression': '',
        'metadata': [{'key': 'length', 'value': '15', 'set_by': 'thirduser'}],
        'is_valid': True,
    },
    {
        'source_id': SOURCES[2]['source_id'],  # source_id == 3
        'column_name': 'datetime_utc',
        'description': 'Старое время',
        'db_type': 'DateTime',
        'native_type': 'DATETIME',
        'expression': '{datetime} + 3600',
        'metadata': [
            {'key': 'used_columns', 'value': '["datetime"]', 'set_by': ''},
            {'key': 'utc_offset', 'value': '0', 'set_by': 'thirduser'},
        ],
        'is_valid': False,
    },
    {
        'source_id': SOURCES[2]['source_id'],  # source_id == 3
        'column_name': 'one_more_datetime',
        'description': 'Еще одно время',
        'db_type': 'Nullable(Nothing)',
        'native_type': 'UNSUPPORTED_TYPE',
        'expression': 'NULL',
        'metadata': [
            {'key': 'used_columns', 'value': '[]', 'set_by': ''},
            {'key': 'o_key', 'value': '"o_value"', 'set_by': 'o_user'},
        ],
        'is_valid': True,
    },
    {
        'source_id': SOURCES[3]['source_id'],  # source_id == 4
        'column_name': 'key',
        'description': 'Ключ',
        'db_type': 'String',
        'native_type': 'STR',
        'expression': '',
        'metadata': [],
        'is_valid': True,
    },
    {
        'source_id': SOURCES[3]['source_id'],  # source_id == 4
        'column_name': 'value',
        'description': 'Значение',
        'db_type': 'String',
        'native_type': 'STR',
        'expression': '',
        'metadata': [],
        'is_valid': True,
    },
]

# see test_atlas_backend/web/static/default/pg_col_dim_relation.sql
COLUMNS_DIMENSIONS_REL = [
    {
        'source_id': COLUMNS[1]['source_id'],  # source_id == 3
        'column_name': COLUMNS[1]['column_name'],  # column_name == 'city'
        'dimension_id': DIMENSIONS[0]['dimension_id'],  # dimension_id == 1
    },
    {
        'source_id': COLUMNS[2]['source_id'],  # source_id == 3
        'column_name': COLUMNS[2]['column_name'],  # column_name == 'dttm'
        'dimension_id': DIMENSIONS[1]['dimension_id'],  # dimension_id == 2
    },
    {
        'source_id': COLUMNS[2]['source_id'],  # source_id == 3
        'column_name': COLUMNS[2]['column_name'],  # column_name == 'dttm'
        'dimension_id': DIMENSIONS[4]['dimension_id'],  # dimension_id == 5
    },
    {
        'source_id': COLUMNS[0]['source_id'],  # source_id == 3
        'column_name': COLUMNS[0]['column_name'],  # column_name == 'record_id'
        'dimension_id': DIMENSIONS[5]['dimension_id'],  # dimension_id == 6
    },
]

# see test_atlas_backend/web/static/default/pg_metric_group.sql
GROUPS = [
    {
        'group_id': 1,
        'ru_name': 'Метрики1',
        'en_name': 'Metrics1',
        'ru_description': 'Группа с метриками',
        'en_description': 'Group with metrics',
    },
    {
        'group_id': 2,
        'ru_name': 'Метрики2',
        'en_name': 'Metrics2',
        'ru_description': 'Еще одна группа с метриками',
        'en_description': 'One more metric group',
    },
]

# see test_atlas_backend/web/static/default/pg_metric.sql
METRICS = [
    {
        'metric_id': 1,
        'ru_name': 'Метрика1',
        'en_name': 'Metric1',
        'ru_description': 'Описание метрики',
        'en_description': 'Metric description',
        'group_id': GROUPS[0]['group_id'],  # group_id == 1
    },
    {
        'metric_id': 2,
        'ru_name': 'Метрика2',
        'en_name': 'Metric2',
        'ru_description': 'Описание метрики2',
        'en_description': 'Metric2 description',
        'group_id': GROUPS[1]['group_id'],  # group_id == 2
    },
    {
        'metric_id': 3,
        'ru_name': 'Еще одна метрика',
        'en_name': 'One more metric',
        'ru_description': 'Описание метрики3',
        'en_description': 'Metric3 description',
        'group_id': GROUPS[0]['group_id'],  # group_id == 1
    },
]

# see test_atlas_backend/web/static/default/pg_metric_instance.sql
INSTANCES = [
    {
        'metric_id': METRICS[0]['metric_id'],  # metric_id == 1
        'source_id': SOURCES[2]['source_id'],  # source_id == 3
        'expression': 'MAX({id} + {time})',
        'use_final': False,
        'filters': ['{id} > 100'],
        'default_time_dimension_id': 0,
    },
    {
        'metric_id': METRICS[1]['metric_id'],  # metric_id == 2
        'source_id': SOURCES[2]['source_id'],  # source_id == 3
        'expression': 'MIN({id})',
        'use_final': False,
        'filters': [
            '{time} >= toDateTime(\'2022-01-01 00:00:00\')',
            '{id} > 50',
        ],
        'default_time_dimension_id': 0,
    },
    {
        'metric_id': METRICS[2]['metric_id'],  # metric_id == 3
        'source_id': SOURCES[0]['source_id'],  # source_id == 1
        'expression': '1',
        'use_final': False,
        'filters': [],
        'default_time_dimension_id': 0,
    },
]

# вспомогательный словарь, не соответствует ни одной таблице в БД
# № metric_id source_id dimension_id
# 0         1         3            1
# 1         1         3            2
# 2         1         3            5
# 3         2         3            1
# 4         2         3            2
# 5         2         3            5
INSTANCES_DIMENSIONS_REL = []
for instance in INSTANCES:
    source_id = instance['source_id']
    for relation in COLUMNS_DIMENSIONS_REL:
        if relation['source_id'] != source_id:
            continue
        INSTANCES_DIMENSIONS_REL.append(
            {
                'metric_id': instance['metric_id'],
                'source_id': source_id,
                'dimension_id': relation['dimension_id'],
            },
        )


# see test_atlas_backend/web/static/default/pg_default_time_dimension.sql
DEFAULT_TIME_DIMENSIONS = [
    {
        # metric_id == 1
        'metric_id': INSTANCES_DIMENSIONS_REL[1]['metric_id'],
        # source_id == 3
        'source_id': INSTANCES_DIMENSIONS_REL[1]['source_id'],
        # dimension_id == 2
        'dimension_id': INSTANCES_DIMENSIONS_REL[1]['dimension_id'],
    },
    {
        # metric_id == 2
        'metric_id': INSTANCES_DIMENSIONS_REL[5]['metric_id'],
        # source_id == 3
        'source_id': INSTANCES_DIMENSIONS_REL[5]['source_id'],
        # dimension_id == 5
        'dimension_id': INSTANCES_DIMENSIONS_REL[5]['dimension_id'],
    },
]

# see test_atlas_backend/web/static/default/pg_solomon_metric_delivery.sql
DELIVERY_SETTINGS = [
    {
        'delivery_id': 1,
        'metric_id': INSTANCES[0]['metric_id'],  # metric_id == 1
        'source_id': INSTANCES[0]['source_id'],  # source_id == 3
        'duration': '5m',
        'grid': '1m',
        'sensor': 'id1',  # f'id{delivery_id}'
    },
    {
        'delivery_id': 2,
        'metric_id': INSTANCES[0]['metric_id'],  # metric_id == 1
        'source_id': INSTANCES[0]['source_id'],  # source_id == 3
        'duration': '0s',
        'grid': '5m',
        'sensor': 'id2',  # f'id{delivery_id}'
    },
]

# see test_atlas_backend/web/static/default/pg_solomon_metric_dimension.sql
SOLOMON_METRIC_DIMENSION = [
    {
        'delivery_id': DELIVERY_SETTINGS[0]['delivery_id'],  # delivery_id == 1
        'source_id': DELIVERY_SETTINGS[0]['source_id'],  # source_id == 3
        'dimension_id': DIMENSIONS[0]['dimension_id'],  # dimension_id == 1
    },
    {
        'delivery_id': DELIVERY_SETTINGS[0]['delivery_id'],  # delivery_id == 1
        'source_id': DELIVERY_SETTINGS[0]['source_id'],  # source_id == 3
        'dimension_id': DIMENSIONS[4]['dimension_id'],  # dimension_id == 5
    },
    {
        'delivery_id': DELIVERY_SETTINGS[1]['delivery_id'],  # delivery_id == 2
        'source_id': DELIVERY_SETTINGS[1]['source_id'],  # source_id == 3
        'dimension_id': DIMENSIONS[4]['dimension_id'],  # dimension_id == 5
    },
]


def get_objects(
        collection: tp.List[tp.Dict[str, tp.Any]], **filters: tp.Any,
) -> tp.List[tp.Dict[str, tp.Any]]:
    res: tp.List[tp.Dict[str, tp.Any]] = []
    for item in collection:
        for key, value in filters.items():
            if callable(value):
                if not value(item[key]):
                    break
            elif item[key] != value:
                break
        else:
            res.append(copy.deepcopy(item))
    return res
