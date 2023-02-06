#!/usr/bin/env python

import os
import shutil
import logging
from robot.kwyt.library.local_kwyt import LocalKwyt
from robot.library.yuppie.modules.environment import Environment
from robot.library.yuppie.modules.sys_mod import Sys
from robot.library.yuppie.core.errors import Error
from robot.jupiter.library.python.jupiter_util.env import make_dir
import yatest.common


TEST_TIMESTAMP = '1539098100'


def test_entry(links):
    env = Environment(mr_prefix='//home', diff_test=False)
    difftools_dir = make_dir(yatest.common.output_path("diff_tools"))
    diff_tool_bin = yatest.common.binary_path("robot/kwyt/tools/diff/dump_diff/dump_diff")
    shutil.copyfile(diff_tool_bin, os.path.join(difftools_dir, "dump_diff"))

    try:
        kwyt = LocalKwyt(
            arcadia=env.arcadia,
            bin_dir=env.binary_path,  # clustermaster
            kwyt_binaries_dir=yatest.common.binary_path('robot/kwyt/packages/binaries'),
            configs_dir=yatest.common.binary_path('robot/kwyt/packages/configs'),
            working_dir=env.output_path,
            cluster=env.cluster,
            test_data_prefix=env.mr_prefix,
            test_data=('it_data.tar.gz', ),
            yatest_links=links,
            testing=True,
            attr_value_format="<format=text>yson"
        )

        # Set "time" for the tests
        kwyt.get_cm().set_var('TEST_TIMESTAMP', TEST_TIMESTAMP)

        convert_hosts(kwyt, env)
        convert_sitemaps(kwyt, env)
        convert_pages(kwyt, env)

        merge_sitemaps(kwyt, env)
        # the order of the following tests is important (since pages merge produces hosts acks)
        hosts_ack_revision = merge_pages(kwyt, env)
        check_hosts_ack_table(kwyt, env, 'robots', hosts_ack_revision)
        check_hosts_ack_table(kwyt, env, 'status', hosts_ack_revision)

        merge_hosts(kwyt, env, 'robots')
        merge_hosts(kwyt, env, 'status')

        stats_sitemaps(kwyt, env)
        stats_hosts(kwyt, env, 'robots')
        stats_hosts(kwyt, env, 'status')
        stats_pages(kwyt, env)

    except BaseException as err:
        if env.hang_test:
            logging.info('Got error: %s', err)
            Sys.hang()
        else:
            raise


def stats_pages(kwyt, env):
    kwyt.get_cm().check_call_target('stats-pages-process', timeout=60*5)
    kwyt.dump_table(env.table_dumps_dir, 'kwyt/stats/pages/stats.all')
    kwyt.dump_table(env.table_dumps_dir, 'kwyt/stats/pages/stats.acks.0')


def stats_hosts(kwyt, env, kind):
    kwyt.get_cm().check_call_target('stats-hosts-' + kind + '-process', timeout=60*5)
    kwyt.dump_table(env.table_dumps_dir, 'kwyt/stats/hosts/' + kind + '/stats.last')


def stats_sitemaps(kwyt, env):
    kwyt.get_cm().check_call_target('stats-sitemaps-process', timeout=60*5)
    kwyt.dump_table(env.table_dumps_dir, 'kwyt/stats/sitemaps/stats.last')


def merge_hosts(kwyt, env, kind):
    kwyt.get_cm().check_call_target('merger-hosts-' + kind + '-merge', timeout=60*10)
    kwyt.dump_table(env.table_dumps_dir, 'kwyt/hosts/' + kind)


def check_hosts_ack_table(kwyt, env, kind, revision):
    ack_table = 'kwyt/acks/hosts/' + kind + '/ack.0.' + str(revision)
    ensure_ready_for_merge(kwyt, ack_table)
    kwyt.dump_table(env.table_dumps_dir, ack_table, 'ack.0.0')


def merge_pages(kwyt, env):
    hosts_ack_revision = kwyt.get_revision('kwyt/pages/000/data')
    kwyt.get_cm().check_call_target('merger-pages-merge', timeout=60*20)
    kwyt.dump_table(env.table_dumps_dir, 'kwyt/pages/000/data')
    kwyt.dump_table(env.table_dumps_dir, 'kwyt/pages/000/attributes')
    for table in kwyt.yt.list(os.path.join(env.mr_prefix, 'kwyt/acks/pages/000')):
        if 'delayed' in table:
            kwyt.dump_table(env.table_dumps_dir, 'kwyt/acks/pages/000/' + table, '.'.join(table.split('.')[:-1]) + '.0')
    return hosts_ack_revision


def merge_sitemaps(kwyt, env):
    kwyt.get_cm().check_call_target('merger-sitemaps-merge', timeout=60*10)
    kwyt.dump_table(env.table_dumps_dir, 'kwyt/sitemaps/data')


def convert_pages(kwyt, env):
    delta_revision = kwyt.get_oldest_table_revision('kwyt-import/lb/zora/pages')
    kwyt.get_cm().check_call_target('delta-pages-convert', timeout=60*10)

    delta_table = 'kwyt/pages/000/delta.' + str(delta_revision)
    ensure_ready_for_merge(kwyt, delta_table)

    # sort the delta tables to overcome possible order differences on different orders of input tables
    kwyt.sort_table(
        delta_table,
        'Host',
        'Path',
        'LastAccess',
        'TextCRC',
        'Size',
        'HttpCode',
        'ZoraCtx')

    # dump delta table
    kwyt.dump_table(env.table_dumps_dir, delta_table, 'delta.0')

    # remove the produced delta tables to remove an influence on the following hosts merge test
    kwyt.remove_table(delta_table)


def convert_sitemaps(kwyt, env):
    delta_revision = kwyt.get_oldest_table_revision('kwyt-import/lb/zora/sitemaps')
    kwyt.get_cm().check_call_target('delta-sitemaps-convert', timeout=60*10)

    delta_table = 'kwyt/sitemaps/delta.' + str(delta_revision)
    ensure_ready_for_merge(kwyt, delta_table)

    # sort the delta tables to overcome possible order differences on different orders of input tables
    kwyt.sort_table(
        delta_table,
        'Host',
        'Path',
        'LastAccess',
        'TextCRC',
        'SourceName',
        'MimeType',
        'Size',
        'HttpModTime',
        'HttpCode')

    # dump delta table
    kwyt.dump_table(env.table_dumps_dir, delta_table, 'delta.0')

    # remove the produced delta tables to remove an influence on the following hosts merge test
    kwyt.remove_table(delta_table)


def convert_hosts(kwyt, env):
    hosts_delta_revision = kwyt.get_oldest_table_revision('kwyt-import/lb/zora/hosts')
    kwyt.get_cm().check_call_target('delta-hosts-convert', timeout=60*10)

    delta_revision = str(hosts_delta_revision)
    robots_delta_table = 'kwyt/hosts/delta.robots.' + delta_revision
    ensure_ready_for_merge(kwyt, robots_delta_table)

    status_delta_table = 'kwyt/hosts/delta.status.' + delta_revision
    ensure_ready_for_merge(kwyt, status_delta_table)

    # sort the delta tables to overcome possible order differences on different orders of input tables
    sort_hosts(kwyt, robots_delta_table)
    sort_hosts(kwyt, status_delta_table)

    # dump delta tables
    kwyt.dump_table(env.table_dumps_dir, robots_delta_table, 'delta.robots.0')
    kwyt.dump_table(env.table_dumps_dir, status_delta_table, 'delta.status.0')

    # remove the produced delta tables to remove an influence on the following hosts merge test
    kwyt.remove_table(robots_delta_table)
    kwyt.remove_table(status_delta_table)


def ensure_ready_for_merge(kwyt, table):
    if not kwyt.is_ready_for_merge(table):
        raise Error('The ' + table + ' table does not have the ready-for-merge attribute')


def sort_hosts(kwyt, table):
    kwyt.sort_table(
        table,
        'Host',
        'LastAccess',
        'IP',
        'IPv6',
        'HostStatus',
        'RobotsHTTPCode',
        'RobotsLastAccess')
