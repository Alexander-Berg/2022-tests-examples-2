import pytest


async def test_stq_order_claims_for_existing_order(
        stq_runner, db_select_orders, make_order,
):
    order_nr = 'order-nr'
    order_status = 'created'

    make_order(eats_id=order_nr, order_status=order_status)

    claim_id = 'claim-id'
    corp_client_alias = 'default'
    attempt = 1

    await stq_runner.eats_subventions_order_claims.call(
        task_id='unique',
        kwargs={
            'order_nr': order_nr,
            'claim_id': claim_id,
            'corp_client_alias': corp_client_alias,
            'attempt': attempt,
        },
    )

    orders = db_select_orders()
    assert len(orders) == 1
    order = orders[0]
    assert order['eats_id'] == order_nr
    assert order['order_status'] == order_status
    assert order['claim_id'] == claim_id


async def test_stq_order_claims_for_non_existent_order(
        stq_runner, db_select_orders,
):
    order_nr = 'order-nr'
    order_default_status = 'created'
    claim_id = 'claim-id'
    corp_client_alias = 'default'
    attempt = 1

    await stq_runner.eats_subventions_order_claims.call(
        task_id='unique',
        kwargs={
            'order_nr': order_nr,
            'claim_id': claim_id,
            'corp_client_alias': corp_client_alias,
            'attempt': attempt,
        },
    )

    orders = db_select_orders()
    assert len(orders) == 1
    order = orders[0]
    assert order['eats_id'] == order_nr
    assert order['order_status'] == order_default_status
    assert order['claim_id'] == claim_id


@pytest.mark.parametrize(
    'task_claim, task_attempt', [('new-claim-id', 3), ('old-claim-id', 1)],
)
async def test_stq_order_claims_order_of_tasks(
        stq_runner, db_select_orders, make_order, task_claim, task_attempt,
):
    order_nr = 'order-nr'
    order_status = 'created'
    profile_id = 'profile-id'
    current_claim_id = 'claim-id'
    current_attempt = 2
    corp_client_alias = 'default'

    make_order(
        eats_id=order_nr,
        order_status=order_status,
        eats_profile_id=profile_id,
        claim_id=current_claim_id,
        claim_attempt=current_attempt,
        corp_client_type=corp_client_alias,
    )

    await stq_runner.eats_subventions_order_claims.call(
        task_id='unique',
        kwargs={
            'order_nr': order_nr,
            'claim_id': task_claim,
            'corp_client_alias': corp_client_alias,
            'attempt': task_attempt,
        },
    )

    orders = db_select_orders()
    assert len(orders) == 1
    order = orders[0]
    assert order['eats_id'] == order_nr
    assert order['order_status'] == order_status
    assert order['claim_attempt'] == max(current_attempt, task_attempt)
    if task_attempt > current_attempt:
        assert order['claim_id'] == task_claim
        assert order['eats_profile_id'] is None
    else:
        assert order['claim_id'] == current_claim_id
        assert order['eats_profile_id'] == profile_id
