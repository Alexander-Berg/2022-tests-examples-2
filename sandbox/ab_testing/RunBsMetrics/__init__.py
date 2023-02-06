import datetime
import logging
import os
import sys
import time
from datetime import datetime

import sandbox.sdk2.vcs.svn as sdk_svn
import urllib2
from sandbox import sdk2
from sandbox.common import errors
from sandbox.projects.common import file_utils
from sandbox.sandboxsdk.environments import PipEnvironment

from sandbox.projects.ab_testing.resource_types import RUN_ABT_METRICS_REPORT


# noinspection PyMethodMayBeStatic, DuplicatedCode
class RunBsMetrics(sdk2.Task):
    class Requirements(sdk2.Requirements):
        cores = 1
        ram = 16 * 1024
        disk_space = 20 * 1024
        environments = [PipEnvironment('yandex-yt')]

    class Parameters(sdk2.Parameters):
        kill_timeout = 12 * 60 * 60  # 12 hours is enough
        description = 'RunBsMetrics'
        resources_id = sdk2.parameters.String('Resource files for stat_collector and stat_fetcher')
        package_id = sdk2.parameters.String('Keyword "stable" to auto-use prod package, '
                                            'keyword "last_commit" to auto-use last commit package, '
                                            'keyword "previous_commit" to auto-use before last commit package, '
                                            'or yandex-search-ab-testing-bs resource id',
                                            default='stable')
        package_task_id = sdk2.parameters.String('Build task for yandex-search-ab-testing-bs')
        vault_owner = sdk2.parameters.String('Owner of vault item', default='AB-TESTING')
        vault_name = sdk2.parameters.String('Name of vault item', default='yt-token')
        yt_pool = sdk2.parameters.String('YT pool for calculation', default='abt-prod-other')
        cluster = sdk2.parameters.String('YT cluster', default='hahn')
        output_prefix = sdk2.parameters.String('YT prefix for output result', default='//home/abt/regrabt/bs/out/')
        calculate_features = sdk2.parameters.Bool('Features will be read from yt and written to the result',
                                                  default=False)

    def get_ab_pkg(self):
        ab_testing_pkg = sdk2.Resource.find(
            type="AB_TESTING_YA_PACKAGE",
            attrs={"released": "stable", "resource_name": "yandex-search-ab-testing"}
        ).first()
        if not ab_testing_pkg:
            raise errors.TaskFailure("Could not find AB_TESTING_YA_PACKAGE")
        logging.info("Get last AB_TESTING_YA_PACKAGE: {id: %s, task_id: %s}", ab_testing_pkg.id, ab_testing_pkg.task_id)
        return sdk2.ResourceData(ab_testing_pkg)

    def get_bs_pkg(self, package_id, package_task_id):
        if not package_id.isdigit() and package_task_id.isdigit():
            bs_pkg_resource = sdk2.Resource.find(
                type="BS_COLLECTOR_YA_PACKAGE",
                task_id=package_task_id,
                attrs={"resource_name": "yandex-search-ab-testing-bs"}
            ).first()
        elif package_id.isdigit():
            bs_pkg_resource = sdk2.Resource.find(
                type="BS_COLLECTOR_YA_PACKAGE",
                id=package_id,
                attrs={"resource_name": "yandex-search-ab-testing-bs"}
            ).first()
        elif package_id == "stable":
            bs_pkg_resource = sdk2.Resource.find(
                type="BS_COLLECTOR_YA_PACKAGE",
                attrs={"released": "stable", "resource_name": "yandex-search-ab-testing-bs"}
            ).first()
        elif package_id == "last_commit":
            bs_pkg_resource = sdk2.Resource.find(
                attrs={"branch": "trunk", "build_type": "release", "resource_name": "yandex-search-ab-testing-bs"},
                state="READY",
                owner="AB-TESTING",
                type="BS_COLLECTOR_YA_PACKAGE",
            ).first()
        elif package_id == "previous_commit":
            bs_pkg_resource = sdk2.Resource.find(
                attrs={"branch": "trunk", "build_type": "release", "resource_name": "yandex-search-ab-testing-bs"},
                state="READY",
                owner="AB-TESTING",
                type="BS_COLLECTOR_YA_PACKAGE",
            ).offset(1).first()
        else:
            raise errors.TaskError("Parameters package_id and package_task_id is wrong")
        if not bs_pkg_resource:
            raise errors.TaskFailure("Could not find BS_COLLECTOR_YA_PACKAGE for package_id=%s, package_task_id=%",
                                     package_id, package_task_id)
        logging.info("Get BS_COLLECTOR_YA_PACKAGE: {id: %s, task_id: %s}", bs_pkg_resource.id, bs_pkg_resource.task_id)
        return sdk2.ResourceData(bs_pkg_resource), bs_pkg_resource.id

    def get_bs_features(self):
        features_bs = sdk2.Resource.find(
            type="BS_FEATURES_JSON"
        ).first()
        if not features_bs:
            raise errors.TaskFailure("Could not find features.json")
        logging.info("Get last features_bs.json: {id: %s, task_id: %s, description: '%s'}",
                     features_bs.id, features_bs.task_id, features_bs.description)
        return sdk2.ResourceData(features_bs)

    def get_bs_metrics(self):
        metrics_bs = sdk2.Resource.find(
            type="BS_METRICS_JSON"
        ).first()
        if not metrics_bs:
            raise errors.TaskFailure("Could not find metrics_bs.json")
        logging.info("Get last metrics_bs.json: {id: %s, task_id: %s, description: '%s'}",
                     metrics_bs.id, metrics_bs.task_id, metrics_bs.description)
        return sdk2.ResourceData(metrics_bs)

    def merge_configs(self, donor, recipient):
        for key, value in donor.items.iteritems():
            if key not in recipient.items:
                recipient[key] = value

    def on_execute(self):
        logging.info("RunBsMetrics execution started")
        now = datetime.now()

        logging.info('Get shellabt')
        shellabt_path = sdk_svn.Arcadia.get_arcadia_src_dir(
            "arcadia:/arc/trunk/arcadia/quality/ab_testing/scripts/shellabt/")
        sys.path.append(shellabt_path)
        # noinspection PyUnresolvedReferences
        import shellabt

        logging.info('Get all external resources')
        bs_pkg, package_id = self.get_bs_pkg(str(self.Parameters.package_id), str(self.Parameters.package_task_id))
        ab_pkg = self.get_ab_pkg()
        bs_features = self.get_bs_features()
        bs_metrics = self.get_bs_metrics()

        logging.info('Create config')
        conf = shellabt.FreeConfig()
        conf['yt_token'] = sdk2.Vault.data(self.Parameters.vault_owner, self.Parameters.vault_name)
        output_prefix = str(self.Parameters.output_prefix)
        conf['yt_prefix'] = output_prefix
        conf['yt_pool'] = str(self.Parameters.yt_pool)
        conf['server'] = str(self.Parameters.cluster)
        conf['date'] = "20200101"  # dummy date
        conf['collector_out_table'] = '{}run_bs_metrics_{}_{}'.format(output_prefix, str(package_id),
                                                                      now.strftime("%Y%m%d_%H%M%S_%f"))
        conf['fetcher_out_path'] = 'result.txt'
        conf['features_json'] = str(bs_features.path)
        conf['flows_json'] = sdk_svn.Arcadia.get_arcadia_src_dir(
            "arcadia:/arc/trunk/arcadia/quality/ab_testing/bs_collector/regr/") + '/flows.json'
        conf['metrics.json'] = str(bs_metrics.path)
        conf['fetcher_out_path'] = 'fetcher_out.txt'
        conf['fetcher_out_table'] = 'fetcher_out_table.json'
        week_path = 'even_week' if (now.today().isocalendar()[1]) % 2 == 0 else 'odd_week'
        conf['sample_path'] = "//home/abt/regrabt/bs/samples/{}/ratio_07".format(week_path)

        bs_paths = shellabt.DebianYaPackagePaths(str(bs_pkg.path), '/Berkanavt/ab_testing/bin')
        self.merge_configs(donor=bs_paths, recipient=conf)

        ab_paths = shellabt.DebianYaPackagePaths(str(ab_pkg.path), '/Berkanavt/ab_testing/bin')
        self.merge_configs(donor=ab_paths, recipient=conf)

        msgs = ["conf:"]
        for k, v in conf.items.items():
            if "token" not in k:
                msgs.append('"{}":"{}"'.format(k, v))
            else:
                msgs.append('"{}":"{}"'.format(k, 'X' * len(v)))
        logging.info("\n\t".join(msgs))

        logging.info('Run bs_collector')
        stat = shellabt.StatRunner(conf)
        stat.run_bs_collector(
            time=conf['date'],
            sample_path=conf['sample_path'],
            flows=conf['flows_json'],
            features=conf['features_json'],
            result_table=conf['collector_out_table']
        )

        logging.info('Set expiration for %s', conf['collector_out_table'])
        import yt.wrapper
        client = yt.wrapper.YtClient(proxy=conf['server'], token=conf['yt_token'])
        client.set_attribute(conf['collector_out_table'], 'expiration_time', int(time.time() + 7 * 24 * 60 * 60) * 1000)

        logging.info('Run stat_fetcher')
        collector_config_path = 'sc_conf.txt'
        with open(collector_config_path, 'wt') as f:
            f.write('[task]\nname=\nexperiment=0')
        stat.run_stat_fetcher(
            config_path=collector_config_path,
            target_date=conf['date'],
            collector_table=conf['collector_out_table'],
            result_path=conf['fetcher_out_table']
        )

        logging.info('Load result to file')
        suite = shellabt.SuiteResult()
        metrics_info = shellabt.load_only_metrics(conf['stat_fetcher'])
        stat_result = shellabt.StatResult.from_file(conf['fetcher_out_table'], metrics_info)
        suite.add(stat_result)

        dirname = 'result_tables'
        dirname = os.path.abspath(dirname)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        filename_fetcher = 'metrics.json'
        fetcher_file = os.path.join(dirname, filename_fetcher)
        suite.to_file(fetcher_file)

        resource_name = 'BS calculated metrics, package_id_' + str(package_id)

        logging.info('Create "{}" resource'.format(resource_name))
        resource = RUN_ABT_METRICS_REPORT(self, resource_name, filename_fetcher)
        resource_data = sdk2.ResourceData(resource)
        resource_data.path.write_bytes(file_utils.read_file(fetcher_file))
        resource_data.ready()

        logging.info("RunBsMetrics execution completed")
