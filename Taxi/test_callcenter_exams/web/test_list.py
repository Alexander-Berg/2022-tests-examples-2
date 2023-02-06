import pytest

HEADERS = {
    'Cookie': 'Session_id=123',
    'Content-Type': 'application/json',
    'X-Yandex-UID': '44',
}


@pytest.mark.parametrize(
    ['url', 'resp_code', 'resp'],
    [
        (f'/v1/list', 200, ['q_1', 'q_2', 'q_3', 'q_4']),
        (f'/v1/list?name=_', 200, ['q_1', 'q_2', 'q_3', 'q_4']),
        (f'/v1/list?name=3', 200, ['q_3']),
        (f'/v1/list?name=question', 200, []),
        (f'/v1/list?name=', 200, ['q_1', 'q_2', 'q_3', 'q_4']),
    ],
)
@pytest.mark.pgsql('callcenter_exams', files=['callcenter_exams.sql'])
async def test_list_by_pattern(web_app_client, url, resp_code, resp):
    response = await web_app_client.get(url, headers=HEADERS)

    assert response.status == resp_code
    data = await response.json()
    assert data['questions'] == resp
