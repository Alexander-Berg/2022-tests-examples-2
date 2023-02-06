# coding: utf8

import datetime

import aiohttp
from dateutil import parser

from sibilla.test import request


_accounts: dict = {}
_external_entity_ids: dict = {}


async def remap_account_id(query: request.Query):
    """Change old account id to new from previous query"""
    query['json']['entries'][0]['account_id'] = _accounts[
        query['json']['entries'][0]['account_id']
    ]


async def fix_balance_query(query: request.Query):
    if 'account_id' not in query['json']['accounts'][0]:
        return
    query['json']['accounts'][0]['entity_external_id'] = _external_entity_ids[
        query['json']['accounts'][0]['account_id']
    ]
    del query['json']['accounts'][0]['account_id']
    accrued_at = parser.isoparse(
        query['json']['accrued_at'][0],
    ) + datetime.timedelta(0, 60)
    query['json']['accrued_at'][0] = accrued_at.strftime(
        '%Y-%m-%dT%H:%M:%S.%fZ',
    )


async def store_account(
        query: request.Query, response: aiohttp.ClientResponse,
):
    response_data = await response.json()
    resp_acc_id = response_data['account_id']
    req_acc_id = query['json']['account_id']
    req_acc_ext_id = query['json']['entity_external_id']
    _accounts[req_acc_id] = resp_acc_id
    _external_entity_ids[resp_acc_id] = req_acc_ext_id
