# -*- coding: utf-8 -*-

import json
import subprocess

from sandbox import sdk2
from sandbox.sandboxsdk import environments
from sandbox.sandboxsdk.svn import Arcadia


class TestVideoVitrina(sdk2.Task):
    error_message = 'Category is empty'
    filter_name_error_message = 'Invalid filter name'
    uids_count = 10

    filter_categs_arcadia_path = 'arcadia:/arc/trunk/arcadia/extsearch/video/quality/recommender/1492/cuba/config/filter_categs.json'
    filter_categs_local_path = 'filter_categs.json'

    class Parameters(sdk2.Task.Parameters):
        beta_url = sdk2.parameters.String("Beta's url", default="https://yandex.ru/video/api", required=True)
        custom_cgi = sdk2.parameters.String("Custom cgi", default="vitrina_cold_start=enable&vitrina_allowed_categs=film,tv_show,series,anim_film,anim_series&region=225&vitrina_new=1", required=True)
        yt_token_vault = sdk2.parameters.String('YT token vault name', default='alex0512_yt_banach_vault_token', required=True)

    class Requirements(sdk2.Task.Requirements):
        environments = [environments.PipEnvironment("yandex-yt"), environments.PipEnvironment('yandex-yt-yson-bindings-skynet')]

    def convert_filter_name(self, filter_name):
        filter_prefix = 'FILTER_'
        if not filter_name.startswith(filter_prefix):
            raise RuntimeError(self.filter_name_error_message)
        return filter_name.replace(filter_prefix, '', 1).lower()

    def add_item_to_cgi(self, cgi, item):
        if len(item) == 0:
            return cgi
        if len(cgi) != 0:
            cgi += '&'
        cgi += item
        return cgi

    def exclude_cgi_uid(self, cgi):
        cgiItems = cgi.split('&')
        cgiFinal = ''
        for item in cgiItems:
            if (item.startswith('yandexuid')):
                continue
            cgiFinal = self.add_item_to_cgi(cgiFinal, item)
        return cgiFinal

    def find_empty(self, serp_file, types):
        vitrina = json.load(open(serp_file))
        categories = vitrina['netflix']['categories']

        isEmpty = {}
        for t in types:
            isEmpty[t] = True

        typeKey = 'type'
        queriesKey = 'queries'
        for category in categories:
            if typeKey not in category.keys() or queriesKey not in category.keys():
                continue
            isEmpty[category[typeKey]] = (len(category[queriesKey]) == 0)

        for t in types:
            if isEmpty[t]:
                return t
        return None

    def check_uids(self, uids, beta_url, custom_cgi, filter_categs):
        for uid in uids:
            for vitrina_filter, categs in filter_categs.iteritems():
                cgi = self.add_item_to_cgi(custom_cgi, 'yandexuid=' + uid)
                cgi = self.add_item_to_cgi(cgi, 'vitrina_filter=' + self.convert_filter_name(vitrina_filter))
                serp_wget = "wget " + "\"" + beta_url + "?" + cgi + "\""
                subprocess.check_output(['bash', '-c', serp_wget])
                serp_file = serp_wget.split('/')[-1][:-1]
                empty_categ = self.find_empty(serp_file, categs)
                if empty_categ is not None:
                    raise RuntimeError(self.error_message + ': ' + vitrina_filter + '/' + empty_categ)

    def on_execute(self):
        from yt.wrapper import YtClient
        beta_url = self.Parameters.beta_url
        custom_cgi = self.Parameters.custom_cgi
        custom_cgi = self.exclude_cgi_uid(custom_cgi)

        try:
            yt_token = sdk2.Vault.data(self.Parameters.yt_token_vault)
            client = YtClient(proxy='banach', token=yt_token, config={'read_retries': {'enable': False}})
            backup_table = client.read_table('//home/videoindex/recommender/backup/vitrina/upload.latest/recommendations_merged.filter_none', format='yson', raw=False, unordered=True)
            uids = []
            for row in backup_table:
                uids.append(row['key'])
                if len(uids) == self.uids_count:
                    break

            Arcadia.export(self.filter_categs_arcadia_path, self.filter_categs_local_path)
            filter_categs = json.load(open(self.filter_categs_local_path))

            self.check_uids(uids, beta_url, custom_cgi, filter_categs)
        except Exception as e:
            for message in [self.error_message, self.filter_name_error_message]:
                if str(e).startswith(message):
                    raise e
