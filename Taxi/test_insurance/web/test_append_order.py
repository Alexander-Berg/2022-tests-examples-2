import datetime

import pytest

EXPECTED_REPORT_LINE = (
    b'1\t1234\t2020-01-02\t2020-01-02T13:00:00.611000Z'
    b'\t2020-01-03\t2020-01-03T04:00:00.802000Z\t4\n'
)


@pytest.fixture
def mock_client_mds(mockserver, patch):
    def _mock_mds(old_content, new_content):
        @patch('taxi.clients.mds.MDSClient.download')
        async def _download(*args, **kwargs):
            return old_content

        @patch('taxi.clients.mds.MDSClient.upload')
        async def _upload(f_obj, *args, **kwargs):
            actual = f_obj.read()
            assert actual == new_content
            return 'new_mds_key'

        @patch('taxi.clients.mds.MDSClient.remove')
        async def _remove(*args, **kwargs):
            pass

    return _mock_mds


@pytest.mark.now('2020-10-17T10:05:00+03:00')
async def test_simple(
        web_app_client,
        mockserver,
        load_json,
        mock_client_mds,  # pylint: disable=W0621
        mongodb,
):
    mock_client_mds(b'OLD_CONTENT\n', b'OLD_CONTENT\n' + EXPECTED_REPORT_LINE)

    @mockserver.json_handler('/archive-api/v1/yt/lookup_rows')
    def _handler(request):
        return load_json('archive-api-response.json')

    @mockserver.json_handler('/taxi-tariffs/v1/tariff_settings/list')
    def _tariff_zones(http_request):
        if http_request.query.get('cursor'):
            return {'zones': [], 'next_cursor': ''}
        return load_json('response_tariff.json')

    response = await web_app_client.post(
        '/internal/append_order', params={'order_id': '1234'},
    )
    assert response.status == 200
    content = await response.json()
    assert content == {
        'insurer_id': '1',
        'report_date': '2020-01-03',
        'mds_url': '$mockserver/mds/get-taxi/new_mds_key',
    }

    export_info = mongodb.insured_orders_export.find_one(
        {'insurer_id': '1', 'date': datetime.datetime(2020, 1, 3)},
    )
    assert export_info['mds_key'] == 'new_mds_key'

    orders_count = mongodb.insured_orders_counts.find_one(
        {'insurer_id': '1', 'date': datetime.datetime(2020, 1, 3)},
    )
    assert orders_count['orders_count'] == 1
