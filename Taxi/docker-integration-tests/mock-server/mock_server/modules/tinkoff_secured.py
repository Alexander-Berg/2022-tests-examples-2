from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_post(
            r'/api/v1/card/{ucid}/spend-limit', self.spend_limit,
        )
        self.router.add_post(
            r'/api/v1/card/{ucid}/cash-limit', self.cash_limit,
        )
        self.router.add_get('/api/v3/bank-accounts', self.get_bank_accounts)
        self.router.add_get(r'/api/v1/card/{ucid}/limits', self.limits)
        self.card_spend_limits = {}
        self.card_spend_remains = {}
        self.card_cash_limits = {}

    async def spend_limit(self, request):
        cid = int(request.match_info['ucid'])
        data = await request.json()
        self.card_spend_limits[cid] = data['limitValue']
        self.card_spend_remains[cid] = data['limitValue']

        return web.json_response()

    async def cash_limit(self, request):
        cid = int(request.match_info['ucid'])
        self.card_cash_limits[cid] = 0
        return web.json_response()

    async def limits(self, request):
        cid = int(request.match_info['ucid'])

        if (
                cid not in self.card_spend_limits
                or cid not in self.card_cash_limits
        ):
            return web.Response(status=404)
        return web.json_response(
            {
                'ucid': cid,
                'spendLimit': {
                    'limitPeriod': 'IRREGULAR',
                    'limitValue': self.card_spend_limits[cid],
                    'limitRemain': self.card_spend_remains[cid],
                },
                'cashLimit': {
                    'limitPeriod': 'IRREGULAR',
                    'limitValue': 0,
                    'limitRemain': 0,
                },
            },
        )

    async def get_bank_accounts(self, _):
        return web.json_response(
            [
                {
                    'accountNumber': '1',
                    'name': 'name',
                    'currency': 'RUB',
                    'bankBik': '123456',
                    'accountType': 'account_type',
                    'activationDate': '20.10.2020',
                    'balance': {
                        'otb': 900,
                        'authorized': 900,
                        'pendingPayments': 100,
                        'pendingRequisitions': 100,
                    },
                },
            ],
        )
