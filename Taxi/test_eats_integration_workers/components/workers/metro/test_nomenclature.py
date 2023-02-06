import json

import pytest

from taxi.stq import async_worker_ng

from eats_integration_workers.stq import nomenclature

MDS_TEST_PREFIX = '/mds_s3/eats_integration_workers'


@pytest.mark.config(
    EATS_INTEGRATION_WORKERS_METRO_PARSER_SETTINGS={
        'promoItemIds': [],
        'roundMode': 'math',
        'isActiveDevFilter': True,
        'is_visible_filtered': False,
    },
    EATS_INTEGRATION_WORKERS_ENABLE_DEV_FILTERS={'metro': True},
)
@pytest.mark.parametrize(
    'place_id, brand_id, external_id, place_group_id, task_id, '
    'stock_reset_limit, dev_filter_name',
    [['123', '123', '1234', '1234', '12345', 1, 'dev_filter.json']],
)
@pytest.mark.pgsql('eats_integration_workers', files=['content_filters.sql'])
async def test_should_correct_run(
        stq_runner,
        mockserver,
        load_json,
        patch,
        place_id,
        brand_id,
        external_id,
        place_group_id,
        task_id,
        stock_reset_limit,
        dev_filter_name,
):
    @mockserver.handler('/test_get_nomenclature')
    def _get_test_get_nomenclature(request):
        return mockserver.make_response(
            load_json('test_request_nomenclature.json')['data'], 200,
        )

    @mockserver.handler('/test_get_stocks')
    def _get_test_get_stocks(request):
        return mockserver.make_response(
            json.dumps(load_json('test_request_stocks.json')), 200,
        )

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
            request.path
            == f'{MDS_TEST_PREFIX}/integration/collector/nomenclature'
            f'/nomenclature_{place_id}.json'
        )
        json_body = load_json('mds_data.json')

        assert json_body == request.json

        data = (
            json.dumps(request.json)
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
        )
        return mockserver.make_response(
            f'<Body>{data}</Body>', headers={'ETag': 'asdf'},
        )

    await stq_runner.eats_integration_workers_nomenclature.call(
        task_id=task_id,
        args=(),
        kwargs={
            'id': place_id,
            'place_id': place_id,
            'external_id': external_id,
            'place_group_id': place_group_id,
            'brand_id': brand_id,
            'stock_reset_limit': stock_reset_limit,
            'dev_filter': load_json(dev_filter_name),
            'menu_parser_options': {},
            'last_update_stocks': None,
            'last_update_articuls': None,
            'parser_name': 'metro',
            'integration_task_id': task_id,
        },
    )


@pytest.mark.config(
    EATS_INTEGRATION_WORKERS_METRO_PARSER_SETTINGS={
        'promoItemIds': [],
        'roundMode': 'math',
        'isActiveDevFilter': True,
        'is_visible_filtered': True,
    },
    EATS_INTEGRATION_WORKERS_ENABLE_DEV_FILTERS={'metro': True},
)
@pytest.mark.parametrize(
    'place_id, brand_id, external_id, place_group_id, task_id, '
    'stock_reset_limit, dev_filter_name',
    [['123', '123', '1234', '1234', '12345', 1, 'dev_filter.json']],
)
@pytest.mark.pgsql('eats_integration_workers', files=['content_filters.sql'])
async def test_should_correct_run_is_visible_filtered(
        stq3_context,
        # stq_runner,
        mockserver,
        load_json,
        patch,
        place_id,
        brand_id,
        external_id,
        place_group_id,
        task_id,
        stock_reset_limit,
        dev_filter_name,
):
    @mockserver.handler('/test_get_nomenclature')
    def _get_test_get_nomenclature(request):
        return mockserver.make_response(
            load_json('test_request_nomenclature.json')['data'], 200,
        )

    @mockserver.handler('/test_get_stocks')
    def _get_test_get_stocks(request):
        return mockserver.make_response(
            json.dumps(load_json('test_request_stocks.json')), 200,
        )

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
            request.path
            == f'{MDS_TEST_PREFIX}/integration/collector/nomenclature'
            f'/nomenclature_{place_id}.json'
        )
        json_body = load_json('mds_data_is_non_filtered.json')

        assert json_body == request.json

        data = (
            json.dumps(request.json)
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
        )
        return mockserver.make_response(
            f'<Body>{data}</Body>', headers={'ETag': 'asdf'},
        )

    task_info = async_worker_ng.TaskInfo(
        id='1', exec_tries=0, reschedule_counter=1, queue='',
    )

    await nomenclature.task(
        stq3_context,
        task_info,
        **{
            'id': place_id,
            'place_id': place_id,
            'external_id': external_id,
            'place_group_id': place_group_id,
            'brand_id': brand_id,
            'stock_reset_limit': stock_reset_limit,
            'dev_filter': load_json(dev_filter_name),
            'menu_parser_options': {},
            'last_update_stocks': None,
            'last_update_articuls': None,
            'parser_name': 'metro',
            'integration_task_id': task_id,
        },
    )
