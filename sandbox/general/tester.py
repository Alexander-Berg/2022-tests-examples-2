# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import logging
import time
import json
import imp
import os
import glob
import requests

import sandbox.sdk2 as sdk2
from sandbox.common.errors import TaskError
from sandbox.projects.common import solomon
from sandbox.projects.common import file_utils as fu
from sandbox.sdk2 import svn
from sandbox.sdk2 import ssh
from sandbox.sandboxsdk.channel import channel

from box import json_to_str
from box import Box

STABLE_REVISION = 4284618


class Tester:
    """
         Непрерывное тестирование с низким RPS(1-10)
    """

    def __init__(self, task, parameters, path):
        self.task = task
        self.yt_token = sdk2.Vault.data('gav1995', 'yt-token')
        self.soy_token = sdk2.Vault.data('gav1995', 'soy-token')
        self.Parameters = self.Parameters(parameters, self.yt_token)
        self.path = path
        self.start_time = time.time()
        self.run_count = 0
        self.production = []
        self.test = []
        self.config = ''
        self.config_changed = False
        self.boxes = []
        self.in_fly = []
        self.workers = []
        self.revision = STABLE_REVISION
        self.falled = []

    def init(self):
        self.time = time.time()
        self.production = []
        self.test = []
        self.config_changed = False
        self.boxes = []

    class Parameters:
        def __init__(self, parameters, yt_token):
            self.run_boxes_count = parameters.run_boxes_count
            self.monitoring_time = parameters.monitoring_time
            self.max_resend_count = parameters.max_resend_count
            self.host = parameters.host
            self.solomon_project = parameters.solomon_project
            self.solomon_cluster = parameters.solomon_cluster
            self.solomon_service_monitoring = parameters.solomon_service_monitoring
            self.solomon_service_testing = parameters.solomon_service_testing
            self.test_data_url = parameters.test_data_url
            self.ssh_key = parameters.ssh_key
            self.ssh_owner = parameters.ssh_owner
            self.yt_res_dir = parameters.yt_res_dir
            self.yt_request_table = parameters.yt_request_table
            import yt.wrapper as yt
            yt.config["proxy"]["url"] = "hahn"
            yt.config["token"] = yt_token
            tables_json = yt.list(self.yt_res_dir, format='json')
            tables_json = yt.list(self.yt_res_dir, format='json')
            to_remove = [table for table in json.loads(tables_json) if (datetime.now() - timedelta(parameters.yt_res_ttl)).isoformat().replace(":", "-") > table]
            for table in to_remove:
                logging.info("removing {}".format(table))
                yt.remove(self.yt_res_dir + '/' + table)

    def get_test_values(self):
        # construct test_values from config
        self.test = []
        self.is_config_changed = False
        log = svn.Arcadia.log(self.path, self.revision, 'BASE')
        i = 1
        check_error = []
        logging.info('new revisions ' + str(log))
        while(log[-i]['revision'] > self.revision):
            for filename in glob.glob(self.path+'/functions/*.pyc'):
                logging.info('remove ' + filename)
                os.remove(filename)
                logging.info('after remove '+str(glob.glob(self.path+'/functions/*.pyc')))
            report, ok = self.check_test()
            logging.info('check revision ' + str(log[-i]['revision']) + ' is ' + str(ok))
            if ok:
                break
            else:
                check_error.append(report)
                revision = log[-i]['revision']
                logging.info('roll back revision' + str(revision))
                svn.Arcadia.merge(self.Parameters.test_data_url, self.path, str(-revision))
                i += 1
        if i > 1:
            i -= 1
            with ssh.Key(self.task, self.Parameters.ssh_owner, self.Parameters.ssh_key):
                svn.Arcadia.commit(self.path, "roll back to stable revision", user='gav1995')
            logging.info('roll back commited to revision'+str(log[-i-1]['revision']))
            broken_author = log[-i]['author']
            broken_revision = log[-i]['revision']
            correct_revision = log[-i - 1]['revision']
            for j in range(-i, 0):
                msg = 'Config was broken by ' + broken_author + ' in revision ' + str(broken_revision)
                msg += '. We couldn\'t support your config in revision ' + str(log[j]['revision']) + '.'
                msg += ' We rolled back config to revision ' + str(correct_revision) + '.'
                msg += ' Please update your local version of config before commit!'
                msg += ' \nReport of tester.py on your revision:\n' + check_error[-j - 1]
                channel.sandbox.send_email(mail_to=log[j]['author'], mail_cc='', mail_subject='NoapacheUpperTest: config was broken and rolled back', mail_body=msg)

        curr_revision = self.get_curr_revision()
        if self.revision != curr_revision:
            self.is_config_changed = True
            self.revision = curr_revision
            self.falled = []

        logging.info('config_revision = ' + str(self.revision))
        new_conf = fu.json_load(self.path + '/config.json')
        boxes = fu.json_load(self.path + '/production_list.json')
        self.production = boxes['production']
        if self.is_config_changed:
            self.test = boxes['test']
        new_conf = [test for test in new_conf if not test['name'] in self.falled]
        tests = [test for test in new_conf if test['name'] in self.test]
        production = [test for test in new_conf if test['name'] in self.production and test['name'] not in self.test]
        return production, tests

    def get_curr_revision(self):
        return max(int(svn.Arcadia.info(self.path + name)['commit_revision']) for name in ('/config.json', '/boxes', '/functions', '/tests.json'))

    def check_test(self):
        module = imp.load_source('tester.py', self.path + '/tester.py')
        return vars(module)['check_serp_tester'](self.path + '/')

    def get_system_config_signals(self):
        stats = dict()
        stats['run_config_time'] = time.time() - self.time
        stats['is_config_changed'] = self.is_config_changed
        stats['config_revision'] = self.revision % 10000 / 1000.0
        return stats

    def push_results(self, stats, service):
        """Send sensor values to solomon"""
        logging.info("stats to " + service + " " + str(stats))
        sensors = solomon.create_sensors(stats)
        common_labels = {
            "host": "solomon-push",
            "project": self.Parameters.solomon_project,
            "cluster": self.Parameters.solomon_cluster,
            "service": service
        }
        try:
            solomon.upload_to_solomon(common_labels, sensors)
        except:
            logging.error("can't push data to " + service + " retry count lately")

    def push_all_to_solomon(self):

        test = dict()
        prod = dict()

        for box in self.boxes:
            if box.get_test_flag():
                test.update(box.get_for_solomon())
            else:
                prod.update(box.get_for_solomon())

        signals = self.get_system_config_signals()
        if test:
            test.update(signals)
            logging.info("Push in Solomon testing service = " + json_to_str(test))
            self.push_results(test, self.Parameters.solomon_service_testing)

        if prod:
            prod.update(signals)
            logging.info("Push in Solomon monitoring service = " + json_to_str(prod))
            self.push_results(prod, self.Parameters.solomon_service_monitoring)

    def send_requests(self):
        self.batch = []
        for idx, box in enumerate(self.boxes):
            for row in box.batch:
                b = dict()
                b.update(row)
                b["method"] = "GET"
                b["cookies"] = []
                b["headers"] = []
                b["id"] = "{}_{}".format(idx, row['id'])
                self.batch.append(b)
        logging.info("send {}".format(len(self.batch)))
        import yt.wrapper as yt
        yt.config["proxy"]["url"] = "hahn"
        yt.config["token"] = self.yt_token
        yt.write_table(yt.TablePath(self.Parameters.yt_request_table), self.batch, format='json')
        logging.info("save {} to request table {}".format(len(self.batch), self.Parameters.yt_request_table))
        pid = "ContinuesNoapacheupperTest{}".format(datetime.now().isoformat()).replace(':', '-')
        logging.info("pid = {}".format(pid))
        headers = {
            "Authorization": "OAuth {}".format(self.soy_token)
        }
        response = requests.post(
            'http://soyproxy.yandex.net/hahn/soy_api/create',
            data=json.dumps({
                "input_table": self.Parameters.yt_request_table,
                "pool": "geo_continues_upper_test",
                "id": pid,
                "max_retries_per_row": self.Parameters.max_resend_count
            }),
            headers=headers
        )
        logging.info("response = {}".format(response))
        response = response.json()
        logging.info("status = {}".format(response['status']))
        if(response['status'] != 'ok'):
            raise TaskError(str(response))
        return pid

    def wait(self, pid):
        tm = - time.time()
        headers = {
            "Authorization": "OAuth {}".format(self.soy_token)
        }
        response = requests.get("http://soyproxy.yandex.net/hahn/soy_api/status?id={}".format(pid), headers=headers).json()
        while(response["operation_status"] != 'completed'):
            logging.info("status = {}".format(response["operation_status"]))
            time.sleep(10)
            response = requests.get("http://soyproxy.yandex.net/hahn/soy_api/status?id={}".format(pid), headers=headers).json()
        logging.info("response = {}".format(response))
        tm += time.time()
        logging.info('waiting time {}'.format(tm))
        return response

    def get_response(self, stat):
        output_table = stat["output_path"]
        import yt.wrapper as yt
        yt.config["proxy"]["url"] = "hahn"
        yt.config["token"] = self.yt_token
        table = yt.read_table(yt.TablePath(output_table, columns=["id", "FetchedResult"]), format='json')
        for row in table:
            try:
                if row["FetchedResult"]:
                    resp = json.loads(row["FetchedResult"])
                else:
                    resp = None
                ok = True
            except:
                resp = row["FetchedResult"]
                ok = False
            ids = row["id"].split('_')
            box_num = int(ids[0])
            qreq = int(ids[1])
            self.boxes[box_num].put_response(qreq, ok, resp)
            logging.debug('recieve ' + str(row["id"]) + ' to ' + str(box_num) + ' qreq = ' + str(qreq))

    def run(self):
        pid = self.send_requests()
        stat = self.wait(pid)
        self.get_response(stat)
        for box in self.boxes:
            box.run()
        for box in self.boxes:
            if not box.get_state():
                self.falled.append(box.get_name())

    def run_config(self):
        try:
            logging.critical("iteration "+str(self.run_count)+" started")
            self.init()
            logging.info("init finished")
            prod, test = self.get_test_values()
            logging.info("get_test_values finished prod = " + json_to_str(prod) + "test " + json_to_str(test))
            log_table = self.Parameters.yt_res_dir + '/'+datetime.now().isoformat().replace(":", "-")
            self.boxes = [Box(self.task, box, self.path, self.Parameters.host, log_table, self.yt_token, False) for box in prod]
            self.boxes.extend([Box(self.task, box, self.path, self.Parameters.host, log_table, self.yt_token, True) for box in test])
            logging.info('start running')
            self.run()
            logging.info('finish running')
            self.push_all_to_solomon()

            logging.critical("iteration " + str(self.run_count) + " finished")
        except TaskError as TE:
            logging.error("-------requester error!---------" + str(TE))
        self.run_count += 1

    def need_run_config(self):
        if self.Parameters.monitoring_time and time.time() - self.start_time > self.Parameters.monitoring_time * 60 * 60:
            logging.log(0, "end: begin_time: " + str(self.start_time) + " time.time(): " + str(time.time()))
            return False

        if self.Parameters.run_boxes_count and self.run_count == self.Parameters.run_boxes_count:
            logging.log(0, "run_count = " + str(self.run_count))
            return False

        return True
