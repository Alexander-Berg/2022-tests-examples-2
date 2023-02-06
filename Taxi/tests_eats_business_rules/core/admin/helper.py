DEFAULT_HEADERS = {'Content-Type': 'application/x-www-form-urlencoded'}


class AdminTest:
    def __init__(self):
        self._request = None

    def request(self, request):
        self._request = request
        return self

    async def run(self, taxi_eats_business_rules):
        response = await taxi_eats_business_rules.post(
            'core/v1/fine/create', json=self._request, headers=DEFAULT_HEADERS,
        )
        assert response.status_code == 200
