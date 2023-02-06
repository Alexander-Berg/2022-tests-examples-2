import datetime
import json

import pytest


MDS_TEST_PREFIX = '/mds_s3/eats_integration_workers'


def _is_available(stock, stock_reset_limit):
    if stock is None:
        return True
    stock = int(float(stock))
    if stock_reset_limit:
        return stock >= stock_reset_limit > 0

    return stock > 0


@pytest.mark.config(
    EATS_INTEGRATION_WORKERS_METRO_PARSER_SETTINGS={
        'promoItemIds': [],
        'roundMode': 'math',
        'parse_zero_stock': True,
    },
    EATS_INTEGRATION_WORKERS_PLACE_ITEMS_SETTINGS={
        'get_items_from_database': False,
    },
)
@pytest.mark.parametrize(
    'place_id, brand_id, external_id, place_group_id, task_id, '
    'stock_reset_limit, mds_response, dev_filter, parse_zero_stock, mds_data',
    [
        [
            '123',
            '123',
            '1234',
            '1234',
            '12345',
            None,
            'with_none_stock_limit',
            {},
            True,
            'mds_data_null.json',
        ],
        [
            '123',
            '123',
            '1234',
            '1234',
            '12345',
            2,
            'with_non_zero_stock_limit',
            {},
            True,
            'mds_data_null.json',
        ],
        [
            '123',
            '123',
            '1234',
            '1234',
            '12345',
            None,
            'with_none_stock_limit',
            {},
            False,
            'mds_data.json',
        ],
        [
            '123',
            '123',
            '1234',
            '1234',
            '12345',
            2,
            'with_non_zero_stock_limit',
            {},
            False,
            'mds_data.json',
        ],
    ],
)
async def test_should_correct_run_with_getting_data_from_core(
        stq3_context,
        taxi_config,
        pgsql,
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
        mds_response,
        dev_filter,
        parse_zero_stock,
        mds_data,
):
    taxi_config.set_values(
        {
            'EATS_INTEGRATION_WORKERS_METRO_PARSER_SETTINGS': {
                'parse_zero_stock': parse_zero_stock,
            },
        },
    )

    @mock_eats_core_retail('/v1/place/items/retrieve')
    def mock_get_items(request):
        if 'cursor' in request.json:
            return load_json('eats_core_retail_get_items_2.json')

        return load_json('eats_core_retail_get_items.json')

    @mockserver.handler('/test_get_stocks')
    def _get_test_get_stocks(request):
        return mockserver.make_response(
            json.dumps(load_json('test_request_availability.json')), 200,
        )

    @mockserver.handler('/test_get_token')
    def _get_test_get_token(request):
        return mockserver.make_response(
            json.dumps(load_json('test_token.json')), 200,
        )

    @mockserver.handler('/mds_s3', prefix=True)
    async def _mds_s3_mock(request, **kwargs):
        assert (
            request.path
            == f'{MDS_TEST_PREFIX}/integration/collector/availability'
            f'/availability_{place_id}.json'
        )
        json_body = load_json(mds_data)[mds_response]
        assert json_body == request.json

        temp_data = get_place_stocks(pgsql)
        for item in json_body['items']:
            assert item['available'] == _is_available(
                temp_data[item['origin_id']], stock_reset_limit,
            )
        last_updated_at = get_last_update_stocks(pgsql, place_id)
        assert (
            datetime.datetime.now() - last_updated_at
        ) < datetime.timedelta(seconds=60)

        return mockserver.make_response(
            f'<Body>{json.dumps(request.json)}</Body>',
            headers={'ETag': 'asdf'},
        )

    await stq_runner.eats_integration_workers_availability.call(
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

    assert mock_get_items.has_calls


@pytest.mark.config(
    EATS_INTEGRATION_WORKERS_METRO_PARSER_SETTINGS={
        'promoItemIds': [],
        'roundMode': 'math',
        'parse_zero_stock': True,
    },
    EATS_INTEGRATION_WORKERS_PLACE_ITEMS_SETTINGS={
        'get_items_from_database': True,
    },
)
@pytest.mark.parametrize(
    'place_id, brand_id, external_id, place_group_id, task_id, '
    'stock_reset_limit, mds_response, dev_filter, parse_zero_stock, mds_data',
    [
        [
            '123',
            '123',
            '1234',
            '1234',
            '12345',
            None,
            'with_none_stock_limit',
            {},
            True,
            'mds_data_null.json',
        ],
        [
            '123',
            '123',
            '1234',
            '1234',
            '12345',
            2,
            'with_non_zero_stock_limit',
            {},
            True,
            'mds_data_null.json',
        ],
        [
            '123',
            '123',
            '1234',
            '1234',
            '12345',
            None,
            'with_none_stock_limit',
            {},
            False,
            'mds_data.json',
        ],
        [
            '123',
            '123',
            '1234',
            '1234',
            '12345',
            2,
            'with_non_zero_stock_limit',
            {},
            False,
            'mds_data.json',
        ],
    ],
)
@pytest.mark.pgsql(
    'eats_integration_workers',
    files=['place_items_data.sql', 'pg_eats_integration_workers.sql'],
)
async def test_should_correct_run_with_getting_data_from_database(
        stq3_context,
        taxi_config,
        stq_runner,
        pgsql,
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
        mds_response,
        dev_filter,
        parse_zero_stock,
        mds_data,
):
    taxi_config.set_values(
        {
            'EATS_INTEGRATION_WORKERS_METRO_PARSER_SETTINGS': {
                'parse_zero_stock': parse_zero_stock,
            },
        },
    )

    @mockserver.handler('/test_get_stocks')
    def _get_test_get_stocks(request):
        return mockserver.make_response(
            json.dumps(load_json('test_request_availability.json')), 200,
        )

    @mockserver.handler('/test_get_token')
    def _get_test_get_token(request):
        return mockserver.make_response(
            json.dumps(load_json('test_token.json')), 200,
        )

    @mockserver.handler('/mds_s3', prefix=True)
    async def _mds_s3_mock(request, **kwargs):
        assert (
            request.path
            == f'{MDS_TEST_PREFIX}/integration/collector/availability'
            f'/availability_{place_id}.json'
        )
        json_body = load_json(mds_data)[mds_response]
        assert json_body == request.json

        temp_data = get_place_stocks(pgsql)
        for item in json_body['items']:
            assert item['available'] == _is_available(
                temp_data[item['origin_id']], stock_reset_limit,
            )

        last_updated_at = get_last_update_stocks(pgsql, place_id)
        assert (
            datetime.datetime.now() - last_updated_at
        ) < datetime.timedelta(seconds=60)
        return mockserver.make_response(
            f'<Body>{json.dumps(request.json)}</Body>',
            headers={'ETag': 'asdf'},
        )

    await stq_runner.eats_integration_workers_availability.call(
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
    'place_id, brand_id, external_id, place_group_id, task_id, '
    'stock_reset_limit, dev_filter, menu_parser_options, '
    'parse_zero_stock, mds_data',
    [
        [
            '123',
            '123',
            '1234',
            '1234',
            '12345',
            1,
            {},
            {},
            False,
            'mds_data_new_api.json',
        ],
    ],
)
async def test_correct_run_new_api(
        stq3_context,
        taxi_config,
        pgsql,
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
        menu_parser_options,
        parse_zero_stock,
        mds_data,
):
    taxi_config.set_values(
        {
            'EATS_INTEGRATION_WORKERS_METRO_PARSER_SETTINGS': {
                'is_new_api_for_stocks': True,
            },
        },
    )

    @mockserver.handler(f'/test_get_stocks/{external_id}')
    def _get_test_get_stocks(request):
        return mockserver.make_response(
            json.dumps(load_json('test_request_nem_stocks.json')), 200,
        )

    @mockserver.handler('/test_get_token')
    def _get_test_get_token(request):
        return mockserver.make_response(
            json.dumps(load_json('test_token.json')), 200,
        )

    @mockserver.handler('/mds_s3', prefix=True)
    async def _mds_s3_mock(request, **kwargs):
        assert (
            request.path
            == f'{MDS_TEST_PREFIX}/integration/collector/availability'
            f'/availability_{place_id}.json'
        )
        json_body = load_json(mds_data)
        assert json_body == request.json
        return mockserver.make_response(
            f'<Body>{json.dumps(request.json)}</Body>',
            headers={'ETag': 'asdf'},
        )

    await stq_runner.eats_integration_workers_availability.call(
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
            'menu_parser_options': menu_parser_options,
            'last_update_stocks': None,
            'last_update_articuls': None,
            'parser_name': 'metro',
            'integration_task_id': task_id,
        },
    )


def get_place_stocks(pgsql):
    with pgsql['eats_integration_workers'].cursor() as cursor:
        cursor.execute(
            'SELECT articul, stocks FROM eats_integration_workers.place_stocks',  # noqa: F401,E501
        )
        data = {row[0]: row[1] for row in cursor}
    return data


def get_last_update_stocks(pgsql, place_id):
    with pgsql['eats_integration_workers'].cursor() as cursor:
        cursor.execute(
            f'SELECT last_update_stocks '
            f'FROM eats_integration_workers.parser_infos '
            f'where place_id=\'{place_id}\'',
        )
        last_update_stocks = [row[0] for row in cursor][0]
    return last_update_stocks
