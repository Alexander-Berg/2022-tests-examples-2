import hashlib

import aiohttp.web
import pytest

from fleet_reports.generated.stq3 import stq_context as context
from fleet_reports.stq import vat_taximeter


@pytest.mark.client_experiments3(
    consumer='fleet/reports/park_branding',
    config_name='fleet_park_branding',
    args=[
        {
            'name': 'park_id',
            'type': 'string',
            'value': '1b0512eca97c4a1bbe53b50bdc0d5179',
        },
        {'name': 'park_city', 'type': 'string', 'value': 'tel_aviv'},
        {'name': 'park_country', 'type': 'string', 'value': 'izr'},
        {'name': 'fleet_type', 'type': 'string', 'value': 'yandex'},
    ],
    value={'brand_id': 'Yango'},
)
@pytest.mark.pgsql('fleet_reports', files=('fleet_reports.sql',))
async def test_success(
        stq3_context: context.Context, load_json, mockserver, patch,
):
    @mockserver.json_handler('/fleet-reports-storage/internal/v1/file/upload')
    async def _mock_do(request):
        return aiohttp.web.json_response({})

    @patch('fleet_reports.stq.vat_taximeter._make_pdf_report')
    async def _make_pdf_report(stq3_context, report_data, locale, brand):
        assert report_data.park_id == '1b0512eca97c4a1bbe53b50bdc0d5179'
        assert report_data.driver_id == '7750dd3fc1104b6298bcf2483db20b50'
        assert locale == 'en'
        assert brand == 'Yango'
        return b'PDF-1.5'

    operation_id = hashlib.md5(
        ':'.join(
            [
                '1b0512eca97c4a1bbe53b50bdc0d5179',
                '7750dd3fc1104b6298bcf2483db20b50',
                '2021-04-01',
            ],
        ).encode(),
    ).hexdigest()

    await vat_taximeter.task(
        stq3_context,
        '1b0512eca97c4a1bbe53b50bdc0d5179',
        'tel_aviv',
        'izr',
        'yandex',
        '7750dd3fc1104b6298bcf2483db20b50',
        operation_id,
        '2021-04-01',
        'en',
    )
