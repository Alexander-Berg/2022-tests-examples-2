# coding: utf-8
from __future__ import unicode_literals

import copy
import decimal
import json
import os

import pytest

from taxi.internal.yt_replication.schema import loaders
import helpers


EXCLUDED_RULES = (
    'pbl',
    'pbl_db',
    'pbl_clid',
    'pbl_scout',
    'payment_header_batch_ids',
    'partner_payments_reports',
    'taximeter_report_payments',
)


def parametrize_real_data_testcase():
    replication_rules = loaders.load_all_rules()
    parameters = []
    for rule_name, rep_rule in sorted(replication_rules.iteritems()):
        if rule_name in EXCLUDED_RULES:
            continue
        for output in rep_rule.outputs:
            for dest_rule in output.destination_rules.itervalues():
                dest_name = dest_rule.destination.name

                parameters.append((dest_name, dest_rule))
    return pytest.mark.parametrize(
        'dest_name,dest_rule', parameters
    )


@pytest.mark.now('2017-12-31T10:00:00')
@parametrize_real_data_testcase()
@pytest.mark.filldb(_fill=False)
@pytest.mark.asyncenv('blocking')
def test_realdata_mapper(load, dest_name, dest_rule, monkeypatch):
    testcase_path = os.path.join('realdata', '%s.json' % dest_name)
    docs = json.loads(load(testcase_path), object_hook=_object_hook)
    for index, doc in enumerate(docs):
        input_data = doc['input']
        input_data_copy = copy.deepcopy(input_data)
        result = list(dest_rule.mapper(input_data))
        if input_data_copy != input_data:
            testcase_description = (
                'Mapper should not modify input doc %s: ' % testcase_path
            )
            helpers.check_difference(
                input_data, input_data_copy, testcase_description
            )
        if result != doc['expected']:
            testcase_description = (
                'Mapper output does not match expected values %s, '
                'document index %d. The exact difference in ' % (
                    testcase_path, index
                )
            )
            helpers.check_difference(
                result, doc['expected'], testcase_description
            )

    _check_testcase_fullness(dest_rule, testcase_path, docs)


def _check_testcase_fullness(dest_rule, testcase_path, docs):
    columns = [column.output_column for column in dest_rule.mapper.columns]
    unmapped_columns = set(columns)
    for index, doc in enumerate(docs):
        for mapped_doc in doc['expected']:
            for field, value in mapped_doc.iteritems():
                if value is not None and field in unmapped_columns:
                    unmapped_columns.remove(field)
    unmapped_columns.discard('_dummy')
    assert not unmapped_columns, (
        '%s: please, add not only "value -> None" mapper '
        'tests for %s output columns' % (testcase_path, unmapped_columns)
    )


def _object_hook(dct):
    if '$decimal' in dct:
        return decimal.Decimal(dct['$decimal'])
    else:
        return helpers.bson_object_hook(dct)
