import pytest


@pytest.mark.servicetest
async def test_create_comments(web_app_client, stq):
    assert not stq.startrack_reports_create_comment.has_calls
    response = await web_app_client.post(
        '/v2/create_comments/',
        json={
            'action': 'action',
            'data': {},
            'tickets': [{'key': 'TAXIRATE-35'}],
            'template_kwargs': {
                'time': '2019-01-01T03:00:00+03:00',
                'login': 'ydemidenko',
            },
        },
        headers={'Accept-Language': 'ru'},
    )
    assert response.status == 200
    assert stq.startrack_reports_create_comment.times_called == 1
