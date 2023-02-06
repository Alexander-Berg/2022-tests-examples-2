# -*- coding: utf-8 -*-

import urllib
import pytz
import time


class BaseReportsCreator(object):
    def __init__(self, task=None):
        self._task = task
        self._report = {}

    def get_report(self, subtask):
        pass

    def _format_reports_info(self, title, links):
        return '<p><strong>{}</strong></p>{}'.format(title, ''.join(links))

    def _format_link(self, base_url, title, params={}):
        params.update({
            'orgId': 1,
            'from': self._convert_time_to_ms(self._task.created),
            'to': self._convert_time_to_ms(self._task.updated)
        })
        link_url = '{}?{}'.format(base_url, urllib.urlencode(params))

        return '<a href={}>{}</a>'.format(link_url, title)

    def _convert_time_to_ms(self, dt_time):
        local_tz = pytz.timezone('Europe/Moscow')

        return int(time.mktime(dt_time.astimezone(local_tz).timetuple()))
