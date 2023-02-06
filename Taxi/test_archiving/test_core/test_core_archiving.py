import dataclasses
import os
import typing

import pytest

from archiving import core
from archiving import cron_run
from archiving import data_preparing
from archiving import loaders
from archiving.filters import base

_TEST_RULES_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'static', 'rules'),
)

_NOW = '2019-11-21T09:00:00'
_REPLICATION_MOCK_MIN_TS = '2019-11-20T07:50:00'


@dataclasses.dataclass(frozen=True)
class ResultChecker:
    before_archiving_ids: typing.Set
    after_archiving_ids: typing.Set


_RULES_RESULTS = {
    'test_rule': ResultChecker(
        before_archiving_ids=set(map(str, range(13))),
        after_archiving_ids={'0', '1', '2', '3', '5', '9', '10', '11', '12'},
    ),
    'test_rule_filter': ResultChecker(
        before_archiving_ids=set(map(str, range(11))),
        after_archiving_ids={'0', '1', '2', '3', '4', '5', '6', '9'},
    ),
}


def _parametrize_archiving_rules():
    all_rules_preparing_info = loaders.get_rules_static_info(
        rules_dir=_TEST_RULES_DIR,
    )
    test_ids = []
    parametrize_values = []
    rule_preparing_info: loaders.RulePreparingInfo
    for rule_preparing_info in all_rules_preparing_info:
        rule_name = rule_preparing_info.name
        if rule_name in _RULES_RESULTS:
            result_checker = _RULES_RESULTS[rule_name]
            before_docs = result_checker.before_archiving_ids
            expected_docs = result_checker.after_archiving_ids
            test_ids.append(rule_name)
            parametrize_values.append((rule_name, before_docs, expected_docs))
    return pytest.mark.parametrize(
        'archiving_rule_name, before_docs, expected_docs',
        parametrize_values,
        ids=test_ids,
    )


# pylint: disable=protected-access
@_parametrize_archiving_rules()
@pytest.mark.now(_NOW)
async def test_archive_documents(
        cron_context,
        patch_test_env,
        monkeypatch,
        load_all_mongo_docs,
        archiving_rule_name,
        before_docs,
        expected_docs,
        fake_task_id,
        replication_state_min_ts,
        requests_handlers,
):
    replication_state_min_ts.apply(
        {archiving_rule_name: ('updated', _REPLICATION_MOCK_MIN_TS)},
    )
    monkeypatch.setattr(
        data_preparing, 'FILTERING_CLASSES', _TEST_SINGLE_FILTERS,
    )
    monkeypatch.setattr(
        data_preparing, 'AGGREGATION_CLASSES', _TEST_AGGREGATION_FILTERS,
    )
    archivers = await cron_run.prepare_archivers(
        cron_context, archiving_rule_name, fake_task_id,
    )
    assert len(archivers) == 1
    archiver = next(iter(archivers.values()))
    assert set(await load_all_mongo_docs(archiving_rule_name)) == before_docs
    await core.remove_documents(archiver, cron_context.client_solomon)
    assert set(await load_all_mongo_docs(archiving_rule_name)) == expected_docs


class Mod3Filter(base.SingleDocFilter):
    def can_be_removed(self, doc):
        if int(doc['_id']) % 3 != 0:
            return True
        return False


class BiggerThan5Agg(base.AggDocFilter):
    async def get_docs_for_deletion(self, docs):
        return [doc for doc in docs if int(doc['_id']) > 5]


_TEST_SINGLE_FILTERS = {'mod3filter': Mod3Filter}
_TEST_AGGREGATION_FILTERS = {'biggerthan5agg': BiggerThan5Agg}
