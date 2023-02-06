import textwrap
from unittest import TestCase

import pytest
from docutils.core import publish_doctree, publish_from_doctree

from tools.doc.cross_ref.ref_parser import DmpRefParser, EntityResolver, ReferenceParsingError
from tools.doc.primitives import DocTask, DocTable, DocDomain

test_etl = "test_etl"
test_prefix_key = "Test"


def _format_task(doc_task: DocTask) -> str:
    return f"task/{doc_task.etl_service_name}/{doc_task.name}"


def _format_table(doc_table: DocTable) -> str:
    return f"table/{doc_table.db_type}/{doc_table.db_name}/{doc_table.display_name}"


def _format_domain(doc_domain: DocDomain) -> str:
    return f"domain/{doc_domain.prefix_key}/{doc_domain.type}/{doc_domain.code}/{doc_domain.module_name}/{doc_domain.attr_name}"


def _setup():
    dmp_ref_parser = DmpRefParser()
    doc_tasks = [
        DocTask(
            pk=f"{test_etl}.test_task",
            etl_service_name=test_etl,
            name="test_task",
            description=None,
            module_path=__file__,
            module_name=__name__,
            # DmpRefParser tests don't use source/target table PKs
            sources=[],
            external_sources=[],
            targets=[],
            external_targets=[],
            requirements=[],
            scheduler=None,
            data_source="test",
            hidden=False,
            links={},
        ),
    ]
    dmp_ref_parser.register_ref_type("dmp-task", EntityResolver(doc_tasks, _format_task))

    doc_tables = [
        DocTable(
            pk=f"{__name__}.TestTable",
            name="test_table",
            title=None,
            description="Table description",
            footer=None,
            sox_flg=False,
            auxiliary_flg=False,
            fields=[],  # fields are not used in tests for DmpRefParser
            doc_levels=None,
            domain_pk=None,
            db_type="greenplum",
            db_name="ritchie",
            db_path="test_schema.test_table",
            partition_scale=None,
            partition_field=None,
            is_external=False,
            module_path=__file__,
            module_name=f"{__name__}.TestTable",
            data_source="code",
            links={},
        ),
    ]
    dmp_ref_parser.register_ref_type("dmp-table", EntityResolver(doc_tables, _format_table))

    doc_domains = [
        DocDomain(
            pk=f"{__name__}.test_domain",
            module_path=__file__,
            prefix_key=test_prefix_key,
            type="core",
            code="test",
            description="Domain description",
            # Responsible/Data owner are not used in DmpRefParser tests
            responsible=[],
            data_owner=[],
            additional=[],
            module_name=__name__,
            attr_name="test_domain",
        ),
    ]
    dmp_ref_parser.register_ref_type("dmp-domain", EntityResolver(doc_domains, _format_domain))

    return dmp_ref_parser


def _replace_docutils(text: str):
    tree = publish_doctree(text)
    return publish_from_doctree(tree, writer_name='pseudoxml').decode().strip()


class TestRefParser(TestCase):
    dmp_ref_parser: DmpRefParser
    replace_template: str
    replace_unknown_template: str

    @classmethod
    def setUpClass(cls):
        cls.dmp_ref_parser = _setup()

        cls.replace_template = "{ref_type}/{label}/{link}"
        cls.replace_unknown_template = "{ref_type}:{entity_tag}:not found"

        cls.dmp_ref_parser.register_in_docutils()

    def replace(self, text: str):
        return self.dmp_ref_parser.dmp_ref_replace(
            text,
            self.replace_template,
            self.replace_unknown_template,
        )

    def test_text_parsing(self):
        text = f"""
        Test string with links:
        
        :dmp-task:`{test_etl}.test_task`
        :dmp-table:`{__name__}.TestTable`
        :dmp-domain:`{__name__}.test_domain`
        """.strip()

        expected_text = f"""
        Test string with links:
        
        dmp-task/test_task/task/{test_etl}/test_task
        dmp-table/test_schema.test_table/table/greenplum/ritchie/test_schema.test_table
        dmp-domain/{test_prefix_key.lower()}.core.test/domain/{test_prefix_key}/core/test/{__name__}/test_domain
        """.strip()
        parsed_text = self.replace(text)

        assert parsed_text == expected_text, \
            "DmpRefParser.dmp_ref_replace failed to parse the text with `:dmp-*:` references"

    def test_text_with_custom_labels(self):
        text = f"""
        Test string with links:
        
        :dmp-task:`custom task name <{test_etl}.test_task>`
        :dmp-table:`custom table name <{__name__}.TestTable>`
        :dmp-domain:`custom domain name <{__name__}.test_domain>`
        """.strip()

        expected_text = f"""
        Test string with links:
        
        dmp-task/custom task name/task/{test_etl}/test_task
        dmp-table/custom table name/table/greenplum/ritchie/test_schema.test_table
        dmp-domain/custom domain name/domain/{test_prefix_key}/core/test/{__name__}/test_domain
        """.strip()
        parsed_text = self.replace(text)

        assert parsed_text == expected_text, \
            "DmpRefParser.dmp_ref_replace failed to parse the text with custom names for references"

    def test_text_with_newlines_in_custom_labels(self):
        text = f"""
        Test string with links:
        
        :dmp-task:`custom task name \n <{test_etl}.test_task>`
        :dmp-table:`custom table name \n <{__name__}.TestTable>`
        :dmp-domain:`custom domain name \n <{__name__}.test_domain>`
        """.strip()

        expected_text = f"""
        Test string with links:
        
        dmp-task/custom task name/task/{test_etl}/test_task
        dmp-table/custom table name/table/greenplum/ritchie/test_schema.test_table
        dmp-domain/custom domain name/domain/{test_prefix_key}/core/test/{__name__}/test_domain
        """.strip()
        parsed_text = self.replace(text)

        assert parsed_text == expected_text, \
            "DmpRefParser.dmp_ref_replace failed to parse the text with custom names for references"

    def test_text_with_colon_in_custom_labels(self):
        text = f"""
        Test string with links:
        
        Task: link to :dmp-task:`custom task name \n <{test_etl}.test_task>`
        Table: link to :dmp-table:`custom table name \n <{__name__}.TestTable>`
        Domain: link to :dmp-domain:`custom domain name \n <{__name__}.test_domain>`
        """.strip()

        expected_text = f"""
        Test string with links:
        
        Task: link to dmp-task/custom task name/task/{test_etl}/test_task
        Table: link to dmp-table/custom table name/table/greenplum/ritchie/test_schema.test_table
        Domain: link to dmp-domain/custom domain name/domain/{test_prefix_key}/core/test/{__name__}/test_domain
        """.strip()
        parsed_text = self.replace(text)

        assert parsed_text == expected_text, \
            "DmpRefParser.dmp_ref_replace failed to parse the text with custom names for references"

    def test_text_with_unknown_entity_tags(self):
        text = (
            ":dmp-task:`this.task.does.not.exist`\n"
            ":dmp-table:`this.table.does.not.exist`\n"
            ":dmp-domain:`this.domain.does.not.exist`"
        )

        expected_text = (
            "dmp-task:this.task.does.not.exist:not found\n"
            "dmp-table:this.table.does.not.exist:not found\n"
            "dmp-domain:this.domain.does.not.exist:not found"
        )
        parsed_text = self.replace(text)

        assert parsed_text == expected_text, \
            "DmpRefParser.dmp_ref_replace failed to parse the text with unknown entity_tags"

    def test_text_with_unknown_ref_type(self):
        text = ":some_ref:`test.ref.body`"
        parsed_text = self.replace(text)

        assert parsed_text == text, \
            "DmpRefParser.dmp_ref_replace failed to parse the text with unknown ref_type"

    def test_role_parsing(self):
        text = f"""
        Test string with links:
        
        :dmp-task:`{test_etl}.test_task`
        :dmp-table:`{__name__}.TestTable`
        :dmp-domain:`{__name__}.test_domain`
        """.strip()

        expected_text = f"""
<document source="<string>">
    <paragraph>
        Test string with links:
    <block_quote>
        <paragraph>
            <reference refuri="task/{test_etl}/test_task">
                test_task
            
            <reference refuri="table/greenplum/ritchie/test_schema.test_table">
                test_schema.test_table
            
            <reference refuri="domain/{test_prefix_key}/core/test/{__name__}/test_domain">
                {test_prefix_key.lower()}.core.test
            
        """.strip()

        parsed_text = _replace_docutils(text)
        assert parsed_text == expected_text, \
            "DmpRefParser role interface failed to parse a reference from docutils"

    def test_role_with_custom_labels(self):
        text = f"""
        Test string with links:
        
        :dmp-task:`custom task name <{test_etl}.test_task>`
        :dmp-table:`custom table name <{__name__}.TestTable>`
        :dmp-domain:`custom domain name <{__name__}.test_domain>`
        """.strip()

        expected_text = f"""
<document source="<string>">
    <paragraph>
        Test string with links:
    <block_quote>
        <paragraph>
            <reference refuri="task/{test_etl}/test_task">
                custom task name
            
            <reference refuri="table/greenplum/ritchie/test_schema.test_table">
                custom table name
            
            <reference refuri="domain/{test_prefix_key}/core/test/{__name__}/test_domain">
                custom domain name
            
        """.strip()

        parsed_text = _replace_docutils(text)
        assert parsed_text == expected_text, \
            "DmpRefParser role interface failed to parse a reference with custom name from docutils"

    def test_role_with_newlines_in_custom_labels(self):
        text = f"""
        Test string with links:
        
        :dmp-task:`custom task name
        <{test_etl}.test_task>`
        :dmp-table:`custom table name
        <{__name__}.TestTable>`
        :dmp-domain:`custom domain name
        <{__name__}.test_domain>`
        """.strip()

        expected_text = f"""
<document source="<string>">
    <paragraph>
        Test string with links:
    <block_quote>
        <paragraph>
            <reference refuri="task/{test_etl}/test_task">
                custom task name
            
            <reference refuri="table/greenplum/ritchie/test_schema.test_table">
                custom table name
            
            <reference refuri="domain/{test_prefix_key}/core/test/{__name__}/test_domain">
                custom domain name
            
        """.strip()

        parsed_text = _replace_docutils(text)
        assert parsed_text == expected_text, \
            "DmpRefParser role interface failed to parse a reference with custom name from docutils"

    def test_role_with_colon_in_custom_labels(self):
        text = f"""
        Test string with links:
        
        Task: link to :dmp-task:`custom task name
        <{test_etl}.test_task>`
        Table: link to :dmp-table:`custom table name
        <{__name__}.TestTable>`
        Domain: link to :dmp-domain:`custom domain name
        <{__name__}.test_domain>`
        """.strip()

        expected_text = f"""
<document source="<string>">
    <paragraph>
        Test string with links:
    <block_quote>
        <paragraph>
            Task: link to 
            <reference refuri="task/{test_etl}/test_task">
                custom task name
            
            Table: link to 
            <reference refuri="table/greenplum/ritchie/test_schema.test_table">
                custom table name
            
            Domain: link to 
            <reference refuri="domain/{test_prefix_key}/core/test/{__name__}/test_domain">
                custom domain name
            
        """.strip()

        parsed_text = _replace_docutils(text)
        assert parsed_text == expected_text, \
            "DmpRefParser role interface failed to parse a reference with custom name from docutils"

    def test_role_with_unknown_entity_tags(self):
        text = (
            ":dmp-task:`this.task.does.not.exist` "
            ":dmp-table:`this.table.does.not.exist` "
            ":dmp-domain:`this.domain.does.not.exist`"
        )

        expected_text = """
<document source="<string>">
    <paragraph>
        this.task.does.not.exist
         
        this.table.does.not.exist
         
        this.domain.does.not.exist
    <system_message level="3" line="1" source="<string>" type="ERROR">
        <paragraph>
            Could not find referenced tag: `this.task.does.not.exist`
    <system_message level="3" line="1" source="<string>" type="ERROR">
        <paragraph>
            Could not find referenced tag: `this.table.does.not.exist`
    <system_message level="3" line="1" source="<string>" type="ERROR">
        <paragraph>
            Could not find referenced tag: `this.domain.does.not.exist`
        """.strip()

        parsed_text = _replace_docutils(text)
        assert parsed_text == expected_text, \
            "DmpRefParser role interface failed to parse a reference with unknown tag from docutils"

    def test_ref_validation_on_non_existing_reference_strict(self):
        text = ":dmp-task:`this.task.does.not.exist`"
        with pytest.raises(ReferenceParsingError) as e:
            self.dmp_ref_parser.dmp_ref_validate(text, strict_mode=True)
        assert e.value.message == f"Could not parse '{text}'. Unknown entity tag `this.task.does.not.exist`", \
            "DmpRefParser returns invalid message on validation error"

    def test_ref_validation_on_non_existing_reference(self):
        text = ":dmp-task:`this.task.does.not.exist` "
        expected = not self.dmp_ref_parser.dmp_ref_validate(text, strict_mode=False)
        assert expected, "DmpRefParser returns True on validation error"

    def test_ref_validation_valid_text(self):
        text = textwrap.dedent(f"""
        Test string with links:

        :dmp-task:`{test_etl}.test_task`
        :dmp-table:`{__name__}.TestTable`
        :dmp-domain:`{__name__}.test_domain`
        """)
        expected = self.dmp_ref_parser.dmp_ref_validate(text, strict_mode=True)
        assert expected, "DmpRefParser returns False on valid input validation"
        expected = self.dmp_ref_parser.dmp_ref_validate(text, strict_mode=False)
        assert expected, "DmpRefParser returns False on valid input validation"
