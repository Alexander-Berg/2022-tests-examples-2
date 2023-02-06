# coding: utf8

import asyncio
import dateutil.parser
import datetime

from sibilla import test
from taxi.stq import client
from taxi import secdist

STQ_BILLING_ROLLUP_BALANCES_QUEUE = 'billing_rollup_balances'
SINGLE_TASK_ID = '1'

STQ_CLIENTS = {
    STQ_BILLING_ROLLUP_BALANCES_QUEUE,
}


class TestSuite(test.TestSuite):
    def before_suite(self):
        self.accounts = {}
        self.external_entity_ids = {}
        client.init(secdist.load_secdist(), clients=STQ_CLIENTS)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(client.put(queue=STQ_BILLING_ROLLUP_BALANCES_QUEUE,
                                task_id=SINGLE_TASK_ID, eta=0,
                                kwargs={'log_extra': None}, loop=loop))

    def remap_account_id(self, request):
        request['account_id'] = self.accounts[request['account_id']]

    def fix_balance_query(self, request):
        request['accounts'][0]['entity_external_id'] = self.external_entity_ids[
            request['accounts'][0]['account_id']]
        del request['accounts'][0]['account_id']
        accrued_at = dateutil.parser.isoparse(request['accrued_at'][0]) + datetime.timedelta(0, 60)
        request['accrued_at'][0] = accrued_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    def store_account(self, request, response):
        self.accounts[request['account_id']] = response['account_id']
        self.external_entity_ids[response['account_id']] = request[
            'entity_external_id']

    def print_balance_query(self, request, response):
        for idx in range(len(response)):
            # account_id can be different for different runs
            del response[idx]['account']['account_id']
