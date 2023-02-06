import pytest


CHECK_FETCH_USER_LOCALE = pytest.mark.parametrize(
    'archive_api_error, select_rows_resp, order_archive_resp, exp_locale',
    [
        (True, None, [], 'eu'),
        (False, [], [], 'eu'),
        (False, [{'id': 'some_id'}], {'_id': 'some_id', 'order': {}}, 'eu'),
        (
            False,
            [{'id': 'some_id'}],
            {'_id': 'some_id', 'order': {'user_locale': 'ru'}},
            'ru',
        ),
    ],
)


@pytest.fixture
def mock_yt_locale_fetch(mockserver):
    def _impl(exp_phone_id, response_items, error=False):
        @mockserver.json_handler('/archive-api/v1/yt/select_rows')
        def _archive_api_mock(request):
            if error:
                return mockserver.make_response(status=500)

            assert request.json['query']['query_params'] == [
                (
                    '//home/taxi/unstable/replica/mongo/indexes/'
                    'order_proc/phone_id_created'
                ),
                exp_phone_id,
            ]

            return {'source': 'source', 'items': response_items}

        return _archive_api_mock

    return _impl
