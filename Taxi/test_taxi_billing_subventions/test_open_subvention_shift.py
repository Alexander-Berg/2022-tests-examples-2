from typing import Collection

import pytest


_TAXI_ORDER_ENABLED = {
    'BILLING_FUNCTIONS_TAXI_ORDER_MIGRATION': {
        'by_zone': {
            '__default__': {
                'enabled': [{'since': '1999-06-18T07:15:00+00:00'}],
            },
        },
    },
}
_TAXI_ORDER_TEST = {
    'BILLING_FUNCTIONS_TAXI_ORDER_MIGRATION': {
        'by_zone': {
            '__default__': {'test': [{'since': '1999-06-18T07:15:00+00:00'}]},
        },
    },
}


@pytest.mark.now('2020-09-02T00:00:00.000000+00:00')
@pytest.mark.parametrize(
    'test_data_json',
    [
        pytest.param(
            'geo_booking/valid_request.json',
            marks=pytest.mark.config(**_TAXI_ORDER_ENABLED),
        ),
        pytest.param(
            'geo_booking/rule_not_found.json',
            marks=pytest.mark.config(**_TAXI_ORDER_ENABLED),
        ),
        pytest.param(
            'geo_booking/rule_not_geo_booking.json',
            marks=pytest.mark.config(**_TAXI_ORDER_ENABLED),
        ),
        pytest.param(
            'geo_booking/compare_with_existing.json',
            marks=pytest.mark.config(**_TAXI_ORDER_TEST),
        ),
        pytest.param(
            'goal/valid_request.json',
            marks=pytest.mark.config(**_TAXI_ORDER_ENABLED),
        ),
        pytest.param(
            'goal/rule_not_found.json',
            marks=pytest.mark.config(**_TAXI_ORDER_ENABLED),
        ),
        pytest.param(
            'goal/rule_not_goal.json',
            marks=pytest.mark.config(**_TAXI_ORDER_ENABLED),
        ),
        pytest.param(
            'goal/compare_with_existing.json',
            marks=pytest.mark.config(**_TAXI_ORDER_TEST),
        ),
        pytest.param(
            'nmfg/valid_request.json',
            marks=pytest.mark.config(**_TAXI_ORDER_ENABLED),
        ),
        pytest.param(
            'nmfg/valid_request_only_required.json',
            marks=pytest.mark.config(**_TAXI_ORDER_ENABLED),
        ),
        pytest.param(
            'nmfg/rule_not_found.json',
            marks=pytest.mark.config(**_TAXI_ORDER_ENABLED),
        ),
        pytest.param(
            'nmfg/rule_not_nmfg.json',
            marks=pytest.mark.config(**_TAXI_ORDER_ENABLED),
        ),
        pytest.param(
            'nmfg/compare_with_existing.json',
            marks=pytest.mark.config(**_TAXI_ORDER_TEST),
        ),
    ],
)
async def test(
        db,
        billing_subventions_client,
        request_headers,
        stq_client_patched,
        load_json,
        test_data_json,
        docs_mock,
        random_mock,
):

    test_data = load_json(test_data_json)
    docs = docs_mock(test_data.get('existing_shift_ended'))

    request = test_data['request']
    response = await billing_subventions_client.post(
        test_data['uri'], json=request, headers=request_headers,
    )

    expected_response = test_data['expected_response']
    assert await response.json() == expected_response

    expected_create_requests = test_data['expected_create_requests']
    assert docs.create_requests == expected_create_requests

    expected_search_requests = test_data['expected_search_requests']
    assert docs.search_requests == expected_search_requests


@pytest.fixture(name='docs_mock')
def _make_docs_mock(patch):
    def _mock(existing_doc: dict = None):
        class Data:
            create_requests: Collection[dict] = []
            search_requests: Collection[dict] = []

        @patch('taxi.billing.clients.billing_docs.BillingDocsApiClient.create')
        async def _create(data, log_extra=None):
            Data.create_requests.append(data)
            return {'doc_id': 2, 'process_at': '2100-01-01T00:00:00+00:00'}

        @patch('taxi.billing.clients.billing_docs.BillingDocsApiClient.search')
        async def _search(data, log_extra=None):
            Data.search_requests.append(data)
            return existing_doc

        return Data()

    return _mock


@pytest.fixture(name='random_mock')
def _make_random_mock(patch):
    @patch('random.randint')
    def _randint(left, right):
        return 2
