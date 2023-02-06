import textwrap

import astroid
import mock
import pylint.testutils
import tools.pylint.tables.linter
import tools.pylint.tables.symbols
from tests.tools.pylint.tables.fuzzy_checker import FuzzyMessageMatchCheckerTestcase


class TestAttributeMultipleAssignmentsChecker(FuzzyMessageMatchCheckerTestcase):
    CHECKER_CLASS = tools.pylint.tables.linter.TableLinter

    def test_generic_class_with_multiple_assignments_does_not_raise_message(self):
        code = """
        class NonTable():
            a = 2 + 2
            a = 5
        """
        code = textwrap.dedent(code)
        module = astroid.parse(code)

        with mock.patch(
            'tools.pylint.tables.linter.TableLinter.field_hooks',
            [tools.pylint.tables.linter.check_multiple_field_assignments],
        ):
            with self.assertNoMessages():
                self.walk(module)

    def test_multiple_field_assignment_raises_message_on_generic_table(self):
        code = """
        import dmp_suite.table

        class SomeTable(dmp_suite.table.Table):
            a = dmp_suite.table.Field()
            a = dmp_suite.table.Field() #@
        """
        code = textwrap.dedent(code)

        node = astroid.extract_node(code)
        # Тайпгард
        assert isinstance(node, astroid.nodes.Assign)
        module = node.root()

        message = pylint.testutils.MessageTest(
            tools.pylint.tables.symbols.Symbols.MULTIPLE_ATTRIBUTE_ASSIGNMENTS.value.mnemonic,
            node=node.targets[0],
        )

        with mock.patch(
            'tools.pylint.tables.linter.TableLinter.field_hooks',
            [tools.pylint.tables.linter.check_multiple_field_assignments],
        ):
            with self.assertFuzzyAddsMessages(message):
                self.walk(module)

    def test_message_is_not_raised_for_different_names(self):
        code = """
        class SomeTable(dmp_suite.table.Table):
            a = dmp_suite.table.Field()
            A = dmp_suite.table.Field()
        """
        code = textwrap.dedent(code)
        module = astroid.parse(code)

        with mock.patch(
            'tools.pylint.tables.linter.TableLinter.field_hooks',
            [tools.pylint.tables.linter.check_multiple_field_assignments],
        ):
            with self.assertNoMessages():
                self.walk(module)

    def test_message_is_not_raised_for_different_tables(self):
        code = """
        class Foo(dmp_suite.table.Table):
            a = dmp_suite.table.Field()


        class Bar(dmp_suite.table.Table):
            a = dmp_suite.table.Field()
        """
        code = textwrap.dedent(code)
        module = astroid.parse(code)

        with mock.patch(
            'tools.pylint.tables.linter.TableLinter.field_hooks',
            [tools.pylint.tables.linter.check_multiple_field_assignments],
        ):
            with self.assertNoMessages():
                self.walk(module)

    def test_message_is_not_raised_for_inherited_tables(self):
        code = """
        class Foo(dmp_suite.table.Table):
            a = dmp_suite.table.Field()


        class Bar(Foo):
            a = dmp_suite.table.Field()
        """
        code = textwrap.dedent(code)
        module = astroid.parse(code)

        with mock.patch(
            'tools.pylint.tables.linter.TableLinter.field_hooks',
            [tools.pylint.tables.linter.check_multiple_field_assignments],
        ):
            with self.assertNoMessages():
                self.walk(module)
