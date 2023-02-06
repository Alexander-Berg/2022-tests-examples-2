# pylint: disable=W0612
import json

import pytest

MDS_TEST_PREFIX = '/mds_s3/eats_retail_retail_parser'


@pytest.mark.config(
    EATS_RETAIL_RETAIL_PARSER_RETRIES_SETTINGS={'task_price_worker': 1},
)
@pytest.mark.pgsql(
    'eats_retail_retail_parser',
    files=['add_retail_info_data.sql', 'fill_measure_info.sql'],
)
@pytest.mark.parametrize('round_mode_epgr', ['floor', 'ceil', 'round'])
@pytest.mark.parametrize('round_mode_config', ['floor', 'ceil', 'round'])
@pytest.mark.parametrize('epgr_response_200', [True, False])
async def test_should_correct_run_with_getting_data_from_retail(
        taxi_config,
        stq_runner,
        stq3_client,
        mockserver,
        load_json,
        mock_processing,
        mock_eats_place_groups_replica,
        round_mode_epgr,
        round_mode_config,
        epgr_response_200,
):
    actual_round_mode = (
        round_mode_epgr if epgr_response_200 else round_mode_config
    )

    @mockserver.handler(f'/nomenclature/origin_place_id/composition')
    def mock_get_items(request):
        return mockserver.make_response(
            json.dumps(load_json('test_request_prices.json')), 200,
        )

    @mockserver.handler('/security/oauth/token')
    def get_test_get_token(request):
        return mockserver.make_response(
            json.dumps(load_json('test_token.json')), 200,
        )

    @mock_processing('/v1/eda/integration_menu_processing/create-event')
    def create_event(request):
        assert (
            request.json['s3_link'] == 'integration/collector/prices/'
            'prices_place_group_id_origin_place_id.json'
        )
        assert request.query['item_id'] == 'task_uuid'
        assert request.headers['X-Idempotency-Token'] == 'parser_task_uuid'
        return {'event_id': 'task_uuid'}

    @mockserver.handler('/mds_s3', prefix=True)
    async def _mds_s3_mock(request, **kwargs):
        assert (
            request.path == f'{MDS_TEST_PREFIX}/integration/collector/prices'
            f'/prices_place_group_id_origin_place_id.json'
        )
        json_body = load_json('mds_data.json')[actual_round_mode]
        assert json_body == request.json
        return mockserver.make_response(
            f'<Body>{json.dumps(request.json)}</Body>',
            headers={'ETag': 'asdf'},
        )

    @mock_eats_place_groups_replica('/v1/parser_info')
    async def _eats_place_groups_replica_parser_info(request, **kwargs):
        if epgr_response_200:
            return mockserver.make_response(
                json.dumps(
                    {
                        'place_id': 'place_id',
                        'parser_options': {
                            'priceRoundingStrategy': round_mode_epgr,
                        },
                    },
                ),
                200,
            )
        return mockserver.make_response('{}', 404)

    taxi_config.set(
        EATS_RETAIL_RETAIL_PARSER_PARSER_SETTINGS={
            'roundMode': round_mode_config,
        },
    )

    await stq3_client.invalidate_caches()

    await stq_runner.eats_retail_retail_parser_prices.call(
        task_id='task_id',
        args=(),
        kwargs={
            'retail_data': dict(
                place_group_id='place_group_id',
                place_id='place_id',
                brand_id='brand_id',
                task_type='price',
                forwarded_data={
                    'origin_place_id': 'origin_place_id',
                    'task_uuid': 'task_uuid',
                },
            ),
        },
    )

    assert mock_get_items.has_calls


@pytest.mark.config(
    EATS_RETAIL_RETAIL_PARSER_RETRIES_SETTINGS={'task_price_worker': 1},
    EATS_RETAIL_RETAIL_PARSER_PARSER_SETTINGS={
        'brand_ids_for_paging': ['brand_id'],
    },
)
@pytest.mark.pgsql(
    'eats_retail_retail_parser',
    files=['add_retail_info_data.sql', 'fill_measure_info.sql'],
)
async def test_should_correct_run_with_getting_data_from_retail_paging(
        stq_runner,
        mockserver,
        load_json,
        mock_processing,
        mock_eats_place_groups_replica,
):
    @mockserver.handler(f'/nomenclature/origin_place_id/composition')
    def mock_get_items(request):
        return mockserver.make_response(
            json.dumps(load_json('test_request_price_paging.json')), 200,
        )

    @mockserver.handler('/security/oauth/token')
    def get_test_get_token(request):
        return mockserver.make_response(
            json.dumps(load_json('test_token.json')), 200,
        )

    @mock_processing('/v1/eda/integration_menu_processing/create-event')
    def create_event(request):
        assert (
            request.json['s3_link'] == 'integration/collector/prices/'
            'prices_place_group_id_origin_place_id.json'
        )
        assert request.query['item_id'] == 'task_uuid'
        assert request.headers['X-Idempotency-Token'] == 'parser_task_uuid'
        return {'event_id': 'task_uuid'}

    @mockserver.handler('/mds_s3', prefix=True)
    async def _mds_s3_mock(request, **kwargs):
        assert (
            request.path == f'{MDS_TEST_PREFIX}/integration/collector/prices'
            f'/prices_place_group_id_origin_place_id.json'
        )
        json_body = load_json('mds_data_paging.json')
        assert json_body == request.json
        return mockserver.make_response(
            f'<Body>{json.dumps(request.json)}</Body>',
            headers={'ETag': 'asdf'},
        )

    @mock_eats_place_groups_replica('/v1/parser_info')
    async def _eats_place_groups_replica_parser_info(request, **kwargs):
        return mockserver.make_response('{}', 404)

    await stq_runner.eats_retail_retail_parser_prices.call(
        task_id='task_id',
        args=(),
        kwargs={
            'retail_data': dict(
                place_group_id='place_group_id',
                place_id='place_id',
                brand_id='brand_id',
                task_type='price',
                forwarded_data={
                    'origin_place_id': 'origin_place_id',
                    'task_uuid': 'task_uuid',
                },
            ),
        },
    )

    assert mock_get_items.has_calls
