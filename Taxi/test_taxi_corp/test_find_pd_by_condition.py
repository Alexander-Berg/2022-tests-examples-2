import pytest

from taxi_corp.util import personal_data


@pytest.mark.parametrize(
    ['config_value', 'expected_find_pd_calls', 'target_field'],
    [
        (personal_data.RETURN_CORP_PD, 0, 'email'),
        (personal_data.READ_BOTH_RETURN_CORP_PD, 1, 'email'),
        (personal_data.READ_BOTH_RETURN_EXT_PD, 1, 'email'),
        (personal_data.RETURN_EXT_PD, 1, 'email'),
    ],
)
async def test_find_pd_by_condition(
        taxi_corp_real_auth_client,
        patch,
        config_value,
        expected_find_pd_calls,
        target_field,
):

    config = taxi_corp_real_auth_client.server.app.config
    config.CORP_READ_PD_CONDITION = config_value

    item = {'_id': 'cool_id', 'email': 'lol@ya.ru', 'email_id': 'lol_email_id'}

    @patch('taxi_corp.util.personal_data.retrieve')
    async def _find(*args, **kwargs):
        return 'lol@ya.ru'

    app = taxi_corp_real_auth_client.server.app
    find_result = await personal_data.find_pd_by_condition(app, item, 'email')

    assert item[target_field] == find_result
    assert len(_find.calls) == expected_find_pd_calls
