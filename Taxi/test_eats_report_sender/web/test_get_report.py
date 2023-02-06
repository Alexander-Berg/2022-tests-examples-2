import pytest


@pytest.mark.parametrize(
    ('uuid', 'status_code', 'expected_response'),
    [
        (
            'uuid1',
            200,
            {
                'id': 1,
                'uuid': 'uuid1',
                'brand_id': 'brand_id2',
                'created_at': '2021-06-21T03:00:00+03:00',
                'period': 'daily',
                'status': 'in_progress',
                'type': 'sftp',
                'report_type': 'test_report_type',
                'updated_at': '2021-06-22T03:00:00+03:00',
            },
        ),
        ('not_existed', 404, None),
    ],
)
@pytest.mark.pgsql('eats_report_sender', files=['reports.sql'])
async def test_should_correct_get_report(
        uuid, status_code, expected_response, load_json, web_app_client,
):
    response = await web_app_client.get('/v1/report', params={'uuid': uuid})
    assert response.status == status_code
    if expected_response:
        response_json = await response.json()
        assert response_json == expected_response


async def test_400_get_report_without_params(web_app_client):
    response = await web_app_client.get('/v1/report')
    assert response.status == 400
