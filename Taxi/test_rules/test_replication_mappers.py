import os
import typing

import pytest

from replication_core import load
from replication_core.pytest_plugins import mappers as parametrize_mappers
from replication_core.rules import classes

from replication import replication_yaml as replication_yaml_module
from replication import settings
from replication.common.pytest import mappers_util
from replication.common.pytest import replication_rules
from replication.common.yt_tools import schema_validation
from replication.foundation import consts
from . import conftest


@conftest.any_rules
def test_construct_generated_mappers(replication_ctx):
    replication_rules.run_test_construct_gen_mappers(replication_ctx)


# pylint: disable=too-many-nested-blocks
def _get_base_dirs():
    replication_yaml = replication_yaml_module.load(
        settings.REPLICATION_YAML_PATH,
    )
    scopes_info = replication_yaml.get_scopes_info()
    root_path = replication_yaml.get_root_path()
    base_dir = os.path.join(root_path, scopes_info.path)
    to_evolve = []
    if scopes_info.evolve_settings is not None:
        for evolve_settings in scopes_info.evolve_settings:
            to_evolve.extend(list(evolve_settings.iter_rule_scopes_paths()))
            evolve_settings.ensure_repo_pythonpath()
    if scopes_info.evolve is not None:
        to_evolve.extend(
            [
                os.path.join(root_path, to_evolve_path)
                for to_evolve_path in scopes_info.evolve
            ],
        )
    return base_dir, to_evolve


def _parametrize_yt_targets(base_dir, extra_dirs=None):
    rule_scopes = load.load_rule_scopes(base_dir, ensure_pythonpath=True)
    for extra_dir in extra_dirs or ():
        extra_scopes = load.load_rule_scopes(extra_dir, ensure_pythonpath=True)
        rule_scopes = rule_scopes.evolve(extra_scopes)

    values: typing.List[typing.Tuple[classes.RuleScope, classes.TargetObj]]
    values = [
        (rule_scope, target)
        for rule_scope in rule_scopes
        for rule in rule_scope.rules.values()
        for target in rule.targets.values()
        if (
            target.target_type == consts.TARGET_TYPE_YT
            and target.mapper_doc
            and not target.mapper_doc.get('test_skip_reason')
            and target.target_doc
            # The test does not support target schema validation with
            # 'overrides' key in schema.
            and not any(
                override.get('attributes', {}).get('schema')
                for override in target.target_doc.get('overrides', ())
            )
        )
    ]
    return pytest.mark.parametrize(
        ('rule_scope', 'target'),
        values,
        ids=[target.target_name for rule_scope, target in values],
    )


def _parametrize_mapper_index(base_dir, extra_dirs=None):
    rule_scopes = load.load_rule_scopes(base_dir, ensure_pythonpath=True)
    for extra_dir in extra_dirs or ():
        extra_scopes = load.load_rule_scopes(extra_dir, ensure_pythonpath=True)
        rule_scopes = rule_scopes.evolve(extra_scopes)
    values: typing.List[typing.Tuple[str, str]] = []
    for rule_scope in rule_scopes:
        for rule in rule_scope.rules.values():
            for target_name, target in rule.targets.items():
                mapper_path = target.declaration.get('mapper')
                if mapper_path != '$index':
                    continue
                mapper_testcase_full_path = os.path.join(
                    rule_scope.rule_scope_dir,
                    'mappers-tests',
                    'index',
                    target_name,
                )
                values.append((mapper_testcase_full_path, target_name))

    return pytest.mark.parametrize(
        ('testcase_path', 'target_name'),
        values,
        ids=[target_name for _, target_name in values],
    )


if settings.HAS_ENV_DMP_INSTALL_DIR:  # TODO: get rid of conditional
    _RULES_DIR, _EXTRA_DIRS = _get_base_dirs()

    @pytest.mark.now('2019-09-01T01:12:00+0000')
    @pytest.mark.nofilldb
    @parametrize_mappers.parametrize_mappers(
        _RULES_DIR,
        extra_dirs=_EXTRA_DIRS,
        map_parameters=conftest.MAPPING_PARAMS,
        test_extra_plugins=parametrize_mappers.TestExtraPlugins(
            test_extra_plugins=['replication.common.pytest.mappers_util'],
            extra_premap_getters=mappers_util.premaps_getter,
        ),
    )
    def test_data_mapper(
            mapper_check,
            rule_scope,
            mapper_path,
            mapper,
            testcase_path,
            freeze_time,
    ):
        mapper_check(testcase_path, mapper)

    @pytest.mark.nofilldb
    @_parametrize_yt_targets(_RULES_DIR, extra_dirs=_EXTRA_DIRS)
    def test_yt_schema_types(
            rule_scope: classes.RuleScope,
            target: classes.TargetObj,
            load_mapper_testcase,
    ):
        assert target.target_path
        assert target.target_doc
        target_validator = schema_validation.SchemaValidator(
            target.target_doc['attributes']['schema'],
        )
        testcases: typing.List[dict] = load_mapper_testcase(
            target.mapper_testcase_full_path,
        )
        assert testcases

        problems_by_doc: typing.Dict[typing.Tuple[int, int], typing.List[dict]]
        problems_by_doc = {}
        for case_no, case in enumerate(testcases):
            for doc_no, mapped_doc in enumerate(case['expected']):
                problems = target_validator.validate(mapped_doc)
                if problems:
                    problems_by_doc[(case_no, doc_no)] = problems

        if problems_by_doc:
            target_full_path = os.path.join(
                rule_scope.rule_scope_dir, 'yt-targets', target.target_path,
            )
            error_message = (
                f'One or more expected documents in testcase do not match'
                f' YT target schema.\n'
                f'Testcase path: {target.mapper_testcase_full_path}\n'
                f'Target path: {target_full_path}\n'
                + '\n'.join(
                    f'Case#{case_no} Doc#{doc_no} Problems:\n'
                    + '\n'.join(str(problem) for problem in problems)
                    for (case_no, doc_no), problems in problems_by_doc.items()
                )
            )
            pytest.fail(error_message)

    @conftest.dmp_rules_only
    @pytest.mark.nofilldb
    @_parametrize_mapper_index(_RULES_DIR, extra_dirs=_EXTRA_DIRS)
    def test_generated_mapper_index(
            replication_ctx,
            monkeypatch,
            mapper_check,
            testcase_path,
            target_name,
    ):
        target = replication_ctx.rule_keeper.rules_storage.get_target_by_name(
            target_name,
        )

        # pylint: disable=protected-access

        # the line below is needed to remove premapper
        # which expects field `data` in input test doc
        premappers = target.mapper._mapper._premappers[1:]
        monkeypatch.setattr(target.mapper._mapper, '_premappers', premappers)

        mapper_check(
            testcase_path,
            target.mapper._mapper,  # pylint: disable=protected-access
        )
