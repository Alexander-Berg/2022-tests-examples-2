import datetime

import jsonschema
import pytest

from taxi.util import yaml_util

from archiving import classes
from archiving import cron_run
from archiving import data_preparing
from archiving import loaders
from archiving import settings
from test_archiving import consts

_NOW = datetime.datetime(2020, 1, 1)

_FILTER_DICTS = {
    data_preparing.PreparingFuncTypes.aggregation: (
        data_preparing.AGGREGATION_CLASSES
    ),
    data_preparing.PreparingFuncTypes.filtering: (
        data_preparing.FILTERING_CLASSES
    ),
}


@pytest.mark.norerun
async def test_rules_filters(
        cron_context, rules_directories, requests_handlers,
):
    rules_dir = rules_directories(real_rules=True)[0]
    rules = await loaders.load_all_archiving_rules(
        cron_context.clients.archiving_admin,
        cron_context.config,
        rules_dir=rules_dir,
    )
    rule: classes.ArchivingRule
    for rule in rules:
        for preparing_func in rule.preparing_funcs:
            assert preparing_func.name in _FILTER_DICTS[preparing_func.type]


@pytest.mark.norerun
def test_validate_rules(rules_directories):
    schema_path = settings.ROOT_DIR_OBJ.joinpath(
        'schemas', 'archiving_rules.yaml',
    )
    rules_dirs = rules_directories(real_rules=True, test_rules=True)
    schema = yaml_util.load_file(schema_path)
    for directory in rules_dirs:
        for preparing_info in loaders.get_rules_static_info(directory):
            jsonschema.validate(preparing_info.raw_rule, schema)


def _parametrize_rule_names():
    all_rules_preparing_info = loaders.get_rules_static_info(
        rules_dir=settings.RULES_DIR,
    )
    rule_names = []
    for preparing_info in all_rules_preparing_info:
        rule_names.append(preparing_info.name)
    return pytest.mark.parametrize('rule_name', rule_names)


@_parametrize_rule_names()
@pytest.mark.norerun
@pytest.mark.now(_NOW.isoformat())
async def test_construct_archivers(
        cron_context,
        rule_name,
        monkeypatch,
        replication_state_min_ts,
        fake_task_id,
        requests_handlers,
        pg_secdist_patch,
):
    archiving_rule: classes.ArchivingRule = await loaders.load_rule(
        cron_context.clients.archiving_admin, rule_name, cron_context.config,
    )

    async def _fake_patch_docs_preparer(*args, **kwargs):
        return None

    monkeypatch.setattr(
        cron_run, '_patch_doc_preparer', _fake_patch_docs_preparer,
    )
    replication_state_min_ts.apply(consts.ORDER_PROCS_MIN_TS_MOCK)
    replication_rule_name = archiving_rule.replication_metainfo.rule_name
    ttl_info = archiving_rule.ttl_info
    field = 'fake' if ttl_info is None else ttl_info.field
    if replication_rule_name is not None:
        replication_state_min_ts.apply_simple(
            [archiving_rule.replication_metainfo.rule_name]
            + (archiving_rule.replication_metainfo.dependent_rule_names or []),
            field=field,
            replication_min_ts=_NOW,
        )

    await cron_run.prepare_archivers(cron_context, rule_name, fake_task_id)
