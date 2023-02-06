import pytest
from nile.api.v1 import Record

from .impl import unfold_params

default_param = Record(
    type_id=None,
    param_id=None,
    str_value=None,
    xsl_name=None,
    modification_date=None,
    bool_value=None,
    numeric_value=None,
    option_id=None,
)
default_result = Record(
    msku=None,
    param_type_id=None,
    param_id=None,
    param_en_name=None,
    param_value_flg=None,
    param_value=None,
    param_value_text=None,
    param_option_id=None,
    param_option_hash=None,
    utc_modification_dttm=None,
)

params = lambda msku, xs: [Record(msku=msku, params=xs)]

bool_value_param = params(1, [
    default_param.transform(
        type_id=1,
        param_id=123,
        modification_date=1642717522000,
        bool_value=False,
        option_id=1,
    ),
])
bool_value_result = [default_result.transform(
    msku=1,
    param_type_id=1,
    param_id=123,
    param_value_flg=False,
    param_option_id=1,
    param_option_hash='356a192b7913b04c54574d18c28d46e6395428ab',
    utc_modification_dttm='2022-01-20 22:25:22',
)]

numeric_value_param = params(2, [
    default_param.transform(
        type_id=1,
        param_id=123,
        modification_date=1642717522000,
        numeric_value=123.123,
        option_id=2,
    ),
    default_param.transform(
        type_id=1,
        param_id=321,
        modification_date=1642717522000,
        numeric_value='haha',
        option_id=2,
    ),
])
numeric_value_result = [
    default_result.transform(
        msku=2,
        param_type_id=1,
        param_id=123,
        param_option_id=2,
        param_value=123.123,
        utc_modification_dttm='2022-01-20 22:25:22',
        param_option_hash='da4b9237bacccdf19c0760cab7aec4a8359010b0',
    ),
    default_result.transform(
        msku=2,
        param_type_id=1,
        param_id=321,
        param_option_id=2,
        param_value=None,
        utc_modification_dttm='2022-01-20 22:25:22',
        param_option_hash='da4b9237bacccdf19c0760cab7aec4a8359010b0',
    )
]

null_option_id_params = [
    x.transform(params=[param.transform('option_id') for param in x.params])
    for x in bool_value_param + numeric_value_param
]
null_option_id_result = [
    x.transform(param_option_id=None, param_option_hash='7984b0a0e139cabadb5afc7756d473fb34d23819')
    for x in bool_value_result + numeric_value_result
]

str_value_param = params(3, [
    default_param.transform(
        type_id=4,
        param_id=123,
        modification_date=1642717522000,
        str_value=[
            {'value': 'sale text'},
            {'value': 'not sale text'}
        ],
    ),
])
str_value_result = [
    default_result.transform(
        msku=3,
        param_type_id=4,
        param_id=123,
        utc_modification_dttm='2022-01-20 22:25:22',
        param_value_text='not sale text',
        param_option_hash='3e0a8cb0d4555eeba0f4f2debc3408353263b68c',
    ),
    default_result.transform(
        msku=3,
        param_type_id=4,
        param_id=123,
        utc_modification_dttm='2022-01-20 22:25:22',
        param_value_text='sale text',
        param_option_hash='9997f08c10a5384817f66dba3a6941dcb35d0098',
    ),
]

deleted_param = params(1, [])
deleted_result = []


@pytest.mark.parametrize('given, expected', [
    (bool_value_param, bool_value_result),
    (numeric_value_param, numeric_value_result),
    (str_value_param, str_value_result),
    (null_option_id_params, null_option_id_result),
    (deleted_param, deleted_result),
])
def test_unfold_params(given, expected):
    to_dict = lambda xs: [x.to_dict() for x in xs]
    sort = lambda xs: sorted(xs, key=lambda k: (k['msku'], k['param_id'], k['param_option_hash']))
    assert sort(to_dict(unfold_params(given))) == sort(to_dict(expected))
