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

        def dump_docs(response):
            result = []
            for idx in range(len(response)):
                result.append(
                    {
                        "external_obj_id": response[idx]["external_obj_id"],
                        "kind": response[idx]["kind"],
                        "status": response[idx]["status"],
                        "support_info": response[idx]["data"]
                    }
                )
            return result

        return {
            'drop_account_id': drop_account_id,
            'dump_docs': dump_docs
        }

