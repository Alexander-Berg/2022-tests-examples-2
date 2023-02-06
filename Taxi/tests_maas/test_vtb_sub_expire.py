import pytest


@pytest.mark.pgsql('maas', files=['subscriptions.sql'])
async def test_expire_disabled(get_subscription_by_id, taxi_maas):

    subscription_before = get_subscription_by_id('maas_sub_id')

    response = await taxi_maas.post(
        '/vtb/v1/sub/expire', json={'maas_sub_id': 'maas_sub_id'},
    )
    assert response.status == 422
    response_body = response.json()
    assert response_body['errorCode'] == '10'
    assert response_body['errorCause'] == 'sub_expire_is_not_enabled'

    subscription_after = get_subscription_by_id('maas_sub_id')
    assert subscription_after == subscription_before
