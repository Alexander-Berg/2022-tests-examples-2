# -*- coding: utf-8 -*-

import re
from sandbox.projects.sandbox_ci.sandbox_ci_compare_load_test.reports_creator.base import BaseReportsCreator

CONTAINERS_URLS_MAPPING = {
    'production': [
        {
            'urls': [
                'https://grafana.qatools.yandex-team.ru/d/117d3f9a698f1ebbe2c2e8eed5d85770/selenium-session_created-selenium-cloud',
                'https://grafana.qatools.yandex-team.ru/d/0f561ec85b13c9c1082ff55f207bd669/selenium-cloud-containers-selenium-cloud'
            ],
            'browsers': ['firefox', 'chrome-desktop', 'iphone', 'ipad']
        },
        {
            'urls': [
                'https://grafana.qatools.yandex-team.ru/d/060c21b611a23f520554d88b57b27f81/selenium-session_created-android-cloud-serp',
                'https://grafana.qatools.yandex-team.ru/d/2022080b21093178b19681f85859dcdd/selenium-cloud-containers-android-cloud'
            ],
            'browsers': ['chrome-phone', 'chrome-pad', 'searchapp-phone', 'searchapp', 'yandex-browser-phone']
        }
    ],
    'inokentiy': [
        {
            'urls': ['https://grafana.qatools.yandex-team.ru/d/c190bc5b62c37173dda35462c8023674/selenium-session_created-selenium-cloud-test-load'],
            'browsers': ['firefox', 'chrome-desktop', 'iphone', 'ipad', 'chrome-phone', 'chrome-pad', 'searchapp-phone', 'searchapp', 'yandex-browser-phone']
        }
    ],
    'web4-ssd-test-1': [
        {
            'urls': ['https://grafana.qatools.yandex-team.ru/d/6253ea9f1dc5f1b00111c5461a2bea73/selenium-cloud-containers-selenium-cloud-test-load'],
            'browsers': ['edge-desktop', 'firefox', 'chrome-desktop', 'iphone', 'ipad', 'chrome-phone', 'chrome-pad', 'searchapp-phone', 'searchapp', 'yandex-browser-phone']
        }
    ],
    'web4-ssd-test-2': [
        {
            'urls': ['https://grafana.qatools.yandex-team.ru/d/f05c0472c3a7248f5c3f8e97d2a4e382/selenium-cloud-containers-selenium-cloud-test-load-2'],
            'browsers': ['firefox', 'chrome-desktop', 'iphone', 'ipad', 'chrome-phone', 'chrome-pad', 'searchapp-phone', 'searchapp', 'yandex-browser-phone']
        }
    ]
}


class ContainersReportsCreator(BaseReportsCreator):
    @property
    def title(self):
        return 'grafana'

    def get_report(self, subtask):
        containers_ino = next((cnt for title, cnt in CONTAINERS_URLS_MAPPING.iteritems() if re.search(title, self._task.grid_url)), None)

        if not containers_ino:
            containers_ino = CONTAINERS_URLS_MAPPING['production']

        containers_urls = next((cnt['urls'] for cnt in containers_ino if self._task.browser_id in cnt['browsers']), None)
        reports_links = map(lambda url: self._format_link(url, url), containers_urls)
        return self._format_reports_info('Containers start/used', reports_links)
