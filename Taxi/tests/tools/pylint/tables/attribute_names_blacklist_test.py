import io
import textwrap
import unittest.mock

import astroid
import mock
import pylint.testutils
import pytest
import tools.pylint.tables.linter

MOCK_BLACKLIST = """
sql

DATE
   \t
YeAr
"""


class TestAttributeNamesBlacklistChecker(
    pylint.testutils.CheckerTestCase,
):
    CHECKER_CLASS = tools.pylint.tables.linter.TableLinter

    def setup_method(self):
        blacklist_mocker = unittest.mock.Mock(
            side_effect=lambda *args, **kwargs: io.StringIO(MOCK_BLACKLIST)
        )
        self.CHECKER_CLASS._get_blacklist_file = blacklist_mocker
        super(TestAttributeNamesBlacklistChecker, self).setup_method()

    @pytest.mark.parametrize('name', ['sql', 'date', 'year'])
    def test_names_from_blacklist_file_are_blacklisted(self, name):
        assert name in self.checker.blacklist

    def test_blank_lines_are_not_included_in_blacklist(self):
        for name in self.checker.blacklist:
            assert name.strip()

    def test_valid_name_does_not_raise_linter_error(self):
        code = """
        import dmp_suite.greenplum.table


        class TestTable(dmp_suite.greenplum.table.GPTable):

            compliant_integer_field = dmp_suite.greenplum.table.Int()
        """
        code = textwrap.dedent(code).strip()

        node = astroid.parse(code)

        with mock.patch(
            'tools.pylint.tables.linter.TableLinter.field_hooks',
            [tools.pylint.tables.linter.check_attribute_blacklist],
        ):
            with self.assertNoMessages():
                self.walk(node)

    @pytest.mark.parametrize(
        'name',
        [
            'sql',
            'SQL',
            'Sql',
            'date',
            'DATE',
            'Date',
            'year',
            'YEAR',
            'Year',
        ],
    )
    def test_blacklisted_name_raises_linter_error_in_any_case(self, name):
        code = f"""
        import dmp_suite.greenplum.table


        class TestTable(dmp_suite.greenplum.table.GPTable):

            {name} = dmp_suite.greenplum.table.Int() #@
        """
        code = textwrap.dedent(code).strip()

        assignment = astroid.extract_node(code)

        # Тайпгард
        assert isinstance(assignment, astroid.nodes.Assign)

        node = assignment.root()

        message = pylint.testutils.MessageTest(
            tools.pylint.tables.symbols.Symbols.BLACKLISTED_ATTRIBUTE_NAME.value.mnemonic,
            node=assignment.targets[0],
            args=(name, name.upper()),
        )

        with mock.patch(
            'tools.pylint.tables.linter.TableLinter.field_hooks',
            [tools.pylint.tables.linter.check_attribute_blacklist],
        ):
            with self.assertAddsMessages(message):
                self.walk(node)

    def test_composite_name_is_not_blacklisted(self):
        code = f"""
        import dmp_suite.greenplum.table


        class TestTable(dmp_suite.greenplum.table.GPTable):

            sql_date = dmp_suite.greenplum.table.Int() #@
        """
        code = textwrap.dedent(code).strip()

        node = astroid.parse(code)

        with mock.patch(
            'tools.pylint.tables.linter.TableLinter.field_hooks',
            [tools.pylint.tables.linter.check_attribute_blacklist],
        ):
            with self.assertNoMessages():
                self.walk(node)
