# coding: utf8

from sibilla import test

class TestSuite(test.Suite):

    @staticmethod
    def processors():

        def drop_account_id(response):
            for item in response:
                # account_id can be different for different runs
                del item['account']['account_id']
            return response

        def sanity_accounts(response):
            # 1. remove all unfit sub-accounts with zero balance
            idx4kill = [
                ix 
                for ix in range(len(response))
                if response[ix]['account']['sub_account'].startswith('unfit/')
                and float(response[ix]['balances'][0]['balance']) == 0.0
            ]
            for ix in reversed(idx4kill):
                response.pop(ix)
            # 2. remove all floating ids whose not significat to accounting
            for item in response:
                del item['account']['account_id']
                del item['account']['agreement_id']
            # 3. sort output dataset for convenient comparison in the future
            response.sort(key=lambda x: [
                x['account']['entity_external_id'],
                x['account']['sub_account'],
                x['balances'][0]['balance'],
            ])
            return response

        return {
            'drop_account_id': drop_account_id,
            'sanity_accounts': sanity_accounts,
        }

