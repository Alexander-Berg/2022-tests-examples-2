import io
import re
import textwrap
import unittest.mock

import astroid
import mock
import pylint.testutils
import pytest
import tools.pylint.tables
from tests.tools.pylint.tables.fuzzy_checker import FuzzyMessageMatchCheckerTestcase

MOCK_CONFIGURATION = """
types:
    greenplum:
        HnhmLinkElement:
            rules:
                - wildcard

        Int:
            rules:
                - ids
                - integers

        String:
            rules:
                - ids
                - strings
        Uuid:
            rules:
                - ids
                - uuid
        Zipcode:
            rules:
                - zipcode
            strict: true

    yt:
        Int:
            rules:
                - ids
                - integers
        String:
            rules:
                - ids
                - strings
                - uuid

rules:
    strings:
        description: >
            Строковые значения
        masks:
            - compliant_string_.+
    ids:
        description: >
            Идентификаторы
        masks:
            - id_.+
    uuid:
        description: >
            UUID
        masks:
            - .+_uuid
    integers:
        description: >
            Целочисленные значения
        masks:
            - compliant_integer_.+
    zipcode:
        description: >
            Почтовый индекс
        masks:
            - .+_zipcode

    wildcard:
        description: >
            Правило для игнорирования нейминга
        masks:
            - .+
"""


class TestAttributeNamingChecker(FuzzyMessageMatchCheckerTestcase):
    CHECKER_CLASS = tools.pylint.tables.TableLinter

    def setup_method(self):
        config_mocker = unittest.mock.Mock(
            side_effect=lambda *args, **kwargs: io.StringIO(MOCK_CONFIGURATION)
        )
        self.CHECKER_CLASS._get_naming_configuration_file = config_mocker
        super(TestAttributeNamingChecker, self).setup_method()

    def test_configuration_parser(self):
        expected = {
            'greenplum.String': re.compile('((id_.+)|(compliant_string_.+))$'),
            'greenplum.Int': re.compile('((id_.+)|(compliant_integer_.+))$'),
            'greenplum.Uuid': re.compile('((id_.+)|(.+_uuid))$'),
            'greenplum.Zipcode': re.compile('((.+_zipcode))$'),
            'greenplum.HnhmLinkElement': re.compile('((.+))$'),
            'yt.String': re.compile('((id_.+)|(compliant_string_.+)|(.+_uuid))$'),
            'yt.Int': re.compile('((id_.+)|(compliant_integer_.+))$'),
        }

        actual = self.checker.regex_storage

        assert expected == actual

    def test_strict_types_extraction_from_configuration(self):
        expected = {'greenplum.Zipcode'}

        actual = self.checker.strict_types

        assert expected == actual

    def test_parse_non_table_class(self):
        code = """
        import dmp_suite.table

        class NotTable:

            field = dmp_suite.table.Field()
        """
        code = textwrap.dedent(code).strip()

        node = astroid.parse(code)

        with mock.patch(
            'tools.pylint.tables.linter.TableLinter.field_hooks',
            [tools.pylint.tables.linter.check_attribute_naming],
        ):
            with self.assertNoMessages():
                self.walk(node)

    @pytest.mark.parametrize(
        'service,base,fields',
        [
            (
                'greenplum',
                'dmp_suite.greenplum.table.GPTable',
                ('Int', 'String', 'Uuid'),
            ),
            (
                'yt',
                'dmp_suite.yt.table.YTTable',
                ('Int', 'String', 'String'),
            ),
        ],
    )
    def test_parse_compliant_table(self, service, base, fields):
        code = f"""
        import dmp_suite.{service}.table


        class TestTable({base}):

            compliant_integer_field = dmp_suite.{service}.table.{fields[0]}()
            compliant_string_field = dmp_suite.{service}.table.{fields[1]}()
            field_uuid = dmp_suite.{service}.table.{fields[2]}()
        """
        code = textwrap.dedent(code).strip()

        node = astroid.parse(code, 'module')

        with mock.patch(
            'tools.pylint.tables.linter.TableLinter.field_hooks',
            [tools.pylint.tables.linter.check_attribute_naming],
        ):
            with self.assertNoMessages():
                self.walk(node)

    @pytest.mark.parametrize(
        'service,base,fields',
        [
            (
                'greenplum',
                'dmp_suite.greenplum.table.GPTable',
                ('Int', 'String', 'Uuid'),
            ),
            (
                'yt',
                'dmp_suite.yt.table.YTTable',
                ('Int', 'String', 'String'),
            ),
        ],
    )
    def test_parse_non_compliant_table(self, service, base, fields):
        code = f"""
        import dmp_suite.{service}.table


        class TestTable({base}):

            non_compliant_integer_field = dmp_suite.{service}.table.{fields[0]}() #@
            non_compliant_string_field = dmp_suite.{service}.table.{fields[1]}() #@
            non_compliant_uuid_field = dmp_suite.{service}.table.{fields[2]}() #@
        """
        code = textwrap.dedent(code).strip()

        assignments = astroid.extract_node(code)
        module = assignments[0].root()

        messages = [
            pylint.testutils.MessageTest(
                tools.pylint.tables.symbols.Symbols.INVALID_ATTRIBUTE_NAME.value.mnemonic,
                node=assignment.targets[0],
            )
            for assignment in assignments
        ]

        with mock.patch(
            'tools.pylint.tables.linter.TableLinter.field_hooks',
            [tools.pylint.tables.linter.check_attribute_naming],
        ):
            with self.assertFuzzyAddsMessages(*messages):
                self.walk(module)

    @pytest.mark.parametrize(
        'service,base,fields',
        [
            (
                'greenplum',
                'dmp_suite.greenplum.table.GPTable',
                ('Int', 'String', 'Uuid'),
            ),
            (
                'yt',
                'dmp_suite.yt.table.YTTable',
                ('Int', 'String', 'String'),
            ),
        ],
    )
    def test_id_rule(self, service, base, fields):
        code = f"""
        import dmp_suite.{service}.table


        class TestTable({base}):

            id_integer_field = dmp_suite.{service}.table.{fields[0]}() #@
            id_string_field = dmp_suite.{service}.table.{fields[1]}() #@
            id_uuid_field = dmp_suite.{service}.table.{fields[2]}() #@
        """
        code = textwrap.dedent(code).strip()

        module = astroid.parse(code)

        with mock.patch(
            'tools.pylint.tables.linter.TableLinter.field_hooks',
            [tools.pylint.tables.linter.check_attribute_naming],
        ):
            with self.assertNoMessages():
                self.walk(module)

    def test_derived_type(self):
        """Проверям, что правила для типов-родителей действуют на наследников."""
        code = """
        import dmp_suite.greenplum.table


        class TestTable(dmp_suite.greenplum.table.GPTable):

            compliant_integer_field = dmp_suite.greenplum.table.BigInt()
        """
        code = textwrap.dedent(code).strip()

        module = astroid.parse(code)

        with mock.patch(
            'tools.pylint.tables.linter.TableLinter.field_hooks',
            [tools.pylint.tables.linter.check_attribute_naming],
        ):
            with self.assertNoMessages():
                self.walk(module)

    def test_strict_types_passes_own_check(self):
        """
        Проверяем, что если мы ввели семантический тип (Zipcode),
        то он проходит собственную проверку.
        """

        code = """
        import dmp_suite.greenplum.table

        class Zipcode(dmp_suite.greenplum.table.String):
            pass


        class TestTable(dmp_suite.greenplum.table.GPTable):

            some_zipcode = Zipcode()
        """
        code = textwrap.dedent(code).strip()

        module = astroid.parse(code)

        with mock.patch(
            'tools.pylint.tables.linter.TableLinter.field_hooks',
            [tools.pylint.tables.linter.check_attribute_naming],
        ):
            with self.assertNoMessages():
                self.walk(module)

    def test_strict_rules_does_not_elevate(self):
        """
        Проверяем, что семантичский тип Zipcode
        не матчится с проверами для String.
        """

        code = """
        import dmp_suite.greenplum.table

        class Zipcode(dmp_suite.greenplum.table.String):
            pass


        class TestTable(dmp_suite.greenplum.table.GPTable):

            compliant_string_field = Zipcode() #@
        """
        code = textwrap.dedent(code).strip()

        node = astroid.extract_node(code)
        # Тайпгард
        assert isinstance(node, astroid.nodes.Assign)
        module = node.root()
        message = pylint.testutils.MessageTest(
            tools.pylint.tables.symbols.Symbols.INVALID_ATTRIBUTE_NAME.value.mnemonic,
            node=node.targets[0],
        )
        with mock.patch(
            'tools.pylint.tables.linter.TableLinter.field_hooks',
            [tools.pylint.tables.linter.check_attribute_naming],
        ):
            with self.assertFuzzyAddsMessages(message):
                self.walk(module)

    def test_partially_compliant_table(self):
        code = """
        import dmp_suite.greenplum.table


        class TestTable(dmp_suite.greenplum.table.GPTable):

            compliant_integer_field = dmp_suite.greenplum.table.Int()
            non_compliant_integer_field = dmp_suite.greenplum.table.Int() #@
        """

        node = astroid.extract_node(code)
        # Тайпгард
        assert isinstance(node, astroid.nodes.Assign)
        module = node.root()
        message = pylint.testutils.MessageTest(
            tools.pylint.tables.symbols.Symbols.INVALID_ATTRIBUTE_NAME.value.mnemonic,
            node=node.targets[0],
        )

        with mock.patch(
            'tools.pylint.tables.linter.TableLinter.field_hooks',
            [tools.pylint.tables.linter.check_attribute_naming],
        ):
            with self.assertFuzzyAddsMessages(message):
                self.walk(module)

    def test_field_with_type_that_was_not_mentioned_in_configuration(self):
        code = """
        import dmp_suite.greenplum.table


        class TestTable(dmp_suite.greenplum.table.GPTable):

            compliant_integer_field = dmp_suite.greenplum.table.Numeric() #@
        """

        node = astroid.extract_node(code)
        # Тайпгард
        assert isinstance(node, astroid.nodes.Assign)
        module = node.root()
        message = pylint.testutils.MessageTest(
            tools.pylint.tables.symbols.Symbols.INVALID_ATTRIBUTE_NAME.value.mnemonic,
            node=node.targets[0],
        )

        with mock.patch(
            'tools.pylint.tables.linter.TableLinter.field_hooks',
            [tools.pylint.tables.linter.check_attribute_naming],
        ):
            with self.assertFuzzyAddsMessages(message):
                self.walk(module)

    def test_naming_in_hnhm_links_are_ignored(self):
        code = """
        from dmp_suite.greenplum.hnhm.table import HnhmLink, HnhmLinkElement

        class Table(HnhmLink):
            non_compliant_field = HnhmLinkElement(
                entity=SomeEntity(),
                comment='comment'
            )
        """

        node = astroid.parse(code)
        with mock.patch(
            'tools.pylint.tables.linter.TableLinter.field_hooks',
            [tools.pylint.tables.linter.check_attribute_naming],
        ):
            with self.assertNoMessages():
                self.walk(node)
