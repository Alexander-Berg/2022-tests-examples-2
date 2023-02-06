import pytest


HEADERS = {
    'Cookie': 'Session_id=123',
    'Content-Type': 'application/json',
    'X-Yandex-UID': '44',
}


@pytest.mark.parametrize(
    ['url', 'resp_code', 'resp'],
    [
        (f'/v1/variant/list', 200, ['v_1', 'v_2']),
        (f'/v1/variant/list?name=1', 200, ['v_1']),
        (f'/v1/variant/list?name=4', 200, []),
    ],
)
@pytest.mark.pgsql('callcenter_exams', files=['callcenter_exams.sql'])
async def test_list_by_pattern(web_app_client, url, resp_code, resp):
    response = await web_app_client.get(url, headers=HEADERS)

    assert response.status == resp_code
    data = await response.json()
    assert data['variants'] == resp
