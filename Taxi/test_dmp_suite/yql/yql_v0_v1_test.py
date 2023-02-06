import pytest
from dmp_suite.yql import YqlQuery, YqlSyntaxVersions


@pytest.mark.slow
@pytest.mark.parametrize('syntax_version, query_string', [
    (YqlSyntaxVersions.V1, 'SELECT 1 as `foo`;'),
])
def test_syntax_version_query(syntax_version, query_string):
    query = YqlQuery(query_string, syntax_version=syntax_version)
    assert query.syntax_version == syntax_version
    query.execute()


def test_syntax_version_1_is_default():
    query = YqlQuery('SELECT 1 as `foo`;')
    assert query.syntax_version == YqlSyntaxVersions.V1
