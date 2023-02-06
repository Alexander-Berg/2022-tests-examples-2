async def test_suggest_inn(
        taxi_cargo_payments,
        default_corp_client_id,
        mock_corp_api,
        billing_replication_contract,
        billing_replication_person,
):
    """
      Basic use-case of /suggest-inn handle.
    """
    inn = '0123456788'
    billing_replication_person.inn = inn

    response = await taxi_cargo_payments.post(
        'api/b2b/cargo-payments/v1/suggest-inn',
        headers={'X-B2B-Client-Id': default_corp_client_id},
    )

    assert response.json()['autofill_inn'] == inn
    assert response.json()['client_inns'] == [inn]
