import pytest
from mock import mock

from dmp_suite.dev_prefix.greenplum import get_dev_gp_location_class
from dmp_suite.greenplum.table import GPLocationBase, GPTable


@pytest.mark.parametrize(
    'user, base_schema, base_table_name, expected_table_name',
    [
        ('test_user', 'base_schema', 'base_table', 'test_user_base_schema_base_table'),
        ('test-user', 'base_schema', 'base_table', 'test_user_base_schema_base_table'),
        ('test_user', 'test_user_base_schema', 'base_table', 'test_user_base_schema_base_table'),
        ('test_user', 'test_userbase_schema', 'base_table', 'test_userbase_schema_base_table'),
    ],
)
def test_get_dev_gp_location(user, base_schema, base_table_name, expected_table_name):
    with mock.patch.dict('os.environ', dict(USER=user)):
        class MyTable(GPTable):
            pass

        class MockLocation(GPLocationBase):
            def get_pattern_params(self, pattern: str) -> dict:
                return {}

            def schema(self):
                return base_schema

            def table_name(self):
                return base_table_name

        dev_schema = 'my_dev'

        dev_location_class = get_dev_gp_location_class(
            MockLocation,
            dev_schema,
        )
        dev_location = dev_location_class(MyTable)
        assert dev_location.schema() == dev_schema
        assert dev_location.table_name() == expected_table_name
