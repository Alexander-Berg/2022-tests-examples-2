# pylint: disable=W0612,C0103
import datetime
import json

import asynctest
import pytest

from eats_retail_auchan_parser.services import mds3_service
from eats_retail_auchan_parser.stq import nomenclature

MDS_TEST_PREFIX = '/mds_s3/eats_retail_auchan_parser'

MDS3Service = mds3_service.MDS3Service
DATE_AUCHAN_FORMAT = '%Y_%m_%d'


class TaskInfo:
    id = 'task_id'
    exec_tries = 0


@pytest.mark.config(
    EATS_RETAIL_AUCHAN_CLIENT_SETTINGS={
        'feed_url': '$mockserver/test_nomenclature',
    },
    EATS_RETAIL_AUCHAN_PARSER_DECIMAL_PRICE={'value': 'true'},
)
async def test_should_correct_run_with_getting_data_from_retail(
        stq3_context,
        taxi_config,
        mockserver,
        monkeypatch,
        load_json,
        patch,
        pgsql,
        mock_processing,
):
    current_date = datetime.datetime.now().strftime(DATE_AUCHAN_FORMAT)

    monkeypatch.setattr(
        MDS3Service,
        'get_files_list',
        asynctest.CoroutineMock(
            return_value=[
                f'stock_price/{current_date}/stock_price_123_20211018123819.json',  # noqa: F401,E501
                f'stock_price/{current_date}/stock_price_020_20211018123821.json',  # noqa: F401,E501
                f'stock_price/{current_date}/stock_price_123_20211018123820.json',  # noqa: F401,E501
            ],
        ),
    )

    monkeypatch.setattr(
        MDS3Service,
        'get_file_by_key',
        asynctest.CoroutineMock(
            return_value=json.dumps(load_json('price_stocks.json')),
        ),
    )

    @mockserver.handler(f'/test_nomenclature')
    def mock_get_items(request):
        return mockserver.make_response(
            load_json('test_request_nomenclature.json')['data'], 200,
        )

    @mock_processing('/v1/eda/integration_menu_processing/create-event')
    def create_event(request):
        assert (
            request.json['s3_link'] == 'integration/collector/nomenclature/'
            'nomenclature_place_group_id_123.json'
        )
        assert request.query['item_id'] == 'task_uuid'
        assert request.headers['X-Idempotency-Token'] == 'parser_task_uuid'
        return {'event_id': 'task_uuid'}

    @mockserver.handler('/mds_s3', prefix=True)
    async def _mds_s3_mock(request, **kwargs):
        assert (
            request.path
            == f'{MDS_TEST_PREFIX}/integration/collector/nomenclature'
            f'/nomenclature_place_group_id_123.json'
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

    task_info = TaskInfo()
    assert _get_count(pgsql) == 0
    await nomenclature.task(
        stq3_context,
        task_info,
        **{
            'retail_data': dict(
                place_group_id='place_group_id',
                place_id='place_id',
                task_type='nomenclature',
                forwarded_data={
                    'origin_place_id': '123',
                    'task_uuid': 'task_uuid',
                },
            ),
        },
    )

    assert mock_get_items.has_calls

    # Кешируется ли фид
    await nomenclature.task(
        stq3_context,
        task_info,
        **{
            'retail_data': dict(
                place_group_id='place_group_id',
                place_id='place_id',
                task_type='nomenclature',
                forwarded_data={
                    'origin_place_id': '123',
                    'task_uuid': 'task_uuid',
                },
            ),
        },
    )
    assert mock_get_items.times_called == 1


def _get_count(pgsql):
    with pgsql['eats_retail_auchan_parser'].cursor() as cursor:
        cursor.execute(f'select count(*) from measure_info')
        count = list(row[0] for row in cursor)[0]
    return count
