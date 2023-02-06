from tests_corp_billing import util


class Service:
    def __init__(self):
        self._accs = {}
        self._balances = {}
        self._next_id = 1

    def set_balance_at(self, account, accrued_at, balance):
        self.create_acc(account)
        key = util.account_to_tuple(account)
        if key not in self._balances:
            self._balances[key] = {}

        accrued_at = util.to_timestamp(accrued_at).replace(microsecond=0)
        self._balances[key][accrued_at] = util.normalize_money(balance)

    def create_acc(self, account):
        key = util.account_to_tuple(account)
        if key not in self._accs:
            entity = account.get('entity')
            entity = entity or account['entity_external_id']
            agreement = account.get('agreement') or account['agreement_id']
            acc = {
                'account_id': self._next_id,
                'entity_external_id': entity,
                'agreement_id': agreement,
                'currency': account['currency'],
                'sub_account': account['sub_account'],
            }
            self._accs[key] = acc
            self._next_id += 1
        return self._accs[key]

    def get_balances(self, req_body):
        stamps = list(sorted(map(util.to_timestamp, req_body['accrued_at'])))

        entries = []
        for acc in req_body['accounts']:
            key = util.account_to_tuple(acc)
            acc = self._accs.get(key)
            if not acc:
                continue

            entries.append({'account': acc, 'balances': []})

            balances_dict = self._balances.get(key, {})
            balances = list(sorted(balances_dict.items()))
            for accrued_at in stamps:
                entries[-1]['balances'].append(
                    {
                        'accrued_at': util.to_timestring(accrued_at),
                        'balance': util.normalize_money(0),
                        'last_created': '2020-01-01T12:00:00.000+00:00',
                        'last_entry_id': 12345678,
                    },
                )
                for balance_at, balance in balances:
                    if balance_at >= accrued_at:
                        break
                    entries[-1]['balances'][-1]['balance'] = balance

        return {'entries': entries}
