import json
import logging
import base64
from library.python import resource
from sandbox.projects.yabs.partner_share.lib.fast_changes import fast_changes


logging.basicConfig(level=logging.DEBUG)


def test_update_conditions():
    resource_content = resource.find('sandbox/projects/yabs/partner_share/lib/fast_changes/local_test/filter.json')
    resource_json = json.loads(resource_content)
    filters = resource_json['filters']
    fast_changes.update_conditions(filters)

    for filter in filters:
        for condition in filter.get('conditions', []):
            if condition['field'] == 'Login':
                assert condition['value'] == "'aark','okwedook'"  # Check that spaces are deleted


def test_generate_changes_chyt_query():
    resource_content = resource.find('sandbox/projects/yabs/partner_share/lib/fast_changes/local_test/filter.json')
    resource_json = json.loads(resource_content)
    filters = resource_json['filters']
    fast_changes.update_conditions(filters)

    result_dir = '//home/yabs/tac-manager/request/TESTTACCHANGES-21/filter'
    query = fast_changes.generate_changes_chyt_query('chyt.hahn/lelby_ckique', filters, result_dir, 1000000)
    base64_query = base64.b64encode(query.encode())

    return base64_query


def test_generate_changes_imps_chyt_query():
    resource_content = resource.find('sandbox/projects/yabs/partner_share/lib/fast_changes/local_test/filter.json')
    resource_json = json.loads(resource_content)
    filters = resource_json['filters']
    fast_changes.update_conditions(filters)

    result_dir = '//home/yabs/tac-manager/request/test6/filter'
    query = fast_changes.generate_changes_imps_chyt_query(
        chyt_cluster='chyt.hahn/lelby_ckique',
        filters=filters,
        result_dir=result_dir,
        ignore_partner_share_above=1000000,
        turnover_table_path='//home/yabs/tac-manager/turnover/last',
    )
    return query
