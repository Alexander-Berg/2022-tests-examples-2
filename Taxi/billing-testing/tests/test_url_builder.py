# coding: utf8

from sibilla import utils
from taxi import discovery


def test_url_builder():
    def _t(expect, actual):
        assert expect == utils.prepare_url(actual)

    _t('42', '42')
    _t('http://ya.ru/test', {'service': 'http://ya.ru', 'uri': '/test'})
    _t(
        discovery.find_service('billing_docs').url + '/test',
        {'service': '@billing_docs', 'uri': '/test'},
    )
    _t(
        discovery.find_service('billing_docs').url + '/test',
        '@billing_docs/test',
    )
