# -*- coding: utf-8 -*-


class LinkBuilder(object):
    def __init__(self, task):
        self._task = task

    def make_testcop_link(self):
        url = 'https://testcop.si.yandex-team.ru/task/{}'.format(self._task.id)
        return self.__make_link('Testcop', url)

    def __make_link(self, text, url):
        return '<a href="{}" target="_blank">{}</a>'.format(url, text)
