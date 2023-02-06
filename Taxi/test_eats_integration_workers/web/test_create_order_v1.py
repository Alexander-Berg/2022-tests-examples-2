import pytest


@pytest.mark.parametrize(
    'testcase,status',
    [
        ['200', 200],
        ['404_not_existed_server', 404],
        ['400_wrong_server_format', 400],
        ['404_if_404_in_metro', 404],
        ['500_if_401_in_metro', 500],
        ['500_if_406_in_metro', 500],
        ['500_if_504_in_metro', 500],
    ],
)
async def test_should_return_correct_data(
        web_app_client, load_json, metro_mocks, testcase, status,
):
    metro_mocks(testcase)

    response = await web_app_client.post(
        '/v1/create-order', json=load_json('requests.json')[testcase],
    )
    assert response.status == status
    json_result = await response.json()
    assert json_result == load_json('responses.json')[testcase]
