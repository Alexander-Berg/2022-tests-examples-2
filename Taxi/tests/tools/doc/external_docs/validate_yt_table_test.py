from unittest import TestCase

from tools.doc.collector.yt_utils import (
    validate_external_doc_tables,
    ReportKeyCollisionDMP,
    ReportKeyCollisionExternal,
    ReportDomainAbsence,
    ReportLackOfDocLevels,
    ReportDocPathCollision,
    ReportDocLevelForbiddenCharacters,
    ReportDocLevelNonASCII,
    ReportDocLevelDifferenceInTitle,
    ReportDocLevelDifferenceInDescription,
    ReportDBPathCollision,
    validate_external_doc_table_links,
    ReportTableLinkSourceAbsence,
    ReportTableLinkTargetAbsence,
    ReportTableLinkDataSourceMismatch,
)
from tools.doc.primitives import DocTable, DocDomain, DocTask
from tools.doc.primitives.table import DocLevel


class TestExternalDocValidation(TestCase):
    @staticmethod
    def _dummy_fields() -> dict:
        return dict(
            name="table",
            title=None,
            description=None,
            footer=None,
            sox_flg=False,
            auxiliary_flg=False,
            fields=[],
            partition_scale=None,
            partition_field=None,
            is_external=False,
            module_path=None,
            module_name=None,
            links={}
        )

    def setUp(self) -> None:
        self.maxDiff = None     # Отключить сокращение диффа из-за длины

        self.dmp_doc_tables = [
            DocTable(
                pk="tools.dmp.table1",
                doc_levels=(
                    DocLevel("tools", "tools", title="Tools prefix",
                             description="This is a directory for holding all tables for tests"),
                    DocLevel("tools/yt", "yt"),
                    DocLevel("tools/yt/table1", "table1"),
                ),
                db_type="yt",
                db_name="hahn",
                db_path="//home/table1",
                domain_pk="test.domain",
                data_source="code",

                # not needed for tests
                **self._dummy_fields()
            ),
            DocTable(
                pk="tools.dmp.table2",
                doc_levels=(
                    DocLevel("tools", "tools", title="Tools prefix",
                             description="This is a directory for holding all tables for tests"),
                    DocLevel("tools/yt", "yt"),
                    DocLevel("tools/yt/table2", "table2"),
                ),
                db_type="yt",
                db_name="hahn",
                db_path="//home/table2",
                domain_pk="test.domain",
                data_source="code",

                # not needed for tests
                **self._dummy_fields()
            ),
            DocTable(
                pk="tools2.dmp.table1",
                doc_levels=(
                    DocLevel("tools2", "tools2", title="Second tools prefix"),
                    DocLevel("tools2/yt", "yt"),
                    DocLevel("tools2/yt/table1", "table1"),
                ),
                db_type="yt",
                db_name="hahn",
                db_path="//home/tools2/table1",
                domain_pk="test.domain",
                data_source="code",

                # not needed for tests
                **self._dummy_fields()
            ),
            DocTable(
                pk="tools3.dmp.table1",
                doc_levels=(
                    DocLevel("tools3", "tools3", title="One more prefix"),
                    DocLevel("tools3/yt", "yt"),
                    DocLevel("tools3/yt/one-more", "one-more", title="Some random subfolder"),
                    DocLevel("tools3/yt/one-more/table1", "table1"),
                ),
                db_type="yt",
                db_name="hahn",
                db_path="//home/tools3/table1",
                domain_pk="test.domain",
                data_source="code",

                # not needed for tests
                **self._dummy_fields()
            ),
        ]

        self.domains = [
            DocDomain(
                pk="test.domain",
                prefix_key="test",
                type="core",
                code="domain",

                # not needed for tests
                description="",
                responsible=[],
                data_owner=[],
                additional=[],
                module_name="",
                attr_name="",
                module_path="",
            )
        ]

    def test_correct_table(self):
        external = DocTable(
            pk="external.table1",
            doc_levels=(
                DocLevel("external", "external", title="External tables"),
                DocLevel("external/yt", "yt"),
                DocLevel("external/yt/table1", "table1"),
            ),
            db_type="yt",
            db_name="hahn",
            db_path="//home/external/table1",
            domain_pk=None,
            data_source="external",

            # not needed for tests
            **self._dummy_fields()
        )
        correct_tables, errors = validate_external_doc_tables(self.dmp_doc_tables, [external], self.domains)
        self.assertListEqual(correct_tables, [external], "Correct table must pass")
        self.assertEqual(len(errors), 0, "Correct table should not have any errors")

    def test_pk_collision(self):
        external = DocTable(
            pk="tools.dmp.table1",
            doc_levels=(
                DocLevel("external", "external", title="External tables"),
                DocLevel("external/yt", "yt"),
                DocLevel("external/yt/table1", "table1"),
            ),
            db_type="yt",
            db_name="hahn",
            db_path="//home/external/table1",
            domain_pk=None,
            data_source="external",

            # not needed for tests
            **self._dummy_fields()
        )
        correct_tables, errors = validate_external_doc_tables(self.dmp_doc_tables, [external], self.domains)
        pk_collision_report = ReportKeyCollisionDMP.from_external_doc_table(external)
        self.assertListEqual(errors, [pk_collision_report], "External table with PK collision must have an error")
        self.assertEqual(len(correct_tables), 0, "Incorrect table must not pass validation")

    def test_pk_collision_with_external(self):
        external1 = DocTable(
            pk="external.table1",
            doc_levels=(
                DocLevel("external", "external", title="External tables"),
                DocLevel("external/yt", "yt"),
                DocLevel("external/yt/table1", "table1"),
            ),
            db_type="yt",
            db_name="hahn",
            db_path="//home/external/table1",
            domain_pk=None,
            data_source="external",

            # not needed for tests
            **self._dummy_fields()
        )
        external2 = DocTable(
            pk="external.table1",
            doc_levels=(
                DocLevel("external2", "external2", title="External tables"),
                DocLevel("external2/yt", "yt"),
                DocLevel("external2/yt/table1", "table1"),
            ),
            db_type="yt",
            db_name="hahn",
            db_path="//home/external2/table1",
            domain_pk=None,
            data_source="external",

            # not needed for tests
            **self._dummy_fields()
        )
        correct_tables, errors = validate_external_doc_tables(self.dmp_doc_tables, [external1, external2], self.domains)
        pk_collision_report = ReportKeyCollisionExternal.from_external_doc_tables(external2, external1)
        self.assertListEqual(errors, [pk_collision_report], "External table with PK collision must have an error")
        self.assertListEqual(correct_tables, [external1], "Incorrect table must not pass validation")

    def test_table_with_existing_domain(self):
        external = DocTable(
            pk="external.table1",
            doc_levels=(
                DocLevel("external", "external", title="External tables"),
                DocLevel("external/yt", "yt"),
                DocLevel("external/yt/table1", "table1"),
            ),
            db_type="yt",
            db_name="hahn",
            db_path="//home/external/table1",
            domain_pk="test.domain",
            data_source="external",

            # not needed for tests
            **self._dummy_fields()
        )
        correct_tables, errors = validate_external_doc_tables(self.dmp_doc_tables, [external], self.domains)
        self.assertListEqual(correct_tables, [external], "Correct table with correct domain_pk must pass")
        self.assertEqual(len(errors), 0, "Correct table should not have any errors")

    def test_table_with_not_existing_domain(self):
        external = DocTable(
            pk="external.table1",
            doc_levels=(
                DocLevel("external", "external", title="External tables"),
                DocLevel("external/yt", "yt"),
                DocLevel("external/yt/table1", "table1"),
            ),
            db_type="yt",
            db_name="hahn",
            db_path="//home/external/table1",
            domain_pk="random.domain",
            data_source="external",

            # not needed for tests
            **self._dummy_fields()
        )
        correct_tables, errors = validate_external_doc_tables(self.dmp_doc_tables, [external], self.domains)
        no_domain_report = ReportDomainAbsence.from_external_doc_table(external)
        self.assertListEqual(
            errors,
            [no_domain_report],
            "External table with non-existent domain PK must have an error",
        )
        self.assertListEqual(correct_tables, [], "Incorrect table must not pass validation")

    def test_table_with_wrong_number_of_doc_levels(self):
        external = DocTable(
            pk="external.table1",
            doc_levels=(
                # Технический слой, который всегда автоматически добавляется, поэтому не засчитывается в валидации
                DocLevel("yt", "yt"),
            ),
            db_type="yt",
            db_name="hahn",
            db_path="//home/external/table1",
            domain_pk=None,
            data_source="external",

            # not needed for tests
            **self._dummy_fields()
        )
        correct_tables, errors = validate_external_doc_tables(self.dmp_doc_tables, [external], self.domains)
        wrong_doc_levels = ReportLackOfDocLevels.from_external_doc_table(external)
        self.assertListEqual(errors, [wrong_doc_levels], "External table with empty doc_levels must have an error")
        self.assertListEqual(correct_tables, [], "Incorrect table must not pass validation")

    def test_table_colliding_doc_path(self):
        external = DocTable(
            pk="external.table1",
            doc_levels=(
                DocLevel("tools", "tools"),
                DocLevel("tools/yt", "yt"),
                DocLevel("tools/yt/table1", "table1"),
            ),
            db_type="yt",
            db_name="hahn",
            db_path="//home/external/table1",
            domain_pk=None,
            data_source="external",

            # not needed for tests
            **self._dummy_fields()
        )
        correct_tables, errors = validate_external_doc_tables(self.dmp_doc_tables, [external], self.domains)
        wrong_doc_levels = ReportDocPathCollision.from_external_doc_tables(external, self.dmp_doc_tables[0])
        self.assertListEqual(errors, [wrong_doc_levels], "External table with colliding doc path must have an error")
        self.assertListEqual(correct_tables, [], "Incorrect table must not pass validation")

    def test_table_with_forbidden_symbol_in_doc_level(self):
        external = DocTable(
            pk="external.table1",
            doc_levels=(
                DocLevel("external", "external"),
                DocLevel("external/yt", "yt"),
                DocLevel("external/yt/subfolder/table1", "subfolder/table1"),
            ),
            db_type="yt",
            db_name="hahn",
            db_path="//home/external/table1",
            domain_pk=None,
            data_source="external",

            # not needed for tests
            **self._dummy_fields()
        )
        correct_tables, errors = validate_external_doc_tables(self.dmp_doc_tables, [external], self.domains)
        wrong_doc_levels = ReportDocLevelForbiddenCharacters.from_external_doc_table_and_doc_level(
            external,
            external.doc_levels[2],
        )
        self.assertListEqual(
            errors,
            [wrong_doc_levels],
            "External table with forbidden symbol in doc_level must have an error",
        )
        self.assertListEqual(correct_tables, [], "Incorrect table must not pass validation")

    def test_table_with_forbidden_symbols_in_all_doc_levels(self):
        external = DocTable(
            pk="external.table1",
            doc_levels=(
                DocLevel("<external>", "<external>"),
                DocLevel("<external>/yt,gp", "yt,gp"),
                DocLevel("<external>/yt,gp/subfolder/table1", "subfolder/table1"),
            ),
            db_type="yt",
            db_name="hahn",
            db_path="//home/external/table1",
            domain_pk=None,
            data_source="external",

            # not needed for tests
            **self._dummy_fields()
        )
        correct_tables, errors = validate_external_doc_tables(self.dmp_doc_tables, [external], self.domains)
        wrong_doc_levels = [
            ReportDocLevelForbiddenCharacters.from_external_doc_table_and_doc_level(
                external,
                doc_level,
            )
            for doc_level in external.doc_levels
        ]
        self.assertListEqual(
            errors,
            wrong_doc_levels,
            "External table with forbidden symbols in multiple doc_levels must have an error for every wrong level"
        )
        self.assertListEqual(correct_tables, [], "Incorrect table must not pass validation")

    def test_table_with_forbidden_symbols_and_non_ascii_names_in_all_doc_levels(self):
        external = DocTable(
            pk="external.table1",
            doc_levels=(
                DocLevel("<внешние>", "<внешние>"),
                DocLevel("<внешние>/yt,gp,🔥", "yt,gp,🔥"),
                DocLevel("<внешние>/yt,gp,🔥/subfolder/自業自得/table1", "subfolder/自業自得/table1"),
            ),
            db_type="yt",
            db_name="hahn",
            db_path="//home/external/table1",
            domain_pk=None,
            data_source="external",

            # not needed for tests
            **self._dummy_fields()
        )
        correct_tables, errors = validate_external_doc_tables(self.dmp_doc_tables, [external], self.domains)
        wrong_doc_levels = []
        for doc_level in external.doc_levels:
            wrong_doc_levels.append(
                ReportDocLevelForbiddenCharacters.from_external_doc_table_and_doc_level(external, doc_level)
            )
            wrong_doc_levels.append(
                ReportDocLevelNonASCII.from_external_doc_table_and_doc_level(external, doc_level)
            )

        self.assertListEqual(
            errors,
            wrong_doc_levels,
            "External table with forbidden symbols in multiple doc_levels must have an error for every wrong level"
        )
        self.assertListEqual(correct_tables, [], "Incorrect table must not pass validation")

    def test_doc_level_title_difference_with_dmp(self):
        external = DocTable(
            pk="external.table1",
            doc_levels=(
                    DocLevel("tools", "tools", title="Tools prefix from external"),
                    DocLevel("tools/yt", "yt"),
                    DocLevel("tools/yt/table_ext1", "table_ext1"),
            ),
            db_type="yt",
            db_name="hahn",
            db_path="//home/external/table1",
            domain_pk=None,
            data_source="external",

            # not needed for tests
            **self._dummy_fields()
        )
        correct_tables, errors = validate_external_doc_tables(self.dmp_doc_tables, [external], self.domains)
        wrong_doc_levels = ReportDocLevelDifferenceInTitle.from_external_doc_table_and_doc_levels(
            external,
            external.doc_levels[0],
            self.dmp_doc_tables[0].doc_levels[0],
        )
        self.assertListEqual(
            errors,
            [wrong_doc_levels],
            "External table with colliding title for doc_level must have an error",
        )
        self.assertListEqual(correct_tables, [], "Incorrect table must not pass validation")

    def test_doc_level_description_difference_with_dmp(self):
        external = DocTable(
            pk="external.table1",
            doc_levels=(
                    DocLevel("tools", "tools", description="Some description to collide with dmp"),
                    DocLevel("tools/yt", "yt"),
                    DocLevel("tools/yt/table_ext1", "table_ext1"),
            ),
            db_type="yt",
            db_name="hahn",
            db_path="//home/external/table1",
            domain_pk=None,
            data_source="external",

            # not needed for tests
            **self._dummy_fields()
        )
        correct_tables, errors = validate_external_doc_tables(self.dmp_doc_tables, [external], self.domains)
        wrong_doc_levels = ReportDocLevelDifferenceInDescription.from_external_doc_table_and_doc_levels(
            external,
            external.doc_levels[0],
            self.dmp_doc_tables[0].doc_levels[0],
        )
        self.assertListEqual(
            errors,
            [wrong_doc_levels],
            "External table with colliding description for doc_level must have an error",
        )
        self.assertListEqual(correct_tables, [], "Incorrect table must not pass validation")

    def test_doc_level_title_and_description_difference_with_dmp(self):
        external = DocTable(
            pk="external.table1",
            doc_levels=(
                    DocLevel("tools", "tools", title="Tools prefix from external",
                             description="Some description to collide with dmp"),
                    DocLevel("tools/yt", "yt"),
                    DocLevel("tools/yt/table_ext1", "table_ext1"),
            ),
            db_type="yt",
            db_name="hahn",
            db_path="//home/external/table1",
            domain_pk=None,
            data_source="external",

            # not needed for tests
            **self._dummy_fields()
        )
        correct_tables, errors = validate_external_doc_tables(self.dmp_doc_tables, [external], self.domains)
        collided_title = ReportDocLevelDifferenceInTitle.from_external_doc_table_and_doc_levels(
            external,
            external.doc_levels[0],
            self.dmp_doc_tables[0].doc_levels[0],
        )
        collided_description = ReportDocLevelDifferenceInDescription.from_external_doc_table_and_doc_levels(
            external,
            external.doc_levels[0],
            self.dmp_doc_tables[0].doc_levels[0],
        )
        self.assertListEqual(
            errors,
            [collided_title, collided_description],
            "External table with colliding title and description for doc_level "
            "must have an error for both colliding parameters"
        )
        self.assertListEqual(correct_tables, [], "Incorrect table must not pass validation")

    def test_multiple_doc_levels_title_and_description_difference_with_dmp_and_external(self):
        external1 = DocTable(
            pk="external.table1",
            doc_levels=(
                    DocLevel("tools", "tools"),
                    DocLevel("tools/yt", "yt"),
                    DocLevel("tools/yt/external", "external", title="External folder"),
                    DocLevel("tools/yt/external/table_ext1", "table_ext1"),
            ),
            db_type="yt",
            db_name="hahn",
            db_path="//home/external/table1",
            domain_pk=None,
            data_source="external",

            # not needed for tests
            **self._dummy_fields()
        )
        external2 = DocTable(
            pk="external.table2",
            doc_levels=(
                    DocLevel("tools", "tools", title="Tools prefix from external",
                             description="Some description to collide with dmp"),
                    DocLevel("tools/yt", "yt"),
                    DocLevel("tools/yt/external", "external", title="Colliding with external folder"),
                    DocLevel("tools/yt/external/table_ext2", "table_ext2"),
            ),
            db_type="yt",
            db_name="hahn",
            db_path="//home/external/table2",
            domain_pk=None,
            data_source="external",

            # not needed for tests
            **self._dummy_fields()
        )
        correct_tables, errors = validate_external_doc_tables(self.dmp_doc_tables, [external1, external2], self.domains)
        collided_dmp_title = ReportDocLevelDifferenceInTitle.from_external_doc_table_and_doc_levels(
            external2,
            external2.doc_levels[0],
            self.dmp_doc_tables[0].doc_levels[0],
        )
        collided_dmp_description = ReportDocLevelDifferenceInDescription.from_external_doc_table_and_doc_levels(
            external2,
            external2.doc_levels[0],
            self.dmp_doc_tables[0].doc_levels[0],
        )
        collided_external = ReportDocLevelDifferenceInTitle.from_external_doc_table_and_doc_levels(
            external2,
            external2.doc_levels[2],
            external1.doc_levels[2],
        )
        self.assertListEqual(
            errors,
            [collided_dmp_title, collided_dmp_description, collided_external],
            "External table with colliding title and description for doc_level "
            "must have an error for both colliding with dmp and external"
        )
        self.assertListEqual(correct_tables, [external1], "Incorrect table must not pass validation")

    def test_table_colliding_db_path_with_dmp(self):
        external = DocTable(
            pk="external.table1",
            doc_levels=(
                DocLevel("external", "external"),
                DocLevel("external/yt", "yt"),
                DocLevel("external/yt/table1", "table1"),
            ),
            db_type="yt",
            db_name="hahn",
            db_path="//home/table1",
            domain_pk=None,
            data_source="external",

            # not needed for tests
            **self._dummy_fields()
        )
        correct_tables, errors = validate_external_doc_tables(self.dmp_doc_tables, [external], self.domains)
        wrong_doc_levels = ReportDBPathCollision.from_external_doc_tables(external, self.dmp_doc_tables[0])
        self.assertListEqual(errors, [wrong_doc_levels], "External table with colliding db_path must have an error")
        self.assertListEqual(correct_tables, [], "Incorrect table must not pass validation")

    def test_table_colliding_db_path_with_external(self):
        external1 = DocTable(
            pk="external.table1",
            doc_levels=(
                DocLevel("external", "external"),
                DocLevel("external/yt", "yt"),
                DocLevel("external/yt/table1", "table1"),
            ),
            db_type="yt",
            db_name="hahn",
            db_path="//home/external/table1",
            domain_pk=None,
            data_source="external",

            # not needed for tests
            **self._dummy_fields()
        )
        external2 = DocTable(
            pk="external.table2",
            doc_levels=(
                DocLevel("external", "external"),
                DocLevel("external/yt", "yt"),
                DocLevel("external/yt/other_table", "other_table"),
            ),
            db_type="yt",
            db_name="hahn",
            db_path="//home/external/table1",
            domain_pk=None,
            data_source="external",

            # not needed for tests
            **self._dummy_fields()
        )
        correct_tables, errors = validate_external_doc_tables(self.dmp_doc_tables, [external1, external2], self.domains)
        wrong_doc_levels = ReportDBPathCollision.from_external_doc_tables(external2, external1)
        self.assertListEqual(
            errors,
            [wrong_doc_levels],
            "External table with colliding db_path with external table must have an error",
        )
        self.assertListEqual(correct_tables, [external1], "Incorrect table must not pass validation")

    def test_tables_with_same_db_paths_in_different_clusters(self):
        external1 = DocTable(
            pk="external.table1",
            doc_levels=(
                DocLevel("external", "external"),
                DocLevel("external/yt", "yt"),
                DocLevel("external/yt/table1", "table1"),
            ),
            db_type="yt",
            db_name="hahn",
            db_path="//home/external/table1",
            domain_pk=None,
            data_source="external",

            # not needed for tests
            **self._dummy_fields()
        )
        external2 = DocTable(
            pk="external.table2",
            doc_levels=(
                DocLevel("external", "external"),
                DocLevel("external/yt-arnold", "yt-arnold"),
                DocLevel("external/yt-arnold/table1", "table1"),
            ),
            db_type="yt",
            db_name="arnold",
            db_path="//home/external/table1",
            domain_pk=None,
            data_source="external",

            # not needed for tests
            **self._dummy_fields()
        )
        correct_tables, errors = validate_external_doc_tables(self.dmp_doc_tables, [external1, external2], self.domains)
        self.assertListEqual(correct_tables, [external1, external2], "Correct table must pass")
        self.assertEqual(len(errors), 0, "Correct tables should not have any errors")

    def test_duplicate_table(self):
        external = DocTable(
            pk="external.table1",
            doc_levels=(
                DocLevel("external", "external"),
                DocLevel("external/yt", "yt"),
                DocLevel("external/yt/table1", "table1"),
            ),
            db_type="yt",
            db_name="hahn",
            db_path="//home/external/table1",
            domain_pk=None,
            data_source="external",

            # not needed for tests
            **self._dummy_fields()
        )
        correct_tables, errors = validate_external_doc_tables(self.dmp_doc_tables, [external, external], self.domains)
        expected_errors = [
            ReportKeyCollisionExternal.from_external_doc_tables(external, external),
            ReportDocPathCollision.from_external_doc_tables(external, external),
            ReportDBPathCollision.from_external_doc_tables(external, external),
        ]
        self.assertListEqual(errors, expected_errors, "External table with colliding doc path must have an error")
        self.assertListEqual(correct_tables, [external], "Duplicate table must not pass validation")

    def test_multiple_error_table(self):
        external = DocTable(
            pk="tools.dmp.table1",
            doc_levels=(
                DocLevel("tools", "tools", title="Wrong title", description="Wrong description"),
                DocLevel("tools/yt-hahn,arnold", "yt-hahn,arnold"),
                DocLevel("tools/yt-hahn,arnold/table", "table"),
            ),
            db_type="yt",
            db_name="hahn",
            db_path="//home/table1",
            domain_pk="non-existent",
            data_source="external",

            # not needed for tests
            **self._dummy_fields()
        )
        correct_tables, errors = validate_external_doc_tables(self.dmp_doc_tables, [external], self.domains)
        expected_errors = [
            ReportKeyCollisionDMP.from_external_doc_table(external),
            ReportDomainAbsence.from_external_doc_table(external),
            ReportDBPathCollision.from_external_doc_tables(external, self.dmp_doc_tables[0]),
            ReportDocLevelDifferenceInTitle.from_external_doc_table_and_doc_levels(
                external,
                external.doc_levels[0],
                self.dmp_doc_tables[0].doc_levels[0],
            ),
            ReportDocLevelDifferenceInDescription.from_external_doc_table_and_doc_levels(
                external,
                external.doc_levels[0],
                self.dmp_doc_tables[0].doc_levels[0],
            ),
            ReportDocLevelForbiddenCharacters.from_external_doc_table_and_doc_level(external, external.doc_levels[1]),
        ]

        self.assertListEqual(errors, expected_errors, "External table with colliding doc path must have an error")
        self.assertListEqual(correct_tables, [], "Incorrect table must not pass validation")

    @staticmethod
    def _dummy_link_fields() -> dict:
        return dict(
            etl_service_name="test",
            description=None,
            module_path=None,
            module_name=None,
            external_sources=[],
            external_targets=[],
            requirements=[],
            scheduler=None,
            hidden=True,
            links={},
        )

    def test_valid_table_table_link(self):
        link = DocTask(
            pk="link",
            name="link",
            sources=["tools.dmp.table1"],
            targets=["tools.dmp.table2"],
            data_source="code",

            # not needed for tests
            **self._dummy_link_fields()
        )

        valid_links, errors = validate_external_doc_table_links(self.dmp_doc_tables, [link])
        self.assertListEqual(valid_links, [link], "Correct table link must pass")
        self.assertListEqual(errors, [], "Correct table links should not have any errors")

    def test_table_table_link_to_same_table(self):
        link = DocTask(
            pk="link",
            name="link",
            sources=["tools.dmp.table1"],
            targets=["tools.dmp.table1"],
            data_source="code",

            # not needed for tests
            **self._dummy_link_fields()
        )

        valid_links, errors = validate_external_doc_table_links(self.dmp_doc_tables, [link])
        self.assertListEqual(valid_links, [link], "Correct table link must pass")
        self.assertListEqual(errors, [], "Correct table links should not have any errors")

    def test_table_table_link_with_unknown_source(self):
        link = DocTask(
            pk="link",
            name="link",
            sources=["unknown"],
            targets=["tools.dmp.table2"],
            data_source="code",

            # not needed for tests
            **self._dummy_link_fields()
        )

        valid_links, errors = validate_external_doc_table_links(self.dmp_doc_tables, [link])
        expected_errors = [ReportTableLinkSourceAbsence.from_table_link_task(link)]
        self.assertListEqual(errors, expected_errors, "Table link with unknown table as source must have an error")
        self.assertListEqual(valid_links, [], "Incorrect table link must not pass validation")

    def test_table_table_link_with_unknown_target(self):
        link = DocTask(
            pk="link",
            name="link",
            sources=["tools.dmp.table1"],
            targets=["unknown"],
            data_source="code",

            # not needed for tests
            **self._dummy_link_fields()
        )

        valid_links, errors = validate_external_doc_table_links(self.dmp_doc_tables, [link])
        expected_errors = [ReportTableLinkTargetAbsence.from_table_link_task(link)]
        self.assertListEqual(errors, expected_errors, "Table link with unknown table as target must have an error")
        self.assertListEqual(valid_links, [], "Incorrect table link must not pass validation")

    def test_table_table_link_with_mismatched_data_source(self):
        link = DocTask(
            pk="link",
            name="link",
            sources=["tools.dmp.table1"],
            targets=["tools.dmp.table2"],
            data_source="external",

            # not needed for tests
            **self._dummy_link_fields()
        )

        valid_links, errors = validate_external_doc_table_links(self.dmp_doc_tables, [link])
        expected_errors = [
            ReportTableLinkDataSourceMismatch.from_table_link_task_and_doc_tables(
                link,
                self.dmp_doc_tables[0],
                self.dmp_doc_tables[1],
            ),
        ]
        self.assertListEqual(errors, expected_errors, "Table link with non-matching data_source must have an error")
        self.assertListEqual(valid_links, [], "Incorrect table link must not pass validation")

    def test_table_table_link_with_unknown_source_and_target(self):
        link = DocTask(
            pk="link",
            name="link",
            sources=["unknown"],
            targets=["unknown"],
            data_source="code",

            # not needed for tests
            **self._dummy_link_fields()
        )

        valid_links, errors = validate_external_doc_table_links(self.dmp_doc_tables, [link])
        expected_errors = [
            ReportTableLinkSourceAbsence.from_table_link_task(link),
            ReportTableLinkTargetAbsence.from_table_link_task(link),
        ]
        self.assertListEqual(errors, expected_errors, "Table link with non-matching data_source must have an error")
        self.assertListEqual(valid_links, [], "Incorrect table link must not pass validation")
