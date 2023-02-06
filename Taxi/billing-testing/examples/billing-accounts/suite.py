# coding: utf8
from typing import Dict
from typing import List

from sibilla import test


class TestSuite(test.Suite):
    @staticmethod
    def processors():
        def drop_account_id(response: List[Dict]):
            for _, item in enumerate(response):
                # account_id can be different for different runs
                del item['account']['account_id']
            return response

        return {'drop_account_id': drop_account_id}
