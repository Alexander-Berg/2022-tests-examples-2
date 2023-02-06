from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_get('/v1/clients/by_revision/', _clients_by_revision)
        self.router.add_get(
            '/v1/contracts/by_revision/', _contracts_by_revision,
        )
        self.router.add_get('/v1/balances/by_revision/', _balances_by_revision)
        self.router.add_post(
            '/v2/balances/by_revision/', _v2_balances_by_revision,
        )


_CLIENTS = [
    {'park_id': '999011', 'client_id': '29593786', 'revision': 1},
    {'park_id': '999012', 'client_id': '29593787', 'revision': 2},
    {'park_id': '999013', 'client_id': '29593788', 'revision': 3},
    {'park_id': '111666', 'client_id': '48976234', 'revision': 4},
    {'park_id': '100504', 'client_id': '43872693', 'revision': 5},
    {'park_id': '111500', 'client_id': '97483434', 'revision': 6},
    {'park_id': '111501', 'client_id': '19376671', 'revision': 7},
    {'park_id': '111502', 'client_id': '19376672', 'revision': 8},
    {'park_id': '111503', 'client_id': '19376673', 'revision': 9},
]
_CONTRACTS = [
    {
        'ID': 553919,
        'client_id': '29593786',
        'type': 'GENERAL',
        'status': 'ACTIVE',
        'CURRENCY': 'RUR',
        'NETTING': 1,
        'NETTING_PCT': '',
        'SERVICES': [128, 124, 111],
        'PAYMENT_TYPE': 2,
        'IS_ACTIVE': 1,
        'CONTRACT_TYPE': 0,
        'revision': 1,
    },
    {
        'ID': 281899,
        'client_id': '29593787',
        'type': 'GENERAL',
        'IS_ACTIVE': 1,
        'CURRENCY': 'RUR',
        'NETTING': 1,
        'SERVICES': [128, 124, 111],
        'status': 'ACTIVE',
        'PAYMENT_TYPE': 2,
        'CONTRACT_TYPE': 0,
        'revision': 2,
    },
    {
        'ID': 281900,
        'client_id': '29593788',
        'type': 'GENERAL',
        'IS_ACTIVE': 1,
        'CURRENCY': 'RUR',
        'NETTING': 1,
        'SERVICES': [128, 124, 111],
        'status': 'ACTIVE',
        'PAYMENT_TYPE': 2,
        'CONTRACT_TYPE': 0,
        'revision': 3,
    },
    {
        'ID': 283898,
        'client_id': '29593788',
        'type': 'GENERAL',
        'IS_ACTIVE': 1,
        'CURRENCY': 'RUR',
        'NETTING': 1,
        'SERVICES': [128, 124, 111],
        'status': 'ACTIVE',
        'PAYMENT_TYPE': 2,
        'CONTRACT_TYPE': 0,
        'revision': 4,
    },
    {
        'ID': 283897,
        'client_id': '19376671',
        'type': 'GENERAL',
        'IS_ACTIVE': 1,
        'CURRENCY': 'RUR',
        'NETTING': 1,
        'SERVICES': [128, 124, 111],
        'status': 'ACTIVE',
        'PAYMENT_TYPE': 2,
        'CONTRACT_TYPE': 0,
        'revision': 5,
    },
    {
        'ID': 283899,
        'client_id': '19376672',
        'type': 'GENERAL',
        'IS_ACTIVE': 1,
        'CURRENCY': 'RUR',
        'NETTING': 1,
        'SERVICES': [128, 124, 111],
        'status': 'ACTIVE',
        'PAYMENT_TYPE': 2,
        'CONTRACT_TYPE': 0,
        'revision': 5,
    },
    {
        'ID': 283900,
        'client_id': '19376673',
        'type': 'GENERAL',
        'IS_ACTIVE': 0,
        'CURRENCY': 'RUR',
        'NETTING': 1,
        'SERVICES': [128, 124, 111],
        'status': 'INACTIVE',
        'PAYMENT_TYPE': 2,
        'CONTRACT_TYPE': 0,
        'revision': 6,
    },
]
_BALANCES = [
    {
        'ContractID': 553918,
        'Balance': '0',
        'CommissionToPay': None,
        'NettingLastDt': '2020-05-15 00:00:00',
        'revision': 1,
    },
    {
        'ContractID': 281899,
        'Balance': '0',
        'CommissionToPay': None,
        'NettingLastDt': None,
        'revision': 2,
    },
    {
        'ContractID': 281900,
        'Balance': '0',
        'CommissionToPay': None,
        'NettingLastDt': None,
        'revision': 3,
    },
    {
        'ContractID': 28387,
        'Balance': '0',
        'CommissionToPay': None,
        'NettingLastDt': None,
        'revision': 4,
    },
    {
        'ContractID': 283898,
        'Balance': '0',
        'CommissionToPay': None,
        'NettingLastDt': None,
        'revision': 4,
    },
    {
        'ContractID': 283899,
        'Balance': '0',
        'CommissionToPay': None,
        'NettingLastDt': None,
        'revision': 5,
    },
    {
        'ContractID': 283900,
        'Balance': '0',
        'CommissionToPay': None,
        'NettingLastDt': None,
        'revision': 6,
    },
]


async def _make_response(request, field, items):
    if request.method == 'POST':
        body = await request.json()
        revision = int(body['revision'])
        limit = int(body['limit'])
    else:
        revision = int(request.query['revision'])
        limit = int(request.query['limit'])
    items_for_response = [
        item for item in items if item['revision'] > revision
    ][:limit]
    return web.json_response(
        {
            field: [item for item in items_for_response],
            'max_revision': (
                max(item['revision'] for item in items_for_response)
                if items_for_response
                else 0
            ),
        },
    )


async def _clients_by_revision(request):
    return await _make_response(request, 'clients', _CLIENTS)


async def _contracts_by_revision(request):
    return await _make_response(request, 'contracts', _CONTRACTS)


async def _balances_by_revision(request):
    return await _make_response(request, 'balances', _BALANCES)


async def _v2_balances_by_revision(request):
    return await _make_response(request, 'balances', [])
