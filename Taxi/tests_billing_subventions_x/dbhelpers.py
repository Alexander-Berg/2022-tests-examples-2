import pathlib
import re

from tests_billing_subventions_x import types


def get_draft_spec(pgsql, internal_draft_id):
    sql = load_sql('draft_get_spec.sql')
    cursor = pgsql['billing_subventions'].cursor()
    cursor.execute(sql, (internal_draft_id,))
    rows = cursor.fetchall()
    if not rows:
        return None
    description = [column.name for column in cursor.description]
    return dict(zip(description, rows[0]))


def select_subdrafts(pgsql, internal_draft_id):
    sql = """
        SELECT * from subventions.bulk_subdraft_spec
        WHERE internal_draft_id = %s
        ORDER BY spec_ref;
    """
    cursor = pgsql['billing_subventions'].cursor()
    cursor.execute(sql, (internal_draft_id,))
    subdrafts = cursor.fetchall()
    fields = [column.name for column in cursor.description]
    return [dict(zip(fields, d)) for d in subdrafts]


def select_rule_drafts(pgsql, internal_draft_id):
    sql = """
        set timezone='UTC';
        SELECT * FROM subventions.draft_rules_to_add
        where internal_draft_id = %s;
    """
    cursor = pgsql['billing_subventions'].cursor()
    cursor.execute(sql, (internal_draft_id,))
    rows = cursor.fetchall()
    description = [column.name for column in cursor.description]
    return [types.RuleDraft(**dict(zip(description, row))) for row in rows]


def select_rules_to_close(pgsql, internal_draft_id):
    sql = """
        SELECT rule_id, new_ends_at FROM subventions.draft_rules_to_close
        WHERE internal_draft_id = %s;
    """
    cursor = pgsql['billing_subventions'].cursor()
    cursor.execute(sql, (internal_draft_id,))
    rows = cursor.fetchall()
    fields = [column.name for column in cursor.description]
    return [dict(zip(fields, row)) for row in rows]


def select_draft_schedule_specs(pgsql, internal_draft_id):
    sql = """
        SELECT schedule_ref, during, value
        FROM subventions.draft_schedule_spec
        WHERE internal_draft_id = %s;
    """
    cursor = pgsql['billing_subventions'].cursor()
    cursor.execute(sql, (internal_draft_id,))
    rows = cursor.fetchall()
    fields = [column.name for column in cursor.description]
    return [dict(zip(fields, row)) for row in rows]


def get_rule_by_id(pgsql, rule_id):
    sql = load_sql('select_rules_by_ids.sql')
    cursor = pgsql['billing_subventions'].cursor()
    cursor.execute(sql, ([rule_id],))
    fields = [column.name for column in cursor.description]
    return dict(zip(fields, cursor.fetchone() or []))


def get_rules_by_draft_id(pgsql, draft_id):
    sql = load_sql('added_by_draft.sql')
    cursor = pgsql['billing_subventions'].cursor()
    cursor.execute(sql, (draft_id,))
    fields = [column.name for column in cursor.description]
    return [dict(zip(fields, row)) for row in cursor.fetchall()]


def get_schedule_by_id(pgsql, rule_id):
    sql = """
        SELECT during, amount as value
        FROM subventions.schedule
        WHERE rule_id = %s
        ORDER BY during;
    """
    cursor = pgsql['billing_subventions'].cursor()
    cursor.execute(sql, (rule_id,))
    fields = [column.name for column in cursor.description]
    return [
        types.ScheduleRange(**dict(zip(fields, row)))
        for row in cursor.fetchall()
    ]


def get_budget_by_id(pgsql, budget_id):
    cursor = pgsql['billing_subventions'].cursor()
    sql = """
        SELECT * FROM subventions.budget
        WHERE budget_id = %s"""
    cursor.execute(sql, (budget_id,))
    fields = [column.name for column in cursor.description]
    rows = cursor.fetchall()
    assert len(rows) == 1
    return dict(zip(fields, rows[0]))


def load_sql(fname):
    name = pathlib.Path(__file__).parent.absolute() / f'../../src/sql/{fname}'
    with open(name) as script:
        sql = re.sub(r'/\*.*\*/', '', script.read(), flags=re.DOTALL)
        sql = re.sub(r'--.*', '', sql)
        sql = re.sub(r'\$\d+', '%s', sql)
    return sql.strip()
