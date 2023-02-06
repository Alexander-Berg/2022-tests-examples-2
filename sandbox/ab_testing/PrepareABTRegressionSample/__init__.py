# -*- coding: utf-8 -*-
import logging
import json
import re

import posixpath

from datetime import datetime, timedelta

from sandbox.projects.common import utils
from sandbox.projects.ab_testing import PREPARE_ABT_REGRESSION_SAMPLE_REPORT

from sandbox.sandboxsdk.svn import Arcadia
from sandbox.sandboxsdk import environments
from sandbox.sandboxsdk.task import SandboxTask
from sandbox.sandboxsdk.parameters import SandboxStringParameter, SandboxBoolParameter
from sandbox.sandboxsdk.errors import SandboxTaskFailureError


FILTER_SCRIPT_NAME = './regrabt-filter.py'

FILTER_SCRIPT_CONTENT = """
import sys
import zlib

def main():
    cutoff = int(sys.argv[1])
    prev = None
    for l in sys.stdin:
        key = l.split('\t', 1)[0]
        if key != prev:
           fetch = abs(zlib.crc32(key)) < cutoff
        prev = key

        if fetch:
            sys.stdout.write(l)

main()
"""

def retry(retries=3, exception=Exception):
    def wrapper(func):
        def wrapped(*args, **kwargs):
            for i in range(1, retries + 1):
                try:
                    return func(*args, **kwargs)
                except exception as e:
                    logging.warning("Failed {}/{}. Exception {}".format(i, retries, e))
                    if i == retries:
                        raise SandboxTaskFailureError("Max retries exceeded")
        return wrapped
    return wrapper


def parse_date(date, now):
    if not date:
        return now
    elif date.startswith('-'):
        return now - timedelta(days=int(date[1:]))
    else:
        return datetime.strptime(date, '%Y%m%d')


def template_path(path, date):
    if isinstance(path, list):
        return posixpath.join([template_path(i, date) for i in path])
    elif isinstance(path, str) or isinstance(path, unicode):
        m = re.match('^<<(.+)>>$', path)
        if m:
            path = m.group(1)
            path = path.replace('%Y%m%d', date.strftime('%Y%m%d'))
            path = path.replace('%Y-%m-%d', date.strftime('%Y-%m-%d'))
        return path
    else:
        raise ValueError('Error argument type "%s" for template_path' % type(path))


@retry()
def make_sample_table(table, output_prefix, cutoff, reduce_fields, sort_fields):
    import yt.wrapper as yt
    output_table = posixpath.join(output_prefix.rstrip('/'), table.strip('/'))
    logging.info('Run sample reduce from "%s" to "%s"', table, output_table)
    mkpath = '//' + posixpath.join(*(output_table.strip('/').split('/')[:-1]))
    logging.info('Create path: %s', mkpath)
    yt.mkdir(mkpath, recursive=True)

    #yt.set_attribute(output_table, 'compression_codec', 'brotli_3')
    yt.run_reduce('python %s %d' % (FILTER_SCRIPT_NAME, cutoff), table, output_table, sort_by=sort_fields, reduce_by=reduce_fields, format='dsv', local_files=[FILTER_SCRIPT_NAME])
    yt.run_sort(output_table, sort_by=['key', 'subkey'])
    if not yt.exists(output_table):  # Once it happens
        raise RuntimeError("Table %s wasn't created" % output_table)
    return output_table


class PrepareABTRegressionSample(SandboxTask):
    type = 'PREPARE_ABT_REGRESSION_SAMPLE'

    environment = (environments.PipEnvironment('yandex-yt'), environments.PipEnvironment('yandex-yt-transfer-manager-client'),)

    class MRCluster(SandboxStringParameter):
        name = 'mr_cluster'
        description = 'MR cluster'
        default_value = 'hahn'

    class CopyCluster(SandboxStringParameter):
        name = 'copy_cluster'
        description = 'Copy cluster'
        default_value = 'freud'

    class OutputTemplate(SandboxStringParameter):
        name = 'output_template'
        description = 'Parent directory for output sample tables. Added: {YYYYMMDD}_{cutoff}/'
        default_value = ''

    class OutputPrefix(SandboxStringParameter):
        name = 'output_prefix'
        description = 'Full prefix for output sampled tables'
        default_value = ''

    class Date(SandboxStringParameter):
        name = 'date'
        description = 'DATE for calculations. Can be YYYYMMDD or empty for current day or "-%d" for current day minus %d days'
        default_value = ''

    class Cutoff(SandboxStringParameter):
        name = 'cutoff'
        description = 'Hash cutoff'
        default_value = '21474836'

    class UpdateMissing(SandboxBoolParameter):
        name = 'update_missing'
        description = 'Update missing'
        default_value = False

    class SkipEmptyTables(SandboxBoolParameter):
        name = 'skip_empty_tables'
        description = 'Skip empty tables'
        default_value = False

    input_parameters = [MRCluster, CopyCluster, Date, Cutoff, OutputTemplate, OutputPrefix, UpdateMissing, SkipEmptyTables]

    def __init__(self, *args, **kwargs):
        SandboxTask.__init__(self, *args, **kwargs)

    def on_execute(self):
        from yt.transfer_manager.client import TransferManager
        import yt.wrapper as yt

        logging.info('Test yt %s', yt)

        mr_cluster = utils.get_or_default(self.ctx, self.MRCluster)
        copy_cluster = utils.get_or_default(self.ctx, self.CopyCluster)
        logging.info('Cluster: %s', mr_cluster)

        cutoff = int(utils.get_or_default(self.ctx, self.Cutoff))
        output_template = utils.get_or_default(self.ctx, self.OutputTemplate)
        output_prefix = utils.get_or_default(self.ctx, self.OutputPrefix)

        if int(bool(output_template)) + int(bool(output_prefix)) != 1:
            raise RuntimeError('Only one of OutputTemplate and OutputPrefix have to be set!')

        date = parse_date(utils.get_or_default(self.ctx, self.Date), datetime.now())

        self.set_info('Prepare abt sample %s' % date.strftime("%Y-%m-%d"))

        if output_template:
            output_prefix = posixpath.join(output_template, '%s_%d' % (date.strftime('%Y%m%d'), cutoff))

        logging.info('Output prefix is: %s', output_prefix)

        oauth_token = self.get_vault_data('AB-TESTING', 'yt-token')

        tm = TransferManager(token=oauth_token)

        yt.update_config({
            'token': oauth_token,
            'proxy': {'url': mr_cluster},
        })

        with open(FILTER_SCRIPT_NAME, 'w') as f:
            f.write(FILTER_SCRIPT_CONTENT)

        paths_to_tables_lib = Arcadia.get_arcadia_src_dir('arcadia:/arc/trunk/arcadia/quality/ab_testing/paths_to_tables_lib')
        logging.info('Loading paths.json')
        paths = json.load(open(posixpath.join(paths_to_tables_lib, 'paths.json')))

        paths_to_stat_collector_prepare_lib = Arcadia.get_arcadia_src_dir('arcadia:/arc/trunk/arcadia/quality/ab_testing/stat_collector_sources_lib')
        logging.info('Loading sources.json')
        sources = json.load(open(posixpath.join(paths_to_stat_collector_prepare_lib, 'sources.json')))

        sample_tables = []

        update_missing = utils.get_or_default(self.ctx, self.UpdateMissing)

        skip_empty_tables = utils.get_or_default(self.ctx, self.SkipEmptyTables)

        output_tables = []

        source_names = ["daily", "user_sessions_stats"]
        while len(source_names):
            source_name = source_names.pop()
            source = sources.get(source_name, {})

            source_names.extend(source.get("include", []))

            for table in source.get("tables", []):
                table_date = date + timedelta(days=table.get("shift", 0))
                if "begin" in table and datetime.strptime(table["begin"], "%Y%m%d") > table_date:
                    continue
                if "end" in table and datetime.strptime(table["end"], "%Y%m%d") < table_date:
                    continue

                yt_path = '//' + posixpath.join(*template_path(paths[table["name"]]["yt"]["path"], table_date))
                logging.info('Try item: %s %s', table["name"], yt_path)

                if not yt.exists(yt_path):
                    if skip_empty_tables:
                        logging.info("Table %s doesn't exist", yt_path)
                        continue
                    else:
                        logging.error("Table %s doesn't exist", yt_path)
                        raise SandboxTaskFailureError("Table %s doesn't exist" % yt_path)

                if not yt.is_sorted(yt_path):
                    if skip_empty_tables:
                        logging.info("Table %s not sorted", yt_path)
                        continue
                    else:
                        logging.error("Table %s not sorted", yt_path)
                        raise SandboxTaskFailureError("Table %s doesn't exist" % yt_path)

                output_table = '//' + posixpath.join(output_prefix.strip('/'), yt_path.strip('/'))
                logging.info('Check table path: %s', output_table)
                output_tables.append(output_table)
                if yt.exists(output_table):
                    logging.info("Output table %s exists", output_table)
                    if update_missing:
                        continue
                    else:
                        logging.info("Force resample output table %s", output_table)
                else:
                    logging.info("Output table %s doesn't exists", output_table)

                logging.info('Add %s for samples', yt_path)
                sample_tables.append({
                    "path": yt_path,
                    "sort_by": table.get("sort_by", "key"),
                    "reduce_by": table.get("reduce_by", "key"),
                })

        for table in sample_tables:
            output_table = make_sample_table(table["path"], output_prefix, cutoff, table["reduce_by"], table["sort_by"])

        release_cluster = mr_cluster
        if copy_cluster:
            release_cluster = copy_cluster
            for table in output_tables:
                logging.info('Copy table: %s (%s->%s)', table, mr_cluster, copy_cluster)
                tm.add_task(mr_cluster, table, release_cluster, table, sync=True)

        report_filename = 'report.txt'
        with open(report_filename, 'wt') as f:
            print >>f, '%s:%s' % (release_cluster, output_prefix)

        self.create_resource(
            'prepare-abt-regression-sample-report',
            report_filename,
            resource_type=PREPARE_ABT_REGRESSION_SAMPLE_REPORT,
            attributes={'ttl': 300}
        )


__Task__ = PrepareABTRegressionSample
