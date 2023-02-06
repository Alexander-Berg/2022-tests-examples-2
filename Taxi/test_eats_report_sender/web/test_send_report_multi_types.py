import asynctest
import pytest

from eats_report_sender.services import mds3_service


async def test_send_report_multi_types(
        web_app_client, load_json, stq, monkeypatch,
):
    monkeypatch.setattr(
        mds3_service.MDS3Service,
        'get_files_list',
        asynctest.CoroutineMock(return_value=['file1.json', 'file2.json']),
    )

    response = await web_app_client.post(
        '/v1/report', json=load_json('request_multi_types.json'),
    )
    assert response.status == 200
    assert stq.eats_report_sender_send_report.times_called == 2


@pytest.mark.pgsql('eats_report_sender', files=['reports_multi_types.sql'])
async def test_send_report_multi_types_only_failed(
        web_app_client, load_json, stq, monkeypatch,
):
    monkeypatch.setattr(
        mds3_service.MDS3Service,
        'get_files_list',
        asynctest.CoroutineMock(return_value=['file1.json', 'file2.json']),
    )

    response = await web_app_client.post(
        '/v1/report', json=load_json('request_multi_types.json'),
    )
    assert response.status == 200
    assert stq.eats_report_sender_send_report.times_called == 1
