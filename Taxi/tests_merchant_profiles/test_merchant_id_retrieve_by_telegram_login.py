import pytest


@pytest.mark.config(
    MERCHANT_PROFILES_TELEGRAM_LOGIN_PD_IDS={
        'vkusvill_login_pd_id': 'merchant-id-1',
        'pyatorechka_login_pd_id': 'merchant-id-2',
        'shaverma_login_pd_id': 'merchant-id-3',
    },
)
@pytest.mark.parametrize(
    'telegram_login_pd_id, status, merchant_id',
    [
        pytest.param('vkusvill_login_pd_id', 200, 'merchant-id-1'),
        pytest.param('rolex_login_pd_id', 404, None),
        pytest.param('shaverma_login_pd_id', 200, 'merchant-id-3'),
    ],
)
async def test_merchant_id_retrieve(
        taxi_merchant_profiles,
        load_json,
        telegram_login_pd_id,
        status,
        merchant_id,
):
    response = await taxi_merchant_profiles.get(
        '/merchant/v1/merchant-profiles/id/retrieve_by_telegram_login_pd_id',
        params={'telegram_login_pd_id': telegram_login_pd_id},
    )

    assert response.status == status

    response200 = load_json('response200.json')
    response404 = load_json('response404.json')

    if status == 200:
        response200['merchant_id'] = response200['merchant_id'].format(
            merchant_id,
        )
        assert response.json() == response200
    else:
        response404['message'] = response404['message'].format(
            telegram_login_pd_id,
        )
        assert response.json() == response404
