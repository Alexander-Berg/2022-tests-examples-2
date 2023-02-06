import datetime as dt
import io

import pytest

from taxi.clients import mds_s3

from eats_report_sender.stq import send_accountant_reports


def _has_correct_status(pgsql, uuid, expected_status):
    with pgsql['eats_report_sender'].cursor() as cursor:
        cursor.execute(
            f'select status from accountant_reports where uuid=\'{uuid}\'',
        )
        actual_status = list(row[0] for row in cursor)[0]
    assert expected_status == actual_status


@pytest.mark.config(
    EATS_REPORT_SENDER_ACCOUNTANT_REPORT_PARTNER_INFO_MAPING={
        'weekly': {
            'client_inn': {'field_name_text': 'ИНН/УНП/BIN'},
            'client_name': {'field_name_text': 'Компания'},
            'contract_external_id': {'field_name_text': 'Договор'},
            'msk_report_period_text': {'field_name_text': 'Период'},
        },
    },
)
@pytest.mark.config(
    EATS_REPORT_SENDER_ACCOUNTANT_EMAIL_TEMPLATES={
        'weekly': {
            'body': '',
            'file_name': (
                'Weekly_report_{delivery_type}_INN{client_inn}_'
                '{msk_report_period_text}'
            ),
            'subject': (
                'Информационный отчет по выплатам от Яндекс Еды ИНН '
                '{{ client_inn }} за период {{ period }}.'
            ),
        },
    },
)
@pytest.mark.config(
    EATS_REPORT_SENDER_ACCOUNTANT_REPORT_REPORT_DATA_MAPPING={
        'weekly': {
            'order_dt': {
                'cell_format': {'num_format': 'd mmmm yyyy'},
                'field_name_text': 'Дата заказа',
                'cell_data_type': 'datetime',
            },
            'order_tm': {
                'cell_format': {},
                'field_name_text': 'Время заказа',
                'cell_data_type': 'string',
            },
            'payment_w_vat_cost_lcy': {
                'cell_format': {
                    'font_size': 11,
                    'align': 'right',
                    'num_format': '#,#.##',
                },
                'field_name_text': 'Время заказа',
                'cell_data_type': 'number',
            },
        },
    },
)
async def test_correct_send_accountant_report(
        stq3_context,
        load_json,
        mockserver,
        patch,
        pgsql,
        task_info,
        personal_mock,
        sticker_mock,
):
    @patch('eats_report_sender.components.yql_manager.YqlManager.get_rows')
    def _get_rows(file_name, parameters, title):
        response = load_json('yql_response.json')
        if 'YQL: get report data for client' in title:
            return response['report_data']
        if 'YQL: get partner info for client' in title:
            return response['partner_info']

        raise NotImplementedError()

    @patch(
        'eats_report_sender.services.mds3_service.'
        'AccReportMDS3Service.upload_file',
    )
    async def _upload(*args, **kwargs):
        return mds_s3.S3Object(
            Key=kwargs['key'], Body=kwargs['body'], ETag=None,
        )

    await send_accountant_reports.task(
        stq3_context,
        task_info,
        period='weekly',
        report_date=dt.datetime.strptime(
            '2022-07-01 00:00:00', '%Y-%m-%d %H:%M:%S',
        ),
        balance_internal_id=1,
    )
    _has_correct_status(pgsql, '1', 'success')


@pytest.mark.config(
    EATS_REPORT_SENDER_ACCOUNTANT_EMAIL_TEMPLATES={
        'weekly': {
            'body': '',
            'file_name': (
                'Weekly_report_{delivery_type}_INN{client_inn}_'
                '{msk_report_period_text}'
            ),
            'subject': (
                'Информационный отчет по выплатам от Яндекс Еды ИНН '
                '{{ client_inn }} за период {{ period }}.'
            ),
        },
    },
)
@pytest.mark.pgsql('eats_report_sender', files=['accountant_report.sql'])
async def test_correct_send_accountant_report_if_file_exist(
        stq3_context,
        load_json,
        mockserver,
        patch,
        pgsql,
        task_info,
        personal_mock,
        sticker_mock,
):
    @patch('eats_report_sender.components.yql_manager.YqlManager.get_rows')
    def _get_rows(file_name, parameters, title):
        response = load_json('yql_response.json')
        if 'YQL: get report data for client' in title:
            return response['report_data']
        if 'YQL: get partner info for client' in title:
            return response['partner_info']

        raise NotImplementedError()

    @patch(
        'eats_report_sender.services.mds3_service.'
        'AccReportMDS3Service.get_file',
    )
    async def _get(*args, **kwargs):
        s3file = io.BytesIO(b'\x01\x02')
        kwargs['body'] = s3file.read()
        return mds_s3.S3Object(
            Key=kwargs['key'], Body=kwargs['body'], ETag=None,
        )

    await send_accountant_reports.task(
        stq3_context,
        task_info,
        period='weekly',
        report_date=dt.datetime.strptime(
            '2022-07-01 00:00:00', '%Y-%m-%d %H:%M:%S',
        ),
        balance_internal_id=1,
    )
    _has_correct_status(pgsql, '1', 'success')
