from sqlalchemy import String, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID

from dmp_suite.ctl.extensions.storage.postgresql.model import get_ctl_pg_tables


def test_get_ctl_pg_tables_set_different_schemas():
    et_one, ept_one = get_ctl_pg_tables('test_one')
    et_two, ept_two = get_ctl_pg_tables('test_two')

    assert et_one.__table__.schema == 'test_one'
    assert ept_one.__table__.schema == 'test_one'

    assert et_two.__table__.schema == 'test_two'
    assert ept_two.__table__.schema == 'test_two'


def test_table_name_is_the_same():
    et_one, ept_one = get_ctl_pg_tables('test_one')
    et_two, ept_two = get_ctl_pg_tables('test_two')

    assert et_one.__table__.name == et_two.__table__.name
    assert ept_one.__table__.name == ept_two.__table__.name


def test_pg_entity_columns():
    table_desc, _ = get_ctl_pg_tables('test')
    expected_columns = {
        'id': UUID,
        'domain': String,
        'name': String,
        'utc_created_dttm': TIMESTAMP,
        'utc_updated_dttm': TIMESTAMP,
    }
    actual_columns = table_desc.__table__.columns

    assert len(expected_columns) == len(actual_columns)

    for c in actual_columns:
        assert c.name in expected_columns
        assert isinstance(c.type, expected_columns[c.name])


def test_pg_entity_params_columns():
    _, table_desc = get_ctl_pg_tables('test')
    expected_columns = {
        'id': UUID,
        'entity_id': UUID,
        'parameter_code': String,
        'parameter_value': String,
        'utc_created_dttm': TIMESTAMP,
        'utc_updated_dttm': TIMESTAMP,
    }
    actual_columns = table_desc.__table__.columns

    assert len(expected_columns) == len(actual_columns)

    for c in actual_columns:
        assert c.name in expected_columns
        assert isinstance(c.type, expected_columns[c.name])
