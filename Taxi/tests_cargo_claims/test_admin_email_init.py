async def test_without_performer(
        taxi_cargo_claims, create_default_claim, mockserver, stq,
):
    response = await taxi_cargo_claims.post(
        f'v1/admin/claims/email/init?claim_id={create_default_claim.claim_id}',
        json={
            'idempotency_token': '100500',
            'ticket': 'TICKET-1',
            'comment': 'send again',
            'email': 'test@yandex.ru',
        },
        headers={'X-Real-Ip': '12.34.56.78', 'AcceptLanguage': 'ru'},
    )
    assert response.status_code == 400
    assert stq.cargo_claims_send_email.times_called == 0


async def test_bad_email(taxi_cargo_claims, state_controller, mockserver, stq):
    claim_info = await state_controller.apply(target_status='performer_found')
    claim_id = claim_info.claim_id

    @mockserver.json_handler('/personal/v1/emails/store')
    def _emails_store(request):
        return mockserver.make_response(
            status=400, json={'code': 'not-found', 'message': 'error'},
        )

    response = await taxi_cargo_claims.post(
        f'v1/admin/claims/email/init?claim_id={claim_id}',
        json={
            'idempotency_token': '100500',
            'ticket': 'TICKET-1',
            'comment': 'send again',
            'email': 'not_email',
        },
        headers={'X-Real-Ip': '12.34.56.78', 'AcceptLanguage': 'ru'},
    )
    assert response.status_code == 400
    assert _emails_store.times_called == 1
    assert stq.cargo_claims_send_email.times_called == 0


async def test_wrong_corp_client_id(taxi_cargo_claims, state_controller):
    claim_info = await state_controller.apply(target_status='performer_found')
    claim_id = claim_info.claim_id

    response = await taxi_cargo_claims.post(
        f'v1/admin/claims/email/init?claim_id={claim_id}&'
        f'corp_client_id=another_corp_client_id',
        json={
            'idempotency_token': '100500',
            'ticket': 'TICKET-1',
            'comment': 'send again',
            'email': 'test@yandex.ru',
        },
        headers={'X-Real-Ip': '12.34.56.78', 'AcceptLanguage': 'ru'},
    )
    assert response.status_code == 404


async def test_init_200(taxi_cargo_claims, state_controller, mockserver, stq):
    claim_info = await state_controller.apply(target_status='performer_found')
    claim_id = claim_info.claim_id

    @mockserver.json_handler('/personal/v1/emails/store')
    def _emails_store(request):
        return {'id': 'email_personal_id_1', 'value': 'test@yandex.ru'}

    response = await taxi_cargo_claims.post(
        f'v1/admin/claims/email/init?claim_id={claim_id}',
        json={
            'idempotency_token': '100500',
            'ticket': 'TICKET-1',
            'comment': 'send again',
            'email': 'test@yandex.ru',
        },
        headers={'X-Real-Ip': '12.34.56.78', 'AcceptLanguage': 'ru'},
    )
    assert response.status_code == 200
    assert _emails_store.times_called == 1

    assert stq.cargo_claims_send_email.times_called == 1
    stq_params = stq.cargo_claims_send_email.next_call()
    assert (
        stq_params['kwargs'].get('receiver_email_id') == 'email_personal_id_1'
    )
