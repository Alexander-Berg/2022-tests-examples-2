# -*- coding: utf-8 -*-
from __future__ import print_function
import logging

import allure
import pytest
import re

from common import env
from common.client import MordaClient
from common.geobase import Regions

logger = logging.getLogger(__name__)

GIANT_TTV = 1010
DEFAULT_GIANT_TTV = 101010

DEFAULT_GIANT_TTV_BLOCKS = [
	'topnews',
	'covid_gallery',
	'stocks',
	'weather',
	'tv',
	'informers',
	'bridges',
	'teaser_appsearch'
]

def gen_params(app_info):
	params = []

	ab_flags = [None, 'giant_ttv=' + str(GIANT_TTV), 'default_giant_ttv=' + str(DEFAULT_GIANT_TTV)]
	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 YaBrowser/20.3.2.282 (beta) Yowser/2.5 Safari/537.36'
	geos = [Regions.MOSCOW, Regions.SAINT_PETERSBURG]
	for platform, versions in app_info.iteritems():
		params.extend([
			dict(
				app_version=version,
				app_platform=platform,
				geo=geo,
				lang='ru-RU',
				uuid='0f730a00ff8a443ea2db355519bdd290',
				ab_flags=ab,
				processAssist='1',
				informersCard='2',
				zen_extensions='true'
			)
			for version in versions
			for ab in ab_flags
			for geo in geos
		])
	return params

app_info = {
	'android': ['20090200', '20080200'],
}

def test_params():
	return gen_params(app_info=app_info)

def check_ttv(block_id, ttv, expected, exclusion=False):
	message = 'Block \'' + block_id + '\' has wrong ttv ' + str(ttv)
	if exclusion:
		assert ttv not in expected, message
	else:
		assert ttv in expected, message

@allure.feature('api_search_v2', 'giant_ttv')
@allure.story('Check giant_ttv')
@pytest.mark.parametrize('params', test_params())
def test_giant_ttv(params):
	client = MordaClient(env=env.morda_env())
	response = client.api_search_2(**params).send()

	assert response.is_ok(), 'Failed to get api_search response'
	response = response.json()

	ab_flag = params['ab_flags']
	if not ab_flag:
		for block in response.get('block'):
			check_ttv(block.get('id'), block.get('ttv'), [GIANT_TTV, DEFAULT_GIANT_TTV], True)
	elif (ab_flag.startswith('giant_ttv')):
		for block in response.get('block'):
			check_ttv(block.get('id'), block.get('ttv'), [GIANT_TTV])
	elif (ab_flag.startswith('default_giant_ttv')):
		for block in response.get('block'):
			if block.get('id') in DEFAULT_GIANT_TTV_BLOCKS:
				check_ttv(block.get('id'), block.get('ttv'), [DEFAULT_GIANT_TTV])
			else:
				check_ttv(block.get('id'), block.get('ttv'), [DEFAULT_GIANT_TTV], True)

