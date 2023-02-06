# pylint: disable=C0103,W0612
import datetime
import json

import asynctest

from eats_retail_auchan_parser.services import mds3_service
from eats_retail_auchan_parser.stq import availability

MDS_TEST_PREFIX = '/mds_s3/eats_retail_auchan_parser'

MDS3Service = mds3_service.MDS3Service
DATE_AUCHAN_FORMAT = '%Y_%m_%d'


class TaskInfo:
    id = 'task_id'
    exec_tries = 0


async def test_should_correct_run_with_getting_data_from_retail(
        stq3_context,
        taxi_config,
        stq_runner,
        mockserver,
        monkeypatch,
        load_json,
        patch,
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

    @mock_processing('/v1/eda/integration_menu_processing/create-event')
    def create_event(request):
        assert (
            request.json['s3_link'] == 'integration/collector/availability/'
            'availability_place_group_id_123.json'
        )
        assert request.query['item_id'] == 'task_uuid'
        assert request.headers['X-Idempotency-Token'] == 'parser_task_uuid'
        return {'event_id': 'task_uuid'}

    @mockserver.handler('/mds_s3', prefix=True)
    async def _mds_s3_mock(request, **kwargs):
        assert (
            request.path
            == f'{MDS_TEST_PREFIX}/integration/collector/availability'
            f'/availability_place_group_id_123.json'
        )
        json_body = load_json('mds.json')
        assert json_body == request.json
        return mockserver.make_response(
            f'<Body>{json.dumps(request.json)}</Body>',
            headers={'ETag': 'asdf'},
        )

    task_info = TaskInfo()
    await availability.task(
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
                    'stock_reset_limit': 3,
                },
            ),
        },
    )
