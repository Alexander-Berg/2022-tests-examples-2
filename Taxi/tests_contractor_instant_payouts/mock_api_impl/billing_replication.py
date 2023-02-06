NAME = 'billing-replication'


def _make_contract(contract):
    return {
        'ID': contract['id'],
        'client_id': contract['bcid'],
        'type': contract['type'],
        'PERSON_ID': contract['person_id'],
        'IS_ACTIVE': int(contract['is_active']),
        'SERVICES': contract['services'],
    }


def _make_person(person):
    return {
        'ID': str(person['id']),
        'client_id': person['bcid'],
        'INN': person['inn'],
    }


def _handler_contract(context):
    def handler(request):
        q_bcid = request.query['client_id']
        q_type = request.query['type']

        contracts = []
        for contract in context['taxi']['contracts']:
            if contract['bcid'] != q_bcid:
                continue
            if contract['type'] != q_type:
                continue
            contracts.append(contract)

        return [_make_contract(contract) for contract in contracts]

    return handler


def _handler_person(context):
    def handler(request):
        q_bcid = request.query['client_id']

        persons = []
        for person in context['taxi']['persons']:
            if person['bcid'] != q_bcid:
                continue
            persons.append(person)

        return [_make_person(person) for person in persons]

    return handler


def setup(context, mockserver):
    mocks = {}

    def add(url, handler):
        mocks[url] = mockserver.json_handler('/' + NAME + url + '/')(handler)

    add('/contract', _handler_contract(context))
    add('/person', _handler_person(context))

    return mocks
