# -*- coding: utf-8 -*-
from sandbox import sdk2
import logging
import json
import time
from sandbox.sandboxsdk import environments


class TestpalmTableCreate(sdk2.Task):
    testing=False
    yttoken=''  # Add for tests

    class Requirements(sdk2.Task.Requirements):
        environments = [
            environments.PipEnvironment("yandex-yt", version="0.11.2"),
            environments.PipEnvironment("yandex-yt-yson-bindings"),
            environments.PipEnvironment("yandex-yt-yson-bindings-skynet"),
        ]

    def console(self, text):
        if (self.testing):
            print(text)
        else:
            logging.info(text)

    def on_execute(self):
        import yt.wrapper as yt
        self.console("-----PARAMS-----")
        secret = {
            'yt': self.yttoken,
        } if self.testing else sdk2.yav.Secret("sec-01g13xgyw3ebvrt8yyf8nmhp69", "ver-01g8tgvbfxrg9gw91wq242ewxh").data()
        writeToCluster = 'hahn'
        writeToTable = '//home/iot/ui/datalens/testpalm/'
        clientRead = yt.YtClient(proxy="hahn", token=secret['yt'])
        clientWrite = yt.YtClient(proxy=writeToCluster, token=secret['yt'])
        timeNow = round(time.time())
        iot = {
            'timestamp': timeNow,
            'manual': 0,
            'complete': 0,
            'ready': 0,
            'backlog': 0
        }

        quasar = {
            'timestamp': timeNow,
            'manual': 0,
            'complete': 0,
            'ready': 0,
            'backlog': 0
        }

        self.console("-----GO-THROUGHT-CASES-----")
        iotCases = []
        quasarCases = []
        for test in clientRead.read_table("//home/testpalm/stats/serp/testcases".format()):
            if not((test['project_id'] == 'iot-ui') | (test['project_id'] == 'quasar-ui')):
                continue
            if bool(test['removed']):
                continue
            if test['project_id'] == 'iot-ui':
                iotCases.append(test)
            if test['project_id'] == 'quasar-ui':
                quasarCases.append(test)
            groups = 0
            proj = iot if test['project_id'] == 'iot-ui' else quasar
            if 'attributes' in test:
                att = json.loads(test['attributes'])
                if 'tags' in att:
                    if not('release_Webview' in att['tags']):
                        continue
                if 'filepath' in att:
                    if not(att['filepath'][0] is None):
                        if '/backlog/' in att['filepath'][0]:
                            proj['backlog'] += 1
                            groups += 1
                if 'automation' in att:
                    if not(att['automation'][0] is None):
                        if not('TODO' in att['automation'][0]):
                            proj['ready'] += 1
                            groups += 1
            if 'name' in test:
                if ('[manual]' in test['name']):
                    proj['manual'] += 1
                    groups += 1
            if 'name' in test and 'attributes' in test:
                if 'filepath' in att:
                    if not(att['filepath'][0] is None):
                        if not(('[manual]' in test['name']) or ('automation' in att) or ('/backlog/' in att['filepath'][0])):
                            proj['complete'] += 1
                            groups += 1
            if groups != 1:
                self.console("In two groups: https://testpalm.yandex-team.ru/" + test['project_id'] + "/testcases?testcase=" + test['id'])

        self.console("-----WRITE-----")
        clientWrite.write_table(yt.TablePath(writeToTable + 'iot', append=True), [{
            'timestamp': int(iot['timestamp']),
            'manual': int(iot['manual']),
            'complete': int(iot['complete']),
            'ready': int(iot['ready']),
            'backlog': int(iot['backlog'])
        }], format='json')
        clientWrite.write_table(yt.TablePath(writeToTable + 'quasar', append=True), [{
            'timestamp': int(quasar['timestamp']),
            'manual': int(quasar['manual']),
            'complete': int(quasar['complete']),
            'ready': int(quasar['ready']),
            'backlog': int(quasar['backlog'])
        }], format='json')

        yt_schema = [
            {"name": "id", "type": "string"},
            {"name": "project_id", "type": "string"},
            {"name": "name", "type": "string"},
            {"name": "description", "type": "string"},
            {"name": "created_by", "type": "string"},
            {"name": "attributes", "type": "string"},
            {"name": "removed", "type": "boolean"},
        ]

        self.console("-----WRITE-RAW-----")
        clientWrite.write_table(yt.TablePath(writeToTable + 'raw/iot/' + str(timeNow), attributes={"schema": yt_schema}), iotCases)
        clientWrite.write_table(yt.TablePath(writeToTable + 'raw/quasar/' + str(timeNow), attributes={"schema": yt_schema}), quasarCases)
