# -*- coding: utf-8 -*-

import json
import os
import os.path
import logging

from sandbox.projects import resource_types
from sandbox.projects.common import apihelpers

from sandbox.sandboxsdk.task import SandboxTask
from sandbox.sandboxsdk import process
import sandbox.sandboxsdk.paths as sdk_paths

import task_params as tp


class TestCvdupOnSynthetic(SandboxTask):
    type = "TEST_CVDUP_ON_SYNTHETIC"

    input_parameters = [tp.ImageReduceRes, tp.TestToolRes, tp.ImageParserRes, tp.ImageParserConfig, tp.TransformSpec, tp.GroupSizeSpec, tp.ImageSetRes, tp.MapreduceCluster, tp.MapreducePath, tp.YtToken]

    def __init__(self, *args, **kwargs):
        SandboxTask.__init__(self, *args, **kwargs)

        logging.info('construction complete')

    def generate_self_commands(self, state):
        commands = [
            '{testtool} generate -m {mr_cluster} -s source_image_set -t . -o {mr_path}/testkey_{x} -p image_set_{x}/ -g {group_size} -x "{transform}"'.format(
                testtool=self.testtool_binary,
                mr_cluster=self.ctx['mr_cluster'],
                mr_path=self.ctx['mr_path'],
                transform=self.ctx['transform_spec'],
                group_size=self.ctx['group_size_spec'],
                x=state
            ),
            '{imparser} -c {imparser_config} -d image_set_{x} -o thdb_{x} -n 8 > parse_{x}.log'.format(
                imparser=self.imparser_binary,
                imparser_config=self.imparser_config,
                x=state
            ),
            '{imagereduce} loadthdb --srv {mr_cluster} --local-thdb thdb_{x} --dest-table {mr_path}/set_{x}.main'.format(
                imagereduce=self.imagereduce_binary,
                mr_cluster=self.ctx['mr_cluster'],
                mr_path=self.ctx['mr_path'],
                x=state
            ),
            '{imagereduce} dispatch-input --srv {mr_cluster} --src-table {mr_path}/set_{x}.main --chunks-db {mr_path}/chunksdb --updmain-path {mr_path}/{x}/updmain --statistics-prefix {mr_path}/{x}/statistics'.format(
                imagereduce=self.imagereduce_binary,
                mr_cluster=self.ctx['mr_cluster'],
                mr_path=self.ctx['mr_path'],
                x=state
            ),
            '{imagereduce} simple-self --srv {mr_cluster} --src-table {mr_path}/{x}/updmain --target-state-prefix {mr_path}/{x} --state-id {x}'.format(
                imagereduce=self.imagereduce_binary,
                mr_cluster=self.ctx['mr_cluster'],
                mr_path=self.ctx['mr_path'],
                x=state
            )
        ]
        return commands

    def aggregate_metrics(self, file_names, metric_names):
        accum = {}
        for metric_name in metric_names:
            accum[metric_name] = {'Average': 0.0, 'Values': []}

        for filename in file_names:
            metrics = json.load(open(filename))
            for metric_name in metric_names:
                value = float(metrics[metric_name])
                accum[metric_name]['Average'] += value
                accum[metric_name]['Values'].append(value)

        for metric_name in metric_names:
            if len(accum[metric_name]['Values']) > 0:
                accum[metric_name]['Average'] /= float(len(accum[metric_name]['Values']))

        return accum

    def on_execute(self):
        env = dict(os.environ)

        env['MR_RUNTIME'] = 'YT'
        env['YT_USE_YAMR_STYLE_PREFIX'] = '1'
        env['YT_PREFIX'] = '//home/'
        env['YT_SPEC'] = '{"job_io": {"table_writer": {"max_row_weight": 67108864}}, "map_job_io": {"table_writer": {"max_row_weight": 67108864}}, "reduce_job_io": {"table_writer": {"max_row_weight": 67108864}}, "sort_job_io": {"table_writer": {"max_row_weight": 67108864}}, "partition_job_io": {"table_writer": {"max_row_weight": 67108864}}, "merge_job_io": {"table_writer": {"max_row_weight": 67108864}}}'
        env['YT_TOKEN'] = self.ctx['yt_token'] if self.ctx['yt_token'] else self.get_vault_data('robot-cvdup', 'yt_token')

        logging.info('Get binaries paths')
        self.maprecude_yt_binary = self.sync_resource(apihelpers.get_last_released_resource("MAPREDUCE_YT_EXECUTABLE").id)
        self.imparser_binary = self.sync_resource(self.ctx['imparser_binary'])
        self.imparser_config = self.sync_resource(self.ctx['imparser_config'])
        self.imagereduce_binary = self.sync_resource(self.ctx['imagereduce_binary'])
        self.testtool_binary = self.sync_resource(self.ctx['testtool_binary'])
        self.image_set_archive = self.sync_resource(self.ctx['image_set'])

        logging.info('Generate commands')

        prepare_commands = [
            'mkdir source_image_set image_set_1 image_set_2',
            'tar -xf {}'.format(self.image_set_archive) + ' -C source_image_set',
            'echo | awk {awk_cmd} | {mapreduce_yt} -server {mr_cluster} -subkey -write {mr_path}/chunksdb'.format(
                mapreduce_yt=self.maprecude_yt_binary,
                mr_cluster=self.ctx['mr_cluster'],
                mr_path=self.ctx['mr_path'],
                awk_cmd="'END {print \"\\t\\t\"}'"
            ),
            '{mapreduce_yt} -server {mr_cluster} -sort {mr_path}/chunksdb'.format(
                mapreduce_yt=self.maprecude_yt_binary,
                mr_cluster=self.ctx['mr_cluster'],
                mr_path=self.ctx['mr_path']
            )
        ]

        self_commands1 = self.generate_self_commands('1')
        self_commands2 = self.generate_self_commands('2')

        increment_commands = [
            '{imagereduce} convert2state --srv {mr_cluster} --target-state-prefix {mr_path}/1 --state-id 1'.format(
                imagereduce=self.imagereduce_binary,
                mr_cluster=self.ctx['mr_cluster'],
                mr_path=self.ctx['mr_path']
            ),
            '{imagereduce} simple-inc --srv {mr_cluster} --base-state-prefix {mr_path}/1 --target-state-prefix {mr_path}/2 --state-id 2'.format(
                imagereduce=self.imagereduce_binary,
                mr_cluster=self.ctx['mr_cluster'],
                mr_path=self.ctx['mr_path']
            )
        ]

        reducer = "'awk -v FS=\"\\t\" '\"'\"'{subkeys[$1]=$2;values[$1]=$3;count[$1]=count[$1]+1} END { for (k in count) if (count[k]==1) print k \"\\t\" subkeys[k] \"\\t\" values[k]}'\"'\""
        statistics_commands = [
            '{mapreduce_yt} -server {mr_cluster} -src {mr_path}/testkey_2 -src {mr_path}/testkey_1 -src {mr_path}/testkey_1 -dst {mr_path}/testkey_2uniq -subkey -reduce {reducer}'.format(
                mapreduce_yt=self.maprecude_yt_binary,
                mr_cluster=self.ctx['mr_cluster'],
                mr_path=self.ctx['mr_path'],
                reducer=reducer
            ),
            '{mapreduce_yt} -server {mr_cluster} -sort {mr_path}/testkey_2uniq'.format(
                mapreduce_yt=self.maprecude_yt_binary,
                mr_cluster=self.ctx['mr_cluster'],
                mr_path=self.ctx['mr_path']
            ),
            '{mapreduce_yt} -server {mr_cluster} -merge -src {mr_path}/testkey_1 -src {mr_path}/testkey_2uniq -dst {mr_path}/testkey.merged'.format(
                mapreduce_yt=self.maprecude_yt_binary,
                mr_cluster=self.ctx['mr_cluster'],
                mr_path=self.ctx['mr_path']
            ),
            '{testtool} compare -m {mr_cluster} -r {mr_path}/testkey_1 -a {mr_path}/1/groupthumbs/crc2group.text -o metric_1.json'.format(
                testtool=self.testtool_binary,
                mr_cluster=self.ctx['mr_cluster'],
                mr_path=self.ctx['mr_path']
            ),
            '{testtool} compare-geometry -m {mr_cluster} -k {mr_path}/testkey_1 -a {g_path}/crc2group.text -g {g_path}/groups.text -o {g_path}/transform -j geom_errors_1.json'.format(
                testtool=self.testtool_binary,
                mr_cluster=self.ctx['mr_cluster'],
                mr_path=self.ctx['mr_path'],
                g_path=self.ctx['mr_path'] + '/1/groupthumbs'
            ),
            '{testtool} compare -m {mr_cluster} -r {mr_path}/testkey_2uniq -a {mr_path}/2/groupthumbs/crc2group.text -o metric_2.json'.format(
                testtool=self.testtool_binary,
                mr_cluster=self.ctx['mr_cluster'],
                mr_path=self.ctx['mr_path']
            ),
            '{testtool} compare-geometry -m {mr_cluster} -k {mr_path}/testkey_2uniq -a {g_path}/crc2group.text -g {g_path}/groups.text -o {g_path}/transform -j geom_errors_2.json'.format(
                testtool=self.testtool_binary,
                mr_cluster=self.ctx['mr_cluster'],
                mr_path=self.ctx['mr_path'],
                g_path=self.ctx['mr_path'] + '/2/groupthumbs'
            ),
            '{testtool} compare -m {mr_cluster} -r {mr_path}/testkey.merged -a {mr_path}/2/crc2group -o metric_full.json'.format(
                testtool=self.testtool_binary,
                mr_cluster=self.ctx['mr_cluster'],
                mr_path=self.ctx['mr_path']
            )
        ]

        commands = prepare_commands + self_commands1 + self_commands2 + increment_commands + statistics_commands

        stdout_path = os.path.join(sdk_paths.get_logs_folder(), 'stdout.log')
        stderr_path = os.path.join(sdk_paths.get_logs_folder(), 'stderr.log')
        stdout_file = open(stdout_path, 'wa')
        stderr_file = open(stderr_path, 'wa')

        for cmd in commands:
            logging.info("Start command %s", cmd)
            process.run_process(
                [cmd], work_dir="./", timeout=28800, shell=True, check=True, stdout=stdout_file, stderr=stderr_file, environment=env
            )

        logging.info('Prepare report')

        report_file_name = 'report.json'
        metrics = {}
        metrics['self'] = self.aggregate_metrics(['metric_1.json', 'metric_2.json'], ['F', 'H', 'P', 'R'])
        metrics['geometry'] = self.aggregate_metrics(['geom_errors_1.json', 'geom_errors_2.json'], ['Sx', 'Sy', 'Dx', 'Dy'])
        metrics['increment'] = self.aggregate_metrics(['metric_full.json'], ['F', 'H', 'P', 'R'])
        with open(report_file_name, 'w') as f:
            f.write(json.dumps(metrics, indent=4))

        report_resource = self.create_resource(
            description='Results of {} #{}'.format(self.type, self.id),
            resource_path=report_file_name,
            resource_type=resource_types.CVDUP_TEST_RESULT
        )
        self.mark_resource_ready(report_resource.id)


__Task__ = TestCvdupOnSynthetic
