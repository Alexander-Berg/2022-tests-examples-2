import json

import pytest

MDS_TEST_PREFIX = '/mds_s3/eats_integration_workers'


@pytest.mark.parametrize(
    'place_id, brand_id, external_id, place_group_id,'
    ' task_id, stock_reset_limit, dev_filter',
    [['123', '123', '1234', '1234', '12345', 1, {}]],
)
@pytest.mark.config(
    EATS_INTEGRATION_WORKERS_PLACE_ITEMS_SETTINGS={
        'get_items_from_database': False,
    },
)
async def test_should_correct_run_with_getting_data_from_core(
        stq3_context,
        stq_runner,
        mock_eats_core_retail,
        mockserver,
        load_json,
        patch,
        place_id,
        brand_id,
        external_id,
        place_group_id,
        task_id,
        stock_reset_limit,
        dev_filter,
):
    @mock_eats_core_retail('/v1/place/items/retrieve')
    def mock_get_items(request):
        if 'cursor' in request.json:
            return load_json('eats_core_retail_get_items_2.json')

        return load_json('eats_core_retail_get_items.json')

    @mockserver.handler('/test_get_prices')
    def _get_test_get_prices(request):
        return mockserver.make_response(
            json.dumps(load_json('test_request_prices.json')), 200,
        )

    @mockserver.handler('/test_get_token')
    def _get_test_get_token(request):
        return mockserver.make_response(
            json.dumps(load_json('test_token.json')), 200,
        )

    @mockserver.handler('/mds_s3', prefix=True)
    async def _mds_s3_mock(request, **kwargs):
        assert (
            request.path == f'{MDS_TEST_PREFIX}/integration/collector/prices'
            f'/prices_{place_id}.json'
        )
        json_body = load_json('mds_data.json')

        assert json_body == request.json
        return mockserver.make_response(
            f'<Body>{json.dumps(request.json)}</Body>',
            headers={'ETag': 'asdf'},
        )

    await stq_runner.eats_integration_workers_price.call(
        task_id=task_id,
        args=(),
        kwargs={
            'id': place_id,
            'place_id': place_id,
            'external_id': external_id,
            'place_group_id': place_group_id,
            'brand_id': brand_id,
            'stock_reset_limit': stock_reset_limit,
            'menu_parser_options': {},
            'last_update_stocks': None,
            'last_update_articuls': None,
            'dev_filter': dev_filter,
            'parser_name': 'metro',
            'integration_task_id': task_id,
        },
    )
    assert mock_get_items.has_calls


@pytest.mark.parametrize(
    'place_id, brand_id, external_id, place_group_id, '
    'task_id, stock_reset_limit, dev_filter',
    [['123', '123', '1234', '1234', '12345', 1, {}]],
)
@pytest.mark.config(
    EATS_INTEGRATION_WORKERS_PLACE_ITEMS_SETTINGS={
        'get_items_from_database': True,
    },
)
@pytest.mark.pgsql('eats_integration_workers', files=['place_items_data.sql'])
async def test_should_correct_run_with_getting_data_from_database(
        stq3_context,
        stq_runner,
        mock_eats_core_retail,
        mockserver,
        load_json,
        patch,
        place_id,
        brand_id,
        external_id,
        place_group_id,
        task_id,
        stock_reset_limit,
        dev_filter,
):
    @mockserver.handler('/test_get_prices')
    def _get_test_get_prices(request):
        return mockserver.make_response(
            json.dumps(load_json('test_request_prices.json')), 200,
        )

    @mockserver.handler('/test_get_token')
    def _get_test_get_token(request):
        return mockserver.make_response(
            json.dumps(load_json('test_token.json')), 200,
        )

    @mockserver.handler('/mds_s3', prefix=True)
    async def _mds_s3_mock(request, **kwargs):
        assert (
            request.path == f'{MDS_TEST_PREFIX}/integration/collector/prices'
            f'/prices_{place_id}.json'
        )
        json_body = load_json('mds_data.json')

        assert json_body == request.json
        return mockserver.make_response(
            f'<Body>{json.dumps(request.json)}</Body>',
            headers={'ETag': 'asdf'},
        )

    await stq_runner.eats_integration_workers_price.call(
        task_id=task_id,
        args=(),
        kwargs={
            'id': place_id,
            'place_id': place_id,
            'external_id': external_id,
            'place_group_id': place_group_id,
            'brand_id': brand_id,
            'stock_reset_limit': stock_reset_limit,
            'dev_filter': dev_filter,
            'menu_parser_options': {},
            'last_update_stocks': None,
            'last_update_articuls': None,
            'parser_name': 'metro',
            'integration_task_id': task_id,
        },
    )


@pytest.mark.parametrize(
    'place_id, brand_id, external_id, place_group_id, '
    'task_id, stock_reset_limit, dev_filter',
    [['123', '123', '1234', '1234', '12345', 1, {}]],
)
@pytest.mark.config(
    EATS_INTEGRATION_WORKERS_PLACE_ITEMS_SETTINGS={
        'get_items_from_database': True,
    },
    EATS_INTEGRATION_WORKERS_METRO_PARSER_SETTINGS={
        'use_new_method_for_prices': True,
    },
)
@pytest.mark.pgsql('eats_integration_workers', files=['place_items_data.sql'])
async def test_should_correct_run_with_getting_data_from_database_new_method(
        stq3_context,
        stq_runner,
        mock_eats_core_retail,
        mockserver,
        load_json,
        patch,
        place_id,
        brand_id,
        external_id,
        place_group_id,
        task_id,
        stock_reset_limit,
        dev_filter,
):
    @mockserver.handler('/test_get_prices')
    def _get_test_get_prices(request):
        return mockserver.make_response(
            json.dumps(load_json('test_request_prices_new_method.json')), 200,
        )

    @mockserver.handler('/test_get_token')
    def _get_test_get_token(request):
        return mockserver.make_response(
            json.dumps(load_json('test_token.json')), 200,
        )

    @mockserver.handler('/mds_s3', prefix=True)
    async def _mds_s3_mock(request, **kwargs):
        assert (
            request.path == f'{MDS_TEST_PREFIX}/integration/collector/prices'
            f'/prices_{place_id}.json'
        )
        json_body = load_json('mds_data.json')

        assert json_body == request.json
        return mockserver.make_response(
            f'<Body>{json.dumps(request.json)}</Body>',
            headers={'ETag': 'asdf'},
        )

    await stq_runner.eats_integration_workers_price.call(
        task_id=task_id,
        args=(),
        kwargs={
            'id': place_id,
            'place_id': place_id,
            'external_id': external_id,
            'place_group_id': place_group_id,
            'brand_id': brand_id,
            'stock_reset_limit': stock_reset_limit,
            'dev_filter': dev_filter,
            'menu_parser_options': {},
            'last_update_stocks': None,
            'last_update_articuls': None,
            'parser_name': 'metro',
            'integration_task_id': task_id,
        },
    )
