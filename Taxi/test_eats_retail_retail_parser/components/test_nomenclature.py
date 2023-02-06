# pylint: disable=W0612
import json

import pytest

MDS_TEST_PREFIX = '/mds_s3/eats_retail_retail_parser'


@pytest.mark.config(
    EATS_RETAIL_RETAIL_PARSER_RETRIES_SETTINGS={
        'retail_nomenclature_worker': 1,
    },
)
@pytest.mark.pgsql(
    'eats_retail_retail_parser', files=['add_retail_info_data.sql'],
)
@pytest.mark.parametrize('barcode_type', ['ean13', 'ean12', '', None])
@pytest.mark.parametrize('round_mode_epgr', ['floor', 'ceil', 'round'])
@pytest.mark.parametrize('round_mode_config', ['floor', 'ceil', 'round'])
@pytest.mark.parametrize('epgr_response_200', [True, False])
async def test_should_correct_run_with_getting_data_from_retail(
        stq3_context,
        stq3_client,
        taxi_config,
        stq_runner,
        mockserver,
        load_json,
        pgsql,
        patch,
        mock_processing,
        mock_eats_place_groups_replica,
        barcode_type,
        round_mode_epgr,
        round_mode_config,
        epgr_response_200,
):

    actual_round_mode = (
        round_mode_epgr if epgr_response_200 else round_mode_config
    )
    taxi_config.set(
        EATS_RETAIL_RETAIL_PARSER_PARSER_SETTINGS={
            'default_barcode_type': barcode_type,
            'roundMode': round_mode_config,
        },
    )

    await stq3_client.invalidate_caches()

    @mockserver.handler(f'/nomenclature/origin_place_id/composition')
    def mock_get_items(request):
        return mockserver.make_response(
            json.dumps(load_json('test_request_nomenclature.json')), 200,
        )

    @mockserver.handler('/security/oauth/token')
    def get_test_get_token(request):
        return mockserver.make_response(
            json.dumps(load_json('test_token.json')), 200,
        )

    @mock_processing('/v1/eda/integration_menu_processing/create-event')
    def create_event(request):
        assert (
            request.json['s3_link'] == 'integration/collector/nomenclature/'
            'nomenclature_place_group_id_origin_place_id.json'
        )
        assert request.query['item_id'] == 'task_uuid'
        assert request.headers['X-Idempotency-Token'] == 'parser_task_uuid'
        return {'event_id': 'task_uuid'}

    @mockserver.handler('/mds_s3', prefix=True)
    async def _mds_s3_mock(request, **kwargs):
        if request.method == 'GET':
            return mockserver.make_response(
                f'<Body></Body>', headers={'ETag': 'asdf'},
            )

        assert (
            request.path
            == f'{MDS_TEST_PREFIX}/integration/collector/nomenclature'
            f'/nomenclature_place_group_id_origin_place_id.json'
        )
        mds_data = load_json('mds_data.json')
        json_body = {}
        json_body['menu_categories'] = mds_data['menu_categories']
        json_body['menu_items'] = mds_data['menu_items'][actual_round_mode]
        json_body['place_id'] = mds_data['place_id']
        for item in json_body['menu_items']:
            if item['origin_id'] == '237440':
                item['retail_info']['barcode_type'] = barcode_type
                break
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

    assert _get_count(pgsql) == 0
    await stq_runner.eats_retail_retail_parser_nomenclature.call(
        task_id='task_id',
        args=(),
        kwargs={
            'retail_data': dict(
                place_group_id='place_group_id',
                place_id='place_id',
                brand_id='brand_id',
                task_type='nomenclature',
                forwarded_data={
                    'origin_place_id': 'origin_place_id',
                    'task_uuid': 'task_uuid',
                },
            ),
        },
    )
    assert _get_count(pgsql) == 4
    assert mock_get_items.has_calls


@pytest.mark.config(
    EATS_RETAIL_RETAIL_PARSER_RETRIES_SETTINGS={
        'retail_nomenclature_worker': 1,
    },
    EATS_RETAIL_RETAIL_PARSER_PARSER_SETTINGS={
        'brand_ids_for_paging': ['brand_id'],
        'brand_ids_limit_quantity': ['brand_id'],
        'composition_rate_limit': 2,
    },
)
@pytest.mark.pgsql(
    'eats_retail_retail_parser', files=['add_retail_info_data.sql'],
)
async def test_should_correct_run_with_getting_data_from_retail_paging(
        stq3_context,
        taxi_config,
        stq_runner,
        mockserver,
        pgsql,
        load_json,
        patch,
        mock_processing,
        mock_eats_place_groups_replica,
):
    @mockserver.handler(f'/nomenclature/origin_place_id/composition')
    def mock_get_items(request):
        return mockserver.make_response(
            json.dumps(load_json('test_request_nomenclature_paging.json')),
            200,
        )

    @mockserver.handler('/security/oauth/token')
    def get_test_get_token(request):
        return mockserver.make_response(
            json.dumps(load_json('test_token.json')), 200,
        )

    @mock_processing('/v1/eda/integration_menu_processing/create-event')
    def create_event(request):
        assert (
            request.json['s3_link'] == 'integration/collector/nomenclature/'
            'nomenclature_place_group_id_origin_place_id.json'
        )
        assert request.query['item_id'] == 'task_uuid'
        assert request.headers['X-Idempotency-Token'] == 'parser_task_uuid'
        return {'event_id': 'task_uuid'}

    @mockserver.handler('/mds_s3', prefix=True)
    async def _mds_s3_mock(request, **kwargs):
        if request.method == 'GET':
            return mockserver.make_response(
                f'<Body></Body>', headers={'ETag': 'asdf'},
            )

        assert (
            request.path
            == f'{MDS_TEST_PREFIX}/integration/collector/nomenclature'
            f'/nomenclature_place_group_id_origin_place_id.json'
        )
        json_body = load_json('mds_data_paging.json')
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

    @mock_eats_place_groups_replica('/v1/parser_info')
    async def _eats_place_groups_replica_parser_info(request, **kwargs):
        return mockserver.make_response('{}', 404)

    assert _get_count_quantity_limit(pgsql) == 0
    await stq_runner.eats_retail_retail_parser_nomenclature.call(
        task_id='task_id',
        args=(),
        kwargs={
            'retail_data': dict(
                place_group_id='place_group_id',
                place_id='place_id',
                brand_id='brand_id',
                task_type='nomenclature',
                forwarded_data={
                    'origin_place_id': 'origin_place_id',
                    'task_uuid': 'task_uuid',
                },
            ),
        },
    )
    assert _get_count_quantity_limit(pgsql) == 1

    assert mock_get_items.has_calls


def _get_count(pgsql):
    with pgsql['eats_retail_retail_parser'].cursor() as cursor:
        cursor.execute(f'select count(*) from measure_info')
        count = list(row[0] for row in cursor)[0]
    return count


def _get_count_quantity_limit(pgsql):
    with pgsql['eats_retail_retail_parser'].cursor() as cursor:
        cursor.execute(f'select count(*) from quantity_limit')
        count = list(row[0] for row in cursor)[0]
    return count
