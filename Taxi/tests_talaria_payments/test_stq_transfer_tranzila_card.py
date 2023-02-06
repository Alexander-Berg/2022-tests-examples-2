async def test_main(mockserver, stq_runner):
    @mockserver.json_handler(
        '/yb-trust-paysys/tranzila/transfer-tranzila-card',
    )
    def trust_mock(request):
        assert request.json == {
            'yandex_uid': 4019697866,
            'login_id': 'login_id',
            'tranzila_card_token': 'card_token',
            'tranzila_user': 'tranzila_user',
            'tranzila_terminal': 'wind3dtest',
            'service_id': 1179,
            'card_expiration_month': 11,
            'card_expiration_year': 22,
        }
        return {'card_id': 'card_id'}

    @mockserver.json_handler(
        '/talaria-misc/talaria/v1/wind-user-is-card-migrated',
    )
    def talaria_misc_mock(request):
        assert request.json == {'wind_user_ids': ['wind_user_id_1']}
        return mockserver.make_response(status=200)

    kwargs = {
        'yandex_uid': '4019697866',
        'wind_user_id': 'wind_user_id_1',
        'login_id': 'login_id',
        'tranzila_card_token': 'card_token',
        'tranzila_user': 'tranzila_user',
        'card_expiration_month': 11,
        'card_expiration_year': 22,
    }

    await stq_runner.talaria_payments_transfer_tranzila_card.call(
        task_id='task_id', kwargs=kwargs, expect_fail=False,
    )

    assert trust_mock.times_called == 1
    assert talaria_misc_mock.times_called == 1
