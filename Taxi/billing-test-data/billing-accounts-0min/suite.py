# coding: utf8

from sibilla import test

class TestSuite(test.Suite):
    @staticmethod
    def processors():
        def drop_account_id(response):
            for idx in range(len(response)):
                # account_id can be different for different runs
                del response[idx]['account']['account_id']
            return response
        return {
            'drop_account_id': drop_account_id
        }
