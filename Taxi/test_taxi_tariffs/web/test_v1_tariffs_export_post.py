import pytest

DATE = '2020-08-10T08:54:11.634Z'


@pytest.mark.parametrize(
    ('email', 'resp_code'),
    (
        pytest.param('untrust@us', 400, id='wrong_email'),
        pytest.param('untrust_us@yandex-team.ru', 200, id='ok_email'),
    ),
)
async def test_get_tariffs_list_csv_handle(
        web_app_client, stq, email, resp_code,
):
    response = await web_app_client.post(
        '/v1/tariffs/export',
        json={'date': DATE, 'email': email, 'zones': ['kaluga']},
    )
    assert response.status == resp_code

    if resp_code == 200:
        task = stq.get_tariffs_list_csv.next_call()

        assert task['queue'] == 'get_tariffs_list_csv'
        params = task['kwargs']
        assert params['user_email'] == 'untrust_us@yandex-team.ru'
        assert params['zones'] == ['kaluga']
        assert params['date'] == DATE
