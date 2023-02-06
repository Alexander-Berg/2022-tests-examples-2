# flake8: noqa
# pylint: disable=W0621,E0102,R1705
import pytest


@pytest.fixture
def mock_mds(mockserver):
    @mockserver.json_handler(
        r'/mds/get-taxi/598/725bb76df6fb42b191a1db00dd9b275e',
    )
    def _redirect(request):
        return mockserver.make_response(
            '598/725bb76df6fb42b191a1db00dd9b275e', status=200,
        )


@pytest.mark.parametrize(
    ['request_params', 'expected_result', 'status_code'],
    [
        (
            {
                'countries': ['isr'],
                'status': 'pending',
                'limit': 15,
                'offset': 0,
                'sort': [{'field': 'created', 'direction': 'desc'}],
            },
            {
                'items': [{'id': '95b3c932435f4f008a635faccb6454f6'}],
                'total': 1,
                'offset': 0,
                'limit': 15,
                'sort': [{'field': 'created', 'direction': 'desc'}],
            },
            200,
        ),
        (
            {
                'countries': ['rus'],
                'status': 'accepted',
                'limit': 15,
                'offset': 0,
                'sort': [{'field': 'created', 'direction': 'desc'}],
            },
            {
                'items': [
                    {'id': '6160d53840764ca0a178f5e8437d7028'},
                    {'id': 'f4d44610f5894352817595f6311d95cc'},
                    {'id': 'b41e263a06264fd29e2286c01c1e2e70'},
                ],
                'total': 3,
                'offset': 0,
                'limit': 15,
                'sort': [{'field': 'created', 'direction': 'desc'}],
            },
            200,
        ),
        (
            {
                'countries': ['rus'],
                'status': 'rejected',
                'limit': 15,
                'offset': 0,
                'sort': [{'field': 'created', 'direction': 'desc'}],
            },
            {
                'items': [{'id': 'rejected'}],
                'total': 1,
                'offset': 0,
                'limit': 15,
                'sort': [{'field': 'created', 'direction': 'desc'}],
            },
            200,
        ),
        (
            {
                'countries': ['rus'],
                'status': 'accepted',
                'limit': 1,
                'offset': 0,
                'sort': [{'field': 'created', 'direction': 'asc'}],
            },
            {
                'items': [{'id': 'b41e263a06264fd29e2286c01c1e2e70'}],
                'total': 3,
                'offset': 0,
                'limit': 1,
                'sort': [{'field': 'created', 'direction': 'asc'}],
            },
            200,
        ),
        (
            {
                'search': '1503009020',
                'status': 'accepted',
                'limit': 1,
                'offset': 0,
                'sort': [{'field': 'created', 'direction': 'asc'}],
            },
            {
                'items': [{'id': 'b41e263a06264fd29e2286c01c1e2e70'}],
                'search': '1503009020',
                'total': 1,
                'offset': 0,
                'limit': 1,
                'sort': [{'field': 'created', 'direction': 'asc'}],
            },
            200,
        ),
        (
            {
                'countries': ['rus'],
                'search': ' oSiEi ',
                'status': 'accepted',
                'limit': 1,
                'offset': 0,
                'sort': [{'field': 'created', 'direction': 'asc'}],
            },
            {
                'items': [{'id': 'b41e263a06264fd29e2286c01c1e2e70'}],
                'search': 'oSiEi',
                'total': 2,
                'offset': 0,
                'limit': 1,
                'sort': [{'field': 'created', 'direction': 'asc'}],
            },
            200,
        ),
        (
            {
                'countries': ['rus'],
                'search': 'oSiEi',
                'status': 'badstatus',
                'limit': -1,
                'offset': -1,
                'sort': [{'field': 'badfield', 'direction': 'baddirection'}],
            },
            {
                'message': 'Some parameters are invalid',
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {
                    'reason': (
                        'Invalid value for direction: \'baddirection\' '
                        'must be one of [\'asc\', \'desc\']'
                    ),
                },
            },
            400,
        ),
        (
            {'unexistent_field': ''},
            {
                'message': 'Some parameters are invalid',
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {
                    'reason': 'Unexpected fields: [\'unexistent_field\']',
                },
            },
            400,
        ),
    ],
)
@pytest.mark.config(TVM_RULES=[{'dst': 'personal', 'src': 'corp-requests'}])
async def test_client_requests_search(
        taxi_corp_requests_web,
        mock_personal,
        mock_mds,
        request_params,
        expected_result,
        status_code,
):
    response = await taxi_corp_requests_web.post(
        '/v1/client-requests/search', json=request_params,
    )

    assert response.status == status_code

    response_data = await response.json()

    # проверяем отдельно items
    response_items = response_data.pop('items', None)
    expected_items = expected_result.pop('items', None)
    assert response_data == expected_result

    if response_items is None:
        assert response_items == expected_items
    else:
        # по сути нам в items важны лишь id.
        # Все остальные поля проверены уже в тестах на get ручку
        assert [{'id': v['id']} for v in response_items] == expected_items
