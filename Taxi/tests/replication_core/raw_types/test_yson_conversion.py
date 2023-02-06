from yt.yson import yson_types

from replication_core.raw_types import yson_conversion


def test_nested_complex_types():
    json_value = """
    {
        "$a": {
            "raw_type": "pg_range"
        },
        "$v": {
            "lower": {
                "$a": {
                    "raw_type": "datetime"
                },
                "$v": "2020-05-20T10:00:00"
            },
            "lower_inc": true
        }
    }
    """
    yson_value = yson_conversion.json_to_yson_obj(json_value)
    raw_dttm = yson_types.YsonUnicode('2020-05-20T10:00:00')
    raw_dttm.attributes = {'raw_type': 'datetime'}
    expected_yson_value = yson_types.YsonMap(
        lower=raw_dttm, lower_inc=yson_types.YsonBoolean(1),
    )
    expected_yson_value.attributes = {'raw_type': 'pg_range'}

    assert yson_value == expected_yson_value
