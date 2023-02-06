import datetime

import pytest

from testsuite.utils import http

from selfemployed.entities import nalogru_taxpayer
from selfemployed.fns import client_models
from selfemployed.generated.cron import run_cron
from selfemployed.pg_repo import deserializers


@pytest.mark.pgsql('selfemployed_main', files=['main.sql'])
async def test_fetch_taxpayer_status(se_cron_context, mock_personal, patch):
    to_pd = {
        '+70000000001': 'pp1',
        '+70000000002': 'pp2',
        '+70000000003': 'pp3',
        '000000000001': 'ip1',
        '000000000002': 'ip2',
        '000000000003': 'ip3',
    }
    from_pd = {to_pd[value]: value for value in to_pd}

    @mock_personal('/v1/tins/store')
    async def _store_inn_pd(request: http.Request):
        inn = request.json['value']
        return {'value': inn, 'id': to_pd[inn]}

    @mock_personal('/v1/tins/retrieve')
    async def _retrieve_inn_pd(request: http.Request):
        inn_pd_id = request.json['id']
        return {'value': from_pd[inn_pd_id], 'id': inn_pd_id}

    @mock_personal('/v1/phones/store')
    async def _store_phone_pd(request: http.Request):
        phone = request.json['value']
        return {'value': phone, 'id': to_pd[phone]}

    @mock_personal('/v1/phones/retrieve')
    async def _retrieve_phone_pd(request: http.Request):
        phone_pd_id = request.json['id']
        return {'value': from_pd[phone_pd_id], 'id': phone_pd_id}

    @patch('selfemployed.fns.client.Client.get_taxpayer_status_v2')
    async def _get_taxpayer_status_v2(inn_normalized: str):
        return inn_normalized

    @patch('selfemployed.fns.client.Client.get_taxpayer_status_response_v2')
    async def _get_taxpayer_status_response_v2(msg_id: str):
        if msg_id == '000000000001':
            phone = '+70000000001'
        elif msg_id == '000000000002':
            phone = '+70000000002'
        elif msg_id == '000000000003':
            phone = '+70000000003'
        else:
            raise KeyError(msg_id)

        return client_models.TaxpayerStatus(
            first_name='F',
            second_name='L',
            middle_name='M',
            registration_time=datetime.datetime.fromisoformat(
                '2022-06-12 12:00:00+03:00',
            ),
            region_oktmo_code='123456',
            phone=phone,
            oksm_code='643',
        )

    await run_cron.main(
        ['selfemployed.crontasks.fetch_taxpayer_status', '-t', '0'],
    )

    taxpayer_data = await se_cron_context.pg.main_master.fetch(
        'SELECT * FROM se.taxpayer_status_cache ORDER BY inn_pd_id',
    )

    result = [
        deserializers.deserialize_taxpayer_status(taxpayer_status)
        for taxpayer_status in taxpayer_data
    ]

    assert result == [
        nalogru_taxpayer.TaxpayerStatus(
            inn_pd_id='ip1',
            first_name='F',
            second_name='L',
            middle_name='M',
            registration_time=datetime.datetime.fromisoformat(
                '2022-06-12 12:00:00+03:00',
            ),
            region_oktmo_code='123456',
            phone_pd_id='pp1',
            oksm_code='678',
            activities=[],
        ),
        nalogru_taxpayer.TaxpayerStatus(
            inn_pd_id='ip2',
            first_name='F',
            second_name='L',
            middle_name='M',
            registration_time=datetime.datetime.fromisoformat(
                '2022-06-12 12:00:00+03:00',
            ),
            region_oktmo_code='123456',
            phone_pd_id='pp2',
            oksm_code='643',
            activities=None,
        ),
        nalogru_taxpayer.TaxpayerStatus(
            inn_pd_id='ip3',
            first_name='F',
            second_name='L',
            middle_name='M',
            registration_time=datetime.datetime.fromisoformat(
                '2022-06-12 12:00:00+03:00',
            ),
            region_oktmo_code='123456',
            phone_pd_id='pp3',
            oksm_code='643',
            activities=None,
        ),
    ]
