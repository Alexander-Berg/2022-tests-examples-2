# flake8: noqa
# pylint: disable=W0621
import datetime
import typing as tp

import pytest

from atlas_backend.internal.metrics.query_proc import parameter_parser
from atlas_backend.internal.metrics.query_proc import parameter_types
from atlas_backend.internal.metrics.query_proc import query_builder
from atlas_backend.internal.metrics.query_proc import source_renderer
from atlas_backend.internal.sources.models import base_source_model


def test_build_template_with_selector_param():
    text = """--REGISTER_PARAM Selector car_class
Car class: {{ params.car_class.value }}
Filter: {{ filter.car_class() }}"""

    registered_params = parameter_parser.parse_registered_parameters(text)
    params = parameter_parser.extract_parameter_values(
        {'car_class': 'econom'}, registered_params,
    )
    result = query_builder.render(text, params)
    assert (
        result
        == """--REGISTER_PARAM Selector car_class
Car class: econom
Filter: car_class = 'econom'"""
    )


def test_build_template_with_all_user_param_types():
    text = (
        '\n'
        '--REGISTER_PARAM Selector car_class\n'
        '--REGISTER_PARAM MultiSelector cities\n'
        '--REGISTER_PARAM MultiSelector groceries_ids\n'
        '--REGISTER_PARAM DateRange ts\n'
        '--REGISTER_PARAM NumericInterval ni\n'
        '--REGISTER_PARAM TimeBucketGrid tbg\n'
        '--REGISTER_PARAM ContainsSelector tags\n'
        '--REGISTER_PARAM CorpType corp_type\n'
        '--REGISTER_PARAM PaymentType payment_type\n'
        '--REGISTER_PARAM CellSizeParameter cell_size\n'
        '--REGISTER_PARAM Numeric numeric_param\n'
        'Car class: {{ params.car_class.value }}\n'
        'Cities: {{ params.cities.value }}\n'
        'DateRange: start={{ params.ts.from_ts }} end={{ params.ts.to_ts }}\n'
        'NumericInterval: from={{ params.ni.value.from }} to={{ params.ni.value.to }}\n'
        'TimeBucketGrid: every {{ params.tbg.bucket_size }} seconds starting from {{ params.tbg.start_offset }}\n'
        'Tags: {{ params.tags.value }}\n'
        'CorpType: {{ params.corp_type.value }}\n'
        'PaymentType: {{ params.payment_type.value }}\n'
        'Groceries_ids: {{ params.groceries_ids.value }}\n'
        'CellSize: {{params.cell_size.value}}\n'
        'NumericParam: {{params.numeric_param.value}}\n'
        '\n'
        'Filters:\n'
        '{{ filter.car_class() }}\n'
        '{{ filter.cities() }}\n'
        '{{ filter.ts() }}\n'
        '{{ filter.ni() }}\n'
        '{{ filter.tags() }}\n'
        '{{ filter.corp_type() }}\n'
        '{{ filter.payment_type() }}\n'
        '{{ filter.groceries_ids() }}\n'
        '{{ filter.numeric_param() }}\n'
    )

    registered_params = parameter_parser.parse_registered_parameters(text)

    input_parameters = {
        'car_class': 'econom',
        'cities': ['Москва', 'Казань', 'Город с \'кавычкой'],
        'groceries_ids': [1, 2, 3],
        'ts': {'from': 1561476900, 'to': 1561476950},
        'ni': {'from': 0.1, 'to': 0.2},
        'tbg': {'bucket_size': 40, 'start_offset': 40},
        'tags': 'super_tag',
        'corp_type': 'only_corp',
        'payment_type': 'card',
        'cell_size': 15,
        'numeric_param': 42,
    }
    params = parameter_parser.extract_parameter_values(
        input_parameters, registered_params,
    )
    result = query_builder.render(text, params)
    assert (
        result
        == """
--REGISTER_PARAM Selector car_class
--REGISTER_PARAM MultiSelector cities
--REGISTER_PARAM MultiSelector groceries_ids
--REGISTER_PARAM DateRange ts
--REGISTER_PARAM NumericInterval ni
--REGISTER_PARAM TimeBucketGrid tbg
--REGISTER_PARAM ContainsSelector tags
--REGISTER_PARAM CorpType corp_type
--REGISTER_PARAM PaymentType payment_type
--REGISTER_PARAM CellSizeParameter cell_size
--REGISTER_PARAM Numeric numeric_param
Car class: econom
Cities: ('Москва', 'Казань', "Город с 'кавычкой")
DateRange: start=1561476900 end=1561476950
NumericInterval: from=0.1 to=0.2
TimeBucketGrid: every 40 seconds starting from 40
Tags: super_tag
CorpType: only_corp
PaymentType: card
Groceries_ids: (1, 2, 3)
CellSize: 15
NumericParam: 42

Filters:
car_class = 'econom'
cities IN ('Москва', 'Казань', 'Город с \\\'кавычкой')
ts BETWEEN 1561476900 AND 1561476950
(0.1 <= ni AND ni <= 0.2)
has(tags, 'super_tag')
corp_type IN ('food', 'corp')
payment_type = 'card'
groceries_ids IN (1, 2, 3)
numeric_param = 42"""
    )


def test_render_table_path():
    text = """table_path: {{ table_path() }}
table_path_final: {{ table_path('FINAL') }}"""
    params = {
        'table_path': parameter_types.TablePathParameter(
            name='table_path', value='test_db.test_table',
        ),
    }
    result = query_builder.render(text, params)
    assert (
        result
        == """table_path: test_db.test_table
table_path_final: test_db.test_table FINAL"""
    )


def test_render_quadkey():
    text = """quadkey_substring: {{ quadkey('quadkey123') }}"""
    params = {'cell_size': parameter_types.CellSizeParameter('cell_size', 17)}
    result = query_builder.render(text, params)
    assert result == """quadkey_substring: substring(quadkey123, 1, 17)"""


def test_render_quadkey_none_cell_size():
    text = """quadkey_substring: {{ quadkey('quadkey123') }}"""
    params = {
        'cell_size': parameter_types.CellSizeParameter('cell_size', None),
    }
    result = query_builder.render(text, params)
    assert result == """quadkey_substring: quadkey123"""


@pytest.fixture
def blocked_query_text():
    return """
--DEFINE_ATLAS_BLOCK REPORT::MAP START
<map>
$ATLAS_BLOCK(COMMON)
--DEFINE_ATLAS_BLOCK REPORT::MAP END

--DEFINE_ATLAS_BLOCK REPORT::PLOT START
<plot>
$ATLAS_BLOCK(COMMON)
--DEFINE_ATLAS_BLOCK REPORT::PLOT END

--DEFINE_ATLAS_BLOCK REPORT::DETAIL_DATA START
<detailed>
$ATLAS_BLOCK(COMMON)
--DEFINE_ATLAS_BLOCK REPORT::DETAIL_DATA END

--DEFINE_ATLAS_BLOCK COMMON START
<common>
--DEFINE_ATLAS_BLOCK COMMON END"""


def test_build_map_tempate(blocked_query_text):
    query = query_builder.build_map_template(blocked_query_text)
    assert query == '<map>\n<common>'


def test_build_plot_tempate(blocked_query_text):
    query = query_builder.build_plot_template(blocked_query_text)
    assert query == '<plot>\n<common>'


def test_build_detail_data_tempate(blocked_query_text):
    query = query_builder.build_detail_data_template(blocked_query_text)
    assert query == '<detailed>\n<common>'


@pytest.fixture
def sources(
        source_dict: tp.Dict[str, tp.Any],
) -> tp.Dict[str, source_renderer.SourceRenderer]:
    source = base_source_model.Source.from_db_record(**source_dict)
    source_name = source_dict['source_name']
    return {source_name: source_renderer.SourceRenderer(source)}


DEFAULT_SOURCE_DICT = {
    'source_id': 1000000,
    'source_type': 'chyt',
    'source_cluster': 'hahn',
    'source_path': '//home/some/path',
    'source_name': 'test_source',
    'description': 'test source',
    'is_partitioned': False,
    'partition_key': '',
    'partition_template': '',
    'author': '@source_author',
    'created_at': 1640044800,  # 2021-12-21 00:00:00
    'changed_by': '@source_author',
    'changed_at': 1640044800,  # 2021-12-21 00:00:00
    'data_updated_at': 1609459200,  # 2021-01-01 00:00:00
}


DEFAULT_CH_SOURCE_DICT = {
    'source_id': 1000001,
    'source_type': 'clickhouse',
    'source_cluster': 'atlastest_mdb',
    'source_path': 'db.tb',
    'source_name': 'test_ch_source',
    'description': 'test ch source',
    'is_partitioned': False,
    'partition_key': '',
    'partition_template': '',
    'author': '@source_author',
    'created_at': 1640044800,  # 2021-12-21 00:00:00
    'changed_by': '@source_author',
    'changed_at': 1640044800,  # 2021-12-21 00:00:00
    'data_updated_at': 1609459200,  # 2021-01-01 00:00:00
}


class TestTemplatesWithSources:
    @pytest.mark.parametrize('source_dict', (DEFAULT_SOURCE_DICT,))
    @pytest.mark.parametrize(
        'from_, to_',
        [
            # две минуты
            (
                datetime.datetime.fromisoformat('2021-12-14 23:59:00+00:00'),
                datetime.datetime.fromisoformat('2021-12-15 00:01:00+00:00'),
            ),
            # 11 месяцев
            (
                datetime.datetime.fromisoformat('2021-01-14 23:59:00+00:00'),
                datetime.datetime.fromisoformat('2021-12-15 00:01:00+00:00'),
            ),
            # 20 лет
            (
                datetime.datetime.fromisoformat('2001-12-14 23:59:00+00:00'),
                datetime.datetime.fromisoformat('2021-12-15 00:01:00+00:00'),
            ),
        ],
    )
    async def test_not_partitioned_source(
            self,
            source_dict: tp.Dict[str, tp.Any],
            sources: tp.Dict[str, source_renderer.SourceRenderer],
            from_: datetime.datetime,
            to_: datetime.datetime,
    ) -> None:

        text = (
            '--REGISTER_PARAM DateRange ts\n'
            '--REGISTER_SOURCE test_source\n'
            '{{ sources.test_source.tables(params.ts) }}'
        )

        inputs = {
            'ts': {'from': int(from_.timestamp()), 'to': int(to_.timestamp())},
        }

        registered_params = parameter_parser.parse_registered_parameters(text)
        params = parameter_parser.extract_parameter_values(
            inputs=inputs, registered_params=registered_params,
        )

        result = query_builder.render(text, params, sources)

        assert result == (
            '--REGISTER_PARAM DateRange ts\n'
            '--REGISTER_SOURCE test_source\n'
            '`//home/some/path`'
        )

    @pytest.mark.parametrize(
        'source_dict',
        (
            {
                **DEFAULT_SOURCE_DICT,
                'is_partitioned': True,
                'partition_key': 'ts',
                'partition_template': '%Y-%m',
            },
        ),
    )
    @pytest.mark.parametrize(
        'from_, to_, source_result',
        [
            # две минуты
            (
                datetime.datetime.fromisoformat('2021-12-14 23:59:00+00:00'),
                datetime.datetime.fromisoformat('2021-12-15 00:01:00+00:00'),
                '`//home/some/path/2021-12`',
            ),
            # 11 месяцев
            (
                datetime.datetime.fromisoformat('2021-01-14 23:59:00+00:00'),
                datetime.datetime.fromisoformat('2021-12-15 00:01:00+00:00'),
                'concatYtTablesRange(\'//home/some/path\', \'2021-01\', \'2021-12\')',
            ),
            # 20 лет
            (
                datetime.datetime.fromisoformat('2001-12-14 23:59:00+00:00'),
                datetime.datetime.fromisoformat('2021-12-15 00:01:00+00:00'),
                'concatYtTablesRange(\'//home/some/path\', \'2001-12\', \'2021-12\')',
            ),
        ],
    )
    async def test_month_partitioned_source(
            self,
            source_dict: tp.Dict[str, tp.Any],
            sources: tp.Dict[str, source_renderer.SourceRenderer],
            from_: datetime.datetime,
            to_: datetime.datetime,
            source_result: str,
    ) -> None:

        text = (
            '--REGISTER_PARAM DateRange ts\n'
            '--REGISTER_SOURCE test_source\n'
            '{{ sources.test_source.tables(params.ts) }}'
        )

        inputs = {
            'ts': {'from': int(from_.timestamp()), 'to': int(to_.timestamp())},
        }

        registered_params = parameter_parser.parse_registered_parameters(text)
        params = parameter_parser.extract_parameter_values(
            inputs=inputs, registered_params=registered_params,
        )

        result = query_builder.render(text, params, sources)
        test_value = (
            '--REGISTER_PARAM DateRange ts\n' '--REGISTER_SOURCE test_source\n'
        ) + source_result

        assert result == test_value

    @pytest.mark.parametrize(
        'source_dict',
        (
            {
                **DEFAULT_SOURCE_DICT,
                'is_partitioned': True,
                'partition_key': 'ts',
                'partition_template': '%Y-%m',
            },
        ),
    )
    @pytest.mark.parametrize(
        'from_, to_, source_result',
        [
            # середина месяца
            (
                datetime.datetime.fromisoformat('2021-12-14 12:00:00+00:00'),
                datetime.datetime.fromisoformat('2021-12-15 12:00:00+00:00'),
                '`//home/some/path/2021-12`',
            ),
            # начало месяца
            (
                datetime.datetime.fromisoformat('2021-12-01 12:00:00+00:00'),
                datetime.datetime.fromisoformat('2021-12-02 12:00:00+00:00'),
                'concatYtTablesRange(\'//home/some/path\', \'2021-11\', \'2021-12\')',
            ),
            # начало месяца, граница
            (
                datetime.datetime.fromisoformat('2021-12-01 23:59:59+00:00'),
                datetime.datetime.fromisoformat('2021-12-02 12:00:00+00:00'),
                'concatYtTablesRange(\'//home/some/path\', \'2021-11\', \'2021-12\')',
            ),
            # начало месяца, граница
            (
                datetime.datetime.fromisoformat('2021-12-02 00:00:00+00:00'),
                datetime.datetime.fromisoformat('2021-12-02 12:00:00+00:00'),
                '`//home/some/path/2021-12`',
            ),
            # конец месяца
            (
                datetime.datetime.fromisoformat('2021-12-30 12:00:00+00:00'),
                datetime.datetime.fromisoformat('2021-12-31 12:00:00+00:00'),
                'concatYtTablesRange(\'//home/some/path\', \'2021-12\', \'2022-01\')',
            ),
            # конец месяца, граница
            (
                datetime.datetime.fromisoformat('2021-12-30 12:00:00+00:00'),
                datetime.datetime.fromisoformat('2021-12-31 00:00:00+00:00'),
                'concatYtTablesRange(\'//home/some/path\', \'2021-12\', \'2022-01\')',
            ),
            # конец месяца, граница
            (
                datetime.datetime.fromisoformat('2021-12-30 12:00:00+00:00'),
                datetime.datetime.fromisoformat('2021-12-30 23:59:59+00:00'),
                '`//home/some/path/2021-12`',
            ),
            # начало и конец месяца, границы
            (
                datetime.datetime.fromisoformat('2021-12-01 23:59:59+00:00'),
                datetime.datetime.fromisoformat('2021-12-31 00:00:00+00:00'),
                'concatYtTablesRange(\'//home/some/path\', \'2021-11\', \'2022-01\')',
            ),
        ],
    )
    async def test_default_overlay(
            self,
            source_dict: tp.Dict[str, tp.Any],
            sources: tp.Dict[str, source_renderer.SourceRenderer],
            from_: datetime.datetime,
            to_: datetime.datetime,
            source_result: str,
    ) -> None:

        text = (
            '--REGISTER_PARAM DateRange ts\n'
            '--REGISTER_SOURCE test_source\n'
            '{{ sources.test_source.tables(params.ts) }}'
        )

        inputs = {
            'ts': {'from': int(from_.timestamp()), 'to': int(to_.timestamp())},
        }

        registered_params = parameter_parser.parse_registered_parameters(text)
        params = parameter_parser.extract_parameter_values(
            inputs=inputs, registered_params=registered_params,
        )

        result = query_builder.render(text, params, sources)
        test_value = (
            '--REGISTER_PARAM DateRange ts\n' '--REGISTER_SOURCE test_source\n'
        ) + source_result

        assert result == test_value

    @pytest.mark.parametrize(
        'source_dict',
        (
            {
                **DEFAULT_SOURCE_DICT,
                'is_partitioned': True,
                'partition_key': 'ts',
                'partition_template': '%Y-%m',
            },
        ),
    )
    @pytest.mark.parametrize(
        'from_, to_, source_text, source_result',
        [
            # секунды за границей месяца
            (
                datetime.datetime.fromisoformat('2021-12-01 00:00:01+00:00'),
                datetime.datetime.fromisoformat('2021-12-15 12:00:00+00:00'),
                '{{ sources.test_source.tables(params.ts, seconds=2) }}',
                'concatYtTablesRange(\'//home/some/path\', \'2021-11\', \'2021-12\')',
            ),
            # секунды в границах месяца
            (
                datetime.datetime.fromisoformat('2021-12-01 00:00:02+00:00'),
                datetime.datetime.fromisoformat('2021-12-15 12:00:00+00:00'),
                '{{ sources.test_source.tables(params.ts, seconds=2) }}',
                '`//home/some/path/2021-12`',
            ),
            # минуты за границей месяца
            (
                datetime.datetime.fromisoformat('2021-12-01 00:02:59+00:00'),
                datetime.datetime.fromisoformat('2021-12-15 12:00:00+00:00'),
                '{{ sources.test_source.tables(params.ts, minutes=3) }}',
                'concatYtTablesRange(\'//home/some/path\', \'2021-11\', \'2021-12\')',
            ),
            # минуты в границах месяца
            (
                datetime.datetime.fromisoformat('2021-12-01 00:03:00+00:00'),
                datetime.datetime.fromisoformat('2021-12-15 12:00:00+00:00'),
                '{{ sources.test_source.tables(params.ts, minutes=3) }}',
                '`//home/some/path/2021-12`',
            ),
            # часы за границей месяца
            (
                datetime.datetime.fromisoformat('2021-12-01 03:59:59+00:00'),
                datetime.datetime.fromisoformat('2021-12-15 12:00:00+00:00'),
                '{{ sources.test_source.tables(params.ts, hours=4) }}',
                'concatYtTablesRange(\'//home/some/path\', \'2021-11\', \'2021-12\')',
            ),
            # часы в границах месяца
            (
                datetime.datetime.fromisoformat('2021-12-01 04:00:00+00:00'),
                datetime.datetime.fromisoformat('2021-12-15 12:00:00+00:00'),
                '{{ sources.test_source.tables(params.ts, hours=4) }}',
                '`//home/some/path/2021-12`',
            ),
            # дни за границей месяца
            (
                datetime.datetime.fromisoformat('2021-12-05 23:59:59+00:00'),
                datetime.datetime.fromisoformat('2021-12-15 12:00:00+00:00'),
                '{{ sources.test_source.tables(params.ts, days=5) }}',
                'concatYtTablesRange(\'//home/some/path\', \'2021-11\', \'2021-12\')',
            ),
            # дни в границах месяца
            (
                datetime.datetime.fromisoformat('2021-12-06 00:00:00+00:00'),
                datetime.datetime.fromisoformat('2021-12-15 12:00:00+00:00'),
                '{{ sources.test_source.tables(params.ts, days=5) }}',
                '`//home/some/path/2021-12`',
            ),
            # недели за границей месяца
            (
                datetime.datetime.fromisoformat('2021-12-07 23:59:59+00:00'),
                datetime.datetime.fromisoformat('2021-12-15 12:00:00+00:00'),
                '{{ sources.test_source.tables(params.ts, weeks=1) }}',
                'concatYtTablesRange(\'//home/some/path\', \'2021-11\', \'2021-12\')',
            ),
            # недели в границах месяца
            (
                datetime.datetime.fromisoformat('2021-12-08 00:00:00+00:00'),
                datetime.datetime.fromisoformat('2021-12-15 12:00:00+00:00'),
                '{{ sources.test_source.tables(params.ts, weeks=1) }}',
                '`//home/some/path/2021-12`',
            ),
        ],
    )
    async def test_custom_overlay(
            self,
            source_dict: tp.Dict[str, tp.Any],
            sources: tp.Dict[str, source_renderer.SourceRenderer],
            from_: datetime.datetime,
            to_: datetime.datetime,
            source_text: str,
            source_result: str,
    ) -> None:

        text = (
            '--REGISTER_PARAM DateRange ts\n' '--REGISTER_SOURCE test_source\n'
        ) + source_text

        inputs = {
            'ts': {'from': int(from_.timestamp()), 'to': int(to_.timestamp())},
        }

        registered_params = parameter_parser.parse_registered_parameters(text)
        params = parameter_parser.extract_parameter_values(
            inputs=inputs, registered_params=registered_params,
        )

        result = query_builder.render(text, params, sources)
        test_value = (
            '--REGISTER_PARAM DateRange ts\n' '--REGISTER_SOURCE test_source\n'
        ) + source_result

        assert result == test_value

    @pytest.mark.parametrize(
        'source_dict',
        (
            {
                **DEFAULT_SOURCE_DICT,
                'is_partitioned': True,
                'partition_key': 'ts',
                'partition_template': '%Y-%m',
            },
        ),
    )
    async def test_no_daterange(
            self,
            source_dict: tp.Dict[str, tp.Any],
            sources: tp.Dict[str, source_renderer.SourceRenderer],
    ) -> None:

        text = (
            '--REGISTER_SOURCE test_source\n{{ sources.test_source.tables() }}'
        )

        inputs: tp.Dict = {}

        registered_params = parameter_parser.parse_registered_parameters(text)
        params = parameter_parser.extract_parameter_values(
            inputs=inputs, registered_params=registered_params,
        )

        result = query_builder.render(text, params, sources)

        assert result == (
            '--REGISTER_SOURCE test_source\n'
            'concatYtTablesRange(\'//home/some/path\')'
        )

    @pytest.mark.parametrize('source_dict', (DEFAULT_CH_SOURCE_DICT,))
    @pytest.mark.parametrize(
        'tables_text',
        [
            '{{ sources.test_ch_source.tables(params.ts) }}',
            '{{ sources.test_ch_source.tables() }}',
        ],
    )
    async def test_ch_source(
            self,
            source_dict: tp.Dict[str, tp.Any],
            sources: tp.Dict[str, source_renderer.SourceRenderer],
            tables_text: str,
    ) -> None:

        text = (
            '--REGISTER_PARAM DateRange ts\n'
            '--REGISTER_SOURCE test_ch_source\n'
        ) + tables_text

        inputs = {'ts': {'from': 1, 'to': 946684800}}

        registered_params = parameter_parser.parse_registered_parameters(text)
        params = parameter_parser.extract_parameter_values(
            inputs=inputs, registered_params=registered_params,
        )

        result = query_builder.render(text, params, sources)

        assert result == (
            '--REGISTER_PARAM DateRange ts\n'
            '--REGISTER_SOURCE test_ch_source\n'
            'db.tb'
        )
