# -*- coding: utf-8 -*-

import json
import logging
import time
import urllib2
import datetime as datetime

from sandbox import sdk2

from sandbox.projects.resource_types.releasers import experiment_releasers
from sandbox.projects.common.nanny import nanny
from sandbox.projects.common import task_env


class AbtMetricsJson(sdk2.Resource):
    '''
    Metrics.json (see. USEREXP-5820)
    '''
    any_arch = True
    releasable = True
    auto_backup = True
    releasers = experiment_releasers + ['robot-eksperimentus']

    version = sdk2.parameters.Integer(
        'version',
        default=0,
        required=True
    )


class AbtFeaturesJson(sdk2.Resource):
    '''
    features.json (see. USEREXP-5820)
    '''
    any_arch = True
    releasable = True
    auto_backup = True
    releasers = experiment_releasers + ['robot-eksperimentus']

    version = sdk2.parameters.Integer(
        'version',
        default=0,
        required=True
    )


class BsMetricsJson(sdk2.Resource):
    '''
    Metrics.json (see. USEREXP-14508)
    '''
    any_arch = True
    releasable = True
    auto_backup = True
    releasers = experiment_releasers + ['robot-eksperimentus']

    version = sdk2.parameters.Integer(
        'version',
        default=0,
        required=True
    )


class BsFeaturesJson(sdk2.Resource):
    '''
    features.json (see. USEREXP-14508)
    '''
    any_arch = True
    releasable = True
    auto_backup = True
    releasers = experiment_releasers + ['robot-eksperimentus']

    version = sdk2.parameters.Integer(
        'version',
        default=0,
        required=True
    )


class ZenMetricsJson(sdk2.Resource):
    '''
    Metrics.json (see. USEREXP-5820) and USEREXP-10693
    '''
    any_arch = True
    releasable = True
    auto_backup = True
    releasers = experiment_releasers + ['robot-eksperimentus']

    version = sdk2.parameters.Integer(
        'version',
        default=0,
        required=True
    )


class ZenFeaturesJson(sdk2.Resource):
    '''
    features.json (see. USEREXP-5820) abd USEREXP-10693
    '''
    any_arch = True
    releasable = True
    auto_backup = True
    releasers = experiment_releasers + ['robot-eksperimentus']

    version = sdk2.parameters.Integer(
        'version',
        default=0,
        required=True
    )


class AbtMetricsJsonUpdate(nanny.ReleaseToNannyTask2, sdk2.Task):
    '''
    Update metrics.json and features.json resource for binaries based on abt_resources
    '''
    metrics_json_resources = {
        "abt": AbtMetricsJson,
        "bs": BsMetricsJson,
        "zen": ZenMetricsJson,
    }
    features_json_resources = {
        "abt": AbtFeaturesJson,
        "bs": BsFeaturesJson,
        "zen": ZenFeaturesJson,
    }

    class Requirements(task_env.TinyRequirements):
        ram = 1024  # 1 Gb

    class Parameters(sdk2.Task.Parameters):
        kill_timeout = 15 * 60  # 15 min

        calc_type = sdk2.parameters.String(
            'calc_type',
            default='abt',
            required=True
        )
        version = sdk2.parameters.Integer(
            'version',
            default=0,
            required=True
        )
        metrics_json_url = sdk2.parameters.String(
            'metrics.json URL',
            default='https://ab.yandex-team.ru/api/metrics/picker/abt/preset_all/metrics_json',
            required=True
        )
        features_json_url = sdk2.parameters.String(
            'features.json URL',
            default='https://ab.yandex-team.ru/api/metrics/picker/abt/preset_all/custom_features',
            required=True
        )
        metrics_history_url = sdk2.parameters.String(
            'metrics.json history changes URL',
            default='http://ab.yandex-team.ru/api/metrics/metric/history',
            required=True
        )
        features_history_url = sdk2.parameters.String(
            'feature_custom.json history changes URL',
            default='http://ab.yandex-team.ru/api/metrics/feature/history',
            required=True
        )

    def check_json(self, text):
        logging.info('checking json')
        try:
            json.loads(text)
        except ValueError as e:
            logging.warning('error: {}'.format(str(e)))
            logging.warning('data: {}'.format(str(text)))
            raise ValueError(e)

    def fetch(self, url):
        logging.info('fetching from url {}'.format(url))

        for i in range(1, 11):
            logging.info('fetch attempt {}'.format(i))
            try:
                data = urllib2.urlopen(url).read()
                self.check_json(data)
                return data
            except urllib2.URLError as e:
                logging.warning('error: {}'.format(str(e)))
            except ValueError:
                pass
            time.sleep(10)
        raise Exception('FAILED to fetch from url {}'.format(url))

    def fetch_history(self, url, start_day):
        url = url + '?time__gte=' + start_day.strftime("%Y-%m-%d") + '&page_size=200'
        cur_page = json.loads(self.fetch(url))
        next_page = cur_page['next']
        results = cur_page['results']
        while next_page:
            cur_page = json.loads(self.fetch(next_page))
            results.extend(cur_page['results'])
            next_page = cur_page['next']
        return results

    def get_all_metrics_from_groups(self, metrics_json_dict):
        all_metrics = set()
        for group in metrics_json_dict['group_nodes']:
            all_metrics.update(group['metrics'])

        return all_metrics

    def filter_changes(self, metrics_changes, all_metrics):
        return [change for change in metrics_changes if change['key'] in all_metrics]

    def on_execute(self):

        def add_meta(file_json, id_resource, start_time, end_time, changes):
            file_json = json.loads(file_json)
            file_json['changes_info'] = {}
            info = file_json['changes_info']
            info['id_resource_sandbox'] = id_resource
            info['changes'] = changes
            info['start_time'] = str(start_time)
            info['end_time'] = str(end_time)
            logging.info("Added meta to resource.")
            return json.dumps(file_json)

        logging.info("checking the existence of resource classes")
        metrics_json_resource_class = self.metrics_json_resources[self.Parameters.calc_type]
        features_json_resource_class = self.features_json_resources[self.Parameters.calc_type]

        logging.info("download data")
        metrics_json = self.fetch(self.Parameters.metrics_json_url)
        features_json = self.fetch(self.Parameters.features_json_url)
        DELTA_DAY = 3
        end_time = datetime.datetime.today()
        start_time = end_time - datetime.timedelta(days=DELTA_DAY)
        features_changes = self.fetch_history(self.Parameters.features_history_url, start_time)

        metrics_changes = self.filter_changes(
            self.fetch_history(self.Parameters.metrics_history_url, start_time),
            self.get_all_metrics_from_groups(json.loads(metrics_json))
        )

        logging.info('creating {class_name} resource...'.format(class_name=metrics_json_resource_class.__name__))
        resource = metrics_json_resource_class(
            self,
            "metrics.json for `{calc_type}` calculation".format(calc_type=self.Parameters.calc_type),
            "metrics.json",
            version=self.Parameters.version
        )
        resource_data = sdk2.ResourceData(resource)
        metrics_json = add_meta(metrics_json, resource.id, start_time, end_time, metrics_changes)
        resource_data.path.write_bytes(metrics_json)
        resource_data.ready()

        logging.info('creating {class_name} resource...'.format(class_name=features_json_resource_class.__name__))
        resource = features_json_resource_class(
            self,
            'features.json for `{calc_type}` calculation'.format(calc_type=self.Parameters.calc_type),
            'features.json',
            version=self.Parameters.version
        )
        resource_data = sdk2.ResourceData(resource)
        features_json = add_meta(features_json, resource.id, start_time, end_time, features_changes)
        resource_data.path.write_bytes(features_json)
        resource_data.ready()
