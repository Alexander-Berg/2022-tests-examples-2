import textwrap

import astroid
import pylint.testutils

import tools.pylint.tables


class TestLinterRobustness(pylint.testutils.CheckerTestCase):
    CHECKER_CLASS = tools.pylint.tables.TableLinter

    def test_linter_does_not_raise_an_exception_on_improper_field_instantiation(self):
        code = """
        import dmp_suite.greenplum.table


        class TestTable(dmp_suite.greenplum.table.GPTable):

            improper_field = dmp_suite.greenplum.table.Int
        """

        module = astroid.parse(code)

        # Note: the actual assertion is subject to change, additional functionality
        # can be added to the linter in the future, feel free to change this assertion;
        # what is important is that linter does not raise any exceptions outside of
        # its visit_* handlers on a clearly invalid field assignment.
        with self.assertNoMessages():
            self.walk(module)
