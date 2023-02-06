# -*- coding: utf-8 -*-

import json
import logging
import subprocess

from sandbox import sdk2
from sandbox.sandboxsdk import environments
import sandbox.common.types.task as ctt
import sandbox.common.types.notification as ctn

from test import VideohubHandsTester


class TestVideohub(sdk2.Task):
    error_message_beginning = 'TestVideohub exception'
    uids_count = 10

    class Parameters(sdk2.Task.Parameters):
        beta_url = sdk2.parameters.String("beta_url", default="http://video-http-apphost.yandex.ru", required=False)
        custom_cgi = sdk2.parameters.String("custom_cgi", default="yandexuid=2&region=225&vitrina_filter=vh", required=False)
        yt_token = sdk2.parameters.String('yt_token', default='alex0512_yt_banach_vault_token', required=False)

    class Requirements(sdk2.Task.Requirements):
        environments = [
            environments.PipEnvironment('pyrsistent', version='0.16.0'),
            environments.PipEnvironment("jsonschema", "3.0.2", custom_parameters=['--upgrade-strategy', 'only-if-needed']),
            environments.PipEnvironment("yandex-yt"),
            environments.PipEnvironment('yandex-yt-yson-bindings-skynet')
        ]

    def add_item_to_cgi(self, cgi, item):
        if len(item) == 0:
            return cgi
        if len(cgi) != 0:
            cgi += '&'
        cgi += item
        return cgi

    def exclude_cgi_ids(self, cgi):
        cgiItems = cgi.split('&')
        cgiFinal = ''
        for item in cgiItems:
            if (item.startswith('yandexuid') or item.startswith('vitrina_puid')):
                continue
            cgiFinal = self.add_item_to_cgi(cgiFinal, item)
        return cgiFinal

    def check(self, json_obj, schema, testName):
        from jsonschema import validate, exceptions

        try:
            validate(json_obj, schema)
        except exceptions.ValidationError as e:
            logging.error('TEST {} FAILED: ValidationError:\n"""{}"""'.format(testName, e.message))
            return 2
        except Exception as e:
            logging.error('ERROR ON TEST {}:'.format(testName))
            raise e
            return 1
        else:
            logging.info("TEST {} SUCCESS".format(testName))
            return 0

    def empty_vitrina_group(self, group):
        return len(group['_SerpData']['netflix']['categories'][0]['queries']) == 0

    def empty_videohub_group(self, group):
        return len(group['Docs']) == 0

    def empty_group(self, group):
        if group['GroupType'] == 'vitrina':
            return self.empty_vitrina_group(group)
        else:
            return self.empty_videohub_group(group)

    def check_output(self, serp_file):
        output = json.load(open(serp_file))
        groups = output['Groups']

        vitrina_group_count = 0
        videohub_group_count = 0
        for group in groups:
            if group['GroupType'] == 'vitrina':
                vitrina_group_count = vitrina_group_count + 1
            elif group['GroupType'] == 'videohub':
                videohub_group_count = videohub_group_count + 1
            else:
                raise RuntimeError(self.error_message_beginning + ': unrecognized group type: ' + group['GroupType'])

            if self.empty_group(group):
                raise RuntimeError(self.error_message_beginning + ': empty group')

        if vitrina_group_count != 4:
            raise RuntimeError(self.error_message_beginning + ': vitrina group count is small: ' + str(vitrina_group_count))
        if videohub_group_count < 6:
            raise RuntimeError(self.error_message_beginning + ': videohub group count is small: ' + str(videohub_group_count))

    def check_uids(self, yuids, puids, beta_url, custom_cgi):
        for (yuid, puid) in zip(yuids, puids):
            cgi = self.add_item_to_cgi(custom_cgi, 'yandexuid=' + yuid)
            cgi = self.add_item_to_cgi(cgi, 'vitrina_puid=' + puid)
            serp_wget = "wget " + "\"" + beta_url + "?" + cgi + "\""
            subprocess.check_output(['bash', '-c', serp_wget])
            serp_file = serp_wget.split('/')[-1][:-1]
            self.check_output(serp_file)
            subprocess.Popen(['bash', '-c', 'rm "' + serp_file + '"'])

    def on_execute(self):
        from yt.wrapper import YtClient
        beta_url = self.Parameters.beta_url
        custom_cgi = self.Parameters.custom_cgi
        custom_cgi = self.exclude_cgi_ids(custom_cgi)

        if '__te_apiargs' in self.Context.__values__:
            api_args_str = self.Context.__values__['__te_apiargs']
            api_args = json.loads(api_args_str)
            if 'context' in api_args and 'beta_url' in api_args['context']:
                beta_url = api_args['context']['beta_url']

        if beta_url.endswith('/'):
            beta_url = beta_url[:-1]

        try:
            yt_token = sdk2.Vault.data(self.Parameters.yt_token)
            client = YtClient(proxy='arnold', token=yt_token, config={'read_retries': {'enable': False}})
            uids_table = client.read_table('//home/videodev/alex0512/puid2yuid', format='yson', raw=False, unordered=True)
            yuids = []
            puids = []
            for row in uids_table:
                yuids.append(row['yuid'])
                puids.append(row['puid'])
                if len(yuids) == self.uids_count:
                    break

            self.check_uids(yuids, puids, beta_url, custom_cgi)
        except Exception as e:
            if str(e).startswith(self.error_message_beginning):
                raise e

        VideohubHandsTester(self.check, self.Parameters.beta_url, self.Parameters.custom_cgi).test()

    def on_save(self):
        self.Parameters.notifications = [
            sdk2.Notification(
                [ctt.Status.FAILURE, ctt.Status.EXCEPTION, ctt.Status.NO_RES, ctt.Status.TIMEOUT],
                [self.author],
                ctn.Transport.EMAIL
            )
        ]
