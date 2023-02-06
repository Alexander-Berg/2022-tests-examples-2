def handler(path):
    def wrapper(func):
        return (path, func)

    return wrapper


@handler('/parks/driver-profiles/list')
def parks_01(data, request):
    offset = request.json.get('offset', 0)
    limit = request.json.get('limit', 100)
    query = request.json.get('query', {})

    park = query.get('park', {})
    park_id = park.get('id')
    park_dp = park.get('driver_profile', {})

    dp_id = park_dp.get('id')
    dp_wr = park_dp.get('work_rule_id')
    dp_ws = park_dp.get('work_status')

    parks = []
    drivers = []
    for park in data.get('parks', []):
        if park['id'] == park_id:
            parks.append(park)
            for driver in park.get('drivers', []):
                if dp_id and driver.get('id') not in dp_id:
                    continue
                if dp_wr and driver.get('work_rule_id') not in dp_wr:
                    continue
                if dp_ws and driver.get('work_status') not in dp_ws:
                    continue
                drivers.append(driver)
            break

    return {
        'limit': limit,
        'offset': offset,
        'driver_profiles': [
            {'driver_profile': {'id': driver['id']}}
            for driver in drivers[offset : offset + limit]
        ],
        'parks': [{'id': park['id']} for park in parks],
        'total': len(drivers),
    }


@handler('/fleet-parks/v1/parks/list')
def fleet_parks_01(data, request):
    query = request.json['query']
    q_park = query['park']
    q_park_id = q_park['ids']

    parks = []
    for park in data['parks']:
        if park['id'] in q_park_id:
            parks.append(park)

    return {
        'parks': [
            {
                'id': park['id'],
                'login': 'TESTSUITE-LOGIN',
                'name': 'TESTSUITE-NAME',
                'is_active': True,
                'city_id': park['city'],
                'locale': park['locale'],
                'is_billing_enabled': True,
                'is_franchising_enabled': False,
                'country_id': park['country'],
                'demo_mode': False,
            }
            for park in parks
        ],
    }


@handler('/fleet-transactions-api/v1/parks/driver-profiles/balances/list')
def fleet_transactions_api_01(data, request):
    query = request.json.get('query', {})

    park = query['park']
    park_id = park['id']
    dp_id = park['driver_profile']['ids']

    drivers = []
    for park in data['parks']:
        if park['id'] == park_id:
            for driver in park['drivers']:
                if driver['id'] not in dp_id:
                    continue
                drivers.append(driver)
            break

    return {
        'driver_profiles': [
            {
                'driver_profile_id': driver['id'],
                'balances': [
                    {
                        'accrued_at': driver['balance']['date'],
                        'total_balance': driver['balance']['amount'],
                    },
                ],
            }
            for driver in drivers
        ],
    }


@handler(
    (
        '/fleet-transactions-api'
        '/v1/parks/driver-profiles/transactions/by-platform'
    ),
)
def fleet_transactions_api_02(data, request):
    return {
        'event_at': '2020-01-01T12:00:00+03:00',
        'park_id': request.json['park_id'],
        'driver_profile_id': request.json['driver_profile_id'],
        'category_id': request.json['category_id'],
        'amount': request.json['amount'],
        'currency_code': 'XXX',
        'description': request.json['description'],
        'created_by': {'identity': 'platform'},
    }


ALL_HANDLERS = [
    parks_01,
    fleet_parks_01,
    fleet_transactions_api_01,
    fleet_transactions_api_02,
]


def all_handlers(load_yaml, mockserver):
    handlers = {}

    data = load_yaml('std.yaml')

    def add(path, func):
        handlers[path] = mockserver.json_handler(path)(
            lambda request: func(data, request),
        )

    for path, func in ALL_HANDLERS:
        add(path, func)

    return handlers
