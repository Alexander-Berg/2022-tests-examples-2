import json


def _check_single_entry(log_info, pg_entry, expected_pg_entry):
    assert pg_entry['user_id'] == log_info['user_id']
    assert pg_entry['object_id']
    assert pg_entry['object_type'] == 'Entities.Driver.DriverWorkRule'
    assert pg_entry['park_id'] == log_info['park_id']
    assert json.loads(pg_entry['values']) == json.loads(expected_pg_entry)
    assert pg_entry['user_name'] == log_info['user_name']
    assert pg_entry['counts'] == log_info['counts']
    assert pg_entry['ip'] == log_info['ip']


def _get_log_entries(pgsql):
    cursor = pgsql['misc'].conn.cursor()
    cursor.execute('SELECT * FROM changes_0')
    res = []
    for row in cursor.fetchall():
        res.append({})
        for col in range(len(cursor.description)):
            res[len(res) - 1][cursor.description[col][0]] = row[col]
    return res


def check_work_rule_changes(pgsql, log_info, expected_pg_entry):
    entries = _get_log_entries(pgsql)
    assert len(entries) == 1 or not (entries or expected_pg_entry)
    if expected_pg_entry is None:
        return
    pg_entry = entries[0]
    _check_single_entry(log_info, pg_entry, expected_pg_entry)


def check_work_rules_changes(pgsql, log_info, expected_pg_entries):
    entities = _get_log_entries(pgsql)
    assert len(entities) == len(expected_pg_entries)
    for pg_entry in entities:
        rule_id = pg_entry['object_id']
        assert rule_id in expected_pg_entries
        _check_single_entry(log_info, pg_entry, expected_pg_entries[rule_id])
