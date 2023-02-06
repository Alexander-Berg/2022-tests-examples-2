import asynctest
import pytest

from eats_report_sender.services import mds3_service


@pytest.mark.parametrize(
    'request_name, status_code, stq_has_calls',
    [
        ('without_place_id', 200, True),
        ('with_place_id', 200, True),
        ('without_uuid', 400, False),
        ('without_period', 400, False),
        ('without_brand_id', 400, False),
    ],
)
async def test_should_correct_run(
        request_name,
        status_code,
        stq_has_calls,
        stq,
        web_app_client,
        load_json,
        monkeypatch,
):
    monkeypatch.setattr(
        mds3_service.MDS3Service,
        'get_files_list',
        asynctest.CoroutineMock(return_value=['file1.json', 'file2.json']),
    )
    response = await web_app_client.post(
        '/v1/report', json=load_json('request.json')[request_name],
    )
    assert response.status == status_code

    assert stq.eats_report_sender_send_report.has_calls == stq_has_calls


async def test_raise_exception_if_mds3_directory_empty(
        web_app_client, load_json, monkeypatch,
):
    monkeypatch.setattr(
        mds3_service.MDS3Service,
        'get_files_list',
        asynctest.CoroutineMock(return_value=[]),
    )
    response = await web_app_client.post(
        '/v1/report', json=load_json('request.json')['with_place_id'],
    )
    assert response.status == 400


@pytest.mark.parametrize('request_name', ['without_place_id', 'with_place_id'])
@pytest.mark.pgsql('eats_report_sender', files=['reports.sql'])
async def test_should_return_200_if_duplicate_uuid(
        request_name, web_app_client, load_json, stq,
):
    response = await web_app_client.post(
        '/v1/report', json=load_json('request.json')[request_name],
    )
    assert response.status == 200
    assert not stq.eats_report_sender_send_report.has_calls
