import textwrap

import astroid
import mock
import pylint.testutils
import pytest
import tools.pylint.tables.linter
import tools.pylint.tables.symbols


class TestAttributeDocumentationChecker(pylint.testutils.CheckerTestCase):
    CHECKER_CLASS = tools.pylint.tables.linter.TableLinter

    @pytest.mark.parametrize(
        'code',
        [
            """
            import dmp_suite.greenplum.table

            class SomeTable(dmp_suite.greenplum.table.GPTable):

                some_field = dmp_suite.greenplum.table.Int() #@
            """,
            """
            import dmp_suite.greenplum.table

            class SomeTable(dmp_suite.greenplum.table.GPTable):

                some_field = dmp_suite.greenplum.table.Int(comment='') #@
            """,
            """
            import dmp_suite.greenplum.table

            empty_doc = ''

            class SomeTable(dmp_suite.greenplum.table.GPTable):

                some_field = dmp_suite.greenplum.table.Int(comment=empty_doc) #@
            """,
            """
            import dmp_suite.greenplum.table

            class SomeTable(dmp_suite.greenplum.table.GPTable):

                compliant_field = dmp_suite.greenplum.table.Int(comment='documentation')
                some_field = dmp_suite.greenplum.table.Int(comment='') #@
            """,
            """
            import dmp_suite.table

            class SomeTable(dmp_suite.table.Table):

                some_field = dmp_suite.greenplum.table.Int(comment='') #@
            """,
        ],
    )
    def test_missing_documentation_raises_message(self, code):
        code = textwrap.dedent(code)
        node = astroid.extract_node(code)
        module = node.root()

        # Тайпгард
        assert isinstance(node, astroid.Assign)
        assert isinstance(node.value, astroid.Call)

        message = pylint.testutils.MessageTest(
            tools.pylint.tables.symbols.Symbols.MISSING_ATTRIBUTE_DOCUMENTATION.value.mnemonic,
            node=node.value,
        )

        with mock.patch(
            'tools.pylint.tables.linter.TableLinter.field_hooks',
            [tools.pylint.tables.linter.check_attribute_documentation],
        ):
            with self.assertAddsMessages(message):
                self.walk(module)

    def test_missing_documentation_raises_on_name_assignment(self):
        code = """
            import dmp_suite.table

            field = dmp_suite.greenplum.table.Int(comment='') #@

            class SomeTable(dmp_suite.table.Table):

                some_field = field #@
        """
        code = textwrap.dedent(code)
        assignment, node = astroid.extract_node(code)
        module = node.root()

        # Тайпгард
        assert isinstance(node, astroid.Assign)
        assert isinstance(assignment, astroid.Assign)

        message = pylint.testutils.MessageTest(
            tools.pylint.tables.symbols.Symbols.MISSING_ATTRIBUTE_DOCUMENTATION.value.mnemonic,
            # note that the message should actually relate to the original call
            node=assignment.value,
        )

        with mock.patch(
            'tools.pylint.tables.linter.TableLinter.field_hooks',
            [tools.pylint.tables.linter.check_attribute_documentation],
        ):
            with self.assertAddsMessages(message):
                self.walk(module)

    @pytest.mark.parametrize(
        'code',
        [
            """
            import dmp_suite.greenplum.table

            class SomeTable(dmp_suite.greenplum.table.GPTable):

                some_field = dmp_suite.greenplum.table.Int(comment='documentation')
            """,
            """
            import dmp_suite.greenplum.table

            doc = 'documentation'

            class SomeTable(dmp_suite.greenplum.table.GPTable):

                some_field = dmp_suite.greenplum.table.Int(comment=doc)
            """,
            """
            import dmp_suite.greenplum.hnhm.table

            class SomeTable(dmp_suite.greenplum.hnhm.table.HnhmLink):

                a = dmp_suite.greenplum.hnhm.table.HnhmLinkElement(entity=A(), comment='a')
                b = dmp_suite.greenplum.hnhm.table.HnhmLinkElement(entity=B())
                c = dmp_suite.greenplum.hnhm.table.HnhmLinkPartition(partition_position=1, link_element=b)

            """,
        ],
    )
    def test_documented_field_does_not_raise_message(self, code):
        code = textwrap.dedent(code)
        module = astroid.parse(code)

        with mock.patch(
            'tools.pylint.tables.linter.TableLinter.field_hooks',
            [tools.pylint.tables.linter.check_attribute_documentation],
        ):
            with self.assertNoMessages():
                self.walk(module)
