# -*- coding: utf-8 -*-
import os
import logging
import sys
import time
import posixpath

from datetime import datetime

from sandbox import common

from sandbox.sandboxsdk import environments
from sandbox.sandboxsdk.channel import channel
from sandbox.sandboxsdk.task import SandboxTask
from sandbox.sandboxsdk.parameters import SandboxStringParameter, SandboxBoolParameter

from sandbox.projects.common import utils
from sandbox.projects.common.apihelpers import get_last_resource_with_attrs
from sandbox.projects.common.arcadia import sdk as arcadia_sdk
from sandbox.projects.ab_testing import RUN_ABT_METRICS_REPORT


def try_parse_date(path):
    if len(path) == 8:  # YYYYMMDD
        return path
    elif len(path) == 10:  # YYYY-MM-DD
        try:
            return datetime.strptime(path, '%Y-%m-%d').strftime('%Y%m%d')
        except:
            return path  # Seems it's timestamp. Leave it as string
    else:
        return None


class RunABTMetrics(SandboxTask):
    type = 'RUN_ABT_METRICS'

    cores = 1
    required_ram = 16 * 1024
    execution_space = 20 * 1024

    environment = (
        environments.PipEnvironment('yandex-yt'),
    )

    class Cluster(SandboxStringParameter):
        name = 'cluster'
        description = 'YT cluster'
        default_value = 'hahn'

    class Resources(SandboxStringParameter):
        '''
        Optional field. Can add resource files for stat_collector/stat_fetcher.
        Need files: blockstat.dict, browser.xml, geodata5.bin.
        '''
        name = 'resources_id'
        description = 'Resource files for stat_collector and stat_fetcher'
        default_value = ''

    class Package(SandboxStringParameter):
        '''
        YA_PACKAGE yandex-search-ab-testing
        '''
        name = 'package_id'
        description = 'Keyword "stable" to auto-use prod or yandex-search-ab-testing with stat_{collector, fetcher}'
        default_value = ''

    class PackageTask(SandboxStringParameter):
        '''
        YA_PACKAGE task that has output with resource_name yandex-search-ab-testing
        '''
        name = 'package_task_id'
        description = 'Build task for yandex-search-ab-testing with stat_{collector, fetcher}'
        default_value = ''

    class SamplePath(SandboxStringParameter):
        '''
        Sample path or date (YYYYMMDD/YYYY-MM-DD)
        '''
        name = 'sample_path'
        description = 'Sample path or date (YYYYMMDD/YYYY-MM-DD) or timestamp'
        default_value = ''

    class SampleReport(SandboxStringParameter):
        '''
        Global resource id
        '''
        name = 'sample_report'
        description = 'Alternative input for sample_path'
        default_value = ''

    class VaultGroup(SandboxStringParameter):
        '''
        Vault group of yt token.
        '''
        name = 'vault_group'
        description = 'Vault group'
        default_value = 'AB-TESTING'

    class VaultName(SandboxStringParameter):
        '''
        Vault name of yt token.
        '''
        name = 'vault_name'
        description = 'Vault name'
        default_value = 'yt-token'

    class YtPool(SandboxStringParameter):
        '''
        Vault name of yt token.
        '''
        name = 'yt_pool'
        description = 'YT pool for calculation'
        default_value = ''

    class OutputPrefix(SandboxStringParameter):
        '''
        Vault name of yt token.
        '''
        name = 'output_prefix'
        description = 'YT prefix for output result'
        default_value = '//home/abt/regrabt/out/'

    class CalculateFeatures(SandboxBoolParameter):
        '''
        Features will be read from yt and written to the result.
        '''
        name = 'calculate_features'
        description = 'Features will be read from yt and written to the result'
        default_value = False

    input_parameters = [Cluster, Resources, Package, PackageTask, SamplePath, SampleReport, VaultGroup, VaultName, YtPool, OutputPrefix, CalculateFeatures]

    def __init__(self, *args, **kwargs):
        SandboxTask.__init__(self, *args, **kwargs)

    def _get_latest_stable_abt_package_id(self):
        last_resource = get_last_resource_with_attrs(
            "AB_TESTING_YA_PACKAGE",
            {
                "released": "stable",
                "resource_name": "yandex-search-ab-testing",
            },
            all_attrs=True,
        )

        return last_resource.id if last_resource is not None else None

    def get_shell_abt(self):
        if common.system.inside_the_binary():
            return common.context.NullContextmanager(enter_obj="")
        else:
            return arcadia_sdk.mount_arc_path(
                "arcadia:/arc/trunk/arcadia/quality/ab_testing/scripts/shellabt/", use_arc_instead_of_aapi=True
            )

    def on_execute(self):
        if not self.ctx['sample_path']:
            if not self.ctx["sample_report"]:
                raise ValueError('Sample path not set')

        if not self.ctx['package_id'] and not self.ctx['package_task_id']:
            raise ValueError('Sample path not set')
        with self.get_shell_abt() as shellabt_path:
            if shellabt_path:
                sys.path.append(shellabt_path)

                import shellabt
            else:
                import quality.ab_testing.scripts.shellabt as shellabt

            # TODO: Use config
            collector_config_path = 'sc_conf.txt'
            with open(collector_config_path, 'wt') as f:
                f.write('[task]\nname=\nexperiment=0')

            sample_path = utils.get_or_default(self.ctx, self.SamplePath) or shellabt.read_released_sample_path(self.ctx["sample_report"])

            package_id = utils.get_or_default(self.ctx, self.Package)
            if package_id == "stable":
                logging.info('Stable released package_id was requested')

                package_id = self._get_latest_stable_abt_package_id()
                logging.info('Found stable package_id %s', package_id)

                if package_id is None:
                    raise ValueError("Failed to retrieve stable package_id")
            elif not package_id:
                package_task_id = utils.get_or_default(self.ctx, self.PackageTask)

                logging.info('No package resource id, will try to extract from task: %s', package_task_id)

                package_resource = channel.sandbox.list_resources(
                    task_id=package_task_id,
                    attribute_name="resource_name",
                    attribute_value="yandex-search-ab-testing"
                )[0]

                package_id = package_resource.id

                logging.info('Extracted yandex-search-ab-testing package id from task: %s', package_id)

            logging.info('Syncing resource: %d', package_id)
            package_path = self.sync_resource(package_id)

            conf = shellabt.FreeConfig()
            conf['server'] = utils.get_or_default(self.ctx, self.Cluster)

            date = try_parse_date(sample_path)
            if date is None:
                conf['date'] = shellabt.parse_sample_date(sample_path)
                conf['yt_prefix'] = sample_path
            else:
                conf['date'] = date

            resources_id = utils.get_or_default(self.ctx, self.Resources)

            if resources_id:
                resources = self.sync_resource(resources_id)

                conf['geodata'] = os.path.join(resources, 'geodata5.bin')
                conf['blockstat.dict'] = os.path.join(resources, 'blockstat.dict')
                conf['browser.xml'] = os.path.join(resources, 'browser.xml')

            extract_to = './'
            logging.info('Extracting: %s to %s', package_path, extract_to)
            paths = shellabt.DebianYaPackagePaths(package_path, '/Berkanavt/ab_testing/bin', extract_to)
            conf.merge(paths)

            conf['yt_token'] = self.get_vault_data(utils.get_or_default(self.ctx, self.VaultGroup), utils.get_or_default(self.ctx, self.VaultName))

            yt_pool = utils.get_or_default(self.ctx, self.YtPool)
            if yt_pool:
                conf['yt_pool'] = yt_pool

            conf['output_prefix'] = utils.get_or_default(self.ctx, self.OutputPrefix)
            conf['yt_tmp'] = posixpath.join(conf['output_prefix'], 'tmp')
            conf['collector_out_table'] = '%srun_abt_metrics_%s_%s_%d' % (conf['output_prefix'], conf['date'], package_id, int(time.time()))

            stat = shellabt.StatRunner(conf)

            features_id = ""
            metrics_id = ""
            try:
                features_id = stat.get_features_stat_collector(config_path=collector_config_path).get('changes_info', {}).get('id_resource_sandbox', "")
            except Exception as e:
                logging.info('Exception in get_features_stat_collector: {}'.format(e))

            try:
                metrics_id = stat.get_metrics_stat_fetcher().get('changes_info', {}).get('id_resource_sandbox', "")
            except Exception as e:
                logging.info('Exception in get_metrics_stat_fetcher {}'.format(e))

            logging.info('Obtained id of resource of metrics({}) and features_custom({})'.format(metrics_id, features_id))

            stat.run_stat_collector(
                config_path=collector_config_path,
                target_date=conf['date'],
                result_table=conf['collector_out_table']
            )

            logging.info('Set expiration for %s', conf['collector_out_table'])
            from yt.wrapper import YtClient
            client = YtClient(proxy=conf['server'], token=conf['yt_token'])
            client.set_attribute(conf['collector_out_table'], 'expiration_time', int(time.time() + 36 * 60 * 60) * 1000)

            conf['fetcher_out_path'] = 'result.txt'

            stat.run_stat_fetcher(
                config_path=collector_config_path,
                target_date=conf['date'],
                collector_table=conf['collector_out_table'],
                result_path=conf['fetcher_out_path']
            )

            metrics_info = shellabt.load_only_metrics(conf['stat_fetcher'])
            result = shellabt.StatResult.from_file(conf['fetcher_out_path'], metrics_info)

            suite = shellabt.SuiteResult.from_sample_path(sample_path)

            calculate_features = utils.get_or_default(self.ctx, self.CalculateFeatures)
            if calculate_features:
                if len(conf['date']) == 8:
                    features_path = conf['collector_out_table'] + '/daily/{}/preliminary/main/features/0'.format(conf['date'])
                else:
                    features_path = conf['collector_out_table'] + '/fast/{}/main/main/features/0'.format(conf['date'])

                yt_table = client.TablePath(features_path, exact_key='\t0')
                count_rows_table = client.row_count(yt_table)
                MAX_FEATURE_ROWS = 40000000
                if count_rows_table > MAX_FEATURE_ROWS:
                    last_read_row = list(client.read_table(client.TablePath(features_path, exact_index=MAX_FEATURE_ROWS), raw=False, format='json'))[0]
                    is_last_flow_key = last_read_row['key'] == '\t0'
                    if is_last_flow_key:
                        raise RuntimeError('Features table too big.')

                logging.info('Start to read result of stat_collector. Yt table by path {}'.format(features_path))
                collector_result = shellabt.CollectorResult(list(client.read_table(yt_table, raw=False, format='json')))
                suite.collector_add(collector_result)

            suite.add(result)

            dirname = 'result_tables'
            dirname = os.path.abspath(dirname)
            if not os.path.exists(dirname):
                os.makedirs(dirname)

            filename_fetcher = 'metrics.json'
            fetcher_file = os.path.join(dirname, filename_fetcher)
            suite.to_file(fetcher_file)

            if calculate_features:
                filename_collector = 'feature.json'
                collector_file = os.path.join(dirname, filename_collector)
                suite.collector_to_file(collector_file)
            else:
                filename_collector = None

            name = 'ABT metrics resource %s prefix/date %s' % (package_id, sample_path)
            self.create_resource(
                name, dirname, resource_type=RUN_ABT_METRICS_REPORT,
                attributes={
                    'ttl': 500,
                    'package_id': package_id,
                    'sample_path': sample_path,
                    'metrics_id': metrics_id,
                    'features_id': features_id,
                    'filename_fetcher': filename_fetcher,
                    'filename_collector': filename_collector,
                }
            )


__Task__ = RunABTMetrics
