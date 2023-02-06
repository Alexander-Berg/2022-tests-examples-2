# -*- coding: utf-8 -*-

import os
import re
import json
import logging
import requests

QUOTA_REGEX = '.+@sg\.yandex-team\.ru\:\d+'

QUOTA_BROWSERS_MAPPING = {
    'ie11': 'internet explorer',
    'edge-desktop': 'MicrosoftEdge',
    'firefox': 'firefox',
    'chrome-desktop': 'chrome',
    'chrome-phone': 'android-phone',
    'iphone': 'chrome',
    'iphoneX': 'chrome',
    'yandex-browser-phone': 'chrome',
    'searchapp': 'android-phone',
    'searchapp-phone': 'android-phone',
    'chrome-pad': 'android-phone',
    'ipad': 'chrome'
}


class QuotaManager(object):
    def __init__(self, task):
        self._task = task

    def get_total(self, grid_url):
        quota_data = self._get_quota_data(grid_url)
        logging.debug('get total quota data: {}'.format(quota_data))
        total = 0

        for region in quota_data:
            for host in region['Hosts']:
                total += host['Count']

        return total

    def get_hosts(self, grid_url, hosts_cnt):
        quota_data = self._get_quota_data(grid_url)
        logging.debug('get hosts quota data: {}'.format(quota_data))
        res = []

        for region in quota_data:
            for host in region['Hosts']:
                if re.search(self._task.data_center.lower(), host['Name']):
                    res.append(host['Name'])

                if len(res) == hosts_cnt:
                    return res

        return res

    def _get_quota_data(self, grid_url):
        parsed_quota = re.search(QUOTA_REGEX, grid_url)
        logging.debug('parsed_quota: {}'.format(parsed_quota))
        quota_data = requests.get(os.path.join(parsed_quota.group(0), 'quota'))
        logging.debug('quota_data: {}'.format(parsed_quota))

        all_browser_data = next((x for x in json.loads(quota_data.content) if x['Name'] == QUOTA_BROWSERS_MAPPING[self._task.browser_id]), None)
        curr_browsers_data = next((x for x in all_browser_data['Versions'] if x['Number'] == self._task.browser_version), None)

        return curr_browsers_data['Regions']
