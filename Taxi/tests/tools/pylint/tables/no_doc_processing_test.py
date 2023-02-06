import textwrap
import mock

import astroid
import pylint.testutils
import pytest

import tools.pylint.tables


class TestAttributeNamingChecker(pylint.testutils.CheckerTestCase):
    CHECKER_CLASS = tools.pylint.tables.TableLinter

    @pytest.mark.parametrize(
        'code', [
            """
            import dmp_suite.greenplum.table
            from dmp_suite.table import no_doc


            @no_doc("reason")
            class TestTable(dmp_suite.greenplum.table.GPTable):

                date = dmp_suite.greenplum.table.Int()
            """,
            """
            import dmp_suite.greenplum.table
            import dmp_suite.table


            @dmp_suite.table.no_doc("reason")
            class TestTable(dmp_suite.greenplum.table.GPTable):

                date = dmp_suite.greenplum.table.Int()
            """,
        ]
    )
    def test_composite_name_is_not_blacklisted(self, code):
        code = textwrap.dedent(code).strip()

        node = astroid.parse(code)

        with mock.patch(
            'tools.pylint.tables.linter.TableLinter.field_hooks',
            [tools.pylint.tables.linter.check_attribute_blacklist],
        ):
            with self.assertNoMessages():
                self.walk(node)
