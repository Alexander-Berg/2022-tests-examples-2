async def test_cannot_use_token_with_another_corp(
        state_has_debts, request_pay_debts, employee_uid, employee_login,
):
    operation_token = state_has_debts['actions']['pay_debts']['token']
    response = await request_pay_debts(
        'unknown_corp_client_id',
        employee_uid,
        employee_login,
        operation_token,
    )
    assert response.status_code == 409
    assert response.json()['code'] == 'invalid_token'


async def test_cannot_use_token_by_another_person(
        state_has_debts, request_pay_debts, corp_client_id,
):
    operation_token = state_has_debts['actions']['pay_debts']['token']
    response = await request_pay_debts(
        corp_client_id, 'another_uid', 'another_login', operation_token,
    )
    assert response.status_code == 409
    assert response.json()['code'] == 'invalid_token'
