from tests_bank_communications import utils


async def test_ok_do_nothing(taxi_bank_communications):
    response = await taxi_bank_communications.post(
        '/v1/communications/v1/push_unsubscribe', json={'uuid': 'uuid'},
    )

    assert response.status_code == 200


async def test_deactivate_old_sub(taxi_bank_communications, pgsql):
    utils.insert_push_subscription(pgsql, 'uuid', 'ACTIVE')
    response = await taxi_bank_communications.post(
        '/v1/communications/v1/push_unsubscribe', json={'uuid': 'uuid'},
    )
    assert response.status_code == 200

    last_sub = utils.get_last_subscriptions(pgsql, 'uuid')
    assert last_sub[0]['status'] == 'INACTIVE'
