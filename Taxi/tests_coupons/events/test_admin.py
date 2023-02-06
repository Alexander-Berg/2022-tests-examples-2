import pytest


EVENTS_URL = 'admin/promocodes/events'

HEADERS = {
    'X-Yandex-Uid': '0123456789',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64)',
}


@pytest.fixture(name='mock_yql')
def _mock_yql(mockserver, load):
    class Context:
        _results_data = None

        @property
        def results_data(self):
            if self._results_data is not None:
                return self._results_data
            return load('yql_response_data.txt')

        def set_results_data(self, data):
            self._results_data = data

    context = Context()

    @mockserver.json_handler('/yql/api/v2/operations')
    def _new_operation(request):
        return {'id': 'abcde12345'}

    @mockserver.json_handler(
        r'/yql/api/v2/operations/(?P<operation_id>\w+)', regex=True,
    )
    def _operation_status(request, operation_id):
        return {'id': operation_id, 'status': 'COMPLETED'}

    @mockserver.json_handler(
        r'/yql/api/v2/operations/(?P<operation_id>\w+)/results_data',
        regex=True,
    )
    def _operation_results_data(request, operation_id):
        return mockserver.make_response(context.results_data, status=200)

    return context


async def test_no_coupon(taxi_coupons):
    response = await taxi_coupons.post(EVENTS_URL, headers=HEADERS, json={})
    assert response.status_code == 400


async def test_coupon_only(taxi_coupons, mock_yql):
    mock_yql.set_results_data('')

    response = await taxi_coupons.post(
        EVENTS_URL, headers=HEADERS, json={'coupon': 'promocode'},
    )

    assert response.status_code == 200
    assert response.json() == {'data': []}


def full_query_request():
    return {
        'coupon': 'promocode',
        'phone_id': 'abacaba123',
        'yandex_uid': '01234567890',
        'type': ['activate', 'check'],
        'moment_from': '2020-12-01T00:00:00+03:00',
        'moment_to': '2020-12-31T00:00:00+03:00',
        'limit': 10,
        'offset': 10,
    }


@pytest.mark.now('2020-12-15T11:30:00+0300')
async def test_full_query(taxi_coupons, testpoint, mock_yql):
    @testpoint('coupons_events_query')
    def check_coupons_events_query(query):
        expected_query = full_query_request()
        # TODO: remove after pagination support
        expected_query.pop('limit')
        expected_query.pop('offset')

        assert query == expected_query

    response = await taxi_coupons.post(
        EVENTS_URL, headers=HEADERS, json=full_query_request(),
    )

    assert check_coupons_events_query.times_called == 1

    assert response.status_code == 200
    assert response.json() == {
        'data': [
            {
                'moment': '2020-12-01T18:27:58.147636+03:00',
                'type': 'activate',
                'phone_id': 'abacaba123',
                'yandex_uid': '01234567890',
                'coupon': 'promocode',
                'series': {'name': 'yandextaxi'},
            },
            {
                'moment': '2020-12-02T12:33:14.873828+03:00',
                'type': 'activate',
                'phone_id': 'abacaba123',
                'yandex_uid': '01234567890',
                'coupon': 'promocode',
                'series': {'name': 'yandextaxi'},
            },
            {
                'moment': '2020-12-02T13:39:41.496468+03:00',
                'type': 'check',
                'phone_id': 'abacaba123',
                'yandex_uid': '01234567890',
                'coupon': 'promocode',
                'series': {'name': 'yandextaxi'},
            },
        ],
    }
