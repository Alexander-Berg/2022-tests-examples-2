# pylint: disable=W0612
import json

import pytest

MDS_TEST_PREFIX = '/mds_s3/eats_retail_retail_parser'


@pytest.mark.config(
    EATS_RETAIL_RETAIL_PARSER_RETRIES_SETTINGS={
        'retail_availability_worker': 1,
    },
)
@pytest.mark.pgsql(
    'eats_retail_retail_parser', files=['add_retail_info_data.sql'],
)
async def test_should_correct_run_with_getting_data_from_retail(
        stq3_context,
        taxi_config,
        stq_runner,
        mockserver,
        load_json,
        patch,
        mock_processing,
):
    @mockserver.handler('/nomenclature/origin_place_id/availability')
    def mock_get_items(request):
        return mockserver.make_response(
            json.dumps(load_json('test_request_stocks.json')), 200,
        )

    @mockserver.handler('/security/oauth/token')
    def get_test_get_token(request):
        return mockserver.make_response(
            json.dumps(load_json('test_token.json')), 200,
        )

    @mock_processing('/v1/eda/integration_menu_processing/create-event')
    def create_event(request):
        assert (
            request.json['s3_link'] == 'integration/collector/availability/'
            'availability_place_group_id_origin_place_id.json'
        )
        assert request.query['item_id'] == 'task_uuid'
        assert request.headers['X-Idempotency-Token'] == 'parser_task_uuid'
        return {'event_id': 'task_uuid'}

    @mockserver.handler('/mds_s3', prefix=True)
    async def _mds_s3_mock(request, **kwargs):
        assert (
            request.path
            == f'{MDS_TEST_PREFIX}/integration/collector/availability'
            f'/availability_place_group_id_origin_place_id.json'
        )
        json_body = load_json('mds_data.json')
        assert json_body == request.json
        return mockserver.make_response(
            f'<Body>{json.dumps(request.json)}</Body>',
            headers={'ETag': 'asdf'},
        )

    await stq_runner.eats_retail_retail_parser_availability.call(
        task_id='task_id',
        args=(),
        kwargs={
            'retail_data': dict(
                place_group_id='place_group_id',
                place_id='place_id',
                brand_id='brand_id',
                task_type='availability',
                forwarded_data={
                    'origin_place_id': 'origin_place_id',
                    'task_uuid': 'task_uuid',
                    'stock_reset_limit': 3,
                },
            ),
        },
    )

    assert mock_get_items.has_calls
