from sandbox.projects.yabs.auto_supbs_2.lib.audit_processor_lib.queries import (

    audit_budget_versioned_processor_query1,
    audit_cpc_versioned_processor_query1,
    audit_cpm_versioned_processor_query1,
    audit_any_budget_processor_query1,
    audit_any_budget_processor_query2,
    audit_cpc_processor_query1,
    audit_cpc_processor_query2,
    audit_cpm_processor_query1,
    audit_fix_cpm_processor_query1
)


def test_audit_budget_versioned_processor_query1():
    return audit_budget_versioned_processor_query1.format(available_spent_rate='1', timestamp='01012022')


def test_audit_cpc_versioned_processor_query1():
    return audit_cpc_versioned_processor_query1.format(timestamp='01012022')


def test_audit_cpm_versioned_processor_query1():
    return audit_cpm_versioned_processor_query1.format(timestamp='01012022')


def test_audit_any_budget_processor_query1():
    return audit_any_budget_processor_query1.format(timestamp='01012022')


def test_audit_any_budget_processor_query2():
    return audit_any_budget_processor_query2.format(timestamp='01012022')


def test_audit_cpc_processor_query1():
    return audit_cpc_processor_query1.format(timestamp='01012022')


def test_audit_cpc_processor_query2():
    return audit_cpc_processor_query2.format(timestamp='01012022')


def test_audit_cpm_processor_query1():
    return audit_cpm_processor_query1.format(timestamp='01012022')


def test_audit_fix_cpm_processor_query1():
    return audit_fix_cpm_processor_query1.format(timestamp='01012022')
