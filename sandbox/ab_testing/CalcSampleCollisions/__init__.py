# -*- coding: utf-8 -*-
import os
import logging
import sys
import shutil

import sandbox.sandboxsdk.svn as sdk_svn

from sandbox.projects.ab_testing import WEB_FLAGS_COLLISIONS_RESAULT
from sandbox.projects.resource_types import YA_PACKAGE

from sandbox.sdk2.helpers import subprocess as sp
import sandbox.common.types.resource as ctr
import datetime

from sandbox import sdk2


class CalcSampleCollisions(sdk2.Task):

    class Parameters(sdk2.Task.Parameters):
        cluster = sdk2.parameters.String("YT cluster",
                    default_value="hahn",
                    description="YT cluster",
                    required=True)

        bin_calc_sample = sdk2.parameters.LastReleasedResource(
            "resource with calc_sample_collisions",
            resource_type=YA_PACKAGE,
            state=(ctr.State.READY, ctr.State.NOT_READY),
            required=True)

        vault_group = sdk2.parameters.String("Vault group of yt token.",
            default_value="AB-TESTING",
            description="Vault group of yt token.",
            required=True)

        vault_name = sdk2.parameters.String("Vault name of yt token.",
            default_value="yt-token",
            description="Vault name",
            required=True)

        yt_pool = sdk2.parameters.String("YT pool for calculation.",
            default_value="abt-prod-other",
            description="",
            required=False)

        day_or_timestamp = sdk2.parameters.String("day or timestamp",
            default_value="",
            description="20180401 or 1535389200",
            required=True)

        output_dir = sdk2.parameters.String("Output dir.",
            default_value="//home/abt/tmp/serp/collisions",
            description="Output dir",
            required=True)

        kill_timeout = 5 * 3600

    def get_config(self, conf):
        '''./get_flags.py --day 20180810 --flags flags.txt'''

        cmd = [
            conf['get_flags.py'],
            '--flags', conf['flag2testids.cfg'],
            '--day', conf['day']
        ]

        logging.info('get_flags {}'.format(cmd))
        with sdk2.helpers.ProcessLog(self, logger="get_flags") as pl:
            sp.check_call(cmd, stdout=pl.stdout, stderr=sp.STDOUT)

    def run_statistics(self, conf):
        'MR_RUNTIME=YT ./calc_sample_collisions -i user_sessions -s hahn -t 20180501 -p flag2testids.cfg  -o //home/abt/tmp/serp/collisions/20180501'
        cmd = [
            conf['calc_sample_collisions'],
            '-t', conf['day_or_timestamp'],
            '-p', conf['flag2testids.cfg'],
            '-o', conf['output_table']
        ]

        cmd.append('-i')
        if conf['is_day']:
            cmd.append('user_sessions')
        else:
            cmd.append('fast_user_sessions')

        with sdk2.helpers.ProcessLog(self, logger="calc_sample_collisions") as pl:
            sp.check_call(cmd, stdout=pl.stdout, stderr=sp.STDOUT)

    def sample_yql_scripts(self, conf):
        with open(conf['scripts.yql'], 'wt') as yql:
            yql.write("PRAGMA yt.InferSchema;\n".encode('utf-8'))
            yql.write("select flags, count(reqid)\n".encode('utf-8'))
            yql.write("from\n".encode('utf-8'))
            yql.write("hahn.[{}]\n".format(conf['output_table']).encode('utf-8'))
            yql.write("group by flags".encode('utf-8'))

    def on_execute(self):
        shellabt_path = sdk_svn.Arcadia.get_arcadia_src_dir("arcadia:/arc/trunk/arcadia/quality/ab_testing/scripts/shellabt/")
        sys.path.append(shellabt_path)

        import shellabt

        conf = shellabt.FreeConfig()

        conf['output_table'] = os.path.join(str(self.Parameters.output_dir), str(self.Parameters.day_or_timestamp))

        package_id = self.Parameters.bin_calc_sample
        logging.info('Syncing resource: %d', package_id)
        package_path = str(sdk2.ResourceData(package_id).path)

        conf['is_day'] = len(self.Parameters.day_or_timestamp) == 8
        conf['day_or_timestamp'] = str(self.Parameters.day_or_timestamp)
        if conf['is_day']:
            conf['day'] = conf['day_or_timestamp']
        else:
            conf['day'] = datetime.datetime.strftime(datetime.datetime.utcfromtimestamp(int(self.Parameters.day_or_timestamp)), '%Y%m%d')

        os.environ["YT_PROXY"] = self.Parameters.cluster

        conf['flag2testids.cfg'] = 'flag2testids.cfg'
        conf['scripts.yql'] = 'scripts.yql'

        extract_to = './'
        logging.info('Extracting: %s to %s', package_path, extract_to)
        paths = shellabt.DebianYaPackagePaths(package_path, '/Berkanavt/ab_testing/bin', extract_to)
        conf.merge(paths)
        paths = shellabt.DebianYaPackagePaths(package_path, '/Berkanavt/ab_testing/scripts/tools', extract_to)
        conf.merge(paths)

        os.environ['YT_TOKEN'] = sdk2.Vault.data(self.Parameters.vault_group, self.Parameters.vault_name)
        os.environ['MR_RUNTIME'] = 'YT'
        yt_pool = self.Parameters.yt_pool
        if yt_pool:
            os.environ['YT_POOL'] = yt_pool

        self.get_config(conf)
        self.run_statistics(conf)
        self.sample_yql_scripts(conf)

        logging.info('Create resource')
        name = 'calc_sample_collisions'
        flags = os.path.abspath(conf['flag2testids.cfg'])
        yql = os.path.abspath(conf['scripts.yql'])

        resource = WEB_FLAGS_COLLISIONS_RESAULT(self, "WEB_FLAGS_COLLISIONS_RESAULT", name, ttl=7)
        data = sdk2.ResourceData(resource)
        data.path.mkdir(0o755, parents=True, exist_ok=True)
        logging.info('%s and %s to %s' % (flags, yql, str(data.path)))
        shutil.copy2(flags, str(data.path))
        shutil.copy2(yql, str(data.path))
        data.ready()
