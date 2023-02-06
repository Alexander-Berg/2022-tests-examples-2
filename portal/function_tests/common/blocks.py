# -*- coding: utf-8 -*-
import allure

from common.client import MordaClient
from common.utils import get_field


def fetch_data(morda, blocks, headers=None, cgi_params=None):
    client = MordaClient(morda)

    if cgi_params is None:
        cgi_params = dict()

    if headers is None:
        headers = dict()

    cgi_params['geo'] = morda.region
    request = client.cleanvars(blocks, params=cgi_params)

    for key in headers.keys():
        request.headers[key] = headers[key]
    response = request.send()
    with allure.step('Fetch data'):
        assert response.is_ok(), 'Failed to get cleanvars'
    return response.json()


def existance(data):
    with allure.step('Test if block exists'):
        assert data, 'Failed to get block'


def absence(data):
    with allure.step('Test if block exists'):
        assert not data, 'Failed to get block'


def check_show(data):
    with allure.step('Test if block shows'):
        assert data.get('show'), 'Show must be 1'


def no_show(data):
    with allure.step('Test if block shows'):
        assert not data.get('show'), 'Show must be 0 or absent'


def empty_elements(data):
    with allure.step('check empty'):
        assert len(data) == 0, (
                'Tabs num (' + str(len(data)) + '): must be = 0')


def count_elements(data, count):
    with allure.step('Check tabs'):
        assert len(data) >= count, (
                'Tabs num (' + str(len(data)) + '): must be >= than '+str(count))


def count_elements_range(data, _min, _max):
    with allure.step('Check tabs'):
        assert len(data) >= _min and len(data) <= _max, (
                'Tabs num (' + str(len(data)) + '): must be in [' + str(_min) + ', ' + str(_max)) + ']'


def check_href_host(data, host, key_url='href'):
    main_href = get_field(data, key_url)
    assert main_href.index(host), 'Domain must be '+host
