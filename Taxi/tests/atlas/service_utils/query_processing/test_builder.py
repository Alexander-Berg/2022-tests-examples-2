import pytest
import mock

from atlas.service_utils.query_processing import builder, parameter


def test_build_template_with_selector_param():
    text = '''--REGISTER_PARAM Selector car_class
Car class: {{ params.car_class.value }}
Filter: {{ filter.car_class() }}'''

    registered_params = parameter.parse_registered_parameters(text)
    params = parameter.extract_parameter_values({'car_class': 'econom'}, registered_params)
    result = builder.render(text, params)
    assert result == """--REGISTER_PARAM Selector car_class
Car class: econom
Filter: car_class = 'econom'"""


def test_build_template_with_all_user_param_types():
    text = '''
--REGISTER_PARAM Selector car_class
--REGISTER_PARAM MultiSelector cities
--REGISTER_PARAM MultiSelector grocery_ids
--REGISTER_PARAM DateRange ts
--REGISTER_PARAM NumericInterval ni
--REGISTER_PARAM TimeBucketGrid tbg
--REGISTER_PARAM ContainsSelector tags
--REGISTER_PARAM CorpType corp_type
--REGISTER_PARAM PaymentType payment_type
Car class: {{ params.car_class.value }}
Cities: {{ params.cities.value }}
DateRange: start={{ params.ts.from_ts }} end={{ params.ts.to_ts }}
NumericInterval: from={{ params.ni.value.from }} to={{ params.ni.value.to }}
TimeBucketGrid: every {{ params.tbg.bucket_size }} seconds starting from {{ params.tbg.start_offset }}
Tags: {{ params.tags.value }}
CorpType: {{ params.corp_type.value }}
PaymentType: {{ params.payment_type.value }}
Ids: {{ params.grocery_ids.value }}

Filters: 
{{ filter.car_class() }}
{{ filter.cities() }}
{{ filter.ts() }}
{{ filter.ni() }}
{{ filter.tags() }}
{{ filter.corp_type() }}
{{ filter.payment_type() }}
{{ filter.grocery_ids() }}
'''

    registered_params = parameter.parse_registered_parameters(text)

    input_parameters = {
        'car_class': 'econom',
        'cities': ['Москва', 'Казань', "Город с 'кавычкой"],
        'ts': {
            'from': 1561476900,
            'to': 1561476950
         },
        'ni': {
            'from': 0.1,
            'to': 0.2
        },
        'tbg': {
            'bucket_size': 40,
            'start_offset': 40
        },
        'tags': 'super_tag',
        'grocery_ids': [1, 2],
        'corp_type': 'only_corp',
        'payment_type': 'card'
    }
    params = parameter.extract_parameter_values(input_parameters,
                                                registered_params)
    result = builder.render(text, params)
    assert result == """
--REGISTER_PARAM Selector car_class
--REGISTER_PARAM MultiSelector cities
--REGISTER_PARAM MultiSelector grocery_ids
--REGISTER_PARAM DateRange ts
--REGISTER_PARAM NumericInterval ni
--REGISTER_PARAM TimeBucketGrid tbg
--REGISTER_PARAM ContainsSelector tags
--REGISTER_PARAM CorpType corp_type
--REGISTER_PARAM PaymentType payment_type
Car class: econom
Cities: ('Москва', 'Казань', "Город с 'кавычкой")
DateRange: start=1561476900 end=1561476950
NumericInterval: from=0.1 to=0.2
TimeBucketGrid: every 40 seconds starting from 40
Tags: super_tag
CorpType: only_corp
PaymentType: card
Ids: (1, 2)

Filters: 
car_class = 'econom'
cities IN ('Москва', 'Казань', 'Город с \\\'кавычкой')
ts BETWEEN 1561476900 AND 1561476950
(0.1 <= ni AND ni <= 0.2)
has(tags, 'super_tag')
corp_type IN ('food', 'corp')
payment_type = 'card'
grocery_ids IN (1, 2)"""


def test_render_table_path():
    text = """table_path: {{ table_path() }}
table_path_final: {{ table_path('FINAL') }}"""
    params = {'table_path': parameter.TablePathParameter(name='table_path',
                                                         value='test_db.test_table')}
    result = builder.render(text, params)
    assert result == """table_path: test_db.test_table
table_path_final: test_db.test_table FINAL"""


def test_render_quadkey():
    text = """quadkey_substring: {{ quadkey('quadkey123') }}"""
    params = {'cell_size': parameter.CellSizeParameter('cell_size', 17)}
    result = builder.render(text, params)
    assert result == """quadkey_substring: substring(quadkey123, 1, 17)"""


def test_render_quadkey_none_cell_size():
    text = """quadkey_substring: {{ quadkey('quadkey123') }}"""
    params = {'cell_size': parameter.CellSizeParameter('cell_size', None)}
    result = builder.render(text, params)
    assert result == """quadkey_substring: quadkey123"""


@pytest.fixture
def blocked_query_text():
    return '''
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
--DEFINE_ATLAS_BLOCK COMMON END'''


@pytest.fixture
def metric_with_blocked_query(blocked_query_text):
    metric = mock.Mock()
    metric.sql_query_raw = blocked_query_text
    return metric


def test_build_map_tempate(metric_with_blocked_query):
    query = builder.build_map_template(metric_with_blocked_query)
    assert query == '<map>\n<common>'


def test_build_plot_tempate(metric_with_blocked_query):
    query = builder.build_plot_template(metric_with_blocked_query)
    assert query == '<plot>\n<common>'


def test_build_detail_data_tempate(metric_with_blocked_query):
    query = builder.build_detail_data_template(metric_with_blocked_query)
    assert query == '<detailed>\n<common>'
