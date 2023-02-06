import aiohttp.web

from tests_corp_billing_orders import date_utils
from tests_corp_billing_orders import search_utils


class Service:
    def __init__(self, keep_history):
        self.requests = []
        self._keep_history = keep_history
        self._id_serial = 0
        self._accounts_data_index = {}
        self._accounts_id_index = {}
        self._accounts = []
        self._registred_entitites = set()

    def create_entity_handler(self, request):
        self._save_request(request)
        data = request.json
        self._registred_entitites.add(data['external_id'])

        response = data.copy()
        response['created'] = date_utils.to_timestring()
        return response

    def create_account_handler(self, request):
        self._save_request(request)
        data = request.json

        if data['entity_external_id'] not in self._registred_entitites:
            return aiohttp.web.json_response(status=400)

        accounts = self.find_accounts(data)
        if accounts:
            return accounts[0]

        return self._add_account(data)

    def search_accounts_handler(self, request):
        self._save_request(request)
        data = request.json
        if 'account_id' in data:
            acc = self.find_by_id(data['account_id'])
            return [acc] if acc else []
        return self.find_accounts(data)

    def find_accounts(self, acc):
        accounts = []
        for first in search_utils.get_values_by_key(
                self._accounts_data_index, acc['entity_external_id'],
        ):
            for second in search_utils.get_values_by_key(
                    first, acc.get('agreement_id'),
            ):
                for third in search_utils.get_values_by_key(
                        second, acc.get('currency'),
                ):
                    for index in search_utils.get_values_by_key(
                            third, acc.get('sub_account'),
                    ):
                        accounts.append(self._accounts[index])
        return accounts

    def find_by_id(self, account_id):
        response = None
        if account_id in self._accounts_id_index:
            index = self._accounts_id_index[account_id]
            response = self._accounts[index]
        return response

    def _add_account(self, data):
        acc = data.copy()
        acc['account_id'] = self._next_id()
        acc['opened'] = date_utils.to_timestring()

        self._accounts.append(acc)
        index = len(self._accounts) - 1

        self._accounts_id_index[acc['account_id']] = index
        self._accounts_data_index.setdefault(
            acc['entity_external_id'], {},
        ).setdefault(acc['agreement_id'], {}).setdefault(acc['currency'], {})[
            acc['sub_account']
        ] = (
            index
        )

        return acc

    def _next_id(self):
        self._id_serial += 1
        return self._id_serial

    def _save_request(self, request):
        if self._keep_history:
            self.requests.append(request)
